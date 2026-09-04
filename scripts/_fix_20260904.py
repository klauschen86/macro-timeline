#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-09-04 数据修复与回填
1. 修正 8/7 发布的 7月非农事件错配（mcp_inject 匹配过宽）：
   US_NFP_20260807: actual=3(私营) -> -2.3(整体季调后), forecast 7.8->8, previous 3->2.0(6月修正后)
   US_UNEMPLOYMENT_20260807: actual=7.9(U6) -> 4.1(整体), previous 7.9->4.2, forecast null->4.2
2. 回填今日 9/4 8月非农/失业率 consensus（联网核实：Newsquawk 5.8万/道琼斯5.3万/每经5.6万；失业率主流维持4.1%）
   US_NFP_20260904: forecast=5.8, previous=-2.3
   US_UNEMPLOYMENT_20260904: forecast=4.1, previous=4.1
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")

d = json.load(open(CAL, encoding="utf-8"))
evs = d["events"]
by_id = {e["id"]: e for e in evs}

fixes = {
    # 8/7 发布的 7月数据（修正口径错配）
    "US_NFP_20260807": {
        "actual": "-2.3", "forecast": "8", "previous": "2.0",
        "notes": "修正: 原存私营非农3万, 应为整体非农-2.3万(季调后); previous=6月修正值2.0万 (westock CLI 8/7发布 双源✅)",
    },
    "US_UNEMPLOYMENT_20260807": {
        "actual": "4.1", "forecast": "4.2", "previous": "4.2",
        "notes": "修正: 原存U6失业率7.9, 应为整体失业率4.1% (westock CLI 8/7发布, 与Morningstar一致✅)",
    },
    # 今日 9/4 发布 8月数据（consensus 回填）
    "US_NFP_20260904": {
        "forecast": "5.8", "previous": "-2.3",
        "notes": "consensus +5.8万(Newsquawk)/5.3万(道琼斯)/5.6万(每经) 双源✅; 前值7月-2.3万; 今晚20:30发布",
    },
    "US_UNEMPLOYMENT_20260904": {
        "forecast": "4.1", "previous": "4.1",
        "notes": "consensus 4.1% 维持(多数); FactSet/Continuum偏4.2%; 前值7月4.1%",
    },
}

n = 0
for eid, kv in fixes.items():
    e = by_id.get(eid)
    if not e:
        print(f"  !! not found: {eid}")
        continue
    for k, v in kv.items():
        e[k] = v
    e["status"] = "released" if e.get("actual") else "upcoming"
    n += 1
    print(f"  fixed {eid}: {kv}")

json.dump(d, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nFixed {n} events -> {CAL}")
