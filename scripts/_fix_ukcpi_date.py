# -*- coding: utf-8 -*-
"""2026-10-20 一次性后处理：UK 9月 CPI 日期修正（10-19 → 10-21，ONS 官网日程确证）
注意：run_daily 的 merge_calendars 会用模式日期重置 release_date（只保留 actual/forecast/previous/status/notes），
故本修正须在 run_daily 之后运行，并重新生成 JS。明日批次回填 actual 后如日期再被重置，需重新执行本脚本。
"""
import json
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')

cal = json.load(open(CAL, encoding='utf-8'))
n = 0
for e in cal['events']:
    if e['id'] == 'UK_CPI_20261019' and e.get('release_date') != '2026-10-21':
        e['release_date'] = '2026-10-21'
        e['notes'] = e.get('notes', '') + ' | 2026-10-20后处理: 日期修正10/21(ONS官网日程确证,merge按模式id重置过一次)'
        n += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 重新生成 JS（与 run_daily 同一入口）
output = load_calendar()
generate_js(output)
print(f'UK CPI date fixed: {n} event(s); JS regenerated')
