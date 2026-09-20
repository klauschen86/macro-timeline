# -*- coding: utf-8 -*-
"""2026-09-20 修复脚本（周日）：
1. US_EXISTING_HOME 全系列日期错位清理（模式原按每月21日生成，NAR 实际次月10日左右发布）
2. 回填 4-8 月数据 actual 链（FRED EXHOSLUSM495S 官方 + TE/NAR 交叉验证）
3. 补 9/21 LPR 两事件前值与备注（现行 1Y 3.00% / 5Y 3.50%，连续15个月不变）
"""
import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")

with open(CAL, encoding="utf-8") as f:
    d = json.load(f)
evs = d["events"]

# 1) 删除错位旧事件（全部 pending/无 actual，无数据损失；20260610 为 override 键位修正前的重复）
DELETE_IDS = {
    "US_EXISTING_HOME_20251222", "US_EXISTING_HOME_20260121",
    "US_EXISTING_HOME_20260223", "US_EXISTING_HOME_20260323",
    "US_EXISTING_HOME_20260421", "US_EXISTING_HOME_20260521",
    "US_EXISTING_HOME_20260610", "US_EXISTING_HOME_20260622",
    "US_EXISTING_HOME_20260721", "US_EXISTING_HOME_20260821",
    "US_EXISTING_HOME_20260921", "US_EXISTING_HOME_20261021",
}
before = len(evs)
evs = [e for e in evs if e.get("id") not in DELETE_IDS]
print(f"deleted {before - len(evs)} misdated US_EXISTING_HOME events")

# 2) 回填 actual 链（单位：万套；1M units = 100 万套）
BACKFILL = {
    "US_EXISTING_HOME_20260410": {  # 2026-03 数据（约4/10发布）
        "notes": "3月值待核验：review42 二手源 3.98M 与 NAR 4月报告（环比+0.2%至4.02M）隐含初值~4.01M 存在差异，待 FRED 核验后回填（发布日为模式推算约值）",
    },
    "US_EXISTING_HOME_20260511": {  # 2026-04 数据
        "actual": 404, "status": "released",
        "notes": "FRED EXHOSLUSM495S 2026-04=4.04M SAAR（NAR via FRED；NAR 4月报告初值4.02M后上修）；4月环比+0.2%、库存147万套、中位价$417,700(+0.9%)。发布日为模式推算约值待核实。来源：FRED官方+housingbrief ✅",
    },
    "US_EXISTING_HOME_20260609": {  # 2026-05 数据（NAR官方 6/9 新闻稿）
        "actual": 419, "previous": 404, "status": "released",
        "notes": "NAR 官方新闻稿 2026-06-09 发布：环比+3.2%至4.17M初值（2026年内最高），FRED 现值上修 4.19M；同比+3.2%，中位价 $429,300(+1.3%) 连续35个月同比上涨，库存155万套/4.5个月供应，Yun：销量创12月以来新高。来源：NAR官方+FRED ✅",
    },
    "US_EXISTING_HOME_20260710": {  # 2026-06 数据
        "actual": 413, "previous": 419, "status": "released",
        "notes": "FRED EXHOSLUSM495S 2026-06=4.13M SAAR（5月高点后回落-1.4%）。发布日为模式推算约值待核实。来源：FRED官方 ✅",
    },
    "US_EXISTING_HOME_20260811": {  # 2026-07 数据（TE 确认 8/11 发布）
        "actual": 406, "forecast": 405, "previous": 413, "status": "released",
        "notes": "7月环比-1.7%（TE 日历：actual 4.06M / prev 4.13M / consensus 4.05M）；FRED 同值4.06M。来源：TE+FRED 双源 ✅",
    },
    "US_EXISTING_HOME_20260910": {  # 2026-08 数据（9/10 22:00 BJS 已发布）
        "actual": 398, "forecast": 398, "previous": 406, "status": "released",
        "notes": "8月环比-2.0%完全符合预期（TE：actual 3.98M=consensus，prev 4.06M；Sigmanomics 同），连续4个月下滑、6个月低点；东北-4.0%/中西部-3.1%/南部-1.6%/西部持平；库存162万套+3.2%，中位价 $429,100(+1.6%)；Yun：房贷利率上升压制购房（能源成本+企业债供给推升长端收益率）。9/17 FOMC 加息后房贷利率或续升，关注9月数据。来源：FRED(官方9/10更新)+TE+Sigmanomics 3源 ✅",
    },
    "US_EXISTING_HOME_20261013": {  # 2026-09 数据（未发布）
        "previous": 398,
        "notes": "FRED Next Release Date: Oct 13, 2026（10:00 ET = 22:00 BJS）",
    },
}
n_fill = 0
for e in evs:
    p = BACKFILL.get(e.get("id"))
    if p:
        e.update(p)
        n_fill += 1
print(f"backfilled {n_fill} events")

# 3) LPR 前值与备注（financecalendar PBoC-LPR 页 + TradingEconomics + StatRec 3源）
LPR = {
    "CN_LPR_1Y_20260921": {
        "previous": 3.00,
        "notes": "现行1Y LPR 3.00%：2025-05降10bp后连续15个月不变（8/20为第15次按兵不动）；本次为9/17 FOMC加息后首次报价，市场主流预期按兵不动（financecalendar：consensus未发布；TE预测3.50%），关注中美利差走阔下的跟随上调风险。发布9:15 BJS。来源：financecalendar+TradingEconomics+StatRec 3源 ✅",
    },
    "CN_LPR_5Y_20260921": {
        "previous": 3.50,
        "notes": "现行5Y+ LPR 3.50%（历史低位）：与1Y同于2025-05降10bp后连续15个月不变；主流预期按兵不动、TE预测3.50%；5Y+为房贷定价基准，关注地产拖累下的单独下调可能。发布9:15 BJS。来源：financecalendar+TradingEconomics+StatRec 3源 ✅",
    },
}
n_lpr = 0
for e in evs:
    p = LPR.get(e.get("id"))
    if p:
        e.update(p)
        n_lpr += 1
print(f"updated {n_lpr} LPR events")

d["events"] = evs
with open(CAL, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print(f"saved: {len(evs)} events")

# 自检：断言回填链 prev/actual 咬合
m = {e["id"]: e for e in evs if e.get("id", "").startswith("US_EXISTING_HOME_")}
chain = [("US_EXISTING_HOME_20260511", 404), ("US_EXISTING_HOME_20260609", 419),
         ("US_EXISTING_HOME_20260710", 413), ("US_EXISTING_HOME_20260811", 406),
         ("US_EXISTING_HOME_20260910", 398)]
for i in range(1, len(chain)):
    prev_id = chain[i - 1][0]
    cur_id = chain[i][0]
    assert m[cur_id]["previous"] == m[prev_id]["actual"], f"chain broken at {cur_id}"
print("chain check OK: prev/actual 咬合 4/4")
