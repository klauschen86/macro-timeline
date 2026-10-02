# -*- coding: utf-8 -*-
"""2026-10-02c 修复脚本：mcp_inject 用 westock FormerValue(19.7,上修前旧口径) 冲掉了 DOL 一手上修值(19.8)，恢复之"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
data = json.load(open(PATH, encoding='utf-8'))

def notes_append(e, txt):
    old = e.get('notes') or ''
    marker = txt.split('；')[0]
    base = old.lstrip('；')
    if marker in base:
        return
    e['notes'] = (base + ('；' if base and not base.endswith('；') else '') + txt)

for e in data['events']:
    if e.get('id') == 'US_JOBLESS_CLAIMS_20261001':
        e['previous'] = 19.8
        e['forecast'] = 20.0
        e['actual'] = 19.7
        e['status'] = 'released'
        notes_append(e, '⚠️mcp_inject曾以westock FormerValue=19.7（上修前旧口径）覆盖previous，已按DOL官网一手恢复19.8（10/2）')
    elif e.get('id') == 'US_JOBLESS_CLAIMS_20260924':
        e['previous'] = 19.8

json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

data2 = json.load(open(PATH, encoding='utf-8'))
ok = True
for e in data2['events']:
    if e.get('id') == 'US_JOBLESS_CLAIMS_20261001':
        ok &= (e.get('previous') == 19.8 and e.get('actual') == 19.7 and e.get('forecast') == 20.0)
        print('claims 10/01:', e.get('actual'), e.get('forecast'), e.get('previous'))
    if e.get('id') == 'US_JOBLESS_CLAIMS_20260924':
        ok &= (e.get('previous') == 19.8)
        print('claims 09/24 prev:', e.get('previous'))
print('ALL OK' if ok else 'FAIL')
