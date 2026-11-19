# -*- coding: utf-8 -*-
"""2026-11-19 一次性后处理：
1) UK_CPI_20261117 回填 actual=3.6（ONS 11-18 15:00 BJS 发布，Web 多源 4 家✅）+ 日期修正 11-17→11-18（merge 会重置，须在 run_daily 后跑并重新生成 JS）
2) US_JOBLESS_CLAIMS_20261119 预填 fc/prev（今晚 21:30 BJS）
3) CN_LPR_1Y/5Y_20261120 预填 fc=prev（持平共识推断⚠️）
4) JP_CPI_20261120 预填 fc 2.1（investing+cashbackforex 双源✅）
5) US_JOBLESS_CLAIMS_20261126 加感恩节顺延标注（实际 11-25 周三发布）
"""
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')
MARK = '【2026-11-19'

cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events'] if isinstance(cal, dict) else cal
by = {e.get('id'): e for e in events}
log = []


def notes_of(e):
    return e.get('notes', '') or ''


def append_notes(e, text):
    e['notes'] = (notes_of(e) + ' | ' + text).strip(' |')


# ---------- 1) UK CPI 回填 + 日期修正 ----------
uk = by.get('UK_CPI_20261117')
if uk is None:
    log.append('MISS UK_CPI_20261117')
else:
    if uk.get('actual') is None:
        uk['actual'] = 3.6
        uk['status'] = 'released'
        append_notes(uk,
            '【2026-11-19回填】英10月CPI同比+3.6%(预期口径3.6/预填fc3.7系westock expect_uk单源偏差;低于英央行本月预测3.7),较9月3.5%抬升,创一年来新高;'
            '月率+0.5%(预期0.5✅/前值0.4);核心CPI同比2.8%持平符合预期;服务业CPI同比3.7%持平、低于预期3.8%。'
            '推手:汽车燃料价格(汽油环比+5.2便士/升至174.7便士为2022-08来最高、柴油199.5便士创历史新高)+烟草税提前上调;食品及非酒精饮品同比仅+0.9%创2021-09来最小涨幅形成对冲。'
            '市场:核心/服务业持稳令BoE 12月加息押注90%→80%(至明年底仍预期累计加息3-4次),英镑跌至五周低点附近;BoE回应预计明年年中通胀进一步上升(2027Q2接近5%)。'
            '来源:新华财经(cnfin)+中新社+央视财经+财联社+新华社微特稿 5源✅(Web多源替代双源)')
    if uk.get('release_date') != '2026-11-18':
        uk['release_date'] = '2026-11-18'
        append_notes(uk, '【2026-11-19日期后处理】release_date重置回11-17(merge按模式id重置),修正为11-18(ONS官方确证发布日)。')
    uk.setdefault('time', '15:00')
    log.append('OK UK_CPI_20261117 actual=3.6 rd=2026-11-18')

# ---------- 2) US 初请预填 ----------
jc = by.get('US_JOBLESS_CLAIMS_20261119')
if jc is None:
    log.append('MISS US_JOBLESS_CLAIMS_20261119')
else:
    if jc.get('forecast') is None:
        jc['forecast'] = 19.9
    if jc.get('previous') is None:
        jc['previous'] = 20.0
    append_notes(jc,
        '【2026-11-19预填】今晚21:30 BJS发布(至11/14当周);共识分歧19.6-20.0万:investing.com 19.9万/invest-nav(Nasdaq日历)19.8万/TradingEconomics 19.6万,取中上沿19.9万⚠️;'
        '前值20.0万(11-12实际,连9周≤20万,四周均值19.525万,续请169.7万);下周因感恩节(11-26周四)提前至11-25周三发布。')
    log.append('OK US_JOBLESS_CLAIMS_20261119 fc=19.9 prev=20.0')

