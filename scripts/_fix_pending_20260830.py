#!/usr/bin/env python3
"""一次性修复脚本：补全 8/17 六项 pending 事件 actual + 新增 7月 PCE 事件（2026-08-30 遗留问题处理）"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")

with open(CAL, "r", encoding="utf-8") as f:
    cal = json.load(f)

events = cal["events"]
by_id = {e["id"]: e for e in events}

# ============ 1. 8/17 六项事件补全（实际值均已发布，双源验证通过） ============
fixes = {
    "CN_INDUSTRIAL_20260817": {
        "actual": "4.5", "previous": "5.3",
        "notes": "7月当月同比4.5%（国家统计局8/17发布）；累计同比5.3%（westock macro_valueadded 一致）✅",
    },
    "CN_RETAIL_20260817": {
        "actual": "0.6", "previous": "1.0",
        "notes": "7月当月同比0.6%（westock macro_consumption CUR_YOY）；累计同比1.2%（统计局一致）✅",
    },
    "CN_FAI_20260817": {
        "actual": "-6.7", "previous": "-5.0",
        "notes": "1-7月固定资产投资(不含农户)累计同比-6.7%（妙想Choice/国家统计局）；分项基建-3.6%/制造-1.7%/地产-19.2% ✅",
    },
    "CN_UNEMPLOYMENT_20260817": {
        "actual": "5.2", "previous": "5.0",
        "notes": "7月全国城镇调查失业率5.2%（国家统计局8/17发布，环比+0.2pct，同比持平）✅",
    },
    "US_RETAIL_20260817": {
        "actual": "-0.6", "previous": "0.2",
        "notes": "7月零售销售环比-0.6%（Census Bureau 8/14发布，预期+0.1% miss；同比+5.0%）；日历日期8/17为生成器推算，实际发布8/14",
    },
    "UK_CPI_20260817": {
        "actual": "2.9", "previous": "2.6",
        "notes": "7月CPI同比2.9%（ONS 8/19发布，前值2.6%）；日历日期8/17为生成器推算，实际发布8/19",
    },
}

updated = []
for eid, vals in fixes.items():
    if eid in by_id:
        ev = by_id[eid]
        ev["actual"] = vals["actual"]
        ev["previous"] = vals["previous"]
        ev["status"] = "released"
        ev["source"] = ev.get("source") or "官方统计机构"
        ev["notes"] = vals["notes"]
        updated.append(eid)
    else:
        print(f"[WARN] 未找到事件 {eid}")

# ============ 2. 新增 7月 PCE 事件（8/26 发布，BEA） ============
# 检查是否已存在
existing_pce = [e for e in events if e.get("id", "").startswith("US_PCE_")]
print(f"已有 PCE 事件数: {len(existing_pce)}")

pce_events = [
    {
        "id": "US_PCE_20260826",
        "country": "US",
        "country_name": "美国",
        "indicator": "PCE物价指数（同比）",
        "indicator_en": "PCE Price Index YoY",
        "frequency": "月度",
        "importance": 3,
        "release_date": "2026-08-26",
        "release_time": "20:30",
        "timezone": "EST",
        "period": "2026-07",
        "source": "BEA",
        "source_url": "https://www.bea.gov/",
        "unit": "%",
        "actual": "3.7",
        "previous": "3.7",
        "status": "released",
        "notes": "7月PCE同比3.7%（妙想Choice/BEA 8/26发布，前值6月3.7%持平）；8/25期货日报前瞻预期3.6%",
    },
    {
        "id": "US_PCE_CORE_20260826",
        "country": "US",
        "country_name": "美国",
        "indicator": "核心PCE物价指数（同比）",
        "indicator_en": "Core PCE Price Index YoY",
        "frequency": "月度",
        "importance": 3,
        "release_date": "2026-08-26",
        "release_time": "20:30",
        "timezone": "EST",
        "period": "2026-07",
        "source": "BEA",
        "source_url": "https://www.bea.gov/",
        "unit": "%",
        "actual": "3.3",
        "previous": "3.3",
        "status": "released",
        "notes": "7月核心PCE同比3.3%（妙想Choice/BEA 8/26发布，前值6月3.3%持平）",
    },
]

added = []
for ev in pce_events:
    if ev["id"] not in by_id:
        events.append(ev)
        added.append(ev["id"])

# ============ 3. 重算 meta ============
today = "2026-08-30"
released = [e for e in events if e.get("actual") is not None]
upcoming = [e for e in events if e["release_date"] >= today]
pending = [e for e in events if e.get("status") == "pending"]
with_forecast = [e for e in upcoming if e.get("forecast") is not None]
by_country = {}
for e in events:
    cn = e.get("country_name", "??")
    by_country[cn] = by_country.get(cn, 0) + 1

cal["meta"].update({
    "total_events": len(events),
    "upcoming_events": len(upcoming),
    "released_events": len(released),
    "pending_events": len(pending),
    "upcoming_with_forecast": len(with_forecast),
    "by_country": by_country,
})

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

print(f"更新事件: {len(updated)} -> {updated}")
print(f"新增事件: {len(added)} -> {added}")
print(f"事件总数: {len(events)} / Released: {len(released)} / Upcoming: {len(upcoming)} / Pending: {len(pending)}")
