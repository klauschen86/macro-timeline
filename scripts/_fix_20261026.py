#!/usr/bin/env python3
"""
2026-10-26 批次修正脚本（在 mcp_inject 之后执行，避免注入覆盖）
1. 欧元区 10 月 PMI 初值 3 事件回填（10/23 16:00 BJS 发布，全部不及预期）：
   Mfg 52.4（fc 52.7/prev 52.9）、Svc 51.7（fc 52.5/prev 53.0）、Comp 51.9（fc 52.7/prev 53.1）
   来源：新华财经 cnfin + 金十 + TradingEconomics 3 源一致 ✅
   period 2026-09→2026-10、release_time 10:00→16:00（重申 10/23 修复，上周被 mcp_inject 覆盖回滚）
2. 密歇根 10 月终值回填 48.1（初值 46.3 大幅上修 +1.8 点，与 9 月终值持平）
   1 年通胀预期终值 4.6%（初值 4.7 下调）、5 年 3.4%（初值 3.5 下调）；9 月终值 48.1 口径由 TE 裁决
   来源：TradingEconomics 终值行（single aggregator，UMich 官网 10/23 10am ET 发布）
3. JP_CPI_20261023 previous 1.7→1.9 恢复（westock 注入覆盖了 10/23 核实值 1.9；notes 明确"前值1.9"）
4. US_JOBLESS_CLAIMS_20261022 补双源验证 notes（19.4 万：westock+新华财经+财联社+FRED 4 源 ✅）
5. 补录 US_PMI_FLASH_20261023（S&P 综合PMI初值，10/23 21:45 BJS）：
   综合 57.6（fc 57.6/prev 58.4）、服务业 57.9（fc 58.0）、制造业 56.0（fc 55.5，2022年5月来最高）
   来源：华尔街见闻+Econoday(共识)+TE ✅；企业售价涨幅创 2022 年 8 月来最高——通胀压力升温
6. 补录 UK_RETAIL_SALES_20261023（9 月零售，10/23 14:00 BJS）：环比 -0.4%（fc -0.1/prev 0.5），
   同比 +0.8%；ONS 官方，腾讯/东财/华尔街见闻/TE 4 源 ✅
7. 补录 CA_RETAIL_SALES_20261023（8 月终值+9 月初值，10/23 20:30 BJS）：
   8 月 +1.2%（fc 1.3/7 月 -0.7）、9 月初值 +0.7%；investing+汇通财经 2 源 ✅
8. 预填今晚/明日共识：耐用品订单 fc 1.8（腾讯 1.8/东财 1.5 分歧标注）、新屋销售 fc 65 万套、
   谘商会消费者信心 fc 81（共识 80.8~81）
9. US_PENDING_HOME_SALES_20261020 标注 westock 单源
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

# 1) 欧元区 10 月 PMI 初值 3 事件
eu_fix = {
    "EU_PMI_MFG_FLASH_20261023": (52.4,
        "10月制造业PMI初值52.4，不及预期52.7，前值52.9——回落但连续处扩张区间；"
        "德国54.2超预期53.5(前53.9)、法国49.3(前50.6)回落至荣枯线下。"
        "来源：新华财经cnfin+金十+TradingEconomics 3源一致✅(16:00 BJS/10:00 CEST发布)"),
    "EU_PMI_SVC_FLASH_20261023": (51.7,
        "10月服务业PMI初值51.7，不及预期52.5，前值53.0(10个月高位)——明显降温；"
        "德国51.7(前52.9)、法国48.4(前51.2)双双走弱，法国跌入收缩。"
        "来源：新华财经cnfin+金十+TradingEconomics 3源一致✅"),
    "EU_PMI_COMPOSITE_FLASH_20261023": (51.9,
        "10月综合PMI初值51.9，不及预期52.7，前值53.1——三项全数低于预期，欧元区扩张动能边际放缓；"
        "德国52.8(前53.8)、法国48.4(前51.1)大幅走弱拖累。"
        "来源：新华财经cnfin+金十+TradingEconomics 3源一致✅；周末数据，10/26晨回填"),
}
for eid, (actual, notes) in eu_fix.items():
    e = by_id.get(eid)
    assert e is not None, f"{eid} not found"
    e["period"] = "2026-10"
    e["release_time"] = "16:00"
    e["timezone"] = "BJS"
    e["actual"] = actual
    e["status"] = "released"
    e["notes"] = notes
    changed.append(eid)

# 2) 密歇根 10 月终值
e = by_id.get("US_MICHIGAN_SENTIMENT_20261023")
assert e is not None, "US_MICHIGAN_SENTIMENT_20261023 not found"
e["actual"] = 48.1
e["status"] = "released"
e["notes"] = (
    "10月终值48.1，较初值46.3大幅上修1.8点，与9月终值持平(预期46.3)；现况指数终值50.9(初值44.7创纪录低位，大幅上修)、"
    "预期指数终值46.3(初值47.3)。通胀预期终值双双下调：1年期4.6%(初值4.7)、5年期3.4%(初值3.5)，仍远高于Fed目标。"
    "⚠️9月终值口径分歧(46.3 vs 48.1)由TE终值行裁决：9月终值48.1、10月终值前值=10月初值46.3——10/10批分歧结案。"
    "来源：TradingEconomics终值行(UMich官网10/23 22:00 BJS发布)；周末数据，10/26晨回填"
)
changed.append("US_MICHIGAN_SENTIMENT_20261023")

# 3) JP_CPI previous 恢复 1.9（westock 注入覆盖回滚，且值系字符串类型）
e = by_id.get("JP_CPI_20261023")
assert e is not None, "JP_CPI_20261023 not found"
if float(e.get("previous")) == 1.7:
    e["previous"] = 1.9
    e["actual"] = float(e.get("actual"))
    changed.append("JP_CPI_20261023:previous '1.7'→1.9")

# 4) 初请 19.4 万双源验证 notes
e = by_id.get("US_JOBLESS_CLAIMS_20261022")
assert e is not None
e["notes"] = (
    "至10/17当周初请19.4万(预期20.0/前值19.9)，减少6000人创三个月新低、逼近约57年低点；"
    "四周均值19.78万(前19.85)；续请172.8万(+2.5万超预期172)。前值19.9万当周修正至20.0(FRED口径)，previous保留原报。"
    "双源验证✅：westock(westock CLI)+新华财经+财联社+FRED(194,000) 4源一致；"
    "市场：10月按兵不动概率92.8%、12月加息25bp概率74.8%"
)
changed.append("US_JOBLESS_CLAIMS_20261022")

# 5) 补录美 S&P PMI 初值
if "US_PMI_FLASH_20261023" not in by_id:
    events.append({
        "id": "US_PMI_FLASH_20261023",
        "country": "US", "country_name": "美国",
        "indicator": "S&P Global 综合PMI 初值",
        "indicator_en": "S&P Global US Composite PMI Flash",
        "frequency": "月度", "importance": 2,
        "release_date": "2026-10-23", "release_time": "21:45", "timezone": "BJS",
        "period": "2026-10", "source": "S&P Global", "unit": "",
        "actual": 57.6, "forecast": 57.6, "previous": 58.4,
        "status": "released",
        "notes": (
            "10月综合PMI初值57.6，符合预期57.6，前值58.4(近五年高位)；制造业56.0大超预期55.5(前55.9)，2022年5月来最高；"
            "服务业57.9略不及预期58.0(前58.8)。⚠️企业销售价格涨幅升至2022年8月来最高(油价+原材料+运输成本传导)——"
            "与FOMC黑箱期(10/28决议，12月加息概率74.8%)通胀担忧共振。新订单增速逾四年半新高、就业增速2022年6月来次高、"
            "积压订单2022年5月来最大增幅；Williamson：对应Q4开局GDP年化约5%。"
            "来源：华尔街见闻+Econoday(共识)+TradingEconomics 3源✅；日历外补录(模式生成缺10月)"
        ),
    })
    changed.append("+US_PMI_FLASH_20261023")

# 6) 补录英国 9 月零售
if "UK_RETAIL_SALES_20261023" not in by_id:
    events.append({
        "id": "UK_RETAIL_SALES_20261023",
        "country": "UK", "country_name": "英国",
        "indicator": "零售销售（环比）",
        "indicator_en": "Retail Sales MoM",
        "frequency": "月度", "importance": 2,
        "release_date": "2026-10-23", "release_time": "14:00", "timezone": "BJS",
        "period": "2026-09", "source": "ONS 英国国家统计局", "unit": "%",
        "actual": -0.4, "forecast": -0.1, "previous": 0.5,
        "status": "released",
        "notes": (
            "9月零售销售量环比-0.4%，不及预期-0.1%，前值0.5%(8月修订后+0.7%)；同比+0.8%(预期1.0)；"
            "剔除燃料环比-0.7%。Q3零售量环比+0.7%、同比+1.5%。"
            "来源：ONS官方(腾讯/东方财富转述)+华尔街见闻+TradingEconomics 4源✅；日历外补录"
        ),
    })
    changed.append("+UK_RETAIL_SALES_20261023")

# 7) 补录加拿大 8 月零售终值 + 9 月初值
if "CA_RETAIL_SALES_20261023" not in by_id:
    events.append({
        "id": "CA_RETAIL_SALES_20261023",
        "country": "CA", "country_name": "加拿大",
        "indicator": "零售销售（环比，8月终值）",
        "indicator_en": "Retail Sales MoM Final",
        "frequency": "月度", "importance": 2,
        "release_date": "2026-10-23", "release_time": "20:30", "timezone": "BJS",
        "period": "2026-08", "source": "加拿大统计局", "unit": "%",
        "actual": 1.2, "forecast": 1.3, "previous": -0.7,
        "status": "released",
        "notes": (
            "8月零售环比终值+1.2%(预期1.3/7月-0.7%)，核心(剔除汽车)+0.7%；同日发布的9月初值+0.7%延续扩张。"
            "背景：9月CPI 3.1%(汽油+27.8%推动)、9月就业-6.83万，BoC 10/28决议市场定价加息25bp概率约80%。"
            "来源：investing.com日历表+汇通财经 2源✅；日历外补录"
        ),
    })
    changed.append("+CA_RETAIL_SALES_20261023")

# 8) 预填今晚/明日共识
e = by_id.get("US_DURABLE_GOODS_20261026")
assert e is not None
e["forecast"] = 1.8
e["notes"] = (
    "9月耐用品订单环比共识+1.8%(腾讯美股周报) vs +1.5%(东方财富前瞻)——分歧标注；"
    "剔除运输+0.6%；⚠️前值口径分歧：8月0.0%(tradingcharts) vs -0.1%(东财)，实际发布核对。今晚20:30 BJS发布"
)
changed.append("US_DURABLE_GOODS_20261026")

e = by_id.get("US_NEW_HOME_SALES_20261026")
assert e is not None
e["forecast"] = 65.0
e["notes"] = "9月新屋销售年化共识65万套(腾讯美股周报)，环比约-5%；prev=8月68.4万套。今晚22:00 BJS发布"
changed.append("US_NEW_HOME_SALES_20261026")

e = by_id.get("US_CONSUMER_CONF_20261027")
assert e is not None
e["forecast"] = 81.0
e["notes"] = "10月谘商会消费者信心共识81(东财)/80.8(腾讯)——处2014年来最低区域；prev=9月81.9。明日22:00 BJS发布"
changed.append("US_CONSUMER_CONF_20261027")

# 9) 成屋签约 westock 单源标注
e = by_id.get("US_PENDING_HOME_SALES_20261020")
assert e is not None
if e.get("notes") and "单源" not in e["notes"]:
    e["notes"] += "；actual 66.0 系 westock 单源⚠️(10/26 注入，未双源验证)"
    changed.append("US_PENDING_HOME_SALES_20261020:单源标注")

# ===== 写回 + 回读验证 =====
with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

with open(CAL, "r", encoding="utf-8") as f:
    cal2 = json.load(f)
m = {e["id"]: e for e in cal2["events"]}
assert m["EU_PMI_MFG_FLASH_20261023"]["actual"] == 52.4 and m["EU_PMI_MFG_FLASH_20261023"]["period"] == "2026-10"
assert m["EU_PMI_SVC_FLASH_20261023"]["actual"] == 51.7
assert m["EU_PMI_COMPOSITE_FLASH_20261023"]["actual"] == 51.9 and m["EU_PMI_COMPOSITE_FLASH_20261023"]["release_time"] == "16:00"
assert m["US_MICHIGAN_SENTIMENT_20261023"]["actual"] == 48.1
assert m["JP_CPI_20261023"]["previous"] == 1.9
assert float(m["US_JOBLESS_CLAIMS_20261022"]["actual"]) == 19.4
assert m["US_PMI_FLASH_20261023"]["actual"] == 57.6
assert m["UK_RETAIL_SALES_20261023"]["actual"] == -0.4
assert m["CA_RETAIL_SALES_20261023"]["actual"] == 1.2
assert m["US_DURABLE_GOODS_20261026"]["forecast"] == 1.8
assert m["US_NEW_HOME_SALES_20261026"]["forecast"] == 65.0
assert m["US_CONSUMER_CONF_20261027"]["forecast"] == 81.0
print("ALL OK")
print("changed:", changed)
print("total events:", len(cal2["events"]))
released = sum(1 for e in cal2["events"] if e.get("status") == "released")
print("released:", released)
