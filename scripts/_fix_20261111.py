# -*- coding: utf-8 -*-
"""_fix_20261111.py — 2026-11-11 污染拦截修复
mcp_inject 用错期值覆盖历史已审计事件（第5次复现，同型）：
- US_CPI/PPI/CORE_CPI 2026xxxx（字符串 '0.900000' 型错期值）
- EU_CPI_FLASH_*、EU_FF_*、US_FF_*、US_GDP_ADV/FINAL、US_NYFED_1Y
策略：这些事件整对象从 HEAD 还原；
US_CPI_20261110 / US_CORE_CPI_20261110 / CN_TRADE_20261110 / US_EXISTING_HOME_20261110
仅保留 status upcoming→pending 的合法转换，其余字段以 HEAD 为准。
US_UNEMPLOYMENT_20261106 forecast "" → 还原 null。
写盘后回读 assert。
"""
import json, subprocess, sys

PATH = 'data/calendar.json'
FIELDS = ['actual', 'forecast', 'previous', 'release_date', 'release_time', 'status', 'notes']

head = json.loads(subprocess.check_output(['git', 'show', 'HEAD:data/calendar.json']).decode('utf-8'))
cur = json.load(open(PATH, encoding='utf-8'))
hmap = {e['id']: e for e in head['events']}
cmap = {e['id']: e for e in cur['events']}

# 整对象还原清单（污染）
FULL_RESTORE = [
    'EU_CPI_FLASH_20260901', 'EU_CPI_FLASH_20261002', 'EU_CPI_FLASH_20261104',
    'EU_FF_Core_CPI_Flash_Estimate_y_y_20260701', 'EU_FF_Final_CPI_y_y_20260617',
    'EU_FF_Final_Core_CPI_y_y_20260617', 'EU_FF_Final_Core_CPI_y_y_20260717',
    'US_CORE_CPI_20260512', 'US_CORE_CPI_20260911', 'US_CORE_CPI_20261014',
    'US_CPI_20260512', 'US_CPI_20260911', 'US_CPI_20261014',
    'US_FF_Core_CPI_m_m_20260714', 'US_FF_JOLTS_Job_Openings_20260630',
    'US_GDP_ADV_20261029', 'US_GDP_FINAL_20260930', 'US_NYFED_1Y_INFLATION_20260908',
    'US_PPI_20260414', 'US_PPI_20260910', 'US_PPI_20261015',
]
# 仅还原字段、保留 status 转换（upcoming→pending 合法）
KEEP_STATUS_RESTORE = ['US_CPI_20261110', 'US_CORE_CPI_20261110',
                       'CN_TRADE_20261110', 'US_EXISTING_HOME_20261110']

fixed = 0
# 就地更新 cur['events'] 内对象（cmap 仅为索引，替换引用不生效）
for e in cur['events']:
    eid = e.get('id')
    if eid in FULL_RESTORE and eid in hmap:
        restored = json.loads(json.dumps(hmap[eid], ensure_ascii=False))
        e.clear()
        e.update(restored)
        fixed += 1
    elif eid in KEEP_STATUS_RESTORE and eid in hmap:
        h = hmap[eid]
        for f in FIELDS:
            if f != 'status':
                e[f] = h.get(f)
        fixed += 1
    elif eid == 'US_UNEMPLOYMENT_20261106' and eid in hmap:
        e['forecast'] = hmap[eid].get('forecast')
        fixed += 1

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(cur, f, ensure_ascii=False, indent=2)

# 写盘后回读 assert
chk = {e['id']: e for e in json.load(open(PATH, encoding='utf-8'))['events']}
errors = []
for eid in FULL_RESTORE:
    for fld in FIELDS:
        if chk[eid].get(fld) != hmap[eid].get(fld):
            errors.append((eid, fld))
for eid in KEEP_STATUS_RESTORE:
    for fld in FIELDS:
        if fld != 'status' and chk[eid].get(fld) != hmap[eid].get(fld):
            errors.append((eid, fld))
    if chk[eid].get('status') != 'pending':
        errors.append((eid, 'status!=pending'))
if 'US_UNEMPLOYMENT_20261106' in chk:
    if chk['US_UNEMPLOYMENT_20261106'].get('forecast') != hmap['US_UNEMPLOYMENT_20261106'].get('forecast'):
        errors.append(('US_UNEMPLOYMENT_20261106', 'forecast'))

if errors:
    print('ASSERT FAILED:', errors)
    sys.exit(1)
print(f'OK: {fixed} events fixed, assert passed (readback verified)')
