#!/usr/bin/env python3
"""2026-08-31 人工补全：中国8月官方PMI×2 + 日本7月工业产出（双源验证后按权威源补全）"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")

with open(CAL, "r", encoding="utf-8") as f:
    data = json.load(f)

updates = {
    "CN_PMI_MFG_20260831": {
        "status": "released",
        "actual": 49.8,
        "forecast": 49.6,
        "previous": 49.2,
        "notes": "8月官方制造业PMI 49.8%（统计局8/31 9:30发布，较7月+0.6pct，预期49.6超预期；前值49.2=westock 7/31 49.2 双源✅；8号元素公众号误报49.4%与统计局官网冲突已排除）",
    },
    "CN_PMI_NONMFG_20260831": {
        "status": "released",
        "actual": 49.0,
        "forecast": 49.9,
        "previous": 49.0,
        "notes": "8月非制造业商务活动指数49.0%（统计局8/31 9:30发布，与7月持平，预期49.9低于预期；前值49.0=westock 7/31 49.0 双源✅）",
    },
    "JP_INDUSTRIAL_20260831": {
        "status": "released",
        "actual": 0.1,
        "forecast": -0.6,
        "previous": 1.9,
        "notes": "7月工业产出环比初值+0.1%（METI 8/31 07:50发布，预期-0.6%（Reuters poll -0.7%）超预期；同比+4.1%较6月4.9%放缓；制造商预计8月+6.4%、9月-4.2%",
    },
}

count = 0
for e in data["events"]:
    if e.get("id") in updates:
        e.update(updates[e["id"]])
        count += 1
        print(f"Updated {e['id']}: status={e['status']} actual={e['actual']}")

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nTotal updated: {count}")
