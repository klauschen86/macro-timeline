# -*- coding: utf-8 -*-
"""2026-11-24 b 轮数据层修正（不改脚本代码）：
1) US_GDP_ADV_20261029 修复：当前 2.3/3.5/6.1 系 notes 已记载的「GDP平减指数污染值」（历史修正丢失复发），
   按 notes 记录的修正意图重新落地 actual=3.4/fc=3.2/prev=2.2（今日 cmelitegroup/trade2spike/heygotrade/Globe&Mail
   4 Web 源交叉确认 Q3 advance=3.4% ✅）
2) 感恩节顺延日期纠正（5源✅：cmelitegroup/Globe&Mail/trade2spike/heygotrade/财联社）：
   - US_DURABLE_GOODS_20261126 → 2026-11-25（fc 环比+0.5%/核心+0.7% 共识预填）
   - US_JOBLESS_CLAIMS_20261126 → 2026-11-25（初请感恩节顺延至周三，fc 20.1万/prev 20.3万）
3) 补建 11-25 缺失关键事件（BEA 8:30 ET = 21:30 BJS 同刻组合）：
   - US_PCE_20261125（10月PCE同比 fc 3.6/prev 3.6）
   - US_PCE_CORE_20261125（10月核心PCE同比 fc 3.2/prev 3.1，市场焦点：>3.2% 强化沃勒50bp阵营）
   - US_GDP_2ND_20261125（Q3 GDP二估 fc 3.5/prev 3.4，共识 3.4-3.5 分歧记录）
   - US_BEIGE_BOOK_20261126（褐皮书，11-25 14:00 ET = 11-26 03:00 BJS，事件型）
来源：BEA 日程（cmelitegroup 周历引）+ 财联社下周概览 + Globe&Mail + trade2spike + heygotrade
"""
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')
MARK = '【2026-11-24'

cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events']
by = {e.get('id'): e for e in events}
log = []


def notes_of(e):
    return e.get('notes', '') or ''


def append_notes(e, text):
    e['notes'] = (notes_of(e) + ' | ' + text).strip(' |')


# ---------- 1) GDP初值平减指数污染复发修复 ----------
e = by['US_GDP_ADV_20261029']
e['actual'] = '3.4'
e['forecast'] = '3.2'
e['previous'] = '2.2'
e['status'] = 'released'
append_notes(e, MARK + '修复】历史「平减指数污染值(2.3/3.5/6.1)」修正丢失复发，按10-30批修正意图重新落地 actual=3.4/fc=3.2/prev=2.2；今日cmelitegroup+trade2spike+heygotrade+Globe&Mail 4源交叉确认advance=3.4%✅')
log.append('FIXED US_GDP_ADV_20261029 -> 3.4/3.2/2.2')

# ---------- 2) 感恩节顺延日期纠正 ----------
e = by['US_DURABLE_GOODS_20261126']
e['release_date'] = '2026-11-25'
if e.get('forecast') in (None, ''):
    e['forecast'] = 0.5
if e.get('previous') in (None, ''):
    e['previous'] = 0.0
append_notes(e, MARK + '日期纠正】感恩节顺延：耐用品订单10月随初请/PCE/GDP二估移至11-25 21:30 BJS（8:30 ET）发布（原排期11-26感恩节休市）；共识fc环比+0.5%/核心+0.7%（Globe&Mail+heygotrade双源）；cmelitegroup+trade2spike+财联社 5源✅')
log.append('DATE FIX US_DURABLE_GOODS_20261126 -> 2026-11-25')

e = by['US_JOBLESS_CLAIMS_20261126']
e['release_date'] = '2026-11-25'
if e.get('forecast') in (None, ''):
    e['forecast'] = 20.1
if e.get('previous') in (None, ''):
    e['previous'] = 20.3
append_notes(e, MARK + '日期纠正】初请感恩节顺延至周三11-25 21:30 BJS（week to 11-21，fc 20.1万/prev 20.3万系11-19发布值）；cmelitegroup（"moved from Thursday for the holiday"）+trade2spike+heygotrade+财联社 多源✅')
log.append('DATE FIX US_JOBLESS_CLAIMS_20261126 -> 2026-11-25')

# ---------- 3) 补建 11-25 缺失事件 ----------
def mk_event(eid, indicator, indicator_en, period, forecast, previous, notes, importance=3, unit='%', frequency='月度', source='BEA'):
    return {
        'id': eid, 'country': 'US', 'country_name': '美国',
        'indicator': indicator, 'indicator_en': indicator_en,
        'frequency': frequency, 'importance': importance,
        'release_date': '2026-11-25', 'release_time': '21:30', 'timezone': 'BJS',
        'period': period, 'source': source, 'source_url': 'https://www.bea.gov/',
        'unit': unit, 'forecast': forecast, 'previous': previous, 'status': 'upcoming',
        'notes': notes,
    }

