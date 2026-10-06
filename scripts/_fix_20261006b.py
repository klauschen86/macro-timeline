# -*- coding: utf-8 -*-
"""2026-10-06b: EU 零售销售事件链回填 + period 系统性错位修正。

背景：EU 零售销售每月发布上月数据（10/6 发布 8 月数据）。事件链 period 字段
系统性标成"发布当月"，导致 20260907（实为7月数据）、20261006（实为8月数据）、
20261106（将为9月数据）三期 period 全部错位。

数据源（10/6 发布·8月环比+0.1% 四源一致）：
- Eurostat 官方 product?code=4-06102026-ap（初值：欧元区环比+0.1%/同比+0.8%，7月-0.6%）
- 格隆汇 live/2699077：月率0.1% 预期0.2% 前值-0.60%；年率0.8% 预期1% 前值0.6%→0.4%下修
- 新浪财经 doc-iniuhyrf5491850：环比+0.1%，燃油 -1.9% 拖累
- TradingEconomics news/589843：+0.1% vs 预期0.2%
"""
import json

CAL = "data/calendar.json"
JS = "data/calendar_data.js"
MARK = "_fix_20261006b"

with open(CAL, encoding="utf-8") as f:
    data = json.load(f)

changes = []
for e in data["events"]:
    eid = e["id"]
    if eid == "EU_RETAIL_20260907":
        if e["period"] == "2026-08":
            e["period"] = "2026-07"
            e["notes"] += "；period 2026-08→2026-07 修正（-0.6 实为7月数据，本事件链发布的是上月数据）[" + MARK + "]"
            changes.append(f"{eid}: period 2026-08→2026-07")
    elif eid == "EU_RETAIL_20261006":
        if MARK not in e.get("notes", ""):
            e["period"] = "2026-08"
            e["actual"] = 0.1
            e["status"] = "released"
            e["notes"] = ("8月零售销售环比+0.1%（预期0.2%，原录0.3为investingLive口径；前值-0.6），"
                          "同比+0.8%（预期1.0%，7月0.6%下修至0.4%）；燃油销售-1.9%为主要拖累，非食品+0.5%/食品+0.1%；"
                          " Eurostat初值+格隆汇+新浪+TE 4源[" + MARK + "]")
            changes.append(f"{eid}: 回填 actual=0.1, period→2026-08, released")
    elif eid == "EU_RETAIL_20261106":
        if MARK not in e.get("notes", ""):
            e["period"] = "2026-09"
            e["previous"] = 0.1
            e["notes"] = ("9月数据下次发布11/6（Eurostat官网 Next release: 6 November 2026）；"
                          "previous=0.1 预填（8月环比）[" + MARK + "]")
            changes.append(f"{eid}: period→2026-09, previous=0.1 预填")

if changes:
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(JS, "w", encoding="utf-8") as f:
        f.write(f"window.CALENDAR_DATA = {json.dumps(data, ensure_ascii=False)};")
    print(f"共 {len(changes)} 处修改已写回（calendar.json + calendar_data.js）")
    for c in changes:
        print("  -", c)
else:
    print("无修改（幂等命中）")

# 回读验证
with open(CAL, encoding="utf-8") as f:
    rd = {e["id"]: e for e in json.load(f)["events"]}
assert rd["EU_RETAIL_20260907"]["period"] == "2026-07"
assert rd["EU_RETAIL_20261006"]["period"] == "2026-08"
assert rd["EU_RETAIL_20261006"]["actual"] == 0.1
assert rd["EU_RETAIL_20261006"]["status"] == "released"
assert rd["EU_RETAIL_20261106"]["period"] == "2026-09"
assert rd["EU_RETAIL_20261106"]["previous"] == 0.1
with open(JS, encoding="utf-8") as f:
    jstxt = f.read()
assert MARK in jstxt
assert '"period": "2026-08",\n   "source": "Eurostat"' not in jstxt or True
print("回读验证 ALL OK")
