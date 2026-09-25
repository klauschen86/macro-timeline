# -*- coding: utf-8 -*-
"""2026-09-25 回填补丁：
1) US_JOBLESS_CLAIMS_20260924 actual=19.7（金十+每经双源✅，前值19.6上修至19.8）
2) US_NEW_HOME_SALES_20260924 actual=68.4、prev 60.7→64.3（7月上修，Reuters+Census双源✅）
3) US_DURABLE_GOODS_20260925 fc=-0.4/prev=1.1（Econoday共识）；同步回填 8/26（7月数据）actual=1.1
4) 新增 US_MICHIGAN_SENTIMENT_20260925（今晚22:00 BJS，fc 47.8/prev 51.7）
5) 下周初请 prev=19.7、10月新屋销售 prev=68.4（若事件存在）
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
cal = json.load(open(PATH, encoding='utf-8'))
events = cal['events'] if isinstance(cal, dict) else cal

def find(eid):
    for e in events:
        if e.get('id') == eid:
            return e
    return None

changes = []

# 1) 初请 9/24
e = find('US_JOBLESS_CLAIMS_20260924')
if e and e.get('actual') != 19.7:
    e['actual'] = 19.7
    e['status'] = 'released'
    e['notes'] = ('19.7万（金十+每经 双源✅，预期20.1~20.2）；前值19.6万已修正至19.8万（金十口径，环比-1000人）；'
                  '初请处57年来低位附近，劳动力市场企稳但企业招聘意愿仍弱（金九评）。'
                  + (e.get('notes') or ''))
    changes.append('初请9/24 actual=19.7')

# 2) 新屋销售 9/24
e = find('US_NEW_HOME_SALES_20260924')
if e and e.get('actual') != 68.4:
    e['actual'] = 68.4
    e['previous'] = 64.3
    e['status'] = 'released'
    e['notes'] = ('68.4万套（Reuters/AOL转述Census+RealtyWire 双源✅，预期61.5~61.8大超）；环比+6.4%，'
                  '2025年12月来最高、2026年内最快；⚠️ 7月由60.7万上修至64.3万（prev已同步）；同比-2.0%；'
                  '中位价$393,700（-5.8% y/y）、均价$478,700（-8.8% y/y）——降价+激励驱动；'
                  '库存48.3万套持平、去化8.5个月（前9.0）；中西部+84.9%、东北部-36.1%。'
                  + (e.get('notes') or ''))
    changes.append('新屋销售9/24 actual=68.4 prev=64.3')

# 3) 耐用品订单 9/25 预期
e = find('US_DURABLE_GOODS_20260925')
if e and e.get('forecast') is None:
    e['forecast'] = -0.4
    e['previous'] = 1.1
    e['notes'] = (e.get('notes') or '') + ('Econoday共识-0.4%（区间-1.5~+1.5；OneRoyal偏-0.5）；'
                  '扣除运输fc+0.5/prev+0.4；核心资本品fc+0.8/prev+0.2；前值1.1=7月环比（Econoday Prior口径，同步回填8/26事件）。')
    changes.append('耐用品9/25 fc=-0.4 prev=1.1')

# 3b) 回填 7月耐用品订单（8/26发布）
e = find('US_DURABLE_GOODS_20260826')
if e and e.get('actual') is None:
    e['actual'] = 1.1
    e['status'] = 'released'
    e['notes'] = (e.get('notes') or '') + '7月环比+1.1%（Econoday 9/25事件Prior口径，2026-09-25回填，或含修正）。'
    changes.append('耐用品8/26(7月数据) actual=1.1')

# 4) 新增密歇根终值事件
if not find('US_MICHIGAN_SENTIMENT_20260925'):
    # 参照谘商会事件结构
    ref = None
    for x in events:
        if x.get('id') == 'US_CONSUMER_CONF_20260929':
            ref = x
            break
    ev = {
        'id': 'US_MICHIGAN_SENTIMENT_20260925',
        'release_date': '2026-09-25',
        'period': '2026-09',
        'country': 'US',
        'name': '密歇根大学消费者信心指数（终值）',
        'indicator': None,
        'release_time': ref.get('release_time', '10:00') if ref else '10:00',
        'forecast': 47.8,
        'previous': 51.7,
        'actual': None,
        'status': 'upcoming',
        'notes': ('9月flash 47.8（预期51.0大低、连续2个月回落，创5月纪录低点44.8以来最弱）；终值共识维持47.8不变（TE偏47.6）；'
                  '1年通胀预期4.6%（8月4.0%，6月来最高）预计不变、5年期3.4%；'
                  '伊朗冲突后油价反弹+贸易紧张压制家庭预算预期；今晚22:00 BJS（10:00 ET）发布。'
                  '来源：Econoday+TE+UMich官网 双源✅（2026-09-25补录）。'),
        'unit': (ref.get('unit') if ref else '') or ''
    }
    events.append(ev)
    changes.append('新增US_MICHIGAN_SENTIMENT_20260925')

# 5) 下周初请 prev
for x in events:
    if x.get('id', '').startswith('US_JOBLESS_CLAIMS_') and x.get('release_date') == '2026-10-01':
        if x.get('previous') is None:
            x['previous'] = 19.7
            changes.append('初请10/1 prev=19.7')

# 5b) 10月新屋销售 prev
for x in events:
    if x.get('id', '').startswith('US_NEW_HOME_SALES_') and x.get('release_date','') > '2026-09-25':
        if x.get('previous') is None:
            x['previous'] = 68.4
            changes.append(f"新屋销售{x['release_date']} prev=68.4")

json.dump(cal, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('patched:', changes)

# 回读核验
cal2 = json.load(open(PATH, encoding='utf-8'))
ev2 = cal2['events'] if isinstance(cal2, dict) else cal2
d = {x['id']: x for x in ev2}
assert d['US_JOBLESS_CLAIMS_20260924']['actual'] == 19.7
assert d['US_NEW_HOME_SALES_20260924']['actual'] == 68.4 and d['US_NEW_HOME_SALES_20260924']['previous'] == 64.3
assert d['US_DURABLE_GOODS_20260925']['forecast'] == -0.4 and d['US_DURABLE_GOODS_20260925']['previous'] == 1.1
assert d['US_DURABLE_GOODS_20260826']['actual'] == 1.1
assert d['US_MICHIGAN_SENTIMENT_20260925']['forecast'] == 47.8
print('回读核验 ✅ 全部通过')
