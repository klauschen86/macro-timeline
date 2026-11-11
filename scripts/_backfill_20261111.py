# -*- coding: utf-8 -*-
"""_backfill_20261111.py — 2026-11-11 回填昨晚(11-10)发布的4项数据
①CN_TRADE_20261110 中国10月进出口顺差 1052.8亿美元(海关总署官网+央视网/澎湃 双源✅)
②US_CPI_20261110 环比+0.4%(BLS官网+新华财经 双源✅;官方同比因2025-10停摆缺基期未发布)
③US_CORE_CPI_20261110 环比+0.3%(同上)
④US_EXISTING_HOME_20261110 387万户(⚠️单源:Gate财经日历;预期385万来源阿斯达克)
另:US_CPI_20261112/US_CORE_CPI_20261112 为重复事件(10月CPI已于11-10发布,BLS官网确认),
按 CN_TRADE_20260910 先例加禁填标注不回填。
写盘后回读 assert。
"""
import json, sys

PATH = 'data/calendar.json'
cal = json.load(open(PATH, encoding='utf-8'))
byid = {e['id']: e for e in cal['events']}

UPD = {
 'CN_TRADE_20261110': {
   'actual': 1052.8, 'status': 'released',
   'notes': '10月贸易顺差1052.8亿美元(预期1260=华泰11-8单源预测,大幅低于预期⚠️);出口4123.3亿+35.2%(前值36.3%回落)/进口3070.5亿+41.6%(大超预期+22.0%,进口激增收窄顺差);进出口总值7193.8亿+37.9%。人民币计:顺差7127.8亿元/出口2.79万亿+28.7%/进口2.08万亿+34.7%。结构:集成电路出口+137.1%、自动数据处理设备+114.8%=AI链极高景气;新能源乘用车出口58.2万辆+144.7%。前10月顺差1.04万亿美元。来源:海关总署官网+央视网/澎湃(数据表引海关总署) 双源✅'
 },
 'US_CPI_20261110': {
   'actual': 0.4, 'status': 'released',
   'notes': '⚠️口径:环比季调+0.4%(预期0.3/前值0.6),官方同比因2025-10政府停摆缺基期BLS未发布12个月变化(actual填环比口径);美银插值模型估算同比≈3.8%/核心≈2.7%(非官方,仅供参考)。核心环比+0.3%连续3个月(8-10月),住房+0.3%贡献超30%/食品+0.5%/能源+0.7%(较9月+5.2%大幅回落)/二手车-1.2%。市场影响:2年期美债收益率单日+15bp破4.7%(2025-04来最大),12月FOMC加息概率近100%、50bp概率升至~15%;Waller:核心若≥0.3%"或需更强政策动作"、12/8-9应考虑50bp。来源:BLS官网新闻稿+新华财经+人民日报英文端 多源✅'
 },
 'US_CORE_CPI_20261110': {
   'actual': 0.3, 'status': 'released',
   'notes': '⚠️口径:核心CPI环比季调+0.3%(前值0.3,连续3个月0.3=粘性凸显);官方同比缺失(2025-10停摆缺基期),美银模型估算核心同比≈2.7%(非官方)。分项:娱乐/医疗/车险/家居/教育上涨,二手车-1.2%/通讯-0.1%为少数负增长。Natixis:连续3个月0.3%是"美联储不可接受的节奏",50bp"完全在桌面上"。来源:BLS官网+新华财经+人民日报英文端 多源✅'
 },
 'US_EXISTING_HOME_20261110': {
   'actual': 387, 'forecast': 385, 'status': 'released',
   'notes': '10月成屋销售年化387万户(预期385万/前值399万,环比约-3.0%创近期新低);下次发布12-9 23:00。⚠️单源待补验:Gate财经日历新闻(其"10-13公布"系日期错标,10月数据实际11-10发布);预期值来源阿斯达克"下周备忘"(fc 385/prev 399);10-30《Mortgage Elements》确认9月值399万(+1.5%,-2.2%同比)与日历一致。待NAR原文或权威中文媒体(金十/财联社)补验后升级双源✅'
 },
 'US_CPI_20261112': {
   'notes': '⚠️ 重复事件(模式日期错位): 美国10月CPI已于2026-11-10 21:30 BJS发布(见US_CPI_20261110,BLS官网新闻稿确认为11-10 8:30 ET);11月CPI预计12月中旬发布,本事件禁止回填'
 },
 'US_CORE_CPI_20261112': {
   'notes': '⚠️ 重复事件(模式日期错位): 美国10月核心CPI已于2026-11-10发布(见US_CORE_CPI_20261110),本事件禁止回填'
 },
}

changed = []
for eid, patch in UPD.items():
    e = byid.get(eid)
    if e is None:
        print('MISSING event:', eid); sys.exit(1)
    for k, v in patch.items():
        e[k] = v
    changed.append(eid)

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

# 写盘后回读 assert
chk = {e['id']: e for e in json.load(open(PATH, encoding='utf-8'))['events']}
errs = []
if chk['CN_TRADE_20261110']['actual'] != 1052.8: errs.append('CN_TRADE actual')
if chk['US_CPI_20261110']['actual'] != 0.4: errs.append('US_CPI actual')
if chk['US_CORE_CPI_20261110']['actual'] != 0.3: errs.append('US_CORE actual')
if chk['US_EXISTING_HOME_20261110']['actual'] != 387: errs.append('HOME actual')
for eid in ('US_CPI_20261110','US_CORE_CPI_20261110','CN_TRADE_20261110','US_EXISTING_HOME_20261110'):
    if chk[eid]['status'] != 'released': errs.append(eid+' status')
for eid in ('US_CPI_20261112','US_CORE_CPI_20261112'):
    if chk[eid].get('actual') is not None: errs.append(eid+' should have no actual')
    if '禁止回填' not in (chk[eid].get('notes') or ''): errs.append(eid+' no warn note')
rel = sum(1 for e in chk.values() if e.get('status')=='released')
if errs:
    print('ASSERT FAILED:', errs); sys.exit(1)
print(f'OK: backfilled {len(changed)} events (4 actuals + 2 duplicate-warn), assert passed; Released={rel}')
