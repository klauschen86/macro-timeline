# -*- coding: utf-8 -*-
"""2026-09-18 回填：昨晚美4项+英央行决议 + 今晨日本CPI + 明日前瞻事件"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\calendar.json"
with open(P, encoding='utf-8') as f:
    cal = json.load(f)
events = cal['events'] if isinstance(cal, dict) else cal
idx = {e.get('id'): e for e in events if e.get('id')}

def patch(eid, **kv):
    e = idx.get(eid)
    if not e:
        print(f"MISS {eid}")
        return
    for k, v in kv.items():
        e[k] = v
    print(f"OK {eid}: " + ", ".join(f"{k}={v}" for k, v in kv.items()))

def add_event(e):
    if e['id'] not in idx:
        events.append(e)
        idx[e['id']] = e
        print(f"ADD {e['id']}")
    else:
        print(f"SKIP exists {e['id']}")

# ============ 昨晚 9/17 20:30 美国数据（多源：RTTNews/Census+DOL官方/证券时报/第一财经/tradingcharts） ============
# 初请 19.6万（fc 20.8万/20.5万，prev 20.6万，7月中来最低）
patch('US_INITIAL_CLAIMS_20260917', actual=19.6, forecast=20.8, previous=20.6,
      status='released', notes='初请19.6万(至9/12当周,环比-1万,7月中来最低,低于预期20.8万;RTTNews/证券时报/第一财经多源✅)。四周均值20.6万。')

# 新屋开工 8月 1.309M（7月上修至1.439M）
patch('US_HOUSING_STARTS_20260917', actual=1.309, forecast=1.322, previous=1.439,
      status='released', notes='新屋开工8月年率1.309M,环比-2.6%意外大降(Census/RTTNews官方口径✅);7月上修至1.439M(此前1.239M,Census年度基准修订致7月值大幅上修)。低于预期1.322M。')

# 建筑许可 8月 1.39M
patch('US_BUILDING_PERMITS_20260917', actual=1.390, forecast=1.410, previous=1.443,
      status='released', notes='建筑许可8月1.39M低于预期1.41M,前值1.443M(SignalPro/tradingcharts双源✅;前值同为年度修订后口径)。')

# 费城联储 9月 37.8（8月47.4为五年高位）
patch('US_PHILLY_FED_20260917', actual=37.8, forecast=30.0, previous=47.4,
      status='released', notes='费城联储9月当前活动指数37.8,自8月47.4(五年高位)回落但降幅小于预期30(RTTNews官方✅);仍处扩张区间。')

# ============ 9/17 19:00 英国央行决议 ============
# 找 UK_BOE 9/17 事件
for e in events:
    if 'UK_BOE' in e.get('id', '') and e.get('release_date', '').startswith('2026-09-17'):
        e['actual'] = 3.75
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') + ' | 决议:维持3.75%(连续第6次不变),MPC 6-3投票,3人主张+25bp(含首席经济学家皮尔);8月CPI 3.1%但尚无工资/价格二轮效应证据;通胀风险较7月偏上行;一致通过QT缩减计划:年售200亿英镑+到期债券,年均减持460亿至2034年清零。会后英镑跌至1.3348,富时100收涨1.19%,10Y英债收益率-8.1bp至5.218%(英央行官网+央视+第一财经3源✅)。').strip()
        print(f"OK {e['id']}: UK_BOE actual=3.75")
        break

# ============ 今晨 9/18 07:30 日本CPI ============
for eid, val, note in [
    ('JP_CPI_20260918', 1.9, '日本8月全国CPI同比+1.9%(fc 2.0/prev 1.9,低于预期;财联社+每经双源✅)'),
    ('JP_CORE_CPI_20260918', 1.7, '日本8月核心CPI(除生鲜)同比+1.7%(fc 1.8/prev 1.8,四个月来首次回落,连续7个月低于2%目标;主因政府能源补贴;除能源生鲜+1.9%持平;新华财经+彭博双源✅,不影响日银加息预期)'),
]:
    e = idx.get(eid)
    if e:
        e['actual'] = val
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') + ' | ' + note).strip()
        print(f"OK {eid}: actual={val}")
    else:
        print(f"MISS {eid} (待查找)")

# 补齐 JP_CPI prev（若此前未填）
e = idx.get('JP_CPI_20260918')
if e and not e.get('previous'):
    e['previous'] = 1.9
    print("OK JP_CPI prev=1.9")

# ============ 明日前瞻：9/19周六? 核实周末（9/19周六/9/20周日无主要发布，模式自动覆盖） ============
# 下周关键：9/22(周二)美里士满联储;9/23美PMI初值;9/24美新屋销售+经常账户;9/25美耐用品订单
# 这些由模式自动生成,无需补录

cal['meta'] = cal.get('meta', {})
cal['meta']['updated'] = '2026-09-18'

with open(P, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=1)
print("SAVED")
