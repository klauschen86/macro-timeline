# -*- coding: utf-8 -*-
"""2026-09-10 修复脚本
1. 美PPI/CPI 日期修正（BLS 官方日历 bls.gov/schedule/2026/ 双源 FRED ✅）：
   - US_PPI_20260914 → 9/10（8月PPI 今日 20:30 BJS 发布）
   - US_CPI_20260914 / US_CORE_CPI_20260914 → 9/11（8月CPI 明日 20:30 BJS）
   - US_CPI_20261012 → 10/14；US_PPI_20261014 → 10/15（BLS 官方 10 月日程）
2. US_JOBLESS_CLAIMS_20260910: fc=20.5万(多源) prev=20.6万
3. EU_ECB_20260910: fc=2.50%(存款利率,+25bp) prev=2.25%（中国金融新闻网/经参/Morningstar/SEB 多源✅）
4. UK_GDP_20260914 → 9/11（英国7月GDP 9/11发布，国际金融要情✅），period 修正为 2026-07
"""
import json, io, sys

PATH = 'data/calendar.json'
cal = json.load(open(PATH, encoding='utf-8'))
evs = cal['events']

def find(eid):
    for e in evs:
        if e.get('id') == eid:
            return e
    return None

changes = []

# 1. 日期修正
date_fixes = [
    ('US_PPI_20260914',   '2026-09-10', 'BLS官方日历✅: 8月PPI于2026-09-10 08:30 ET(20:30 BJS)发布(FRED双源✅); 7月PPI实际值仍未回填(US_PPI_20260814 pending), previous暂缺'),
    ('US_CPI_20260914',   '2026-09-11', 'BLS官方日历✅: 8月CPI于2026-09-11 08:30 ET(20:30 BJS)发布, 为9/16 FOMC决议前最后一份CPI(FRED双源✅)'),
    ('US_CORE_CPI_20260914', '2026-09-11', 'BLS官方日历✅: 与CPI同日2026-09-11发布'),
    ('US_CPI_20261012',   '2026-10-14', 'BLS官方日历✅: 9月CPI于2026-10-14 08:30 ET发布'),
    ('US_PPI_20261014',   '2026-10-15', 'BLS官方日历✅: 9月PPI于2026-10-15 08:30 ET发布'),
    ('UK_GDP_20260914',   '2026-09-11', '国际金融要情✅: 英国7月GDP于2026-09-11 07:00 BJS发布; period由2026-08修正为2026-07'),
]
for eid, nd, note in date_fixes:
    e = find(eid)
    if e and e.get('release_date') != nd:
        old = e.get('release_date')
        e['release_date'] = nd
        e['notes'] = (e.get('notes') or '').strip() + ' | ' + note
        changes.append(f'{eid}: {old} -> {nd}')
        if eid == 'UK_GDP_20260914':
            e['period'] = '2026-07'

# 2. 前值/预期回填
e = find('US_CPI_20260914')
if e: e['previous'] = '0.3'   # 7月actual 0.3(US_CPI_20260812)
e = find('US_CORE_CPI_20260914')
if e: e['previous'] = '0.3'   # 7月core actual 0.3

e = find('US_JOBLESS_CLAIMS_20260910')
if e:
    e['forecast'] = '20.5'
    e['previous'] = '20.6'
    e['notes'] = (e.get('notes') or '').strip() + ' | fc多源✅: Longbridge/Finobird/myfxbook均20.5万; Econoday偏20.8万(区间20.2-21.0), 存在分歧'

e = find('EU_ECB_20260910')
if e:
    e['forecast'] = '2.50%'
    e['previous'] = '2.25%'
    e['notes'] = (e.get('notes') or '').strip() + ' | 多源✅(中国金融新闻网/经济参考报/Morningstar/SEB/TradingNews): 路透调查65位经济学家全数预期存款利率+25bp至2.50%, 利率期货定价95-99%; 现行: 存款2.25%/再融资2.40%/边际借贷2.65%; 背景: 欧元区8月通胀3.3%(能源+14.3%), 核心2.4%回落'

print('Changes:')
for c in changes:
    print(' ', c)

json.dump(cal, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'Saved. Total events: {len(evs)}')
