# -*- coding: utf-8 -*-
"""_fix_20260917.py — 回填 9/16-9/17 发布的 actual + 补录英美日缺失事件
回填项（多源 ✅）：
1. 美 8 月零售销售 +1.2%（Census 官方 $773.9bn，9/16 20:30 BJS；共识 0.8 大超，7月上修-0.5；控制组+1.2%；3源✅）
2. FOMC 9/17 凌晨决议：加息 25bp 至 3.75%-4.00%（12:0 全票；点阵图 2026 中值 4.10%；沃什鹰派发布会；4+源✅）
3. 英 8 月 CPI 3.1%（ONS 官方 9/16 14:00 BJS 发布；核心 2.6% 持平；4源✅）
补录项：UK_BOE 今晚决议 / JP_BOJ+JP_CPI(9/18) / 美新屋开工·建筑许可·费城联储(今晚) / 美工业产出(9/18)
清理项：UK_CPI_20260917、JP_CPI_20260925 模式误置重复事件（已加 DATE_OVERRIDES 根治，不会再生）
"""
import json

CAL = 'data/calendar.json'
cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events']

# ---------- 1. 回填 ----------
UPDATES = {
    'US_RETAIL_20260916': {
        'actual': 1.2, 'forecast': 0.8, 'previous': -0.5,
        'notes': '8月零售销售环比+1.2%至$773.9bn（大超共识0.8%，创3月以来新高；同比+6.0%；7月由-0.6上修至-0.5）。控制组（剔除汽车/汽油/建材/餐饮）同样+1.2%，排除纯油价效应；扣除汽车+?未列。发布后现货黄金短线走高、美元微跌（数据先于FOMC）。来源：Census官方CB26-153+腾讯财经+regardsofwallstreet 3源✅（westock/妙想/tdx MCP宏观工具连续第17天未暴露，交叉验证以官方源多源Web替代）',
    },
    'US_FOMC_2026-09-17': {
        'actual': 4.0, 'forecast': 4.0, 'previous': 3.75,
        'notes': 'FOMC以12:0全票通过加息25bp，联邦基金利率目标区间3.50-3.75%→3.75-4.00%（3年来首次加息，符合预期；决议前FedWatch加息概率92.5%）。点阵图：2026年底中值3.75%→4.10%（18人中12人预计年内再加一次、4人两次、2人不加、无人预计降息）；2027中值3.6%→4.1%（移除明年降息）；上调今明两年GDP预期、2026失业率中值4.3%→4.1%、上调PCE通胀预期。沃什发布会鹰派："通胀太高且已持续太久"，夏季通胀数据未见实质改善。市场反应：美股尾盘跳水（道指-1.21%创6月中旬来新低/标普-0.45%/纳指-0.01%）、现货黄金一度跌超1%至4240下方、白银-2%、美元指数站上100、10Y美债收益率会前触及5.02%（2007年来最高）；CME 10月再加息概率>53%，交易员押注年底前再加息两次（大摩预测12月再加25bp）。来源：央视新闻+中新网+腾讯财经+财联社+regardsofwallstreet 5源✅',
    },
    'UK_CPI_20260916': {
        'actual': 3.1, 'forecast': 3.1, 'previous': 2.9,
        'notes': '英国8月CPI同比+3.1%（符合预期，连续第2月回升，5个月新高；7月2.9%）。环比+0.5%（4个月最快）。核心CPI 2.6%持平、服务通胀3.4%持平（核心压力未扩大）；商品通胀2.2%→2.7%（2025年9月来最高）。主因中东局势推高油价：机动车燃料同比+23.0%（前+15.5%），汽油161.3便士/升为2022年11月来最高。CPIH 3.3%。今晚19:00英央行决议：市场预期维持3.75%（交易员定价~20%加息概率+年底前两次加息75%，Reuters）；BoE自身预测通胀Q4见顶~3.2%。来源：ONS官方+中新社+新华财经+BabyPips 4源✅',
    },
    'US_JOBLESS_CLAIMS_20260917': {
        'previous': 20.6,
        'notes': '今晚20:30 BJS发布（前值20.6万为9/10当周实际值）。与8月营建许可、新屋开工、费城联储制造业指数同时段发布。',
    },
}

