# -*- coding: utf-8 -*-
"""2026-11-20 一次性后处理：
0) 还原 mcp_inject 第8次同型污染（25个错期历史事件 + UK_CPI 日期回滚 + US初请 fc/prev 覆盖）→ 从 HEAD 全对象就地还原
1) US_JOBLESS_CLAIMS_20261119 回填 actual=20.3万（11-19 21:30 BJS 发布，Web 3源✅）
2) CN_LPR_1Y/5Y_20261120 回填 actual=3.0/3.5 持平（11-20 09:15 BJS 央行授权发布，Web 2源✅）
3) JP_CPI_20261120 回填 actual=2.2（核心CPI口径，与历史序列一致；11-20 07:30 BJS 总务省发布，新华财经×2+每经 3源✅）
4) CN_M2/SOCIAL_FINANCING/NEW_LOANS_20261112 官方回填（央行11-13发布：M2 7.1%/社融11429亿/新增贷款-1000亿）
保留：US_JOBLESS_CLAIMS_20270121（合法新模式事件）
"""
import json
import os
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')
MARK = '【2026-11-20'

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


# ---------- 0) 污染还原（就地 clear+update，cmap 引用替换不生效教训） ----------
POLLUTED = [
    'US_PPI_20260114', 'US_CORE_CPI_20260311', 'US_CPI_20260311',
    'EU_FF_Final_CPI_y_y_20260617', 'EU_FF_Final_Core_CPI_y_y_20260617',
    'US_FF_JOLTS_Job_Openings_20260630', 'EU_FF_Core_CPI_Flash_Estimate_y_y_20260701',
    'EU_FF_PPI_m_m_20260706', 'US_FF_Core_CPI_m_m_20260714', 'US_FF_Core_PPI_m_m_20260715',
    'EU_FF_Final_Core_CPI_y_y_20260717', 'US_CPI_20260812', 'US_CORE_CPI_20260812',
    'US_NYFED_1Y_INFLATION_20260908', 'US_PPI_20260910', 'US_CPI_20260911',
    'US_CORE_CPI_20260911', 'US_GDP_FINAL_20260930', 'US_CPI_20261014',
    'US_CORE_CPI_20261014', 'US_PPI_20261015', 'EU_CPI_FLASH_20261104',
    'US_UNEMPLOYMENT_20261106', 'US_CPI_20261110', 'US_CORE_CPI_20261110',
    'UK_CPI_20261117', 'US_JOBLESS_CLAIMS_20261119',
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

# ---------- 1) US 初请回填 ----------
jc = by['US_JOBLESS_CLAIMS_20261119']
jc['actual'] = 20.3
jc['status'] = 'released'
append_notes(jc,
    '【2026-11-20回填】实际20.3万(至11/14当周),高于预期19.8万(Econoday)miss;前值上修20.0→20.2万;四周均值19.775万(增2000人);'
    '续请176.3万(预期171万)较下修后前值169.3万跳增7万创8月底以来最高,显示再就业难度上升;受保失业率1.1%。'
    '劳动力市场"初请稳+续请升"分化:初请同比低约8.6%,低初请给美联储继续抗通胀留空间,但续请跳升不支持12月单次加息50bp(利率期货12月+25bp定价约九成/+50bp约8%)。'
    '同日费城联储11月制造业指数6.3(预期20.55/前值20.9)创六个月最低,新订单-0.4转负。'
    '来源:财闻早知道(腾讯/网易)+智通财经(中金在线)+上海证券报 3源✅(Web多源替代双源)')
log.append('OK US_JOBLESS_CLAIMS_20261119 actual=20.3')

# ---------- 2) LPR 回填 ----------
for eid, val, label in (('CN_LPR_1Y_20261120', 3.0, '1年期'), ('CN_LPR_5Y_20261120', 3.5, '5年期以上')):
    e = by[eid]
    e['actual'] = val
    e['status'] = 'released'
    append_notes(e,
        f'【2026-11-20回填】11月{label}LPR {val}%持平(预期3.0/3.5✅/前值3.0/3.5),央行授权全国银行间同业拆借中心11-20 09:15 BJS公布;'
        f'8/20以来连续第4个月不变;11-2起央行将隔夜逆回购(1.25%)改为每日主要操作工具并宣布政策利率"换锚",Q3货政报告提出贷款利率定价基准由单一参考LPR向多元定价基准转型,LPR政策信号意义弱化;'
        f'28家机构调查中5家预计下调但未兑现;符合预填持平推断。'
        f'来源:微信今日新闻晨报(引央行授权发布)+NowPrice官方日历口径 2源✅')
    log.append(f'OK {eid} actual={val}')

# ---------- 3) 日本 CPI 回填 ----------
jp = by['JP_CPI_20261120']
jp['actual'] = 2.2
jp['status'] = 'released'
append_notes(jp,
    '【2026-11-20回填】10月全国核心CPI(除生鲜)同比+2.2%(市场预期2.3 miss/前值2.1,2025-12以来最大涨幅,连续2个月≥2%);'
    '本日历口径与历史一致跟踪核心CPI序列;整体CPI同比+2.3%;核心核心CPI(除生鲜能源)+2.2%(前值2.4回落)。'
    '预填fc 2.1系investing+cashbackforex双源口径偏低,实际市场共识(新华财经引调查)2.3,实际2.2介于两者。'
    '推手:能源成本上升+日元疲弱+AI热潮半导体涨价;略低于预期但物价压力未消退。'
    '市场:日银12月17-18会议加息25bp至1.50%概率约86%(路透调查61/71位经济学家),将成37年来首次自然年内3次加息;植田和男连续两日重申继续加息立场,警告核心CPI可能加快至远超2%;'
    '掣肘:Q3 GDP年率-0.1%四季度来首次负增长,私人消费连续两季为负。'
    '来源:新华财经cnfin×2(引总务省)+每日经济新闻/腾讯+新浪财经 3源✅')
log.append('OK JP_CPI_20261120 actual=2.2')

# ---------- 4) CN 金融数据官方回填（11-13 遗留，央行官网一手） ----------
cn_fin = {
    'CN_M2_20261112': dict(actual=7.1, rd='2026-11-13',
        note='【2026-11-20官方回填】10月末M2同比+7.1%(预期口径广发7.2微高估/前值7.2回落0.1pct,同比低1.1pct);M2余额359.06万亿;M1 +4.4%(较上月回升1.2pct,余额116.9万亿),M2-M1剪刀差收窄至2.7%;M0 +10.7%。'
             '下行主因:当月新增贷款为负拖累存款派生+政府债券融资大增带动财政存款增加(王青/冯琳)。'
             '发布:央行11-13官网发布10月金融统计数据报告(11-12日历日期系模式偏差,官方实际11-13);'
             '11-13拦截的污染稿(M2 8.2%/社融存量8.5%)确证为假——官方真值7.1%/7.2%。'
             '来源:央行报告(光明网/央广网/央视网/中国经济网/每日经济新闻 5源✅)'),
    'CN_SOCIAL_FINANCING_20261112': dict(actual=11429, rd='2026-11-13',
        note='【2026-11-20官方回填】10月新增社融11429亿(预期广发12788亿高估/同比多增3251亿;华夏时报口径1.15万亿/3333亿微异);'
             '1-10月累计28.61万亿(同比少增2.29万亿);10月末社融存量469.16万亿同比+7.2%(较9月回升0.1pct)。'
             '结构:政府债券1.19万亿主力(同比多增7017亿)+企业债3468亿+委托贷款贡献(8000亿新型政策性金融工具经委托贷款落地);直接融资占比52.99%超信贷占比14pct。'
             '发布:央行11-13官网(与M2同批);11-13污染稿"8150亿"确证为假。'
             '来源:中国经营报(11429亿精确值)+北京日报+华夏时报+央视网 4源✅'),
    'CN_NEW_LOANS_20261112': dict(actual=-1000, rd='2026-11-13',
        note='【2026-11-20官方回填】10月新增人民币贷款-1000亿(预期广发-1760亿高估偏弱/同比多减3200亿;环比少增1.18万亿,传统信贷小月);'
             '1-10月累计11.42万亿(前三季度11.52万亿→单月-1000亿,每经自洽验算✅);10月末贷款余额283.33万亿同比+4.7%(续创有记录以来最低,环比回落0.1pct)。'
             '结构:企事业-1600亿(中长贷+1600亿多增1300亿/票据-3117亿)/住户-4300亿(短贷-2700亿/中长贷-1563亿),居民继续降杠杆。'
             '解读:贷款"降速提质"新常态,债贷替换(企业债对贷款替代效应增强)。'
             '发布:央行11-13官网(与M2同批)。'
             '来源:每日经济新闻(累计口径自洽)+北京日报+华夏时报+中国经营报 4源✅'),
}
for eid, d in cn_fin.items():
    e = by.get(eid)
    if e is None:
        log.append(f'MISS {eid}')
        continue
    e['actual'] = d['actual']
    e['status'] = 'released'
    if e.get('release_date') != d['rd']:
        e['release_date'] = d['rd']
        append_notes(e, f"【2026-11-20日期纠正】release_date 11-12→11-13(央行官方11-13发布)。")
    append_notes(e, d['note'])
    log.append(f"OK {eid} actual={d['actual']} rd={d['rd']}")

# ---------- 写回 + 回读 assert ----------
if isinstance(cal, dict):
    cal['events'] = events
with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=1)

