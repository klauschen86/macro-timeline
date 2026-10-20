# -*- coding: utf-8 -*-
"""2026-10-20 回填 10/19 统计局三季度数据 + 10/20 LPR（多源官方核实）"""
import json

CAL = 'data/calendar.json'
cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events'] if isinstance(cal, dict) else cal

# 来源（双源交叉验证）：
# 1) 中国 Q3 数据: 统计局官网 10-19 10:00 发布（stats.gov.cn t20261019_1965618 一手）
#    + 光明网/中国证券网/央视网多源一致 ✅
# 2) 中国 10月 LPR: 央行授权全国银行间同业拆借中心 10-20 09:00 公布
#    澎湃/中新经纬/封面新闻/大河财立方多源一致 ✅（westock CLI feed 滞后"未公布"，以官方公布为准）
fixes = {
    'CN_GDP_20261019': {
        'actual': 4.5, 'status': 'released',
        'note': '2026-10-20回填: Q3 GDP同比4.5%(共识4.4,超预期✅/前值4.3回升0.2pct),环比+1.2%; 前三季累计4.6%(107.11万亿元)符合全年目标,回到4.5~5%目标区间下沿; 一产3.6%/二产3.4%/三产5.2%; 统计局官网一手(stats.gov.cn 10-19 10:00)+光明网/中证网/央视网多源✅'
    },
    'CN_INDUSTRIAL_20261019': {
        'actual': 5.5, 'status': 'released',
        'note': '2026-10-20回填: 9月规上工业增加值同比5.5%(共识5.6,略低0.1pct⚠️/前值5.2加快0.3pct); 制造业6.0%/采矿业1.3%/电热气水5.6%; 出口交货值17132亿+17.0%; 前三季累计5.3%; 统计局官网一手+多源✅'
    },
    'CN_RETAIL_20261019': {
        'actual': 1.1, 'status': 'released',
        'note': '2026-10-20回填: 9月社零同比1.1%(共识0.7,超预期✅/前值0.4加快0.7pct); 9月绝对量42433亿元; 餐饮+2.1%/商品零售+1.0%; 前三季累计370001亿+1.1%; 统计局官网一手+多源✅'
    },
    'CN_FAI_20261019': {
        'actual': -7.2, 'status': 'released',
        'note': '2026-10-20回填: 1-9月固投累计同比-7.2%(共识-7.3,略好✅/与1-8月持平); 总额334115亿元; 一产-3.9%/二产-2.7%/三产-10.0%; 房地产开发投资53364亿-20.6%仍为主要拖累; 9月固投环比+0.07%; 统计局官网一手+多源✅'
    },
    'CN_UNEMPLOYMENT_20261019': {
        'actual': 5.2, 'status': 'released',
        'note': '2026-10-20回填: 9月城镇调查失业率5.2%(前值5.3回落0.1pct); 31大城市5.2%持平; 前三季均值5.2%与上年同期持平; 统计局官网一手+多源✅'
    },
    'CN_LPR_1Y_20261020': {
        'actual': 3.0, 'status': 'released',
        'note': '2026-10-20回填: 10月1年期LPR 3.0%持平(预期3.0✅/前值3.0),连续第17个月不变(自2025-06); 央行授权全国银行间同业拆借中心09:00公布; 7天逆回购1.40%未动,定价基础未变,Q3 GDP 4.5%超预期进一步降低降息紧迫性; 澎湃/中新经纬/大河财立方多源✅(westock CLI feed滞后标"未公布",以央行官方公布为准)'
    },
    'CN_LPR_5Y_20261020': {
        'actual': 3.5, 'status': 'released',
        'note': '2026-10-20回填: 10月5年期以上LPR 3.5%持平(预期3.5✅/前值3.5),连续第17个月不变,上次调整为2025-05各降10bp; 央行授权公布,澎湃/中新经纬多源✅'
    },
}

n = 0
for e in events:
    if e['id'] in fixes:
        f = fixes[e['id']]
        e['actual'] = f['actual']
        e['status'] = f['status']
        e['notes'] = e.get('notes', '') + ' | ' + f['note']
        n += 1

# UK 9月 CPI 日期修正: ONS 官网日程确证 2026-10-21 07:00 BST 发布（statistics.gov.uk release date 21 Oct confirmed）
# 原模式日期 10-19 偏早。注入共识（FactSet economist average + TradingCharts 日历）。
for e in events:
    if e['id'] == 'UK_CPI_20261019':
        e['release_date'] = '2026-10-21'
        e['forecast'] = 3.5
        e['previous'] = 3.1
        e['notes'] = e.get('notes', '') + ' | 2026-10-20日期修正: ONS官网日程确证9月CPI为10/21(周三)07:00 BST发布,原模式日期10/19偏早; 共识3.5%(8月3.1%,10个月新高,FactSet),核心CPI共识2.8%(前2.6%),燃油价格(美伊冲突油价)主拉动; BoE 11/5议息加息预期强化(3.75%→4%),德银预测3.49%/核心2.74%; 实际值待10/21发布后补采'
        n += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'backfilled/updated {n} events')
