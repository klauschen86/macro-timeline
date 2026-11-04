# -*- coding: utf-8 -*-
"""
_fix_20261104.py — 2026-11-04 数据修正脚本（幂等）
修正 3 个事件的日期/时间错标（三源交叉验证：财联社 11-4 05:35 + 金十 11-4 早报 + 新浪 7x24）：
①US_ISM_SERVICES_20261103: 日历错标 11-3 10:00 → 实际 11-4 23:00 BJS（预期54.8/前值54.9）
②US_ADP_20261104: 时间 20:15 → 21:15 BJS（预期6.9万/前值9万）
③EU_CPI_FLASH_20261104: 时间 11:00 → 18:00 BJS（预期年率4.0%/前值3.8%）
注意：不运行 run_daily merge（避免日期重置复现），直接 generate_js。
今日 09:45 财新服务业PMI 执行时刚发布、新闻未收录 actual，留待 11-5 回填。
"""
import json
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')

FIXES = [
    {
        "id": "US_ISM_SERVICES_20261103",
        "release_date": "2026-11-04",
        "release_time": "23:00",
        "forecast": "54.8",
        "notes_append": " | 2026-11-04修正: 日历原错标11-3 10:00发布, 实际为11-4 23:00 BJS发布(三源: 财联社11-4 05:35/金十11-4早报/新浪7x24); 预期54.8/前值54.9(金十)"
    },
    {
        "id": "US_ADP_20261104",
        "release_time": "21:15",
        "forecast": "6.9",
        "notes_append": " | 2026-11-04修正: 发布时间20:15→21:15 BJS(三源一致); 预期6.9万/前值9万(金十)"
    },
    {
        "id": "EU_CPI_FLASH_20261104",
        "release_time": "18:00",
        "forecast": "4.0",
        "notes_append": " | 2026-11-04修正: 发布时间11:00→18:00 BJS(三源一致); 预期年率4.0%(前值3.8%)/月率0.3%(前值0.6%)(金十)"
    },
]


def main():
    with open(CAL, encoding="utf-8") as f:
        cal = json.load(f)
    idx = {e["id"]: e for e in cal["events"]}
    fixed = 0
    for fx in FIXES:
        e = idx.get(fx["id"])
        if not e:
            print("skip (not found):", fx["id"])
            continue
        changed = False
        for key in ("release_date", "release_time", "forecast"):
            if key in fx and e.get(key) != fx[key]:
                old = e.get(key)
                e[key] = fx[key]
                print(f"{fx['id']}: {key} {old} -> {fx[key]}")
                changed = True
        na = fx.get("notes_append")
        if na and na not in (e.get("notes") or ""):
            e["notes"] = (e.get("notes") or "") + na
            changed = True
        if changed:
            fixed += 1
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(cal, f, ensure_ascii=False, indent=2)
    print(f"20261104 fix: fixed={fixed}")
    if fixed:
        generate_js(load_calendar())
        print("JS regenerated")


if __name__ == "__main__":
    main()
