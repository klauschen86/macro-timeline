# -*- coding: utf-8 -*-
"""
_fix_20261030.py — 2026-10-30 回填脚本（幂等）
回填 10-29 晚发布的 4 项美国数据 + 10-30 早日本工业产出
数据来源：网络多源交叉验证（新华社/中新社/新华财经/证券时报/新浪7x24/华尔街见闻）
另修正 mcp_inject 模糊匹配污染：GDP价格指数(2.3/3.5/6.1) 错配到 GDP初值(年化环比)
"""
import json
import os

CAL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "calendar.json")

# (event_id, updates_dict)
FIXES = [
    {
        "id": "US_GDP_ADV_20261029",
        "actual": "3.4",
        "forecast": "3.2",
        "previous": "2.2",
        "status": "released",
        "notes_append": " | 2026-10-30回填: Q3实际GDP年化季率初值+3.4%超预期(预期3.2/Q2前值2.2,五个月最大增幅口径存注); 个人消费+3.8%拉动2.52pct, 非住宅固投+12.7%(AI投资)拉动1.78pct, 私人库存拉动1.61pct, 净出口拖累3.32pct(进口+19.7%); ⚠️修正mcp_inject模糊匹配污染: '美国第三季度GDP价格指数季率初值'(2.3/3.5/6.1,平减指数类衍生指标)错配顶替本事件, actual/fc/prev全部重置; 多源✅中新社10-29 + 新华财经10-29 20:33 + 证券时报"
    },
    {
        "id": "US_PCE_20261029",
        "actual": "3.6",
        "forecast": "3.6",
        "previous": "3.4",
        "status": "released",
        "notes_append": " | 2026-10-30回填: 9月PCE物价指数同比3.6%(符合预期, 前值3.4, 能源价格驱动反弹); 环比0.5%符合预期(前值0.3); 个人支出月率0.5%略低预期0.6; 与Q3 GDP同日发布(BEA合并发布); 双源✅新华财经10-29 19:50 + 每经财经日报10-30"
    },
    {
        "id": "US_PCE_CORE_20261029",
        "actual": "3.1",
        "forecast": "3.1",
        "previous": "3.0",
        "status": "released",
        "notes_append": " | 2026-10-30回填: 9月核心PCE同比3.1%(符合预期, 前值3.0, 续创高位); 环比0.3%符合预期(前值0.2上修至0.3); Q3核心PCE年化季率初值2.5%(预期2.4/前值3.3)降温但月度同比仍高; 数据后CME 12月加息25bp概率~83%; 双源✅新华财经10-29 20:35 + 证券时报10-29"
    },
    {
        "id": "JP_INDUSTRIAL_20261030",
        "actual": "2.2",
        "forecast": "1.2",
        "previous": "-2.4",
        "status": "released",
        "notes_append": " | 2026-10-30回填: 9月工业产出环比初值+2.2%大超预期(预期1.2/前值-2.4, V型反弹); 同比初值+1.9%(预期1.4/前值2.7); 同日日本9月失业率2.4%(预期2.5/前值2.5)、东京10月CPI同比2.8%(预期2.7)升温; 双源✅新浪7x24 10-30 07:50 + 华尔街见闻日历10-30"
    },
]

# 初请已由 MCP 正确注入 19.4，仅补 notes 双源验证记录
NOTES_ONLY = [
    {
        "id": "US_JOBLESS_CLAIMS_20261029",
        "notes_append": " | 2026-10-30双源验证✅: 19.4万低于预期19.9万(证券时报口径19.8), 前值由19.4修正为19.5(新华财经口径,本表保留CLI值19.4); 四周均值19.675万, 续请170.1万低于预期172万; 多源✅新华财经10-29 20:35 + 中新社10-29 + 证券时报; WeStock-MCP CLI 注入"
    },
]


def main():
    with open(CAL_PATH, encoding="utf-8") as f:
        cal = json.load(f)
    events = cal["events"] if isinstance(cal, dict) else cal

    backfilled = 0
    notes_only = 0
    for fx in FIXES:
        ev = next((e for e in events if e.get("id") == fx["id"]), None)
        if ev is None:
            print(f"[MISS] {fx['id']} not found")
            continue
        if ev.get("actual") is not None and ev.get("actual") != "2.3":
            # 非 GDP 污染值且已有 actual → 幂等跳过
            if fx["id"] != "US_GDP_ADV_20261029":
                print(f"[SKIP] {fx['id']} already has actual={ev['actual']}")
                continue
        ev["actual"] = fx["actual"]
        if fx.get("forecast"):
            ev["forecast"] = fx["forecast"]
        if fx.get("previous"):
            ev["previous"] = fx["previous"]
        ev["status"] = fx["status"]
        base = ev.get("notes", "") or ""
        if fx["notes_append"] not in base:
            ev["notes"] = (base + fx["notes_append"]).strip(" |")
        backfilled += 1
        print(f"[OK] {fx['id']}: actual={ev['actual']} fc={ev.get('forecast')} prev={ev.get('previous')}")

    for fx in NOTES_ONLY:
        ev = next((e for e in events if e.get("id") == fx["id"]), None)
        if ev is None:
            print(f"[MISS] {fx['id']} not found")
            continue
        base = ev.get("notes", "") or ""
        if fx["notes_append"] not in base:
            ev["notes"] = (base + fx["notes_append"]).strip(" |")
            notes_only += 1
            print(f"[NOTES] {fx['id']}")

    released = sum(1 for e in events if e.get("status") == "released")
    pending = sum(1 for e in events if e.get("status") == "pending")
    with open(CAL_PATH, "w", encoding="utf-8") as f:
        json.dump(cal, f, ensure_ascii=False, indent=2)
    print(f"Done. backfilled={backfilled} notes_only={notes_only} | total={len(events)} released={released} pending={pending}")


if __name__ == "__main__":
    main()
