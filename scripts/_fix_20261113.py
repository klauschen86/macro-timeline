# -*- coding: utf-8 -*-
"""_fix_20261113.py — 2026-11-13 污染拦截（第6次复现，同型）
mcp_inject 用 CLI 错期字符串值覆盖 36 个历史已审计事件（US_CPI/PPI/CORE 2026xxxx、
EU_FF_*、US_FF_*、EU_CPI_FLASH×3、US_GDP×2、US_NYFED_1Y、US_UNEMPLOYMENT_20261106、
US_CPI/CORE_20261110 等），且 20261112 组 status 变化与 US_JOBLESS_CLAIMS 类型变化均由
inject/日期机制产生，无任何合法新增 actual → 全部 36 事件从 HEAD 还原。
保留：2 条合法 2027-01 新事件（US_PPI_20270114 / US_JOBLESS_CLAIMS_20270114）。
状态 upcoming→pending 的合法更新由随后重跑 run_daily.py 重新生成。
铁律：就地 e.clear()+e.update()（替换引用不生效），写盘后回读 assert。
"""
import json
import subprocess
import sys

PATH = 'data/calendar.json'
RESTORE_IDS = [
    'US_PPI_20260114', 'US_CORE_CPI_20260311', 'US_CPI_20260311',
    'US_PPI_20260414', 'US_CPI_20260512', 'US_CORE_CPI_20260512',
    'EU_FF_Final_CPI_y_y_20260617', 'EU_FF_Final_Core_CPI_y_y_20260617',
    'EU_FF_Core_CPI_Flash_Estimate_y_y_20260701', 'US_FF_Core_CPI_m_m_20260714',
    'US_FF_Core_PPI_m_m_20260715', 'EU_FF_Final_Core_CPI_y_y_20260717',
    'US_CPI_20260812', 'US_CORE_CPI_20260812', 'EU_CPI_FLASH_20260901',
    'US_NYFED_1Y_INFLATION_20260908', 'US_PPI_20260910', 'US_CPI_20260911',
    'US_CORE_CPI_20260911', 'US_GDP_FINAL_20260930', 'EU_CPI_FLASH_20261002',
    'US_CPI_20261014', 'US_CORE_CPI_20261014', 'US_GDP_ADV_20261029',
    'EU_CPI_FLASH_20261104', 'US_UNEMPLOYMENT_20261106',
    'US_CPI_20261110', 'US_CORE_CPI_20261110',
    'CN_M2_20261112', 'CN_SOCIAL_FINANCING_20261112', 'CN_NEW_LOANS_20261112',
    'US_CPI_20261112', 'US_CORE_CPI_20261112', 'US_EXISTING_HOME_20261112',
    'UK_GDP_20261112', 'US_JOBLESS_CLAIMS_20261112',
]

head = json.loads(subprocess.check_output(['git', 'show', 'HEAD:data/calendar.json'], encoding='utf-8'))
hmap = {e['id']: e for e in head['events']}
cur = json.load(open(PATH, encoding='utf-8'))
cmap = {e['id']: e for e in cur['events']}

fixed = 0
missing = []
for eid in RESTORE_IDS:
    if eid not in hmap:
        missing.append(eid)
        continue
    if eid not in cmap:
        missing.append(eid + '(not in cur)')
        continue
    h, c = hmap[eid], cmap[eid]
    if h == c:
        continue  # already clean
    c.clear()
    c.update(h)
    fixed += 1

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(cur, f, ensure_ascii=False, indent=2)

# 写盘后回读 assert
check = json.load(open(PATH, encoding='utf-8'))
kmap = {e['id']: e for e in check['events']}
bad = [eid for eid in RESTORE_IDS if eid in hmap and kmap.get(eid) != hmap[eid]]
assert not bad, f'readback mismatch: {bad}'
# 新事件保留核验
for nid in ['US_PPI_20270114', 'US_JOBLESS_CLAIMS_20270114']:
    assert nid in kmap, f'new event lost: {nid}'

print(f'restored={fixed}, readback OK, new events kept: '
      f'{[n for n in ["US_PPI_20270114","US_JOBLESS_CLAIMS_20270114"] if n in kmap]}')
if missing:
    print('MISSING (not touched):', missing)
print(f"total events: {len(check['events'])}")
