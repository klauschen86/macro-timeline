#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-09-04 补录事件（联网核实：财联社/中国金融信息网/网易/Newsquawk/FactSet/tradingcharts）
1. 7月时薪 m/m + y/y (8/7发布, MCP westock CLI 有 actual, 双源✅ 补录)
2. 8月时薪 m/m + y/y (今日发布, consensus m/m +0.3% 双源✅; y/y consensus分歧故 fc留空)
3. 加拿大 8月就业人数变动 + 失业率 (今日 20:30 发布, tradingcharts prev 7.51万/6.4%, 单源标注)
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")
d = json.load(open(CAL, encoding="utf-8"))
evs = d["events"]
have = {e["id"] for e in evs}

NEW = [
 dict(id="US_FF_Average_Hourly_Earnings_m_m_20260807", country="US", country_name="美国",
      indicator="Average Hourly Earnings m/m", indicator_en="Average Hourly Earnings m/m",
      release_date="2026-08-07", release_time="8:30am", timezone="EST", importance=4,
      actual="0.1%", forecast="0.3%", previous="0.3%", unit="", status="released",
      source="Bureau of Labor Statistics", source_url="", period="2026-07",
      notes="7月时薪月率 0.1%(8/7随非农发布, westock CLI+Morningstar 双源✅)"),
 dict(id="US_FF_Average_Hourly_Earnings_y_y_20260807", country="US", country_name="美国",
      indicator="Average Hourly Earnings y/y", indicator_en="Average Hourly Earnings y/y",
      release_date="2026-08-07", release_time="8:30am", timezone="EST", importance=4,
      actual="3.2%", forecast="3.5%", previous="3.5%", unit="", status="released",
      source="Bureau of Labor Statistics", source_url="", period="2026-07",
      notes="7月时薪年率 3.2%(8/7随非农发布, westock CLI+Continuum 3.2%一致✅)"),
 dict(id="US_FF_Average_Hourly_Earnings_m_m_20260904", country="US", country_name="美国",
      indicator="Average Hourly Earnings m/m", indicator_en="Average Hourly Earnings m/m",
      release_date="2026-09-04", release_time="8:30am", timezone="EST", importance=4,
      actual=None, forecast="0.3%", previous="0.1%", unit="", status="upcoming",
      source="Bureau of Labor Statistics", source_url="", period="2026-08",
      notes="8月时薪月率 consensus +0.3%(Newsquawk/FactSet/Morningstar 双源✅), 前值7月0.1%; 今晚20:30随非农发布"),
 dict(id="US_FF_Average_Hourly_Earnings_y_y_20260904", country="US", country_name="美国",
      indicator="Average Hourly Earnings y/y", indicator_en="Average Hourly Earnings y/y",
      release_date="2026-09-04", release_time="8:30am", timezone="EST", importance=4,
      actual=None, forecast=None, previous="3.2%", unit="", status="upcoming",
      source="Bureau of Labor Statistics", source_url="", period="2026-08",
      notes="8月时薪年率 前值7月3.2%; y/y consensus分歧(Continuum预测降至2.9%)故forecast留空"),
 dict(id="CA_EMPLOYMENT_20260904", country="CA", country_name="加拿大",
      indicator="就业人数变动", indicator_en="Net Change in Employment",
      release_date="2026-09-04", release_time="20:30", timezone="BJS", importance=3,
      actual=None, forecast=None, previous="7.51", unit="万人", status="upcoming",
      source="加拿大统计局", source_url="", period="2026-08",
      notes="8月就业人数变动, 前值7月+7.51万(tradingcharts 75.1K 一致✅); 今晚20:30发布; fc共识未成形留空"),
 dict(id="CA_UNEMPLOYMENT_20260904", country="CA", country_name="加拿大",
      indicator="失业率", indicator_en="Unemployment Rate",
      release_date="2026-09-04", release_time="20:30", timezone="BJS", importance=3,
      actual=None, forecast="6.4", previous="6.4", unit="%", status="upcoming",
      source="加拿大统计局", source_url="", period="2026-08",
      notes="8月失业率 forecast/前值 6.4%(tradingcharts 单源⚠️)"),
]

n = 0
for e in NEW:
    if e["id"] in have:
        print(f"  skip exists: {e['id']}")
        continue
    evs.append(e)
    n += 1
    print(f"  added {e['id']} ({e['indicator']})")

json.dump(d, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nAdded {n} events, total {len(evs)}")