with open(CAL, encoding='utf-8') as f:
    data2 = json.load(f)
by2 = {e['id']: e for e in data2['events']}
ok = True

# 污染还原 assert：与 HEAD 逐字段一致（US_JOBLESS_CLAIMS_20261119 已在还原后合法回填，单独校验）
for eid in POLLUTED:
    if eid == 'US_JOBLESS_CLAIMS_20261119':
        continue
    a, b = hb.get(eid, {}), by2.get(eid, {})
    if json.dumps(a, sort_keys=True, ensure_ascii=False) != json.dumps(b, sort_keys=True, ensure_ascii=False):
        print(f'ASSERT FAIL: {eid} 未还原到HEAD'); ok = False

# 回填 assert
checks = [
    ('US_JOBLESS_CLAIMS_20261119', 20.3, 'released'),
    ('CN_LPR_1Y_20261120', 3.0, 'released'),
    ('CN_LPR_5Y_20261120', 3.5, 'released'),
    ('JP_CPI_20261120', 2.2, 'released'),
    ('CN_M2_20261112', 7.1, 'released'),
    ('CN_SOCIAL_FINANCING_20261112', 11429, 'released'),
    ('CN_NEW_LOANS_20261112', -1000, 'released'),
]
for eid, act, st in checks:
    e = by2.get(eid, {})
    if e.get('actual') != act:
        print(f'ASSERT FAIL: {eid}.actual={e.get("actual")}'); ok = False
    if e.get('status') != st:
        print(f'ASSERT FAIL: {eid}.status={e.get("status")}'); ok = False
    if MARK not in notes_of(e):
        print(f'ASSERT FAIL: {eid} notes marker'); ok = False
if by2.get('US_JOBLESS_CLAIMS_20270121') is None:
    print('ASSERT FAIL: NEW 20270121 事件丢失'); ok = False

print('\n'.join(log))
print('READBACK:', 'ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
