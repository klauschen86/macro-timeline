#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-09-08 回填9/7实际值 + 补录9/8今日发布事件（联网多源核实）
背景: run_daily [Today] 为空，但核实今日确有发布(日历缺中国贸易/日本GDP二次速报等模式)。

数据源与数值:
【9/7 回填 - 4项】
1. 中国8月末外汇储备 34383亿美元 (+195亿/+0.57%)  ✅ SAFE官网+人民网+央广网+中国经济网 4源
2. 中国8月末黄金储备 7673万盎司 (+65万, 连续22个月增持)  ✅ 人民网/央广网/证券日报 多源
3. 欧元区Q2 GDP终值环比 0.6% (初值0.4%上修; 同比+1.2%)  ✅ 新华财经+Goldman Sachs 双源
4. 欧元区7月零售销售: 实际9/4已发布 → 日期修正9/7→9/4, 环比-0.6%(预期+0.2%), 同比+0.6%(预期1.1%)  ✅ 南方财经
【9/8 新增事件】
5. 日本7月经常账户顺差 2.99万亿日元 (预估2.85万亿; 贸易逆差3999亿) 07:50已发  ✅ 腾讯/新浪 双源
6. 日本Q2 GDP二次速报: 环比+0.4%(上修), 年率+1.4%(预估1.8%), 名义环比+1.3%  ✅ 每经/日本观察
7. 中国8月贸易帐: 出口同比fc 25%(招商~22%/机构~25%), 进口同比fc 30%, 顺差fc 1190亿美元(Econoday 1233) — 今日待定(约11:00)
   ⚠️ 警惕: 外贸圈日报混入2025年数据(29.57万亿/3.87万亿为2025-09旧闻), 禁止回填
8. 日本7月贸易帐07:50(并入经常账户notes)/德国7月贸易帐14:00/法国7月贸易帐14:45
9. 美国8月NFIB小企业信心 18:00 / 纽约联储1年通胀预期 23:00
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")
d = json.load(open(CAL, encoding="utf-8"))
evs = d["events"]
by_id = {e["id"]: e for e in evs}

def upd(eid, **kw):
    if eid not in by_id:
        print(f"  !! NOT FOUND: {eid}")
        return
    e = by_id[eid]
    for k, v in kw.items():
        if e.get(k) != v:
            print(f"  ~ {eid} [{k}]: {e.get(k)!r} -> {v!r}")
            e[k] = v
        else:
            print(f"  = {eid} [{k}] already {v!r}")

def add(**kw):
    eid = kw["id"]
    if eid in by_id:
        print(f"  !! EXISTS: {eid}")
        return
    base = {"frequency": "月度", "importance": 2, "timezone": "BJS",
            "source_url": "", "unit": "", "status": "pending",
            "actual": None, "forecast": None, "previous": None, "notes": ""}
    base.update(kw)
    evs.append(base)
    by_id[eid] = base
    print(f"  + ADDED: {eid} ({base['indicator']})")

# ---- 9/7 回填 ----
upd("CN_FX_RESERVES_20260907", actual="34383", status="released",
    notes="8月末外储34383亿美元, 较7月末+195亿/+0.57% (9/7 16:00发布; SAFE官网+人民网+央广网+中国经济网 4源✅); 连续4个月站上3.4万亿")
upd("CN_GOLD_RESERVES_20260907", actual="7673", status="released",
    notes="8月末黄金储备7673万盎司, 环比+65万盎司, 央行连续22个月增持 (9/7 16:00发布; 人民网/央广网/证券日报 多源✅)")
upd("EU_GDP_20260907", actual="0.6", status="released",
    notes="Q2 GDP环比终值0.6%, 由初值0.4%上修(爱尔兰上修), 同比+1.2% (9/7 17:00 BJS发布; 新华财经+Goldman 双源✅); 库存拖累-0.5pct, 净出口贡献+0.9pct")
upd("EU_RETAIL_20260907", release_date="2026-09-04", actual="-0.6", forecast="0.2", status="released",
    notes="7月零售销售环比-0.6%(预期+0.2%), 同比+0.6%(预期1.1%, 前值0.7%) — 实际发布日为9/4 17:00 BJS, 原日期9/7有误已修正 (南方财经✅)")

