# -*- coding: utf-8 -*-
"""2026-10-02d 修复脚本：mcp_inject 注入的字符串型数值归一化为 float（仅纯数字串，带单位/HTML 的不动）"""
import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
data = json.load(open(PATH, encoding='utf-8'))
NUM = re.compile(r'^-?\d+(\.\d+)?$')
fixed = 0
for e in data['events']:
    for k in ('actual', 'forecast', 'previous'):
        v = e.get(k)
        if isinstance(v, str) and NUM.match(v.strip()):
            e[k] = float(v.strip())
            fixed += 1

json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'normalized {fixed} string numerics')

# 回读 + 全量终验
data2 = json.load(open(PATH, encoding='utf-8'))
evs = data2['events']
ids = {e['id'] for e in evs}
assert 'US_FOMC_2026-11-05' not in ids and 'US_FOMC_2026-05-07' not in ids, '幻影复活'
checks = {
  'US_ISM_MFG_20261001': (54.5, 55.0, 54.6, 'released'),
  'US_JOBLESS_CLAIMS_20261001': (19.7, 20.0, 19.8, 'released'),
  'US_JOBLESS_CLAIMS_20260924': (19.7, 20.1, 19.8, 'released'),
  'US_NFP_20261002': (None, 9.0, 16.2, 'upcoming'),
  'US_UNEMPLOYMENT_20261002': (None, 4.1, 4.1, 'upcoming'),
  'EU_CPI_FLASH_20261002': (None, 3.7, 3.2, 'upcoming'),
  'US_FOMC_2026-04-30': (4.25, 4.25, 4.5, 'released'),
  'US_FOMC_2026-10-29': (None, None, 4.0, 'upcoming'),
  'US_GDP_ADV_20261029': (None, None, 2.2, 'upcoming'),
  'US_PCE_20261029': (None, None, 3.4, 'upcoming'),
  'US_PCE_CORE_20261029': (None, None, 3.0, 'upcoming'),
  'US_CPI_20261014': (None, None, 3.4, 'upcoming'),
}
n = 0
for e in evs:
    if e['id'] in checks:
        a, f, p, s = checks[e['id']]
        assert e.get('actual') == a and e.get('forecast') == f and e.get('previous') == p and e.get('status') == s, f"{e['id']}: {e.get('actual')!r},{e.get('forecast')!r},{e.get('previous')!r},{e.get('status')}"
        n += 1
print(f'JSON 终验 {n}/12 断言全过 ✓ 总数 {len(evs)}')
print('ALL OK')
