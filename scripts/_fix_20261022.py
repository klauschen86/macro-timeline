# -*- coding: utf-8 -*-
"""2026-10-22 一次性回填：UK 9月 CPI actual（ONS 10-21 发布，多源核实）
实际值：同比 3.5%（预期 3.5 持平✅ / 前值 3.1，2025-11 以来最高）
核心 CPI 2.8%（前 2.6）；服务 3.7%（前 3.4）；CPIH 3.6%
主因：机动车燃油价格（汽油 2022-08 以来最高、柴油 2022-07 以来最高）
来源：ONS 官方 + 新华社(10-21) + 央视 + 新华财经 多源✅
"""
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')

cal = json.load(open(CAL, encoding='utf-8'))
n = 0
for e in cal['events']:
    if e['id'] == 'UK_CPI_20261019':
        e['actual'] = 3.5
        e['previous'] = 3.1
        e['forecast'] = 3.5
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-22回填actual: 英国9月CPI同比+3.5%（预期3.5持平✅/前值3.1，2025-11以来最高，连续3月回升）；'
            '核心CPI 2.8%（前2.6）、服务3.7%（前3.4）、CPIH 3.6%；主因机动车燃油（汽油162+便士/升2022-08来最高、柴油2022-07来最高，同比+近30%）；'
            '高于BoE 2%目标，10-28预算案前压力加大；来源：ONS官方+新华社+央视+新华财经 4源✅')
        n += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'UK Sep CPI actual backfilled: {n} event(s)')
