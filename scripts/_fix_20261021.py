# -*- coding: utf-8 -*-
"""2026-10-21 一次性回填：美国9月成屋签约销售指数（10-20 22:00 BJS 发布）
actual=66.0（环比-7.3%，预期-0.5%/前值+0.3%，创2001年有纪录以来最低；同比-11.3%）
来源：NAR；Bloomberg / Dow Jones(Morningstar) / HousingWire / 财联社 多源一致 ✅
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
    if e['id'] == 'US_PENDING_HOME_SALES_20261020':
        e['actual'] = 66.0
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-21回填: 9月指数66.0, 环比-7.3%(预期-0.5%/前+0.3%)创2001年有纪录以来最低, 同比-11.3%; '
            '来源NAR, Bloomberg/DowJones/HousingWire/财联社多源一致; 抵押贷款利率9月约+80bp(6.8%→7.6%)主因')
        n += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

output = load_calendar()
generate_js(output)
print(f'Pending home sales backfilled: {n} event(s); JS regenerated')
