# -*- coding: utf-8 -*-
"""2026-09-14: 补充今日(9/14)中国8月金融数据的最新一致预期到 notes（联网多源核实）。
来源：东方财富股吧周历（浙商证券预测）+ 今日头条周末财经解读（经济学家预测均值）+ 腾讯新闻研报摘要。
不改动 actual/prev/forecast 数值字段，仅追加 notes。"""
import json

PATH = "data/calendar.json"
data = json.load(open(PATH, encoding="utf-8"))

ADD = {
    "CN_M2_20260914": "2026-09-14晨: 东财股吧周历确认8月金融数据今日(周一)公布(推测); 预期更新: M2 7.5%(浙商)~7.7%(经济学家均值), M1 4.0%(浙商)",
    "CN_SOCIAL_FINANCING_20260914": "2026-09-14晨: 预期更新: 社融1.65万亿(浙商)~2.13万亿(腾讯研报摘要)~2.3万亿(经济学家均值); 政府债券净融资~1.11万亿为主要支撑, 社融口径贷款~0.55万亿; 余额同比~7.3%(前值7.4%)",
    "CN_NEW_LOANS_20260914": "2026-09-14晨: 预期更新: 新增信贷1000亿(浙商)~4110亿(经济学家均值); 居民短贷环比转正, 票据融资为主要支撑",
}

n = 0
for e in data["events"]:
    if e.get("id") in ADD:
        add = ADD[e["id"]]
        if add not in e.get("notes", ""):
            e["notes"] = (e.get("notes", "") + " | " + add).strip(" |")
            n += 1

json.dump(data, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"notes updated: {n}")