n = 0
for e in events:
    u = UPDATES.get(e.get('id'))
    if not u:
        continue
    for k in ('actual', 'forecast', 'previous'):
        if k in u and e.get(k) is None:
            e[k] = u[k]
    if u.get('actual') is not None:
        e['status'] = 'released'
    old = e.get('notes', '')
    add = u['notes']
    e['notes'] = (old + ' | ' + add) if old and old != add else add
    n += 1
print(f'backfilled {n} events')

# ---------- 2. 删除模式误置重复事件 ----------
DROP = {'UK_CPI_20260917', 'JP_CPI_20260925'}
before = len(events)
events[:] = [e for e in events if e.get('id') not in DROP]
print(f'removed {before - len(events)} duplicate events: {sorted(DROP)}')

# ---------- 3. 补录缺失事件 ----------
def mk(id, country, cname, indicator, indicator_en, date, time, imp, unit, source, notes, fc=None, prev=None):
    return {
        'id': id, 'country': country, 'country_name': cname,
        'indicator': indicator, 'indicator_en': indicator_en,
        'release_date': date, 'release_time': time, 'importance': imp,
        'status': 'upcoming', 'unit': unit, 'source': source,
        'forecast': fc, 'previous': prev, 'notes': notes,
    }

ADDS = [
    mk('UK_BOE_20260917', 'UK', '英国', '英国央行利率决议', 'BOE Rate Decision',
       '2026-09-17', '12:00', 3, '%', 'Bank of England',
       '今晚12:00 BST（19:00 BJS）决议。现行利率3.75%（2025年12月以来维持）。8月CPI回升至3.1%但核心2.6%持平，市场预期维持不变（交易员定价~20%加息概率、年底前累计两次加息75%，Reuters/BabyPips 2026-09-16）；BoE 7月预测通胀Q4见顶~3.2%。来源：BabyPips+中新社+新华财经 多源✅',
       fc=None, prev=3.75),
    mk('JP_BOJ_20260918', '日本', '日本', '日本央行利率决议', 'BOJ Rate Decision',
       '2026-09-18', '11:00', 3, '%', 'Bank of Japan',
       '9/18决议（BJS时间待核，记者会15:30）。现行政策利率1.0%，市场共识与预测均为加息至1.25%（MoneyDJ 2026-09-16）；植田和男记者会聚焦后续加息节奏。',
       fc=1.25, prev=1.0),
    mk('US_HOUSING_STARTS_20260917', '美国', '美国', '新屋开工（年化）', 'Housing Starts',
       '2026-09-17', '20:30', 2, '百万套', 'U.S. Census Bureau',
       '8月新屋开工，与初请/建筑许可/费城联储同时段（20:30 BJS）。7月前值1.239M（环比-12.4%），8月市场预估1.322M。来源：经济通etnet 2026-09-16数据表+MoneyDJ预告 双源✅',
       fc=1.322, prev=1.239),
    mk('US_BUILDING_PERMITS_20260917', '美国', '美国', '建筑许可', 'Building Permits',
       '2026-09-17', '20:30', 2, '%', 'U.S. Census Bureau',
       '8月建筑许可（月率口径），与初请/新屋开工/费城联储同时段。7月环比+5.0%，8月预估未列。来源：经济通etnet 2026-09-16数据表 ✅',
       fc=None, prev=5.0),
    mk('US_PHILLY_FED_20260917', '美国', '美国', '费城联储制造业指数', 'Philly Fed Manufacturing Index',
       '2026-09-17', '20:30', 2, '指数', 'Philadelphia Fed',
       '9月费城联储制造业指数，与初请/营建/新屋开工同时段（MoneyDJ 2026-09-14/16 预告）。预期与前值待发布核实。',
       fc=None, prev=None),
    mk('US_INDUSTRIAL_PRODUCTION_20260918', '美国', '美国', '工业产出（月率）', 'Industrial Production MoM',
       '2026-09-18', '21:15', 2, '%', 'Federal Reserve',
       '8月工业产出月率，9/18 21:15 BJS。7月+0.2%，8月预估+0.3%（产能利用率预估76.5%/前值76.3%）。来源：经济通etnet 2026-09-16数据表 ✅',
       fc=0.3, prev=0.2),
]

existing = {e.get('id') for e in events}
added = 0
for ev in ADDS:
    if ev['id'] not in existing:
        events.append(ev)
        added += 1
print(f'added {added} events')

# ---------- 4. 统计 ----------
cal['events'] = events
json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
rel = sum(1 for e in events if e.get('status') == 'released')
print(f'Released: {rel}, total {len(events)}')
