#!/usr/bin/env python3
"""
2026-10-14 人工补录脚本（自动化 v2.1 步骤 a2 兜底）
westock 数据源滞后（CPI/PPI feed 最新仅 2026-08 期），今日 09:30 国家统计局已发布
9 月数据，依据联网核实的权威来源（国家统计局官网 stats.gov.cn / 央视新闻 / 财联社）回填：
1. 回填 9月中国 CPI 同比 0.9%（预期 1.0 / 前值 0.8，环比 +0.2%，核心CPI +1.0% 与上月持平）
2. 回填 9月中国 PPI 同比 5.0%（预期 4.5 / 前值 3.8，环比 +1.2%，购进价格同比 +6.9%）
注：进出口贸易数据（~11:00 发布）与美国 CPI（今晚 20:30 BJS）尚未发布，不回填。
"""
import json

CAL = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\calendar.json"
data = json.load(open(CAL, encoding="utf-8"))
events = data["events"]
by_id = {e["id"]: e for e in events}

updates = {
    "CN_CPI_20261014": {
        "actual": 0.9, "forecast": 1.0, "previous": 0.8,
        "status": "released",
        "notes": "9月CPI同比+0.9%（预期1.0/前值0.8，涨幅扩大0.1pct；环比+0.2%；核心CPI同比+1.0%与上月持平；食品-1.7%/非食品+1.5%；统计局10/14 09:30发布）",
        "source_url": "https://www.stats.gov.cn/sj/zxfb/202610/t20261014_1965477.html",
    },
    "CN_PPI_20261014": {
        "actual": 5.0, "forecast": 4.5, "previous": 3.8,
        "status": "released",
        "notes": "9月PPI同比+5.0%（预期4.5/前值3.8，涨幅扩大1.2pct；环比+1.2%涨幅扩大0.8pct；购进价格同比+6.9%；主因输入性因素油价煤价上行；统计局10/14发布）",
        "source_url": "https://www.stats.gov.cn",
    },
}

for eid, u in updates.items():
    e = by_id.get(eid)
    if not e:
        print(f"[MISS] {eid} not found")
        continue
    e.update(u)
    print(f"[OK] {eid}: actual={u['actual']} (forecast={u['forecast']}/prev={u['previous']}) -> released")

json.dump(data, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("calendar.json saved.")