NEW_EVENTS = [
    mk_event('US_PCE_20261125', 'PCE物价指数（同比）', 'PCE Price Index YoY', '2026-10', 3.6, 3.6,
             MARK + '补建】10月PCE同比 11-25 21:30 BJS（8:30 ET，BEA与GDP二估同刻组合）发布；fc 3.6%（与9月持平，cmelitegroup+trade2spike双源）/prev 3.6%（9月实际，10-29批回填）。感恩节周数据集中于周三'),
    mk_event('US_PCE_CORE_20261125', '核心PCE物价指数（同比）', 'Core PCE Price Index YoY', '2026-10', 3.2, 3.1,
             MARK + '补建】10月核心PCE同比 11-25 21:30 BJS 发布（美联储首选通胀指标）；fc 3.2%/环比+0.3%（trade2spike+heygotrade+Globe&Mail 3源）/prev 3.1%（9月实际）。市场焦点：>3.2% 强化沃勒(Waller)12-09会议50bp加息阵营，低于则缓解债市压力；威廉姆斯11-23讲话+鲍威尔定调下12月加息25bp已基本消化'),
    mk_event('US_GDP_2ND_20261125', 'GDP二估（年化环比）', 'GDP Second Estimate QoQ Annualized', '2026-Q3', 3.5, 3.4,
             MARK + '补建】Q3 GDP二估 11-25 21:30 BJS 发布；fc 3.5%（trade2spike+heygotrade+Globe&Mail 3源；cmelitegroup共识3.4%，分歧3.4-3.5记录在案）/prev 3.4%（Q3初值，10-30批回填：个人消费+3.8%+AI投资非住宅固投+12.7%拉动）', frequency='季度'),
    {
        'id': 'US_BEIGE_BOOK_20261126', 'country': 'US', 'country_name': '美国',
        'indicator': '美联储褐皮书', 'indicator_en': 'Fed Beige Book',
        'frequency': '8次/年', 'importance': 2,
        'release_date': '2026-11-26', 'release_time': '03:00', 'timezone': 'BJS',
        'period': '2026-11', 'source': 'Federal Reserve', 'source_url': 'https://www.federalreserve.gov/',
        'unit': '', 'forecast': None, 'previous': None, 'status': 'upcoming',
        'notes': MARK + '补建】褐皮书 11-25 14:00 ET = 11-26 03:00 BJS 发布（12-08/09 FOMC 前最后一次；Globe&Mail+cmelitegroup+trade2spike 3源一致，财联社按BJS记于周四=同一时刻口径自洽）。事件型按FOMC纪要先例不回填数值',
    },
]
for ne in NEW_EVENTS:
    if ne['id'] in by:
        log.append(f"SKIP(存在) {ne['id']}")
    else:
        events.append(ne)
        log.append(f"ADDED {ne['id']} rd={ne['release_date']} {ne['release_time']} fc={ne['forecast']}/prev={ne['previous']}")

# ---------- 写盘 + 重生成 JS ----------
with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)
generate_js(load_calendar())
log.append('JS regenerated')

# ---------- 回读 assert ----------
with open(CAL, encoding='utf-8') as f:
    data2 = json.load(f)
by2 = {e['id']: e for e in data2['events']}
ok = True

g = by2.get('US_GDP_ADV_20261029', {})
if (g.get('actual'), g.get('forecast'), g.get('previous')) != ('3.4', '3.2', '2.2'):
    print('ASSERT FAIL: GDP_ADV', g.get('actual'), g.get('forecast'), g.get('previous')); ok = False
if by2.get('US_DURABLE_GOODS_20261126', {}).get('release_date') != '2026-11-25':
    print('ASSERT FAIL: DURABLE date'); ok = False
if by2.get('US_JOBLESS_CLAIMS_20261126', {}).get('release_date') != '2026-11-25':
    print('ASSERT FAIL: CLAIMS date'); ok = False
checks = [
    ('US_PCE_20261125', 3.6, 3.6, '2026-11-25'),
    ('US_PCE_CORE_20261125', 3.2, 3.1, '2026-11-25'),
    ('US_GDP_2ND_20261125', 3.5, 3.4, '2026-11-25'),
    ('US_BEIGE_BOOK_20261126', None, None, '2026-11-26'),
]
for eid, fc, pv, rd in checks:
    e = by2.get(eid, {})
    if e.get('forecast') != fc or e.get('previous') != pv or e.get('release_date') != rd:
        print(f'ASSERT FAIL: {eid}', e.get('forecast'), e.get('previous'), e.get('release_date')); ok = False
    if MARK not in notes_of(e):
        print(f'ASSERT FAIL: {eid} notes marker'); ok = False

print('\n'.join(log))
print('READBACK:', 'ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