jc2 = by.get('US_JOBLESS_CLAIMS_20261126')
if jc2 is not None:
    append_notes(jc2,
        '【2026-11-19日期标注】感恩节(11-26周四)假期,该期数据实际于11-25(周三)21:30 BJS发布(劳工部日程,cmelitegroup发布日程表);模式日期11-26待后续根治。')
    log.append('OK US_JOBLESS_CLAIMS_20261126 感恩节标注')

# ---------- 3) LPR 预填 ----------
for eid, val in (('CN_LPR_1Y_20261120', 3.0), ('CN_LPR_5Y_20261120', 3.5)):
    e = by.get(eid)
    if e is None:
        log.append(f'MISS {eid}')
        continue
    if e.get('forecast') is None:
        e['forecast'] = val
    append_notes(e,
        f'【2026-11-19预填】明日09:00公布11月LPR,预期持平{val}%(预填推断⚠️:日历内核实8/20-10/20连续3期actual均{val}不变+7天逆回购政策利率稳定无变动信号;当日独立机构共识源未检索到2026年最新稿,发布后以官方授权全国银行间同业拆借中心公告回填)。')
    log.append(f'OK {eid} fc={val}')

# ---------- 4) 日本 CPI 预填 ----------
jp = by.get('JP_CPI_20261120')
if jp is None:
    log.append('MISS JP_CPI_20261120')
else:
    if jp.get('forecast') is None:
        jp['forecast'] = 2.1
    if jp.get('previous') is None:
        jp['previous'] = 2.1
    append_notes(jp,
        '【2026-11-19预填】明日07:30 BJS(08:30 JST)发布10月全国CPI;核心CPI(除生鲜)fc 2.1%(investing.com+cashbackforex 双源✅)持平9月2.1%(连续第2月≥2%);'
        '先行指标东京10月CPI 2.7%高位(Mace News);日银10月展望报告:除生鲜CPI将明确超2%后于预测期后半段回落至2%附近。前值2.1%(9月,10-23批4源回填)。')
    log.append('OK JP_CPI_20261120 fc=2.1 prev=2.1')

# ---------- 写回 + 回读 assert ----------
if isinstance(cal, dict):
    cal['events'] = events
with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=1)

with open(CAL, encoding='utf-8') as f:
    data2 = json.load(f)
events2 = data2['events'] if isinstance(data2, dict) else data2
by2 = {e.get('id'): e for e in events2}
ok = True
uk2 = by2.get('UK_CPI_20261117', {})
if uk2.get('actual') != 3.6 or uk2.get('release_date') != '2026-11-18' or uk2.get('status') != 'released':
    print('ASSERT FAIL: UK_CPI_20261117'); ok = False
if MARK not in notes_of(uk2):
    print('ASSERT FAIL: UK notes marker'); ok = False
for eid, fc, prev in (('US_JOBLESS_CLAIMS_20261119', 19.9, 20.0),
                      ('CN_LPR_1Y_20261120', 3.0, None),
                      ('CN_LPR_5Y_20261120', 3.5, None),
                      ('JP_CPI_20261120', 2.1, 2.1)):
    e = by2.get(eid, {})
    if e.get('forecast') != fc:
        print(f'ASSERT FAIL: {eid}.forecast={e.get("forecast")}'); ok = False
    if prev is not None and e.get('previous') != prev:
        print(f'ASSERT FAIL: {eid}.previous={e.get("previous")}'); ok = False
    if MARK not in notes_of(e):
        print(f'ASSERT FAIL: {eid} notes marker'); ok = False
if by2.get('US_JOBLESS_CLAIMS_20261126') and MARK not in notes_of(by2['US_JOBLESS_CLAIMS_20261126']):
    print('ASSERT FAIL: 20261126 notes marker'); ok = False

print('\n'.join(log))
print('READBACK:', 'ALL OK' if ok else 'FAILED')

# ---------- 重新生成 JS ----------
output = load_calendar()
generate_js(output)
print('JS regenerated')
sys.exit(0 if ok else 1)
