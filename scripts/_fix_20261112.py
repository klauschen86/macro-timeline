# -*- coding: utf-8 -*-
"""_fix_20261112.py — 2026-11-12 批次修复与预填
A. US_EXISTING_HOME 日期根治 11-10→11-12（WSJ周报11-9+财联社投资日历11-12 双源确认今日发布;
   Gate财经日历"11-10"系日期错标——该源此前已两次错标）。撤销11-11批误采的 actual=387
   （发布尚未发生,387 疑为 Gate 预期值误采）。generate_calendar.py 加 DATE_OVERRIDES 1 条防回滚。
B. 今日预填（官方10月金融数据截至09:50未落地,机构前瞻分歧大,标注多源）:
   CN_M2 fc 7.2(广发)/分歧7.0(浙商系); CN社融 fc 12788亿(广发表)/分歧1.6-1.7万亿;
   CN贷款 fc -1760亿(广发,淡季转负共识)/分歧-2000亿; UK_GDP fc 0.0(ONS日历预估,单源⚠️)+Q3同日首估notes;
   US初请 fc 19.5万(MoneyDJ+pre-daily双源一致)/prev 18.9。
C. 明日预填: US_PPI fc 6.6(MoneyDJ+WSJ腾讯 双源✅)/prev 6.3;核心同比 fc 5.0持平。
   ⚠️ 11-09批记忆"fc 2.45"系理财宝错误稿,弃用(与9月6.3%及多源6.6%矛盾)。
写盘后回读 assert。
"""
import json, sys, io

CAL = 'data/calendar.json'
GEN = 'scripts/generate_calendar.py'

# ---------- A1. generate_calendar.py 加 DATE_OVERRIDES ----------
src = io.open(GEN, encoding='utf-8').read()
anchor = '("US_EXISTING_HOME", "2026-10"): "2026-10-13",'
assert anchor in src, 'anchor not found in generate_calendar.py'
assert '("US_EXISTING_HOME", "2026-11")' not in src, 'override key already exists!'
src = src.replace(anchor, anchor + '\n    ("US_EXISTING_HOME", "2026-11"): "2026-11-12",', 1)
io.open(GEN, 'w', encoding='utf-8').write(src)
print('A1: DATE_OVERRIDES added ("US_EXISTING_HOME","2026-11") -> 2026-11-12')

# ---------- A2. calendar.json 成屋销售事件改名+撤销误采 ----------
cal = json.load(io.open(CAL, encoding='utf-8'))
byid = {e['id']: e for e in cal['events']}
old = byid.get('US_EXISTING_HOME_20261110')
assert old is not None, 'US_EXISTING_HOME_20261110 missing'
assert byid.get('US_EXISTING_HOME_20261112') is None, 'target id already exists'
old['id'] = 'US_EXISTING_HOME_20261112'
old['release_date'] = '2026-11-12'
old['release_time'] = '23:00'
old['actual'] = None
old['forecast'] = 385
old['previous'] = 399
old['status'] = 'upcoming'
old['notes'] = ('10月成屋销售年化总数,今日(NAR)发布,共识385万套/前值399万(环比约-3%)。'
                '日期根治11-10→11-12:WSJ周报(11-9,腾讯转载)+财联社投资日历 双源确认今日发布;'
                'Gate财经日历"11-10"系日期错标(该源已三次错标),11-11批据此误采actual=387已撤销'
                '(发布尚未发生,387疑为Gate预期值)。11-12 23:00 BJS前后发布,明晨回填。'
                '背景:9月399万+1.5%四个月首增;30Y房贷利率10/8 7.40%创2023来新高压制签约。')
print('A2: US_EXISTING_HOME renamed 20261110->20261112, actual 387 reverted')

