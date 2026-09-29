# -*- coding: utf-8 -*-
"""2026-09-29 修复脚本
1. 回填 9/28 达拉斯联储制造业 9 月 actual=9.8（官网+TE+Finobird 3源）
2. 补今日 9/29 三事件共识：谘商会消费者信心 fc 90.0/prev 89.4；JOLTS fc 722.5万；svc 无共识仅 notes
3. 补录 KC Fed 系列（9/24 遗留项）：9月 released 20.0 + 全年历史链 + 10/22 upcoming
4. 预填达拉斯联储 10 月事件 prev（mfg 10/26 prev=9.8）
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CAL = 'data/calendar.json'
with open(CAL, 'r', encoding='utf-8') as f:
    data = json.load(f)
events = data['events'] if isinstance(data, dict) else data

def find(eid):
    for e in events:
        if e.get('id') == eid:
            return e
    return None

def append_notes(e, text):
    marker = text.split('；')[0].lstrip('；')
    notes = e.get('notes') or ''
    if marker and marker in notes:
        return False
    e['notes'] = (notes + '；' + text) if notes else text
    return True

changed = []

# ============ 1. 回填 9/28 达拉斯联储制造业 actual=9.8 ============
e = find('US_DALLAS_FED_20260928')
assert e, 'US_DALLAS_FED_20260928 not found'
assert e.get('previous') == 11.6, f"prev mismatch: {e.get('previous')}"
e['actual'] = 9.8
e['status'] = 'released'
append_notes(e, "2026-09-29 回填 actual=9.8（达拉斯联储官网+TE+Finobird 3源✅，general business activity 口径）；共识仅 1（TE），实际大超共识；分项：production 29.5(前16.1)/new orders 30.7(前22.0)/employment 15.1(前8.0)/产能利用率 23.9(前12.8)/shipments 24.8/prices paid 52.2(前44.1)/成品价 27.6/工资 27.4/company outlook 8.7(前19.2 单月-55%)/outlook uncertainty 11.3/future general 20.8(前37.2)；生产强劲但前瞻预期大跌+投入价格加速=滞胀结构；样本 9/15-23，113 家中 63 家回应；下次发布 10/26（官网确认）")
changed.append(('US_DALLAS_FED_20260928', 'actual=9.8 released'))

# ============ 2. 谘商会消费者信心 9/29 fc/prev ============
e = find('US_CONSUMER_CONF_20260929')
assert e, 'US_CONSUMER_CONF_20260929 not found'
e['forecast'] = 90.0
e['previous'] = 89.4
append_notes(e, "2026-09-29 补 fc=90.0（Econoday 共识，区间 87.7-91.0；investing 90.1 极小分歧）+prev=89.4（8月实际，investing/helious/financecalendar 3源✅；7月下修至90.2，连续3月回落，1月来最低）；预期分项 68.2 自 2025-02 起持续低于 80 衰退阈值；今晚 22:00 BJS 发布")
changed.append(('US_CONSUMER_CONF_20260929', 'fc=90.0 prev=89.4'))

# ============ 3. JOLTS 9/29 fc ============
e = find('US_JOLTS_20260929')
assert e, 'US_JOLTS_20260929 not found'
e['forecast'] = 722.5
append_notes(e, "2026-09-29 补 fc=722.5万（Econoday 共识 7.225M，区间 7.150-7.300M；OneRoyal 7.24M/MEXC 7.23M 一致✅）；6月曾下修 17.7万至 7.2M；9/17 FOMC 加息后 10/27-28 会议前关键劳动力数据（CME 10月再加息概率约 71%）；今晚 22:00 BJS 发布")
changed.append(('US_JOLTS_20260929', 'fc=722.5'))

# ============ 4. 达拉斯联储服务业 9/29 notes（无共识） ============
e = find('US_DALLAS_FED_SERVICES_20260929')
assert e, 'US_DALLAS_FED_SERVICES_20260929 not found'
append_notes(e, "2026-09-29 核对：9月共识缺失（TE/官方未提供，与 mfg 同），fc 留空；TE 显示 8月 svc 4.2/7月 6.6 与 prev 咬合✅；今晚 22:30 BJS 发布后明晨回填")
changed.append(('US_DALLAS_FED_SERVICES_20260929', 'notes'))

# ============ 5. KC Fed 系列补录（9/24 遗留项） ============
# investing 全年历史链：1月-2.0/2月10.0/3月11.0/4月10.0/5月9.0/6月19.0/7月17.0/8月17.0/9月20.0
KC_HIST = [
    ('US_KC_FED_20260122', '2026-01-22', '2026-01', -2.0, None, 'released'),
    ('US_KC_FED_20260226', '2026-02-26', '2026-02', 10.0, -2.0, 'released'),
    ('US_KC_FED_20260326', '2026-03-26', '2026-03', 11.0, 10.0, 'released'),
    ('US_KC_FED_20260423', '2026-04-23', '2026-04', 10.0, 11.0, 'released'),
    ('US_KC_FED_20260521', '2026-05-21', '2026-05', 9.0, 10.0, 'released'),
    ('US_KC_FED_20260625', '2026-06-25', '2026-06', 19.0, 9.0, 'released'),
    ('US_KC_FED_20260723', '2026-07-23', '2026-07', 17.0, 19.0, 'released'),
    ('US_KC_FED_20260827', '2026-08-27', '2026-08', 17.0, 17.0, 'released'),
    ('US_KC_FED_20260924', '2026-09-24', '2026-09', 20.0, 17.0, 'released'),
    ('US_KC_FED_20261022', '2026-10-22', '2026-10', None, 20.0, 'upcoming'),
]
for eid, rdate, period, actual, prev, status in KC_HIST:
    e = find(eid)
    if e:
        if actual is not None and e.get('actual') is None:
            e['actual'] = actual
            e['status'] = 'released'
        if prev is not None and e.get('previous') is None:
            e['previous'] = prev
        append_notes(e, '2026-09-29 KC Fed 系列补录（investing+Econoday 双源✅）')
        changed.append((eid, 'updated'))
        continue
    ev = {
        'id': eid,
        'country': 'US',
        'country_name': '美国',
        'indicator': '堪萨斯联储制造业指数',
        'indicator_en': 'Kansas City Fed Manufacturing Index',
        'frequency': '月度',
        'importance': 2,
        'release_date': rdate,
        'release_time': '23:00',
        'timezone': 'BJS',
        'period': period,
        'source': 'Kansas City Fed',
        'source_url': 'https://www.kansascityfed.org/research/indicatorsdata/manufacturing/',
        'unit': '',
        'previous': prev,
        'status': status,
        'notes': 'Tenth District 制造业调查（composite，production/new orders/employment/delivery/raw materials 均值），每月第4个周四 23:00 BJS（10:00 CT）发布；Econoday 2026 全年日历核实；2026-09-29 KC Fed 系列补录（investing+Econoday+instaforex 多源✅）',
    }
    if actual is not None:
        ev['actual'] = actual
    events.append(ev)
    changed.append((eid, 'created'))

# prev 链咬合校验（9月 prev=8月 actual）
k9 = find('US_KC_FED_20260924'); k8 = find('US_KC_FED_20260827')
assert k9['previous'] == k8['actual'] == 17.0, 'KC prev chain broken'
k10 = find('US_KC_FED_20261022')
assert k10['previous'] == k9['actual'] == 20.0, 'KC 10月 prev broken'

# ============ 6. 达拉斯联储 10 月事件 prev 预填 ============
for eid, prev_v in [('US_DALLAS_FED_20261026', 9.8)]:
    e = find(eid)
    if e:
        if e.get('previous') is None:
            e['previous'] = prev_v
            append_notes(e, '2026-09-29 预填 prev=9.8（9月实际值）')
            changed.append((eid, f'prev={prev_v}'))

with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ============ 回读核验 ============
with open(CAL, 'r', encoding='utf-8') as f:
    data2 = json.load(f)
ev2 = data2['events'] if isinstance(data2, dict) else data2
m = {e['id']: e for e in ev2}
checks = [
    ('US_DALLAS_FED_20260928', 'actual', 9.8),
    ('US_DALLAS_FED_20260928', 'previous', 11.6),
    ('US_CONSUMER_CONF_20260929', 'forecast', 90.0),
    ('US_CONSUMER_CONF_20260929', 'previous', 89.4),
    ('US_JOLTS_20260929', 'forecast', 722.5),
    ('US_JOLTS_20260929', 'previous', 727.1),
    ('US_KC_FED_20260924', 'actual', 20.0),
    ('US_KC_FED_20260924', 'previous', 17.0),
    ('US_KC_FED_20261022', 'previous', 20.0),
    ('US_DALLAS_FED_20261026', 'previous', 9.8),
]
ok = True
for eid, key, want in checks:
    e = m.get(eid)
    got = e.get(key) if e else None
    stat = 'OK' if got == want else 'FAIL'
    if got != want:
        ok = False
    print(f'{stat} {eid}.{key} = {got} (want {want})')
# svc prev 咬合
e = m.get('US_DALLAS_FED_SERVICES_20260929')
print('svc prev =', e.get('previous'), '(want 4.2)')
print()
print('Changed:', len(changed))
for c in changed:
    print(' -', c[0], c[1])
print()
print('ALL OK' if ok else 'HAS FAILURES')
