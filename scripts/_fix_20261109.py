# -*- coding: utf-8 -*-
"""2026-11-09 回填与日期根治

回填（多源核实，官方优先）：
1. CN_CPI_20261109: 10月CPI同比 +0.7%（fc 0.8/prev 0.9）
   来源：统计局官网解读页 t20261109_1965796 + 财联社 cls.cn/detail/2528534 + 央广网 3源✅
   （westock CLI 10月行未入库，以官方+多源替代双源）
2. CN_PPI_20261109: 10月PPI同比 +5.7%（fc 5.3/prev 5.0，大超预期）
   来源同上 3源✅
3. CN_FX_RESERVES 日期根治 11-09→11-07（外管局 11/7 周六实际发布；模式 around_day(7) 遇周末
   顺延到 11-9 错位——人民网11/7电+中证网+央广网确认 11/7 发布）：actual 34051.78 亿美元
   （westock EXP 3405178 百万 ✅ 机械双源一致 + 人民网/央广/中证网/中国经济网 4 媒体）
4. CN_GOLD_RESERVES 日期根治同上：actual 7830 万盎司（环比+83万，连续24个月增持；
   人民网/央广网/中证网/中国经济网 4源✅；westock 无该指标）
5. 回填 US_EXISTING_HOME_20261013（10/13 发布一直 pending）：9月成屋销售 399 万套
   （预期 395，8月下修 393；新浪/中国经济信息网+etnet+Yahoo/MoneyDJ 4源✅）

预填（明日 11-10 + prev 链）：
- US_CPI_20261110: fc 3.7 / prev 3.7（TE/工商时报/Alpari 共识持平；克利夫兰联储 3.74；
  ⚠️注意：US_CPI_20261014 actual=0.2 疑为环比口径污染（9月同比 3.7 多源确认），待核遗留）
- US_CORE_CPI_20261110: fc 2.5 / prev 2.6（TE/Alpari/克利夫兰 2.48；Kalshi 2.79 异常弃用）
- CN_TRADE_20261110: fc 1260 亿美元顺差（华泰 11-8）/ prev 1335.3
- US_EXISTING_HOME_20261110: prev 399
- prev 链：CN_CPI_20261209 prev 0.7、CN_PPI_20261209 prev 5.7、
  CN_FX_RESERVES_20261207 prev 34051.78、CN_GOLD_RESERVES_20261207 prev 7830

配套：generate_calendar.py DATE_OVERRIDES 新增 2 条（FX/GOLD 2026-11 → 11-07）防 run_daily 回滚。
执行顺序：本脚本 → run_daily.py → 验证不复活 → commit push。
"""
import json
import sys

CAL = "data/calendar.json"

with open(CAL, encoding="utf-8") as f:
    cal = json.load(f)
events = cal["events"]
by_id = {e["id"]: e for e in events}

changed = []

# ---------- 1. CPI ----------
e = by_id["CN_CPI_20261109"]
assert e["release_date"] == "2026-11-09" and e["period"] == "2026-10"
e.update({
    "actual": 0.7, "forecast": 0.8, "previous": 0.9, "status": "released",
    "notes": "10月CPI同比+0.7%（预期0.8/前值0.9，涨幅回落0.2pct；环比持平由上月+0.2%回落；"
             "核心CPI同比+0.8%回落0.2pct；食品-2.9%/非食品+1.5%；"
             "统计局11/9 09:30发布（2026年官方日程表11月9/一 9:30✅）。"
             "来源：统计局官网解读页+财联社+央广网 3源✅（westock 10月值未入库，官方+多源替代双源）"
             "；1-10月平均同比+0.9%。结构：汽油+22.4%上拉/鲜菜-16.9%猪肉-8.6%下拉，"
             "数据存储设备+45.4%等AI链消费品价格显著上涨。"
})
changed.append(e["id"])

# ---------- 2. PPI ----------
e = by_id["CN_PPI_20261109"]
e.update({
    "actual": 5.7, "forecast": 5.3, "previous": 5.0, "status": "released",
    "notes": "10月PPI同比+5.7%（预期5.3/前值5.0，涨幅扩大0.7pct大超预期⚠️，再创年内新高；"
             "环比+0.7%涨幅回落0.5pct；购进价格同比+7.9%。主因输入性能源：煤炭开采+36.6%/石油天然气开采+35.0%/"
             "石油煤炭加工+29.9%/化学原料+16.4%，9行业合计上拉6.14pct；有色采选+16.3%/冶炼+18.6%涨幅回落；"
             "AI链：电气机械+6.2%/计算机通信电子+5.9%。CPI-PPI剪刀差-5.0pct扩大=上游成本挤压中下游利润。"
             "来源：统计局官网解读页+财联社+央广网 3源✅"
})
changed.append(e["id"])

