# -*- coding: utf-8 -*-
"""_fix_20261107.py — 一次性回填 2026-11-06（周五晚）发布的三项数据
多源核实（2026-11-07 执行）：
- 美 10 月非农 +16.5 万人（预期 6.5 万，前值 2.9 万；9 月上修至 6.0/8 月上修至 18.6）
  财联社(cls.cn/detail/2527820)+新浪财经+21经济网 3源✅
- 美 10 月失业率 4.1%（预期 4.2%，前值 4.2%）财联社+21经济网 2源✅
- 欧元区 9 月零售环比 -0.7%（预期 -0.1%，8 月上修 +0.4%；同比 +0.4% 预期 +0.6%）
  新华财经+财联社+腾讯新闻+TradingEconomics 4源✅
数据以数值写入（非字符串），回读 assert 校验。
"""
import json

PATH = "data/calendar.json"

UPDATES = {
    "US_NFP_20261106": {
        "actual": 16.5,
        "forecast": 6.5,
        "previous": 2.9,
        "note": "2026-11-07回填: 美10月非农+16.5万远超预期(预期6.5万,2026年来第三高增幅,超预期中值5个标准差); 9月由2.9上修至6.0/8月由13.3上修至18.6(合计+8.4万); 时薪环比0.4%/同比3.1%均超预期; 新增集中于专业商业服务(+7万)/医疗/运输仓储; CME 12月加息25bp概率升至约77%(前日67%); 财联社+新浪+21经济网 3源✅",
    },
    "US_UNEMPLOYMENT_20261106": {
        "actual": 4.1,
        "forecast": 4.2,
        "previous": 4.2,
        "note": "2026-11-07回填: 美10月失业率4.1%意外回落(预期持平4.2%); 时薪三连热+失业率下降,美联储12月加息预期升温; 财联社+21经济网 2源✅",
    },
    "EU_RETAIL_20261106": {
        "actual": -0.7,
        "forecast": -0.1,
        "previous": 0.4,
        "note": "2026-11-07回填: 欧元区9月零售环比-0.7%大幅不及预期(预期-0.1%,与7月并列2024-06来最大降幅; 非食品-1.2%/食品-0.3%/汽车燃料+1.0%); 同比+0.4%也不及预期0.6%; 8月环比由0.1上修至0.4(previous同步); 分国别德-2.0/法-0.6最弱; 新华财经+财联社+腾讯+TE 4源✅",
    },
}

with open(PATH, encoding="utf-8") as f:
    data = json.load(f)
events = data["events"] if isinstance(data, dict) else data

hit = 0
for e in events:
    upd = UPDATES.get(e["id"])
    if not upd:
        continue
    e["actual"] = upd["actual"]
    e["forecast"] = upd["forecast"]
    e["previous"] = upd["previous"]
    e["notes"] = (e.get("notes") or "").strip() + " | " + upd["note"] if e.get("notes") else upd["note"]
    hit += 1

assert hit == len(UPDATES), f"仅命中 {hit}/{len(UPDATES)} 条，存在幽灵 id"
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 回读校验
with open(PATH, encoding="utf-8") as f:
    back = json.load(f)
for e in back["events"] if isinstance(back, dict) else back:
    if e["id"] in UPDATES:
        assert e["actual"] == UPDATES[e["id"]]["actual"], e["id"]
        assert isinstance(e["actual"], (int, float)), f"{e['id']} actual 非数值"
        print(f"OK {e['id']}: actual={e['actual']} forecast={e['forecast']} previous={e['previous']}")
print(f"回填完成 {hit} 条")
