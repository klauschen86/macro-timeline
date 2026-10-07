#!/usr/bin/env python3
"""
2026-10-07 修复脚本（automation 1781242407195）
1. 财新 9/30 双事件 period 纠错：2026-08 → 2026-09（数据属于 9 月，与 10/1 事件 period=2026-09 及 8月值链矛盾）
2. 删除重复/幽灵事件：
   - CN_CAIXIN_PMI_20261001（与 CN_CAIXIN_PMI_20260930 同值 52.1 重复；删除前断言 9/30 事件 actual=52.1）
   - CN_CAIXIN_SERVICES_PMI_20261005（幽灵，无任何数据；9 月服务业值已记录于 _20260930）
   铁律：删除后回读断言 id 不存在（字段级匹配），并验证 generate_calendar.py 无模式会再生（override 已映射 2026-09→9/30）
3. 财新 11 月事件 prev 预填：制造业 prev=52.1、服务业 prev=51.6（9 月值）
4. 补录 FOMC 会议纪要 2 事件（美联储官网日历+fedratecalc+financecalendar 3 源核实 2026-10-07）：
   - US_FOMC_MINUTES_20261008：9/15-16 会议纪要，10/7 14:00 ET = 10/8 02:00 BJS
   - US_FOMC_MINUTES_20261118：10/27-28 会议纪要，11/17 14:00 ET = 11/18 03:00 BJS（11/1 冬令时后 ET-BJS 差 13h）
幂等：全部操作前检查当前值，已满足则跳过；结束统一回读断言。
"""
import json
import os
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(PROJECT, "data", "calendar.json")

with open(CAL, "r", encoding="utf-8") as f:
    data = json.load(f)
events = data["events"]
by_id = {e.get("id"): e for e in events}

changes = []


def note(msg):
    changes.append(msg)
    print(" *", msg)


# ---------- 1. period 纠错 ----------
for eid in ("CN_CAIXIN_PMI_20260930", "CN_CAIXIN_SERVICES_PMI_20260930"):
    e = by_id.get(eid)
    assert e, f"{eid} 不存在"
    if e.get("period") == "2026-08":
        e["period"] = "2026-09"
        note(f"{eid}: period 2026-08 -> 2026-09")
    else:
        note(f"{eid}: period={e.get('period')} 已正确，跳过")

# ---------- 2. 删除重复/幽灵 ----------
# 前置断言：9/30 事件保有数据
mfg = by_id.get("CN_CAIXIN_PMI_20260930")
svc = by_id.get("CN_CAIXIN_SERVICES_PMI_20260930")
assert mfg and mfg.get("actual") == 52.1, "CN_CAIXIN_PMI_20260930 actual != 52.1，禁止删除 10/1 事件"
assert svc and svc.get("actual") == 51.6, "CN_CAIXIN_SERVICES_PMI_20260930 actual != 51.6，禁止删除 10/5 事件"

for eid in ("CN_CAIXIN_PMI_20261001", "CN_CAIXIN_SERVICES_PMI_20261005"):
    if eid in by_id:
        events.remove(by_id[eid])
        del by_id[eid]
        note(f"删除 {eid}")
    else:
        note(f"{eid} 已不存在，跳过")

# ---------- 3. prev 预填 ----------
prev_fill = [
    ("CN_CAIXIN_PMI_20261102", 52.1),
    ("CN_CAIXIN_SERVICES_PMI_20261104", 51.6),
]
for eid, val in prev_fill:
    e = by_id.get(eid)
    assert e, f"{eid} 不存在"
    if e.get("previous") is None:
        e["previous"] = val
        note(f"{eid}: previous 预填 {val}")
    else:
        note(f"{eid}: previous={e.get('previous')} 已有，跳过")

# ---------- 4. 补录 FOMC 纪要 ----------
MIN_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
new_events = [
    {
        "id": "US_FOMC_MINUTES_20261008",
        "country": "US", "country_name": "美国",
        "indicator": "美联储会议纪要（FOMC Minutes）",
        "indicator_en": "FOMC Meeting Minutes",
        "frequency": "每年8次", "importance": 3,
        "release_date": "2026-10-08", "release_time": "02:00", "timezone": "BJS",
        "period": "2026-09",
        "source": "Federal Reserve", "source_url": MIN_URL, "unit": "",
        "status": "upcoming",
        "notes": "9/15-16 FOMC 会议纪要，10/7 14:00 ET=10/8 02:00 BJS 发布（美联储官网日历+fedratecalc+financecalendar 3源✅ 2026-10-07 补录）；该会议决议加息25bp至3.75-4.00%（3年来首次、12-0全票），点阵图2026中值4.10%暗示年内或再加一次；纪要关注委员对通胀上行风险与再加息路径的讨论，为10/28-29会议定价关键输入",
    },
    {
        "id": "US_FOMC_MINUTES_20261118",
        "country": "US", "country_name": "美国",
        "indicator": "美联储会议纪要（FOMC Minutes）",
        "indicator_en": "FOMC Meeting Minutes",
        "frequency": "每年8次", "importance": 3,
        "release_date": "2026-11-18", "release_time": "03:00", "timezone": "BJS",
        "period": "2026-10",
        "source": "Federal Reserve", "source_url": MIN_URL, "unit": "",
        "status": "upcoming",
        "notes": "10/27-28 FOMC 会议纪要，11/17 14:00 ET=11/18 03:00 BJS 发布（11/1 冬令时后 ET-BJS 差13小时；美联储官网日历确认 2026-10-07 补录）",
    },
]
for ne in new_events:
    if ne["id"] not in by_id:
        events.append(ne)
        by_id[ne["id"]] = ne
        note(f"补录 {ne['id']}")
    else:
        note(f"{ne['id']} 已存在，跳过")

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print(f"\n写入 {CAL}：共 {len(changes)} 处变更")

# ---------- 回读断言（字段级 id 匹配） ----------
with open(CAL, "r", encoding="utf-8") as f:
    check = json.load(f)
ids = {e.get("id") for e in check["events"]}
cmap = {e.get("id"): e for e in check["events"]}

assert "CN_CAIXIN_PMI_20261001" not in ids, "FAIL: 10/1 制造业重复事件未删除"
assert "CN_CAIXIN_SERVICES_PMI_20261005" not in ids, "FAIL: 10/5 服务业幽灵事件未删除"
assert cmap["CN_CAIXIN_PMI_20260930"]["period"] == "2026-09"
assert cmap["CN_CAIXIN_SERVICES_PMI_20260930"]["period"] == "2026-09"
assert cmap["CN_CAIXIN_PMI_20260930"]["actual"] == 52.1
assert cmap["CN_CAIXIN_SERVICES_PMI_20260930"]["actual"] == 51.6
assert cmap["CN_CAIXIN_PMI_20261102"]["previous"] == 52.1
assert cmap["CN_CAIXIN_SERVICES_PMI_20261104"]["previous"] == 51.6
assert "US_FOMC_MINUTES_20261008" in ids and cmap["US_FOMC_MINUTES_20261008"]["release_date"] == "2026-10-08"
assert "US_FOMC_MINUTES_20261118" in ids and cmap["US_FOMC_MINUTES_20261118"]["release_date"] == "2026-11-18"

n_rel = sum(1 for e in check["events"] if e.get("status") == "released")
print(f"回读断言 ALL OK：{len(check['events'])} events，Released {n_rel}")
