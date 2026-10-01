# -*- coding: utf-8 -*-
"""2026-10-01 修复脚本：回填 9/30 晚美国 4 项 + 财新 PMI + 今晚事件预填"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
data = json.load(open(PATH, encoding='utf-8'))
evs = data['events'] if isinstance(data, dict) else data

def notes_append(e, txt):
    old = e.get('notes') or ''
    marker = txt.split('；')[0]
    base = old.lstrip('；')
    if marker in base:
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

# ① ADP 9月 +9.0万（预期7.0；前值3.8下修至3.6）——ADP官网+证券时报+Yahoo+金十 4源✅
patch('US_ADP_20260930', actual=9.0, forecast=7.0, previous=3.6, status='released',
      notes_append='2026-10-01 回填 actual=9.0万（ADP官网+证券时报+Yahoo Finance+金十/网易 4源✅）：大超预期7万（Dow Jones共识6.8万），扭转此前三个月下滑，5月以来招聘首次加速；⚠️前值3.8万下修至3.6万（previous已同步）；教育医疗+5.5万/休闲酒店+2.2万/制造+1.7万/建筑+1.5万，金融-1.6万/专业商业服务-1.1万；基础工资同比+3.2%、总薪酬+4.7%；北部地区+5.6万领跑、中型企业+5.4万为主力；ADP首席经济学家Richardson："强劲报告"；10/2非农共识8.4万/失业率4.1%')
# ② Q2 GDP 终值 +2.2%（预期/二次估算1.5，上修0.7pp）——BEA官方+新华社+证券时报+cnfin 4源✅
patch('US_GDP_FINAL_20260930', actual=2.2, forecast=1.5, previous=1.5, status='released',
      notes_append='2026-10-01 回填 actual=2.2%（BEA官网+新华社+证券时报+新华财经cnfin 4源✅）：较二次估算1.5%上修0.7pp，主因投资/居民消费/政府支出上调；⚠️BEA年度国民账户更新同日完成：Q1增速上修至2.5%；分项：个人消费+3.8%（拉动2.51pp）/非住宅固投+9%/出口+5%/进口+12.6%/政府支出-0.1%；GDI+2.6%（上修0.4pp）、GDP与GDI均值2.4%；企业利润下修169亿美元；PCE物价季度值5.0%（下修0.3pp）/核心3.3%（下修0.3pp）；Q3初值10/29公布')
# ③ 8月PCE同比 3.4%（预期3.7；7月下修3.7→3.4）——金十+cnfin+JEC官方表+财联社 多源✅
patch('US_PCE_20260930', actual=3.4, forecast=3.7, previous=3.4, status='released',
      notes_append='2026-10-01 回填 actual=3.4%（金十+cnfin快讯+JEC官方表3.42%+财联社 多源✅）：低于预期3.7；⚠️7月前值随年度方法论修订由3.7下修至3.4（previous已同步）；环比+0.3%（预期0.4，7月下修0.2→0.1）；能源环比+2.3%（汽油+4.4%）为最大推手；⚠️识别弃用：新浪一文"PCE同比2.6%"与金十/JEC/财联社3.4%矛盾，以BEA口径3.4%为准；个人支出环比+0.9%超预期（7月下修0.2→0.1）、实际支出+0.6%创2025年3月来最大；个人收入+0.2%（预期0.4）；储蓄率4.1%')
# ④ 8月核心PCE同比 3.0%（预期3.3；7月下修3.3→3.0）——金十+cnfin+JEC官方表(3.01%) 多源✅
patch('US_PCE_CORE_20260930', actual=3.0, forecast=3.3, previous=3.0, status='released',
      notes_append='2026-10-01 回填 actual=3.0%（金十+cnfin+JEC官方表3.01% 3源✅）：低于预期3.3，创2月来新低；⚠️7月前值随修订由3.3下修至3.0（previous已同步）；环比+0.2%（预期0.3，7月下修0.2→0.1）；⚠️BEA同日调整投资组合管理/计算机软件及配件/法律服务三项统计方法并回溯修订2021年以来数据——GS事前预估修订后同比约3.17%，实际3.0%低于该预估；市场反应：CME 10月维持利率不变概率52.9%、加息押注降至约9bp（前12bp）、2Y收益率跌至4.843%、金上4210美元——通胀降温+需求韧性并存，10/28-29 FOMC 前关键输入')
# ⑤ 财新9月制造业PMI 52.1（预期51.6/前值51.5）——TE+Gate.io+political.org 3源✅
patch('CN_CAIXIN_PMI_20261001', actual=52.1, forecast=51.6, previous=51.5, status='released', unit='',
      notes_append='2026-10-01 回填 actual=52.1（TE+Gate.io+political.org 3源✅）：大超预期51.6/前值51.5，4月以来最强扩张；内外需同步改善、外销7个月来最快；产出为4月来最快、就业随新订单回升；投入价格4个月来最高、出厂价格小幅上调；⚠️发布时点口径：Gate称9/30公布、日历排10/1 09:45，数值三源一致不受影响；与9/30官方PMI 50.1（小型企业48.9仍收缩）形成"官方企稳+财新更强"组合，关注中小企业分化；财新智库王喆：修复基础仍不稳固')
# ⑥ 今晚 ISM 制造业共识预填（helious 共识55）
patch('US_ISM_MFG_20261001', forecast=55.0, previous=54.6,
      notes_append='今晚22:00 BJS发布（10:00 AM ET）；helious共识55/前值54.6（8月回落1点但连续8个月扩张，价格分项71.1高企）；10月首个工作日发布（每月首个营业日）')
# ⑦ 初请前值链
patch('US_JOBLESS_CLAIMS_20261001', previous=19.7,
      notes_append='今晚20:30 BJS发布（至9/26当周）；前值19.7万（9/24发布，57年低位附近）；共识未获取可靠源，留空')
# ⑧ ADP 10月事件 prev 链预填
patch('US_ADP_20261104', previous=9.0,
      notes_append='prev=9月ADP 9.0万（10/1回填）')
# ⑨ 下月 PCE 事件 prev 链预填（若存在）
patch('US_PCE_20261028', previous=3.4, notes_append='prev=8月PCE 3.4%（10/1回填，年度修订后口径）')
patch('US_PCE_CORE_20261028', previous=3.0, notes_append='prev=8月核心PCE 3.0%（10/1回填，年度修订后口径）')

# 回读校验
json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
data2 = json.load(open(PATH, encoding='utf-8'))
evs2 = data2['events'] if isinstance(data2, dict) else data2
ok = True
expect = {
    'US_ADP_20260930': (9.0, 3.6), 'US_GDP_FINAL_20260930': (2.2, 1.5),
    'US_PCE_20260930': (3.4, 3.4), 'US_PCE_CORE_20260930': (3.0, 3.0),
    'CN_CAIXIN_PMI_20261001': (52.1, 51.5), 'US_ISM_MFG_20261001': (None, 54.6),
    'US_ADP_20261104': (None, 9.0),
}
for e in evs2:
    if e.get('id') in expect:
        a, p = expect[e['id']]
        if a is not None and e.get('actual') != a:
            print(f'MISMATCH {e["id"]} actual={e.get("actual")} expect {a}'); ok = False
        if p is not None and e.get('previous') != p:
            print(f'MISMATCH {e["id"]} previous={e.get("previous")} expect {p}'); ok = False
        if e.get('status') == 'pending' and e['id'] in ('US_ADP_20260930','US_GDP_FINAL_20260930','US_PCE_20260930','US_PCE_CORE_20260930','CN_CAIXIN_PMI_20261001'):
            print(f'MISMATCH {e["id"]} status pending'); ok = False
print('PATCHED:', changes)
print('ALL OK' if ok else 'FAIL')
