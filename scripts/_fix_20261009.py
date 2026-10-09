# -*- coding: utf-8 -*-
"""2026-10-09 修复脚本：回填 10/8 晚美初请 actual + 下周 prev 链"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
data = json.load(open(PATH, encoding='utf-8'))
evs = data['events'] if isinstance(data, dict) else data

def notes_append(e, txt):
    old = e.get('notes') or ''
    marker = txt.split('；')[0]
    base = old.lstrip('；')
    if marker in base or txt[:15] in base:
        return
    e['notes'] = (base + ('；' if base and not base.endswith('；') else '') + txt)

changes = []

def patch(eid, **kw):
    for e in evs:
        if e.get('id') == eid:
            for k, v in kw.items():
                if k == 'notes_append':
                    notes_append(e, v)
                else:
                    e[k] = v
            changes.append(eid)
            return True
    print(f'!! NOT FOUND: {eid}')
    return False

# ① 初请 actual=19.7万（至10/3当周，低于预期20.0）——新华财经cnfin+香港商报+华尔街见闻+EconoTimes 4源✅
patch('US_JOBLESS_CLAIMS_20261008', actual=19.7, forecast=20.0, status='released',
      notes_append='2026-10-09 回填 actual=19.7万（新华财经cnfin+香港商报+华尔街见闻+EconoTimes 4源✅）：低于预期20.0万，连续4周处于57年低位附近；⚠️前值19.7万修正至19.9万后环比-2000人（DOL口径 previous revised level）；四周移动均值19.8万（2022年10月初以来最低）；续请171.6万（+1.7万，略超预期）——"低招聘低裁员"格局：裁员意愿历史极低但再就业周期拉长，9月失业持续时间中位数11.5周接近四年半高位；供给端退休潮+移民政策收紧制约就业增长；市场影响：10月加息预期进一步降温，经济学家普遍将下次加息时点推迟至12月')

# ② 下周初请 prev 链
patch('US_JOBLESS_CLAIMS_20261015', previous=19.7,
      notes_append='prev=19.7万（至10/3当周，10/9回填）')

# 回读核验
json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
ok = True
for e in evs:
    if e.get('id') == 'US_JOBLESS_CLAIMS_20261008':
        assert e['actual'] == 19.7 and e['status'] == 'released', e
        assert '2026-10-09 回填' in (e.get('notes') or ''), 'notes missing'
    if e.get('id') == 'US_JOBLESS_CLAIMS_20261015':
        assert e['previous'] == 19.7, e
print('ALL OK:', changes)
