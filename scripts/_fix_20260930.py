# -*- coding: utf-8 -*-
"""2026-09-30 修复脚本（回填 6 项 + 10 月 prev 预填）
1. 回填 9/30 中国 9 月官方 PMI：制造业 50.1（+0.3pp 重返扩张）/非制造业 50.2（+1.2pp）（统计局官网+中新经纬+新华财经 3源✅）
2. 回填 9/30 日本 8 月工业产出速报：环比 -1.7%（预期 +1.3~1.7，4源✅）
3. 回填 9/29 谘商会消费者信心：81.9（Reuters+AP+Continuum 多源✅）；⚠️ 8月值 89.4→88.6 修正（Reuters 口径 81.9+6.7）
4. 回填 9/29 JOLTS：707.9 万（Reuters+Continuum+stockwirex 3源✅）
5. 回填 9/29 达拉斯联储服务业：-1.8（MNI+TE 双源✅）
6. 预填 10/27 事件 prev：消费者信心 81.9 / 达拉斯服务 -1.8
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

# ============ 1. 中国 9 月官方制造业 PMI ============
e = find('CN_PMI_MFG_20260930')
assert e, 'CN_PMI_MFG_20260930 not found'
e['actual'] = 50.1
e['previous'] = 49.8
e['status'] = 'released'
append_notes(e, "2026-09-30 回填 actual=50.1（国家统计局官网 t20260930_1965449+中新经纬+新华财经 3源✅，09:32 发布）；比上月+0.3pp 重返扩张区间（连续5个月低于50后）；分项：生产 51.7(+1.3)/新订单 50.5(-0.1)/原材料库存 48.2/从业人员 48.4(-0.3)/配送 50.1；大中小企业 50.6/49.7(+0.3)/48.9(+1.0)；综合 PMI 产出 50.7(+1.2)；生产强于需求、就业继续回落；westock CLI/tdx 库数据滞后至 8月，prev 链 8月=49.8 双源咬合✅")
changed.append(('CN_PMI_MFG_20260930', 'actual=50.1 prev=49.8 released'))

# ============ 2. 中国 9 月官方非制造业 PMI ============
e = find('CN_PMI_NONMFG_20260930')
assert e, 'CN_PMI_NONMFG_20260930 not found'
e['actual'] = 50.2
e['previous'] = 49.0
e['status'] = 'released'
append_notes(e, "2026-09-30 回填 actual=50.2（同上 3源✅）；比上月+1.2pp 明显回升（8月 49.0 为低点）；建筑业 50.3(+3.4)/服务业 50.2(+0.9)；非制造业新订单 46.5(+2.4)；投入品价格 52.5(+1.4)/销售价格 50.3(+1.0)；电信 broadcast/货币金融/保险 55+ 高景气，资本市场/房地产仍低于临界点；CLI prev 链 8月=49.0 咬合✅")
changed.append(('CN_PMI_NONMFG_20260930', 'actual=50.2 prev=49.0 released'))

# ============ 3. 日本 8 月工业产出速报 ============
e = find('JP_INDUSTRIAL_20260930')
assert e, 'JP_INDUSTRIAL_20260930 not found'
e['actual'] = -1.7
e['status'] = 'released'
append_notes(e, "2026-09-30 回填 actual=-1.7（新华+TE+新华财经+Reuters 4源✅）；预期 +1.3（新华财经口径）/+1.7（Reuters 中值），大幅低于预期且连续第2个月下滑（2月以来最大降幅）；7月下修 -0.2 为 prev 咬合✅；同比 +3.4%（预期 6.8~7.0，前值 3.9）；指数 102.6（2020=100）；汽车 -6.8%（7/28 熊本 7.1 级地震余震+台风扰动，波及爱知丰田供应链）/通用机械 -6.0%/石油煤炭 -13.3%；生产机械 +6.1%；METI 评估维持\"波动不定\"，预计 9月 +3.2%/10月 +3.1%；日银加息决策关注变量")
changed.append(('JP_INDUSTRIAL_20260930', 'actual=-1.7 released'))

# ============ 4. 谘商会消费者信心 9/29 ============
e = find('US_CONSUMER_CONF_20260929')
assert e, 'US_CONSUMER_CONF_20260929 not found'
e['actual'] = 81.9
e['previous'] = 88.6
e['status'] = 'released'
append_notes(e, "2026-09-30 回填 actual=81.9（Reuters+AP+Continuum+stockwirex 4源✅）；暴跌 6.7 点远低于共识 89.2（日历 fc 90.0 亦大偏），2014年4月来最低（近12.5年低点，低于疫情低点）；⚠️ 8月值 89.4→88.6 修正（Reuters/AP/Continuum 统一口径 81.9+6.7=88.6，昨日 3 源 89.4 系下修前值）；主因中东战争能源涨价+利率上升+生活成本高企（油价/杂货价 write-in 提及创新高）；现况 109.3(-7.9)/预期 63.6(-5.9)；jobs plentiful 23.6%（2021年2月来最低）/hard to get 21.9%；劳动市场差异 1.7%（前4.2）→失业率上行风险；通胀预期均值 6.1%/中位 5.1%（+0.3）；全政治派别、年龄、收入组别全线恶化，11/3 中期选举前警讯")
changed.append(('US_CONSUMER_CONF_20260929', 'actual=81.9 prev 89.4→88.6 released'))

# ============ 5. JOLTS 9/29 ============
e = find('US_JOLTS_20260929')
assert e, 'US_JOLTS_20260929 not found'
e['actual'] = 707.9
e['status'] = 'released'
append_notes(e, "2026-09-30 回填 actual=707.9 万（Reuters+Continuum+stockwirex 3源✅）；大低于共识 722.5 万，-25.6 万至 2025年12月来最低（前值 727.1 万咬合✅）；每失业者对应岗位 1.01（前 1.06，2022 年峰值约 2.0）；分行业：专业商业服务 -11.9 万/医疗社会援助 -11.5 万/州地方政府 -5.8 万，零售/休闲酒店/信息增加；招聘 +4.6 万/离职 -5.8 万/辞职 -2.3 万；⚠️ 回应率仍低（30%）权重宜低；与消费者信心同日双弱=劳动力需求降温信号，10/2 非农（预期 84K）关键")
changed.append(('US_JOLTS_20260929', 'actual=707.9 released'))

# ============ 6. 达拉斯联储服务业 9/29 ============
e = find('US_DALLAS_FED_SERVICES_20260929')
assert e, 'US_DALLAS_FED_SERVICES_20260929 not found'
e['actual'] = -1.8
e['forecast'] = 2.3
e['status'] = 'released'
append_notes(e, "2026-09-30 回填 actual=-1.8（MNI+TE 双源✅，预期 2.3）；5月以来首次转负（前值 4.2 咬合✅）；revenue -0.9（前 6.6，2025年11月来首次负值）/company outlook -3.2（前 3.0）/uncertainty 21.4(+9)；投入价格 42.1（45个月最高，前 35.6）/收价 14.9（41个月最高）——能源成本推升通胀压力；employment 4.1（3个月最高）为少数亮点；未来 general activity 10.7（前 18.6）；与 9/28 制造业 9.8 强劲形成反差（服务弱制造强）；10 月 5 个区域联储活动指数中 3 降 2 升")
changed.append(('US_DALLAS_FED_SERVICES_20260929', 'actual=-1.8 fc=2.3 released'))

# ============ 7. 10/27 事件 prev 预填 ============
e = find('US_CONSUMER_CONF_20261027')
assert e, 'US_CONSUMER_CONF_20261027 not found'
e['previous'] = 81.9
append_notes(e, "2026-09-30 预填 prev=81.9（9月 actual）")
changed.append(('US_CONSUMER_CONF_20261027', 'prev=81.9'))

e = find('US_DALLAS_FED_SERVICES_20261027')
assert e, 'US_DALLAS_FED_SERVICES_20261027 not found'
e['previous'] = -1.8
append_notes(e, "2026-09-30 预填 prev=-1.8（9月 actual，TE 口径）")
changed.append(('US_DALLAS_FED_SERVICES_20261027', 'prev=-1.8'))

# ============ 保存 ============
with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ============ 回读 assert ============
with open(CAL, 'r', encoding='utf-8') as f:
    data2 = json.load(f)
events2 = data2['events'] if isinstance(data2, dict) else data2

def find2(eid):
    for x in events2:
        if x.get('id') == eid:
            return x
    return None

checks = [
    ('CN_PMI_MFG_20260930', 'actual', 50.1), ('CN_PMI_MFG_20260930', 'previous', 49.8),
    ('CN_PMI_NONMFG_20260930', 'actual', 50.2), ('CN_PMI_NONMFG_20260930', 'previous', 49.0),
    ('JP_INDUSTRIAL_20260930', 'actual', -1.7),
    ('US_CONSUMER_CONF_20260929', 'actual', 81.9), ('US_CONSUMER_CONF_20260929', 'previous', 88.6),
    ('US_JOLTS_20260929', 'actual', 707.9),
    ('US_DALLAS_FED_SERVICES_20260929', 'actual', -1.8), ('US_DALLAS_FED_SERVICES_20260929', 'forecast', 2.3),
    ('US_CONSUMER_CONF_20261027', 'previous', 81.9),
    ('US_DALLAS_FED_SERVICES_20261027', 'previous', -1.8),
]
ok = 0
for eid, field, want in checks:
    e = find2(eid)
    assert e, f'{eid} missing after save'
    got = e.get(field)
    assert got == want, f'{eid}.{field}: got {got!r} want {want!r}'
    assert e.get('notes') and '2026-09-30' in e['notes'], f'{eid} notes missing'
    ok += 1
print(f'ALL OK: {ok} field checks + notes verified')
for eid, desc in changed:
    print(' *', eid, '->', desc)
