# -*- coding: utf-8 -*-
"""2026-10-02b 修复脚本：迁移误删的 FOMC 4月决议数据（5/7幻影事件实为4/28-29会议，日期排错但含真实决议值）"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
data = json.load(open(PATH, encoding='utf-8'))
evs = data['events']

for e in evs:
    if e.get('id') == 'US_FOMC_2026-04-30':
        # 从 git HEAD 恢复的 US_FOMC_2026-05-07 真实数据（4/28-29会议决议）
        e['actual'] = 4.25
        e['forecast'] = 4.25
        e['previous'] = 4.5
        e['status'] = 'released'
        e['release_time'] = '14:00'
        e['timezone'] = 'EST'
        e['notes'] = ('官方2026日程：会议4/28-29，决议4/29 14:00 ET=4/30 02:00 BJS；'
                      '决议：降息25bp至4.25%（前值4.5）；'
                      '⚠️原日历误排2026-05-07（模式生成错误日期），2026-10-02修正为4/30并将5/7事件数据迁移至此')
        break
else:
    print('!! US_FOMC_2026-04-30 NOT FOUND'); sys.exit(1)

json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 回读校验
data2 = json.load(open(PATH, encoding='utf-8'))
for e in data2['events']:
    if e.get('id') == 'US_FOMC_2026-04-30':
        ok = (e.get('actual') == 4.25 and e.get('previous') == 4.5
              and e.get('status') == 'released' and e.get('release_date') == '2026-04-30')
        print('US_FOMC_2026-04-30:', e.get('actual'), e.get('forecast'), e.get('previous'), e.get('status'), e.get('release_date'))
        print('ALL OK' if ok else 'FAIL')
