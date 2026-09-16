# -*- coding: utf-8 -*-
"""_fix_20260916b.py — 修正 US_RETAIL_20260916：发布时间 08:30→20:30 BJS（MoneyDJ 2026-09-14 明确"9/16晚间20:30"）+ 补 fc/prev（共识 +0.3% / 前值 -0.6%）"""
import json

CAL = 'data/calendar.json'
cal = json.load(open(CAL, encoding='utf-8'))

for e in cal['events']:
    if e['id'] == 'US_RETAIL_20260916':
        e['release_time'] = '20:30'
        if e.get('forecast') is None:
            e['forecast'] = 0.3
        if e.get('previous') is None:
            e['previous'] = -0.6
        e['notes'] = ('2026-09-16修正:发布时间08:30→20:30 BJS(MoneyDJ 2026-09-14+9/10财经日历双源✅);'
                      '共识 m/m +0.3%(除汽车+0.1%/控制组-0.1%),前值 -0.6%(7月转负)。'
                      '今晚20:30同步公布8月进出口物价。⚠️FOMC决议9/17凌晨02:00 BJS、鲍威尔记者会02:30。')
        print('fixed:', e['id'], e['release_time'], 'fc=', e['forecast'], 'prev=', e['previous'])

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 直接重生成 JS，不跑全量 run_daily（避免模式生成回滚 time 修正）
import run_daily
run_daily.generate_js(cal)
print('JS regenerated')