# ---------- B/C. 预填 ----------
UPD = {
 'CN_M2_20261112': {
   'forecast': 7.2,
   'notes': '10月M2同比,今日公布(央行,时点待定)。机构前瞻分歧:广发7.2%(环比持平)/浙商系7.0%(回落0.2pct),取广发;中财网11-6"7.3%"系可疑前瞻弃用。前值7.2(9月末,央行三季度报告确证)。M1前瞻:浙商3.0%/广发3.3%(前值3.2)。背景:11-2公开市场操作换锚隔夜逆回购(1.25%)后首个完整传导月。来源:广发证券11-5+浙商系研报(新浪) 双源(前瞻)✅,官方值落地后回填'
 },
 'CN_SOCIAL_FINANCING_20261112': {
   'forecast': 12788,
   'notes': '10月社融增量(亿元),今日公布。机构前瞻分歧大:广发12788亿(同比多增4610亿)/浙商系16000亿(多增7843亿)/中财网11-6约17000亿(可疑前瞻),取广发(含分项明细最完整);社融存量增速前瞻7.2%(广发)/7.3%(浙商/中财网)。前值35500亿(9月,广发表35476咬合✅)。支撑:政府债净融资约1.1万亿(低基数同比多增)。官方值落地后以权威源回填'
 },
 'CN_NEW_LOANS_20261112': {
   'forecast': -1760,
   'notes': '10月新增人民币贷款(全口径,亿元),今日公布。机构前瞻一致为负(信贷淡季偏淡):广发-1760亿(同比少增3960亿)/浙商系-2000亿(同比少增4200亿),取广发;票据到期显著高于贴现(票据融资约-3100亿)为主因,新型政策性金融工具8000亿投放完毕对委托贷款形成对冲。前值10800亿(9月,广发表咬合✅)。官方值落地后以权威源回填'
 },
 'UK_GDP_20261112': {
   'forecast': 0.0,
   'notes': '9月月度GDP环比,15:00 BJS(07:00 GMT)发布,同日Q3首估。9月fc 0.0%(ONS日历预估,AskTraders引,单源⚠️)/前值0.1%(8月,生产+0.8%拉动/服务业零增长/建筑-0.2%);Q3环比首估:BoE 11月报告预估0.7%(前值Q2 0.5%),调查口径动能仅0.2%——0.4%需9月单月-0.9%冲击月,概率低。分项日历预估:生产-0.3%/建筑-0.1%。背景:BoE 11-5加息至4.00%(8-1票),12月再加与否存分歧。来源:AskTraders+piptheory+financecalendar 多源(前瞻)✅'
 },
 'US_PPI_20261113': {
   'forecast': 6.6,
   'previous': 6.3,
   'notes': '10月PPI同比,明日21:30 BJS发布。fc 6.6%(前值6.3%,再创新高)/核心同比fc 5.0%(持平)/环比fc 0.4%(前值1.3%)/核心环比fc 0.3%(前值0.7%)。来源:MoneyDJ(11-9)+WSJ周报(腾讯11-9) 双源一致✅。⚠️11-09批记忆"fc 2.45"系理财宝错误稿(前值口径错乱),弃用。背景:9月PPI 6.3%为2022-12来最大,能源贡献商品涨幅80%+;10月CPI环比0.4%超预期后,12月加息概率近100%、50bp概率~15%'
 },
 'US_JOBLESS_CLAIMS_20261112': {
   'forecast': 19.5,
   'previous': 18.9,
   'notes': '截至11/7当周初请(万人),今晚21:30 BJS发布。fc 19.5万(MoneyDJ)/194K(pre-daily预测市场早报) 双源一致✅;前值18.9万(至10/31当周,低于预期,四周均值19.475万)。低招聘低裁员格局延续;12月加息概率近100%背景下劳动力市场韧性是关键观察项'
 },
}
for eid, patch in UPD.items():
    e = byid.get(eid)
    if e is None:
        print('MISSING event:', eid); sys.exit(1)
    for k, v in patch.items():
        e[k] = v
print('B/C: prefilled', len(UPD), 'events')

with io.open(CAL, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

# ---------- 回读 assert ----------
chk = {e['id']: e for e in json.load(io.open(CAL, encoding='utf-8'))['events']}
errs = []
h = chk.get('US_EXISTING_HOME_20261112')
if h is None or h['actual'] is not None or h['forecast'] != 385 or h['previous'] != 399 or h['release_date'] != '2026-11-12':
    errs.append('EXISTING_HOME rename/revert')
if chk.get('US_EXISTING_HOME_20261110') is not None:
    errs.append('old id resurrected')
if chk['US_PPI_20261113']['forecast'] != 6.6 or chk['US_PPI_20261113']['previous'] != 6.3:
    errs.append('US_PPI prefill')
if chk['US_JOBLESS_CLAIMS_20261112']['forecast'] != 19.5 or chk['US_JOBLESS_CLAIMS_20261112']['previous'] != 18.9:
    errs.append('CLAIMS prefill')
if chk['CN_M2_20261112']['forecast'] != 7.2 or chk['CN_SOCIAL_FINANCING_20261112']['forecast'] != 12788 or chk['CN_NEW_LOANS_20261112']['forecast'] != -1760:
    errs.append('CN prefill')
if chk['UK_GDP_20261112']['forecast'] != 0.0:
    errs.append('UK_GDP prefill')
gsrc = io.open(GEN, encoding='utf-8').read()
if '("US_EXISTING_HOME", "2026-11"): "2026-11-12"' not in gsrc:
    errs.append('override in generate_calendar.py')

if errs:
    print('ASSERT FAIL:', errs); sys.exit(1)
print('回读 assert ALL OK')
