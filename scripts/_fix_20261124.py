# -*- coding: utf-8 -*-
"""2026-11-24 一次性后处理：
0) 还原 mcp_inject 第9次同型污染（25个错期历史事件被错期值覆盖）→ 从 HEAD 全对象就地还原
1) EU_PMI_MFG/SVC/COMPOSITE_FLASH_20261123 回填 actual（11-23 17:00 BJS S&P Global 发布，Web 5源✅）：
   制造业 52.9（fc 52.4 超预期，前值52.7）/ 服务业 51.2（五个月低点，fc 49.9 超预期，前值51.4）/ 综合 51.7（持平，前值51.7）
   并还原 run_daily 合并回滚（release_time 17:00 / period 2026-11 / status released）
保留：6 个合法新模式事件（*_20270125）
来源：新华财经cnfin早报 + 陆家嘴财经早餐(腾讯) + 华尔街见闻FM-Radio(腾讯) + 网易财闻早知道 + 大越期货宏观早报，5源一致
"""
import json
import os
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')
MARK = '【2026-11-24'

head = json.loads(subprocess.check_output(['git', 'show', 'HEAD:data/calendar.json'], encoding='utf-8'))
hb = {e['id']: e for e in head['events']}

cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events'] if isinstance(cal, dict) else cal
by = {e.get('id'): e for e in events}
log = []


def notes_of(e):
    return e.get('notes', '') or ''


def append_notes(e, text):
    e['notes'] = (notes_of(e) + ' | ' + text).strip(' |')


# ---------- 0) 污染还原（就地 clear+update） ----------
POLLUTED = [
    'US_PPI_20260114', 'US_CORE_CPI_20260311', 'US_CPI_20260311',
    'US_PPI_20260414', 'EU_FF_Final_CPI_y_y_20260617',
    'EU_FF_Final_Core_CPI_y_y_20260617', 'EU_FF_Core_CPI_Flash_Estimate_y_y_20260701',
    'EU_FF_PPI_m_m_20260706', 'US_FF_Core_PPI_m_m_20260715',
    'EU_FF_Final_Core_CPI_y_y_20260717', 'US_CPI_20260812', 'US_CORE_CPI_20260812',
    'EU_CPI_FLASH_20260901', 'US_CPI_20260911', 'US_CORE_CPI_20260911',
    'US_GDP_FINAL_20260930', 'EU_CPI_FLASH_20261002', 'US_CPI_20261014',
    'US_CORE_CPI_20261014', 'US_PPI_20261015', 'EU_CPI_FLASH_20261104',
    'US_UNEMPLOYMENT_20261106', 'US_CPI_20261110', 'US_CORE_CPI_20261110',
    'US_PPI_20261113',
]
restored = 0
for eid in POLLUTED:
    e = by.get(eid)
    h = hb.get(eid)
    if e is None or h is None:
        log.append(f'RESTORE MISS {eid}')
        continue
    before = json.dumps(e, sort_keys=True, ensure_ascii=False)
    e.clear()
    e.update(h)
    if json.dumps(e, sort_keys=True, ensure_ascii=False) != before:
        restored += 1
        log.append(f'RESTORED {eid}')
    else:
        log.append(f'RESTORED(no-diff) {eid}')
log.append(f'污染还原: {restored}/{len(POLLUTED)} 实际变更')