# ---------- 3/4. 外储+黄金：日期根治 11-09→11-07 ----------
for old_id, new_id, patch in [
    ("CN_FX_RESERVES_20261109", "CN_FX_RESERVES_20261107", {
        "actual": 34051.78, "previous": 34002.51, "status": "released",
        "notes": "10月末外储34051.78亿美元(约3.4052万亿), 较9月末+49.27亿/+0.14%, 连续第7个月站上3.4万亿 "
                 "(外管局11/7周六发布; westock CLI EXP 3405178百万✅机械双源一致+人民网11/7电/央广网/中证网/中国经济网 4媒体✅); "
                 "9月末34002.51 咬合✅(34002.51+49.27); 美元指数上涨+全球资产价格涨跌互现, 汇率折算与资产价格正向; "
                 "日期根治: 外管局11/7(周六)实际发布, 模式around_day(7)遇周末顺延11-9错位, DATE_OVERRIDES已根治"}),
    ("CN_GOLD_RESERVES_20261109", "CN_GOLD_RESERVES_20261107", {
        "actual": 7830, "previous": 7747, "status": "released",
        "notes": "10月末黄金储备7830万盎司, 环比+83万盎司(超9月+74), 连续第24个月增持 "
                 "(外管局11/7同日发布; 人民网/央广网/中证网/中国经济网 4源✅; westock无该指标); "
                 "9月末7747 咬合✅(7747+83); 背景: 10月国际金价-7.2%连续第二个月大幅下降(1月高点5600回撤超30%), "
                 "央行逆势加快增持; 高盛下调2026年底金价目标4650→4150美元; WGC: Q3全球央行购金321吨同比+42%",
    }),
]:
    e = by_id[old_id]
    assert e["release_date"] == "2026-11-09", old_id
    e["id"] = new_id
    e["release_date"] = "2026-11-07"
    e.update(patch)
    by_id.pop(old_id)
    by_id[new_id] = e
    changed.append(f"{old_id}→{new_id}")

# ---------- 5. 回填 US_EXISTING_HOME_20261013 ----------
e = by_id["US_EXISTING_HOME_20261013"]
assert e.get("actual") in (None, "", 0), "already filled?"
e.update({
    "actual": 399, "previous": 393, "status": "released",
    "notes": (e.get("notes") or "") + " | 2026-11-09回填: 9月成屋销售399万套SAAR（预期395/8月下修393，环比+1.5%四个月来首次增长，同比-2.2%；"
             "中位价41.75万美元同比+1.3%创历年9月新高；库存160万套2019-11来最高/4.8个月供应；"
             "30年房贷利率7.4%+2023-11来新高压制。来源：新浪/中国经济信息网+etnet+Yahoo财经/MoneyDJ 4源✅）"
})
changed.append("US_EXISTING_HOME_20261013")

# ---------- 6. 预填明日 11-10 ----------
by_id["US_CPI_20261110"].update({
    "forecast": 3.7, "previous": 3.7,
    "notes": "2026-11-09预填: 10月CPI今晚21:30 BJS(08:30 ET)发布。共识同比3.7%持平9月(TE/工商时报11-8/Alpari 3.7,"
             "克利夫兰联储Nowcasting 3.74,丰云学堂3.75); 环比预期0.2%(9月0.6%五个月新高后大幅回落;CMC 0.3分歧标注); "
             "⚠️口径待核遗留: US_CPI_20261014 actual=0.2 疑为westock注入环比口径(9月同比3.7%工商时报/CMC多源确认), 未盲改;"
             "背景: FOMC 10/28维持利率、12月加息概率85-90%(CME), CPI超预期将强化加息定价"
})
by_id["US_CORE_CPI_20261110"].update({
    "forecast": 2.5, "previous": 2.6,
    "notes": "2026-11-09预填: 核心CPI同比共识2.5%(TE/Alpari 2.5,克利夫兰2.48,丰云2.48;Kalshi 2.79异常弃用⚠️); "
             "环比预期0.2%(9月0.3%回落); 9月核心2.6%(工商时报多源)"
})
by_id["CN_TRADE_20261110"].update({
    "forecast": 1260, "previous": 1335.3,
    "notes": "2026-11-09预填: 10月贸易11:00海关总署发布。华泰11-8预测: 顺差1260亿美元左右(单源⚠️), "
             "出口同比+28.0%(9月36.3%回落)/进口+22.0%(9月31.0%); 韩国10月出口+93.7%佐证AI链景气; "
             "新出口订单PMI 48.7回落1.3pct; prev=9月顺差1335.3(10/14发布)"
})
by_id["US_EXISTING_HOME_20261110"].update({
    "previous": 399,
    "notes": "2026-11-09预填: 10月成屋销售今晚22:00 BJS(10:00 ET,NAR)发布; prev=9月399万套(11-9回填); fc待共识"
})
changed.append("prefill-20261110")

# ---------- 7. prev 链（12月） ----------
by_id["CN_CPI_20261209"]["previous"] = 0.7
by_id["CN_PPI_20261209"]["previous"] = 5.7
by_id["CN_FX_RESERVES_20261207"]["previous"] = 34051.78
by_id["CN_GOLD_RESERVES_20261207"]["previous"] = 7830
changed.append("prev-chain-202612")

# ---------- 写回 + 回读校验 ----------
with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=1)

with open(CAL, encoding="utf-8") as f:
    chk = json.load(f)["events"]
d = {e["id"]: e for e in chk}
assert d["CN_CPI_20261109"]["actual"] == 0.7
assert d["CN_PPI_20261109"]["actual"] == 5.7
assert d["CN_FX_RESERVES_20261107"]["actual"] == 34051.78
assert d["CN_GOLD_RESERVES_20261107"]["actual"] == 7830
assert "CN_FX_RESERVES_20261109" not in d and "CN_GOLD_RESERVES_20261109" not in d
assert d["US_EXISTING_HOME_20261013"]["actual"] == 399
assert d["US_CPI_20261110"]["forecast"] == 3.7
assert d["CN_TRADE_20261110"]["forecast"] == 1260
assert d["CN_CPI_20261209"]["previous"] == 0.7
print("ALL OK:", "; ".join(changed))
