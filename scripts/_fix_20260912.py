# -*- coding: utf-8 -*-
"""2026-09-12 回填与 id 过渡（配合 generate_calendar.py DATE_OVERRIDES 根治）

背景：日期补丁被 run_daily 回滚已 3 次，根因是 merge 按 id 去重而 id 含日期。
本次在 generate_calendar.py 落地 DATE_OVERRIDES（生成期直接产出官方核实日期），
本脚本把现有被回滚的陈旧 id 改名为覆盖后 id，使重生成 merge 正确合并不回滚。

1. id 过渡：US_CPI/US_CORE_CPI/US_PPI/UK_GDP 的 9月/10月 事件改名+日期修正
2. 回填 9/11 actual：美8月CPI 3.4 / 核心CPI 2.4（5源✅）
3. 修正 CPI 前值链误录：8/12 事件（7月数据）actual 0.3→3.4 / 核心 0.3→2.5
4. 9/14 中国金融数据 notes 标注发布窗口 9/12-9/15（FXStreet 预告 9/12）
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_daily

CAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'calendar.json')

with open(CAL, encoding='utf-8') as f:
    data = json.load(f)

events = data['events']
by_id = {e['id']: e for e in events}
PATCH = '| 2026-09-12补丁✅'

# ---------- 1. id 过渡（改名 + 日期/period 修正） ----------
RENAMES = [
    # (旧id, 新id, release_date, period)
    ('US_CPI_20260914', 'US_CPI_20260911', '2026-09-11', None),
    ('US_CORE_CPI_20260914', 'US_CORE_CPI_20260911', '2026-09-11', None),
    ('US_PPI_20260914', 'US_PPI_20260910', '2026-09-10', None),
    ('UK_GDP_20260914', 'UK_GDP_20260911', '2026-09-11', '2026-07'),
    ('US_CPI_20261012', 'US_CPI_20261014', '2026-10-14', None),
    ('US_CORE_CPI_20261012', 'US_CORE_CPI_20261014', '2026-10-14', None),
    ('US_PPI_20261014', 'US_PPI_20261015', '2026-10-15', None),
]
for old_id, new_id, rdate, period in RENAMES:
    e = by_id.get(old_id)
    if e is None:
        print(f"SKIP (not found): {old_id}")
        continue
    e['id'] = new_id
    e['release_date'] = rdate
    if period:
        e['period'] = period
    by_id[new_id] = e
    print(f"renamed {old_id} -> {new_id} (date={rdate})")

# ---------- 2. 回填美8月CPI actual（9/11 20:30 BJS 发布，5源✅） ----------
# 幂等：PATCH 标记已存在则跳过追加
def notes_with(e, text):
    if PATCH in (e.get('notes') or ''):
        return e['notes']
    return (e.get('notes') or '') + text

e = by_id['US_CPI_20260911']
if PATCH not in (e.get('notes') or ''):
    e['status'] = 'released'
    e['actual'] = 3.4
    e['forecast'] = 3.4
    e['previous'] = 3.4
    e['notes'] = notes_with(e, PATCH + ': 美8月CPI同比+3.4%(符合预期,与7月持平), 环比+0.4%(预期0.4,前值0.1); 汽油+3.9%贡献超1/3, 能源环比+2.1%/同比+16.3%; 央视+新华社+国际在线+证券时报+搜狐Wind 5源✅; 前值链修正: 7月同比3.4%(原误录0.3)')
    print('backfilled US_CPI_20260911: actual=3.4')

e = by_id['US_CORE_CPI_20260911']
if PATCH not in (e.get('notes') or ''):
    e['status'] = 'released'
    e['actual'] = 2.4
    e['forecast'] = 2.5
    e['previous'] = 2.5
    e['notes'] = notes_with(e, PATCH + ': 美8月核心CPI同比+2.4%(略低于预期2.5,前值2.5,2021年3月以来最低), 环比+0.3%(超预期0.2,4月以来最大涨幅——高于沃勒阈值0.2%逼近0.3%加息阈值); 住房环比+0.3%; 5源✅; 发布后CME 9月加息25bp概率69.6%→85-91.6%, 年底累计计入约53bp(至少两次加息)')
    print('backfilled US_CORE_CPI_20260911: actual=2.4')

# ---------- 3. 修正 CPI 前值链误录（7月数据，8/12 发布） ----------
e = by_id.get('US_CPI_20260812')
if e and str(e.get('actual')) == '0.3':
    e['actual'] = 3.4
    e['notes'] = (e.get('notes') or '') + PATCH + ': 修正误录——7月CPI同比3.4%(9/11五源报道"8月同比3.4%与7月持平"直接证实), 原actual=0.3系口径误录; 7月环比0.1%; 4-6月历史链审计仍待做'
    print('fixed US_CPI_20260812: actual 0.3 -> 3.4')
e = by_id.get('US_CORE_CPI_20260812')
if e and str(e.get('actual')) == '0.3':
    e['actual'] = 2.5
    e['notes'] = (e.get('notes') or '') + PATCH + ': 修正误录——7月核心CPI同比2.5%(9/11多源报道证实"8月核心2.4%较7月2.5%回落"), 原actual=0.3系口径误录'
    print('fixed US_CORE_CPI_20260812: actual 0.3 -> 2.5')

# ---------- 4. 9/14 中国金融数据：发布窗口标注 ----------
for eid in ('CN_M2_20260914', 'CN_SOCIAL_FINANCING_20260914', 'CN_NEW_LOANS_20260914'):
    e = by_id.get(eid)
    if e and PATCH not in (e.get('notes') or ''):
        e['notes'] = (e.get('notes') or '') + PATCH + ': 发布窗口9/12(周六,FXStreet预告)~9/15; PBOC惯常下午发布, 9/12晨未出; 2025年同期(8月数据)于9/12发布; 发布后按真实日期修正'
        print(f'noted {eid}')

with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 重新生成 JS（不跑 generate+merge，等 MCP 注入后统一跑）
data_out = run_daily.load_calendar()
run_daily.generate_js(data_out)

output = data_out['events']
rel = sum(1 for e in output if e.get('status') == 'released')
print(f"\nDone. Total: {len(output)}, Released: {rel}")