# ---------- 1) EU PMI 2026-11 初值回填 ----------
BACKFILLS = {
    'EU_PMI_MFG_FLASH_20261123': (
        52.9,
        '制造业PMI初值 52.9（fc 52.4 超预期，前值52.7，10月初值52.4已录10-23事件）。'
        '11-23 17:00 BJS S&P Global/HCOB 发布；新华财经cnfin+陆家嘴(腾讯)+华尔街见闻FM-Radio+网易财闻+大越期货 5源✅。'
        '德法分化六年来最大：德国综合55.0（2022-03来最高，远超fc 53.2）/法国综合46.2（六个月低点）。'
    ),
    'EU_PMI_SVC_FLASH_20261123': (
        51.2,
        '服务业PMI初值 51.2（五个月低点，fc 49.9 超预期，前值51.4）。'
        '11-23 17:00 BJS S&P Global/HCOB 发布；新华财经cnfin+陆家嘴+华尔街见闻+网易+大越期货 5源✅。'
    ),
    'EU_PMI_COMPOSITE_FLASH_20261123': (
        51.7,
        '综合PMI初值 51.7 持平（连续第5个月扩张，前值51.7）。'
        '11-23 17:00 BJS S&P Global/HCOB 发布；新华财经cnfin+陆家嘴+华尔街见闻+网易+大越期货 5源✅。'
        '欧元区"制造强、服务弱"分化；德法分化扩大至六年来最大。'
    ),
}
for eid, (act, note) in BACKFILLS.items():
    e = by.get(eid)
    h = hb.get(eid)
    if e is None:
        log.append(f'BACKFILL MISS {eid}')
        continue
    # 先还原到 HEAD（拿回 17:00/2026-11/notes 原始口径），再叠加回填
    if h is not None:
        e.clear()
        e.update(h)
    e['actual'] = act
    e['status'] = 'released'
    append_notes(e, MARK + '回填】' + note)
    log.append(f'BACKFILLED {eid} actual={act} status=released')

# ---------- 写盘 + 重生成 JS ----------
with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

generate_js(load_calendar())
log.append('JS regenerated')

# ---------- 回读 assert ----------
with open(CAL, encoding='utf-8') as f:
    data2 = json.load(f)
by2 = {e['id']: e for e in data2['events']}
ok = True

for eid in POLLUTED:
    a, b = hb.get(eid, {}), by2.get(eid, {})
    if json.dumps(a, sort_keys=True, ensure_ascii=False) != json.dumps(b, sort_keys=True, ensure_ascii=False):
        print(f'ASSERT FAIL: {eid} 未还原到HEAD'); ok = False

checks = [
    ('EU_PMI_MFG_FLASH_20261123', 52.9),
    ('EU_PMI_SVC_FLASH_20261123', 51.2),
    ('EU_PMI_COMPOSITE_FLASH_20261123', 51.7),
]
for eid, act in checks:
    e = by2.get(eid, {})
    if e.get('actual') != act:
        print(f'ASSERT FAIL: {eid}.actual={e.get("actual")}'); ok = False
    if e.get('status') != 'released':
        print(f'ASSERT FAIL: {eid}.status={e.get("status")}'); ok = False
    if e.get('release_time') != '17:00':
        print(f'ASSERT FAIL: {eid}.release_time={e.get("release_time")}'); ok = False
    if e.get('period') != '2026-11':
        print(f'ASSERT FAIL: {eid}.period={e.get("period")}'); ok = False
    if MARK not in notes_of(e):
        print(f'ASSERT FAIL: {eid} notes marker'); ok = False

for eid in ['US_NEW_HOME_SALES_20270125', 'EU_CPI_FLASH_20270125',
            'EU_PMI_MFG_FLASH_20270125', 'EU_PMI_SVC_FLASH_20270125',
            'EU_PMI_COMPOSITE_FLASH_20270125', 'US_DALLAS_FED_20270125']:
    if by2.get(eid) is None:
        print(f'ASSERT FAIL: NEW 20270125 事件丢失: {eid}'); ok = False

# US_CONSUMER_CONF_20261124 今日事件未被误动
cc = by2.get('US_CONSUMER_CONF_20261124', {})
if cc.get('forecast') != 92.1 or cc.get('previous') != 91.7:
    print(f'ASSERT FAIL: US_CONSUMER_CONF_20261124 fc/prev 被改动'); ok = False

print('\n'.join(log))
print('READBACK:', 'ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
