# -*- coding: utf-8 -*-
"""
_fix_20261106.py — 2026-11-06 数据修正脚本（幂等）
背景：westock MCP 未暴露 → CLI 采集 1067 items 注入成功，但 mcp_inject 污染复现（与 11-05 同型）：
  ① CLI 错期数值覆盖历史已审计事件（US_CPI/PPI 2026xxxx、EU_FF_*、US_FF_* 等）
  ② run_daily 模式重生成回滚日期/时间修正（ISM 11-4 23:00、ADP 21:15、EU CPI flash 18:00、耐用品与新屋 10-27）
处理：
  A. 从 HEAD 全对象还原 23 个被污染历史事件（diff vs HEAD 逐字段核验所得）
  B. 保留 US_JOBLESS_CLAIMS_20261105 的 previous/forecast 新填充，source 还原 DOL，
     回填昨晚已发布初请 actual=18.9（Web 多源验证）
  C. 只重生成 JS，不再运行 run_daily（顺序铁律）
"""
import json
import subprocess
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')

# A. 历史污染事件：全对象还原为 HEAD 版本（2026-11-06 diff vs HEAD 核验清单）
RESTORE_IDS = [
    "US_PPI_20260114",
    "US_NFP_20260206",
    "US_CPI_20260311", "US_CORE_CPI_20260311",
    "US_CPI_20260512", "US_CORE_CPI_20260512",
    "US_FF_JOLTS_Job_Openings_20260630",
    "EU_FF_Core_CPI_Flash_Estimate_y_y_20260701",
    "EU_FF_PPI_m_m_20260706",
    "US_FF_Core_PPI_m_m_20260715",
    "EU_FF_Final_Core_CPI_y_y_20260717",
    "US_CPI_20260812", "US_CORE_CPI_20260812",
    "US_PPI_20260910",
    "US_CPI_20260911", "US_CORE_CPI_20260911",
    "EU_CPI_FLASH_20261002",
    "US_PPI_20261015",
    "US_DURABLE_GOODS_20261026", "US_NEW_HOME_SALES_20261026",
    "US_ISM_SERVICES_20261103",
    "US_ADP_20261104",
    "EU_CPI_FLASH_20261104",
]

# B. 初请失业金回填（昨晚 21:30 BJS 已发布，westock 尚未更新）
BACKFILL = {
    "US_JOBLESS_CLAIMS_20261105": {
        "actual": "18.9",
        "forecast": "19.6",
        "previous": "19.5",
        "source": "Department of Labor",
        "status": "released",
        "notes": " | 2026-11-06回填: 截至10/31当周初请18.9万低于预期(预期19.6万金十口径,CLI预期19.5),前值由19.4修正为19.5; 续请171.8万小幅高于预期(预期171); 证券时报(人民财讯/新华财经)+腾讯新闻(金十) 2源✅",
    },
}


def main():
    head_json = subprocess.run(
        ["git", "show", "HEAD:data/calendar.json"],
        capture_output=True, text=True, encoding="utf-8", cwd=SCRIPTS_DIR,
    ).stdout
    head_events = {e["id"]: e for e in json.loads(head_json)["events"]}

    with open(CAL, encoding="utf-8") as f:
        cal = json.load(f)
    idx = {e["id"]: e for e in cal["events"]}

    n_restore = 0
    for eid in RESTORE_IDS:
        cur, old = idx.get(eid), head_events.get(eid)
        if cur is None or old is None:
            print("restore skip (missing):", eid)
            continue
        if json.dumps(cur, sort_keys=True, ensure_ascii=False) != json.dumps(old, sort_keys=True, ensure_ascii=False):
            pos = cal["events"].index(cur)
            cal["events"][pos] = json.loads(json.dumps(old, ensure_ascii=False))
            idx[eid] = cal["events"][pos]
            print("restored:", eid)
            n_restore += 1

    n_bf = 0
    for eid, upd in BACKFILL.items():
        e = idx.get(eid)
        if e is None:
            print("backfill skip (missing):", eid)
            continue
        notes = upd.pop("notes")
        for k, v in upd.items():
            if e.get(k) != v:
                print(f"{eid}: {k} {e.get(k)} -> {v}")
                e[k] = v
        if notes not in (e.get("notes") or ""):
            e["notes"] = (e.get("notes") or "") + notes
        n_bf += 1

    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(cal, f, ensure_ascii=False, indent=2)

    # 回读断言（写盘后重读）
    with open(CAL, encoding="utf-8") as f:
        chk = {e["id"]: e for e in json.load(f)["events"]}
    for eid in RESTORE_IDS:
        if eid in chk and eid in head_events:
            assert json.dumps(chk[eid], sort_keys=True, ensure_ascii=False) == json.dumps(head_events[eid], sort_keys=True, ensure_ascii=False), f"restore assert fail: {eid}"
    bf = chk["US_JOBLESS_CLAIMS_20261105"]
    assert bf["actual"] == "18.9" and bf["status"] == "released" and bf["source"] == "Department of Labor"
    assert chk["US_ISM_SERVICES_20261103"]["release_date"] == "2026-11-04"
    assert chk["US_ADP_20261104"]["release_time"] == "21:15" and chk["US_ADP_20261104"]["actual"] == "8.6"
    assert chk["EU_CPI_FLASH_20261104"]["release_time"] == "18:00" and chk["EU_CPI_FLASH_20261104"]["actual"] == "4.0"
    print(f"restore={n_restore} backfill={n_bf} — asserts OK")

    generate_js(load_calendar())
    print("JS regenerated (no run_daily)")


if __name__ == "__main__":
    main()
