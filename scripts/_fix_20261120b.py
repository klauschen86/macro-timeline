# -*- coding: utf-8 -*-
"""2026-11-20 b轮：run_daily merge 回滚日期修正（不修改脚本代码，合并后重改 + 重新生成 JS）
回滚项：UK_CPI_20261117 11-17→11-18(+time 15:00)、US_RETAIL_20261116 11-16→11-17、
CN_M2/SOCIAL_FINANCING/NEW_LOANS_20261112 11-12→11-13（merge 按模式 id 重置日期，第 N 次同型复发）
"""
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')
cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events'] if isinstance(cal, dict) else cal
by = {e.get('id'): e for e in events}
log = []

FIXES = {
    'UK_CPI_20261117': ('2026-11-18', '15:00'),
    'US_RETAIL_20261116': ('2026-11-17', None),
    'CN_M2_20261112': ('2026-11-13', None),
    'CN_SOCIAL_FINANCING_20261112': ('2026-11-13', None),
    'CN_NEW_LOANS_20261112': ('2026-11-13', None),
}
for eid, (rd, tm) in FIXES.items():
    e = by.get(eid)
    if e is None:
        log.append(f'MISS {eid}')
        continue
    changed = False
    if e.get('release_date') != rd:
        e['release_date'] = rd
        changed = True
    if tm and e.get('time') != tm:
        e['time'] = tm
        changed = True
    log.append(f"{'FIXED' if changed else 'OK'} {eid} rd={e.get('release_date')} time={e.get('time')}")

if isinstance(cal, dict):
    cal['events'] = events
with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=1)

# 回读 assert
data2 = json.load(open(CAL, encoding='utf-8'))
by2 = {e['id']: e for e in data2['events']}
ok = True
for eid, (rd, tm) in FIXES.items():
    e = by2.get(eid, {})
    if e.get('release_date') != rd:
        print(f'ASSERT FAIL: {eid}.release_date={e.get("release_date")}'); ok = False
    if tm and e.get('time') != tm:
        print(f'ASSERT FAIL: {eid}.time={e.get("time")}'); ok = False

print('\n'.join(log))
print('READBACK:', 'ALL OK' if ok else 'FAILED')
if ok:
    output = load_calendar()
    generate_js(output)
    print('JS regenerated')
sys.exit(0 if ok else 1)