# ---- 9/8 新增事件 ----
# 日本 (今日已发布)
add(id="JP_CURRENT_ACCOUNT_20260908", country="JP", country_name="日本",
    indicator="经常帐（万亿日元）", indicator_en="Current Account (JPY Tn)",
    importance=2, release_date="2026-09-08", release_time="07:50",
    period="2026-07", source="日本财务省", unit="万亿日元",
    status="released", actual="2.99", forecast="2.85",
    notes="7月经常账户顺差2.99万亿日元, 高于预估2.85万亿 (9/8 07:50发布; 腾讯/新浪 双源✅); 贸易逆差3999亿日元(预估3855亿), 出口+24.1%/进口+25.9%")
add(id="JP_GDP_Q2_20260908", country="JP", country_name="日本",
    indicator="GDP二次速报（环比%）", indicator_en="GDP QoQ 2nd Estimate",
    importance=3, release_date="2026-09-08", release_time="08:50",
    period="2026-Q2", source="日本内阁府", unit="%",
    status="released", actual="0.4", forecast="0.4", previous="0.2",
    notes="Q2实际GDP二次速报环比+0.4%(较初值上修), 年率+1.4%低于预估1.8%; 名义GDP环比+1.3%符合预期 (9/8发布; 每经/日本观察 双源一致✅)")
# 中国贸易 (今日待定, 约11:00)
add(id="CN_TRADE_BALANCE_20260908", country="CN", country_name="中国",
    indicator="贸易帐（亿美元）", indicator_en="Trade Balance (USD bn)",
    importance=3, release_date="2026-09-08", release_time="11:00",
    period="2026-08", source="海关总署", unit="亿美元",
    status="upcoming", forecast="1190", previous="1125",
    notes="8月贸易帐今日待定发布; 机构预期顺差1190亿美元左右(Econoday共识1233亿); ⚠️ 外贸圈日报混入2025年数据(29.57万亿), 禁止回填")
add(id="CN_EXPORTS_20260908", country="CN", country_name="中国",
    indicator="出口同比（按美元计）", indicator_en="Exports YoY (USD)",
    importance=3, release_date="2026-09-08", release_time="11:00",
    period="2026-08", source="海关总署", unit="%",
    status="upcoming", forecast="25", previous="23.9",
    notes="8月出口同比机构预期25%左右(招商证券~22%, 新出口订单50.1%重返扩张)")
add(id="CN_IMPORTS_20260908", country="CN", country_name="中国",
    indicator="进口同比（按美元计）", indicator_en="Imports YoY (USD)",
    importance=2, release_date="2026-09-08", release_time="11:00",
    period="2026-08", source="海关总署", unit="%",
    status="upcoming", forecast="30", previous="27.5",
    notes="8月进口同比机构预期30%左右(东方金诚; 集成电路进口高增+低基数)")
# 欧洲贸易帐
add(id="DE_TRADE_20260908", country="DE", country_name="德国",
    indicator="季调后贸易帐（亿欧元）", indicator_en="Trade Balance s.a. (EUR bn)",
    importance=1, release_date="2026-09-08", release_time="14:00",
    period="2026-07", source="德国联邦统计局", unit="亿欧元",
    status="upcoming", notes="7月季调后贸易帐 14:00 BJS")
add(id="FR_TRADE_20260908", country="FR", country_name="法国",
    indicator="贸易帐（亿欧元）", indicator_en="Trade Balance (EUR bn)",
    importance=1, release_date="2026-09-08", release_time="14:45",
    period="2026-07", source="法国海关", unit="亿欧元",
    status="upcoming", notes="7月贸易帐 14:45 BJS")
# 美国
add(id="US_NFIB_20260908", country="US", country_name="美国",
    indicator="NFIB小型企业信心指数", indicator_en="NFIB Small Business Optimism",
    importance=2, release_date="2026-09-08", release_time="18:00",
    period="2026-08", source="NFIB", unit="",
    status="upcoming", notes="8月NFIB小企业乐观程度指数 18:00 BJS")
add(id="US_NYFED_1Y_INFLATION_20260908", country="US", country_name="美国",
    indicator="纽约联储1年通胀预期", indicator_en="NY Fed 1-Yr Inflation Expectations",
    importance=2, release_date="2026-09-08", release_time="23:00",
    period="2026-08", source="纽约联储", unit="%",
    status="upcoming", notes="8月纽约联储1年通胀预期 23:00 BJS; 9/16 FOMC 前通胀观察项")

json.dump(d, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nDone. total {len(evs)} events")
