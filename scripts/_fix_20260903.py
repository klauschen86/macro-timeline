#!/usr/bin/env python3
"""
2026-09-03 人工补录脚本（自动化 v2.1 步骤 a2 兜底）
依据联网核实的权威数据（财新/标普全球、TradeVae/永丰金/网易日历共识、金十汇总）：
1. 新增 9/3 财新服务业PMI（今日 09:45 BJS 已发布 actual=50.7）—— calendar 模式缺漏（仅有财新制造业PMI）
2. 更新 9/3 US_ISM_SERVICES forecast/previous（今晚 22:00 BJS 发布）
3. 更新 9/3 US_JOBLESS_CLAIMS forecast/previous（今晚 20:30 BJS 发布）
"""
import json

CAL = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\calendar.json"
data = json.load(open(CAL, encoding="utf-8"))
events = data["events"]
by_id = {e["id"]: e for e in events}

# ---------- 1. 更新已有事件 forecast/previous ----------
updates = {
    "US_ISM_SERVICES_20260903": {
        "forecast": 54.2, "previous": 54.1,
        "notes": "8月ISM非制造业PMI 预期54.2/前值54.1（共识区间53.8~54.9，连续25个月扩张；9/3 22:00 BJS发布，非农前重头戏）",
        "source_url": "https://www.ismworld.org",
    },
    "US_JOBLESS_CLAIMS_20260903": {
        "forecast": 20.5, "previous": 20.3,
        "notes": "截至8/29当周初请失业金 预期20.5万/前值20.3万（金十+TradeVae双源一致；9/3 20:30 BJS发布）",
        "source_url": "https://www.dol.gov/ui/initial",
    },
}

# ---------- 2. 新增 9/3 财新服务业PMI ----------
new_events = [
    {
        "id": "CN_CAIXIN_SERVICES_PMI_20260903",
        "country": "CN", "country_name": "中国",
        "indicator": "财新服务业PMI", "indicator_en": "Caixin Services PMI",
        "frequency": "月度", "importance": 2,
        "release_date": "2026-09-03", "release_time": "09:45", "timezone": "BJS",
        "period": "2026-08", "source": "财新/S&P Global", "source_url": "https://www.caixin.com",
        "unit": "", "actual": 50.7, "forecast": 50.6, "previous": 50.4,
        "status": "released",
        "notes": "8月财新服务业PMI 50.7（预期50.6/前值50.4，连续扩张且略超预期；与官方非制造业49.0弱于荣枯线形成分化；9/3 09:45 BJS发布；双源✅ forexcalendar.app actual=50.7 与网易日历前值50.40一致）",
    },
]

n_upd = n_new = 0
for eid, patch in updates.items():
    if eid in by_id:
        by_id[eid].update(patch)
        n_upd += 1
    else:
        print(f"  !! 未找到 {eid}")

for ne in new_events:
    if ne["id"] in by_id:
        print(f"  !! 已存在 {ne['id']}，跳过")
        continue
    events.append(ne)
    n_new += 1

data["events"] = events
json.dump(data, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"更新 {n_upd} 个事件 forecast/previous，新增 {n_new} 个事件；总计 {len(events)} 事件")
