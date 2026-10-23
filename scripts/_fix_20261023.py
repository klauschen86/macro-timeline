#!/usr/bin/env python3
"""
2026-10-23 批次修正脚本
1. JP_CPI_20261023 回填：日本9月全国CPI同比 2.1%（预期2.1/前值1.9）
   多源：财联社+每经+新华财经+investinglive 4源一致（westock CLI 当日值缺失→Web多源替代双源）
2. EU PMI 初值 3 事件：period 2026-09→2026-10、release_time 10:00→16:00（S&P Global 08:00 UTC）
   预填共识 fc / 9月终值 prev：Mfg 52.7/52.9（fc 双源 metalsmine+gerchik）
   Svc 52.6/53.0（fc 双源）；Composite 52.5/53.1（fc 单源 tradingcharts ⚠️标注）
3. US_MICHIGAN_SENTIMENT_20261023 预填 fc=46.3（metalsmine 共识列）
   prev 保留 46.3（⚠️9月终值口径分歧：10/10批多源记初值前值=48.1，metalsmine previous=46.3，今晚发布核对）
"""
import json
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
CAL = os.path.join(PROJECT_DIR, "data", "calendar.json")

with open(CAL, "r", encoding="utf-8") as f:
    cal = json.load(f)
events = cal["events"]
by_id = {e["id"]: e for e in events}

changed = []

# 1) 日本 9 月全国 CPI
e = by_id.get("JP_CPI_20261023")
assert e is not None, "JP_CPI_20261023 not found"
e["actual"] = 2.1
e["forecast"] = 2.1
e["previous"] = 1.9
e["status"] = "released"
e["notes"] = (
    "9月全国CPI同比2.1%，符合预期2.1%，前值1.9%；核心CPI(除生鲜)2.1%(预期2.1/前值1.7)，"
    "12月以来首超日银2%目标；核心中核心(除食品能源)2.4%大超预期2.3(前值1.9)，输入型压力显现"
    "(油价>110美元推升进口成本，电价补贴仍在压制表观读数)；东京9月核心CPI 2.7%先行印证。"
    "市场影响：BOJ 10/29-30料按兵不动(1.25%)但或上调通胀预测，12月加息至1.5%预期升温；"
    "数据公布后日元小幅走强。来源：财联社+每经+新华财经+investinglive 4源一致✅"
    "(westock CLI当日值缺失，Web多源替代双源验证)"
)
changed.append("JP_CPI_20261023")

# 2) 欧元区 10 月 PMI 初值 3 事件
eu_fix = {
    "EU_PMI_MFG_FLASH_20261023": (52.7, 52.9,
        "10月初值共识52.7(metalsmine+gerchik双源✅)，9月终值52.9(PrimeXBT+metalsmine一致)；"
        "9月初值口径欧元区重返扩张上方；分国先行：德Mfg fc 53.5/法 50.5。今晚16:00 BJS(S&P Global 08:00 UTC)发布"),
    "EU_PMI_SVC_FLASH_20261023": (52.6, 53.0,
        "10月初值共识52.6(metalsmine+gerchik双源✅)，9月终值53.0为10个月高位；"
        "德Svc fc 52.5/法 50.7。今晚16:00 BJS发布"),
    "EU_PMI_COMPOSITE_FLASH_20261023": (52.5, 53.1,
        "10月初值共识52.5(tradingcharts单源⚠️待发布核对)，9月终值53.1为41个月高位(PrimeXBT+tradingcharts一致✅)；"
        "S&P Global估对应季度GDP约+0.4%。今晚16:00 BJS发布"),
}
for eid, (fc, prev, notes) in eu_fix.items():
    e = by_id.get(eid)
    assert e is not None, f"{eid} not found"
    e["period"] = "2026-10"
    e["release_time"] = "16:00"
    e["forecast"] = fc
    e["previous"] = prev
    e["notes"] = notes
    changed.append(eid)

# 3) 密歇根终值预填共识
e = by_id.get("US_MICHIGAN_SENTIMENT_20261023")
assert e is not None, "US_MICHIGAN_SENTIMENT_20261023 not found"
e["forecast"] = 46.3
e["notes"] = (
    "终值共识46.3(metalsmine，与10/9初值46.3持平)；1年期通胀预期终值今晚22:00同发(初值4.7%)。"
    "⚠️前值口径分歧待核对：本事件previous=46.3(10/10批预填+metalsmine previous一致)，"
    "但10/10批多源记录10月初值46.3的前值(9月终值)=48.1——今晚发布后以UMich官方终值报告修正previous。"
    "背景：现况分项初值44.7创纪录最低、油价>110推升通胀预期(1年4.7/5年3.5双升)"
)
changed.append("US_MICHIGAN_SENTIMENT_20261023")

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

# 回读断言
with open(CAL, "r", encoding="utf-8") as f:
    cal2 = json.load(f)
by_id2 = {e["id"]: e for e in cal2["events"]}
assert by_id2["JP_CPI_20261023"]["actual"] == 2.1 and by_id2["JP_CPI_20261023"]["status"] == "released"
assert by_id2["EU_PMI_MFG_FLASH_20261023"]["period"] == "2026-10" and by_id2["EU_PMI_MFG_FLASH_20261023"]["release_time"] == "16:00"
assert by_id2["EU_PMI_SVC_FLASH_20261023"]["forecast"] == 52.6
assert by_id2["EU_PMI_COMPOSITE_FLASH_20261023"]["previous"] == 53.1
assert by_id2["US_MICHIGAN_SENTIMENT_20261023"]["forecast"] == 46.3
print("Fixed:", changed, "— re-read ALL OK")
