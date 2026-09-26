# -*- coding: utf-8 -*-
"""_fix_20260926.py — 回填 9/25 晚两项发布（周六晨执行）
1. US_DURABLE_GOODS_20260925: actual=0.0（Census官方+Econoday双源✅），prev 1.1→0.9（7月上修）
2. US_MICHIGAN_SENTIMENT_20260925: actual=48.1（UMich官网+新华社+ABC多源✅）
3. 下月同系列事件 prev 链预填
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CAL = 'data/calendar.json'
data = json.load(open(CAL, encoding='utf-8'))
events = data if isinstance(data, list) else data.get('events', data)

def find(eid):
    for e in events:
        if e.get('id') == eid:
            return e
    return None

changed = []

# 1) 耐用品订单 8月（9/25 20:30 BJS 发布）
e = find('US_DURABLE_GOODS_20260925')
if e:
    e['actual'] = 0.0
    e['previous'] = 0.9  # Census：7月上修后口径 +0.9%（初值1.1%）
    e['status'] = 'released'
    e['notes'] = ('8月耐用品订单环比 0.0% 基本持平（Census官方"virtually unchanged $338.6B"+Econoday 双源✅），'
                  '高于预期 -0.4%；⚠️7月由+1.1%上修至+0.9%（previous已同步）。扣除运输 +0.3%（预期+0.5%，略低）；'
                  '扣除国防 +0.1%；核心资本品订单 +1.6% 大超预期 +0.8%（前值上修+0.6%）——企业资本开支亮眼；'
                  '运输设备 -0.6%（四个月内三月下降）为唯一拖累。制造动能整体停滞但内生需求稳健。'
                  '来源：Census.gov 9/25 + Econoday（fefundinfo）✅')
    changed.append(('US_DURABLE_GOODS_20260925', e['actual'], e['previous']))

# 2) 密歇根消费者信心终值 9月（9/25 22:00 BJS 发布）
e = find('US_MICHIGAN_SENTIMENT_20260925')
if e:
    e['actual'] = 48.1
    e['status'] = 'released'
    e['notes'] = ('9月密歇根消费者信心终值 48.1（UMich官网+新华社+ABC 多源✅），略高于初值/预期 47.8，前值 51.7；'
                  '环比 -7.0%、同比 -12.7%，为 74 年调查史上第二低终值（仅高于今年5月纪录低点 44.8）；'
                  '现况指数 50.9（前51.9）、预期指数 46.3（前51.5）。主因：高物价+贸易紧张再升级+利率上升；'
                  '1年通胀预期 4.0%→4.6%（6月来最高，伊朗冲突前2月仅3.4%）、5年期 3.4%（结束连续3个月3.3%）。'
                  '关税自发提及率 24%→35%，55% 消费者视高物价为财务负面因素（前53%）。'
                  '来源：sca.isr.umich.edu + news.umich.edu + 新华社9/25 ✅')
    changed.append(('US_MICHIGAN_SENTIMENT_20260925', e['actual'], e['previous']))

# 3) 下月同系列 prev 链预填（若存在 10 月事件）
for e in events:
    eid = e.get('id', '')
    if eid.startswith('US_DURABLE_GOODS_2026') and eid > 'US_DURABLE_GOODS_20260925' and not e.get('previous'):
        e['previous'] = 0.0
        changed.append((eid + ' [prev预填]', '', 0.0))
    if eid.startswith('US_MICHIGAN_SENTIMENT_2026') and eid > 'US_MICHIGAN_SENTIMENT_20260925' and not e.get('previous'):
        e['previous'] = 48.1
        changed.append((eid + ' [prev预填]', '', 48.1))

json.dump(data, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Changed:', len(changed))
for c in changed:
    print(' ', c)

# 回读核验
data2 = json.load(open(CAL, encoding='utf-8'))
ev2 = data2 if isinstance(data2, list) else data2.get('events', data2)
for eid in ('US_DURABLE_GOODS_20260925', 'US_MICHIGAN_SENTIMENT_20260925'):
    for e in ev2:
        if e.get('id') == eid:
            print('VERIFY', eid, '| actual:', e.get('actual'), '| prev:', e.get('previous'), '| status:', e.get('status'))
