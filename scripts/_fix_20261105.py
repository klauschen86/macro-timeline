# -*- coding: utf-8 -*-
"""
_fix_20261105.py — 2026-11-05 数据修正脚本（幂等）
背景：今日 westock MCP 未暴露 → CLI 采集 1055 items 注入成功，但产生两类污染：
  ① mcp_inject 将 CLI 错期数值覆盖到历史已审计事件（CPI/PPI/GDP 环比污染，notes 中均有此前审计记录）
  ② run_daily 模式重生成回滚了 11-04 commit 的日期时间修正（ISM/ADP/EU CPI flash/耐用品/新屋）
处理：
  A. 从 HEAD 还原 18 个历史污染事件（全对象还原）
  B. 日期/时间字段从 HEAD 还原，随后回填昨晚已发布的 3 个 actual（Web 多源验证）：
     - US_ADP_20261104: actual 8.6（预期6.9万金十口径/新华财经6.5/财联社6.7，前值9万；新华财经+证券时报+财联社+21经济 多源✅）
     - EU_CPI_FLASH_20261104: actual 4.0（预期4.0✅/前值3.8，核心2.5持平，能源+20.8%；新华社+中国经济网+新华财经 多源✅）
     - CN_CAIXIN_SERVICES_PMI_20261104: actual 50.8（预期51.7未达⚠️/前值51.6，意外回落三个月最低；Bloomberg/RatingDog 声明）
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

# A. 历史污染事件：全对象还原为 HEAD 版本
RESTORE_IDS = [
    "US_PPI_20260414",
    "US_CPI_20260512", "US_CORE_CPI_20260512",
    "EU_FF_Final_CPI_y_y_20260617", "EU_FF_Final_Core_CPI_y_y_20260617",
    "EU_FF_Core_CPI_Flash_Estimate_y_y_20260701",
    "EU_FF_PPI_m_m_20260706",
    "US_FF_Core_CPI_m_m_20260714", "US_FF_Core_PPI_m_m_20260715",
    "US_CPI_20260812", "US_CORE_CPI_20260812",
    "EU_CPI_FLASH_20260901",
    "US_PPI_20260910",
    "US_CPI_20260911", "US_CORE_CPI_20260911",
    "US_CPI_20261014", "US_CORE_CPI_20261014",
    "US_GDP_ADV_20261029",
]

# B1. 仅还原日期/时间等字段（保留后续回填 actual）
FIELD_RESTORE = {
    "US_ISM_SERVICES_20261103": {"release_date": "2026-11-04", "release_time": "23:00"},
    "US_DURABLE_GOODS_20261026": {"release_date": "2026-10-27"},
    "US_NEW_HOME_SALES_20261026": {"release_date": "2026-10-27"},
    "US_ADP_20261104": {"release_time": "21:15", "forecast": "6.9", "previous": 9.0},
    "EU_CPI_FLASH_20261104": {"release_time": "18:00", "forecast": "4.0", "previous": 3.8},
    "CN_CAIXIN_SERVICES_PMI_20261104": {},
}

# B2. 昨晚发布回填（多源验证）
BACKFILL = {
    "US_ADP_20261104": {
        "actual": "8.6", "status": "released",
        "notes": " | 2026-11-05回填: 10月ADP新增8.6万超预期(预期6.9万金十口径/新华财经6.5/财联社6.7,前值9万连续第2月反弹); 新版ADP报告重结构不宜作非农前瞻(新华财经); 就业集中教育医疗/休闲酒店/交运,专业商业服务-2.7万连续3月收缩(AI替代); 中枢回落至7万附近,高盛:白领岗位收缩为主线; 中期选举落地稀释数据影响(新华财经+证券时报+财联社+21经济 4源✅)",
    },
    "EU_CPI_FLASH_20261104": {
        "actual": "4.0", "status": "released",
        "notes": " | 2026-11-05回填: 欧元区10月CPI初值同比4.0%符合预期(前值3.8,三年最高); 核心2.5%与9月持平=上行全靠能源(+20.8% vs 9月18.9%); 分国别分化: 德2.8%回落/法3.8%升/意5.6%大升/西4.9%; 德央行行长Nagel: ECB 12月很可能需加息(新华社+中国经济网+新华财经 3源✅)",
    },
    "CN_CAIXIN_SERVICES_PMI_20261104": {
        "actual": "50.8", "forecast": "51.7", "status": "released",
        "notes": " | 2026-11-05回填: 10月财新/RatingDog服务业PMI 50.8意外回落(预期51.7未达⚠️/前值51.6,三个月最低,7月以来首次放缓); 新业务流入仍较快但产能制约致增速放缓,投入成本涨幅加快+企业下调售价; 官方非制造业商务活动指数50.0持平临界点(服务业50.0/-0.2pct,建筑业48.0/-2.3pct); 综合PMI 49.7(Bloomberg/RatingDog官方声明+贵州省政府发展研究中心转发统计局 2源✅)",
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
            # 原位替换，保持列表顺序
            pos = cal["events"].index(cur)
            cal["events"][pos] = json.loads(json.dumps(old, ensure_ascii=False))
            idx[eid] = cal["events"][pos]
            print("restored:", eid)
            n_restore += 1

    n_field = 0
    for eid, fields in FIELD_RESTORE.items():
        e = idx.get(eid)
        if e is None:
            print("field-restore skip (missing):", eid)
            continue
        for k, v in fields.items():
            if e.get(k) != v:
                print(f"{eid}: {k} {e.get(k)} -> {v}")
                e[k] = v
                n_field += 1

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
    assert chk["US_ADP_20261104"]["actual"] == "8.6" and chk["US_ADP_20261104"]["release_time"] == "21:15"
    assert chk["EU_CPI_FLASH_20261104"]["actual"] == "4.0" and chk["EU_CPI_FLASH_20261104"]["release_time"] == "18:00"
    assert chk["CN_CAIXIN_SERVICES_PMI_20261104"]["actual"] == "50.8" and chk["CN_CAIXIN_SERVICES_PMI_20261104"]["status"] == "released"
    assert chk["US_ISM_SERVICES_20261103"]["release_date"] == "2026-11-04"
    print(f"restore={n_restore} field_fix={n_field} backfill={n_bf} — asserts OK")

    generate_js(load_calendar())
    print("JS regenerated (no run_daily)")


if __name__ == "__main__":
    main()
