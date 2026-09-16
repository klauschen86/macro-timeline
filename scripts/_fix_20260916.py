# -*- coding: utf-8 -*-
"""_fix_20260916.py — 回填 2026-09-15 发布的中国 8 月经济数据 actual（4 项）
来源：国家统计局官网 t20260915_1965307 + 中国政府网 content_7081120 + 央视网 + 中国网（4 源 ✅，官方权威）
合理性自检：工业 5.2 官方明言"比上月加快0.7pp"→7月=4.5 与 prev=4.5 咬合 ✅；
社零 0.4<prev 0.6 回落 ✅；固投 -7.2<prev -6.7 续降 ✅；失业率 5.3=prev 5.2+0.1（官方明言）✅
"""
import json, io, sys

CAL = 'data/calendar.json'
cal = json.load(open(CAL, encoding='utf-8'))

UPDATES = {
    'CN_INDUSTRIAL_20260915': {
        'actual': 5.2,
        'notes': '8月规上工业增加值同比+5.2%（环比+0.54%，比上月加快0.7pp；超预期fc4.7）。装备制造业+12.1%、高技术制造业+16.7%；制造业+6.1%、采矿业-1.4%。1-8月+5.3%。来源：统计局官网+gov.cn+央视网+中国网 4源✅(2026-09-15 10:00发布)',
    },
    'CN_RETAIL_20260915': {
        'actual': 0.4,
        'notes': '8月社零总额39824亿元，同比+0.4%（低于预期fc0.8，前值0.6回落；限额以上-3.7%为主要拖累）。1-8月+1.1%；服务零售1-8月+4.9%。来源：统计局官网+gov.cn+央视网+中国网 4源✅',
    },
    'CN_FAI_20260915': {
        'actual': -7.2,
        'notes': '1-8月固投(不含农户)293092亿元，同比-7.2%（低于预期fc-7.0，前值-6.7续降）。第二产业-2.9%/第三产业-9.9%；房地产开发投资-19.9%。高技术产业投资+5.2%。来源：统计局官网+gov.cn+央视网+中国网 4源✅',
    },
    'CN_UNEMPLOYMENT_20260915': {
        'actual': 5.3,
        'notes': '8月城镇调查失业率5.3%（高于预期fc5.2，比上月+0.1pp毕业季季节性；官方明言；31大城市5.3%持平）。30-59岁主体人群3.9%持平。1-8月均值5.2%。来源：统计局官网+gov.cn+央视网+中国网 4源✅',
    },
}

n = 0
for e in cal['events']:
    u = UPDATES.get(e.get('id'))
    if u:
        if e.get('actual') is None:
            e['actual'] = u['actual']
        e['status'] = 'released'
        old_notes = e.get('notes', '')
        e['notes'] = (old_notes + ' | ' if old_notes and old_notes not in u['notes'] else '') + u['notes'] if old_notes != u['notes'] else u['notes']
        n += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'updated {n} events')
rel = sum(1 for e in cal['events'] if e.get('status') == 'released')
print(f'Released: {rel}, total {len(cal["events"])}')
