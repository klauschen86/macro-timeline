# -*- coding: utf-8 -*-
"""_fill_20261113.py — 2026-11-13 批次回填（11-12 昨晚发布项）
回填 3 项（多源验证），CN 金融数据 3 事件因污染稿矛盾不回填（详见 notes）。
铁律：就地 e.clear()+e.update()，写盘后回读 assert。
"""
import json

PATH = 'data/calendar.json'

cur = json.load(open(PATH, encoding='utf-8'))
cmap = {e['id']: e for e in cur['events']}

# 1) US_JOBLESS_CLAIMS_20261112: 20.0万（预期19.5 miss，前值上修18.9→19.1）
e = cmap['US_JOBLESS_CLAIMS_20261112']
e['actual'] = 20.0
e['previous'] = 19.1
e['status'] = 'released'
e['notes'] = ('截至11/7当周初请20.0万,预期19.5万(miss),前值由18.9万上修至19.1万;四周均值19.525万,'
              '续请169.7万(-2万)。财联社11-12 21:34快讯+每日新闻摘要(引DOL/新华财经)+陆家嘴财经早餐 三源✅。'
              'TradingEconomics页面189K系缓存旧值弃用(其"前次195K"与上周回填18.9亦矛盾)。'
              '12月加息概率近90%背景下初请反弹但仍处低位,劳动力市场韧性延续。')

# 2) US_EXISTING_HOME_20261112: 375万套（预期385,前值修正397）
e = cmap['US_EXISTING_HOME_20261112']
e['actual'] = 375
e['previous'] = 397
e['status'] = 'released'
e['notes'] = ('10月成屋销售年化375万套,预期385万(miss),前值由399万修正为397万,环比-5.5%,同比-8.8%,'
              '2010年8月以来最低(16年低点);西部地区1999年有记录以来最低。库存159万套(+4.6% YoY,2019年来同期最高)'
              '=5.1个月供应(2015年底来最高);中位价41.67万美元同比仅+0.4%(2月来最小涨幅)。'
              '财联社+每日经济新闻+华尔街见闻 多源✅。背景:30Y房贷利率7%+压制,住房可负担性指数2025年中来最低;'
              'Redfin:上月成交房屋36%曾降价挂牌(有记录来最高)。')

# 3) UK_GDP_20261112: 9月月度GDP环比 +0.2%（同日Q3首估+0.7%）
e = cmap['UK_GDP_20261112']
e['actual'] = 0.2
e['previous'] = 0.0
e['status'] = 'released'
e['notes'] = ('9月月度GDP环比+0.2%(fc 0.0,超预期),8月由+0.1%下修至0.0%;9月服务业+0.2%/生产+0.3%/建筑+0.8%。'
              '同日ONS发布Q3首估:环比+0.7%(Q2 0.5%,2024Q1以来最高,连续三季≥0.5%),同比+1.9%,'
              'AI相关投资与服务业主导(计算机编程3年最快增速)。ONS官网月度报告(权威源)+新华社/中国经济网(Q3) 双源✅。'
              '市场测算BoE 12月加息概率升至73%。隐忧:9月零售回落/消费信心走低/三季度企业投资不及预期。')

# 4) CN 三事件：不回填，仅更新 notes 记录矛盾与发布推迟
for eid, tag in [('CN_M2_20261112', 'M2'), ('CN_SOCIAL_FINANCING_20261112', '社融'),
                 ('CN_NEW_LOANS_20261112', '新增贷款')]:
    e = cmap[eid]
    e['notes'] = (e['notes'] + ' || 2026-11-13批处理:发布推迟至11-13(虎嗅11-13早报"预计11月13日公布",11-12未发)。'
                  '深圳新闻网11-12"已发布"稿(M2 8.2%/社融存量8.5%/新增社融8150亿/M1 6.2%)经合理性自检判AI污染稿弃用:'
                  '①与央行Q3报告(9月末M2 7.2%/社融7.1%,11-11发布,多源确证)冲突;②内部矛盾——称"较上月小幅回落"却跳升1.0pct;'
                  '③10月社融增量8150亿同比少增时存量增速不可能+1.4pct(2025年10月基数8178亿,数学上不可能)。'
                  '11-14批以央行官网《2026年10月金融统计数据报告》权威回填。'
                  '参考前瞻:新增贷款或为负(广发-1760亿/浙商-2000亿),社融1.3-1.6万亿,M2 7.0-7.3%。')

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(cur, f, ensure_ascii=False, indent=2)

# 写盘后回读 assert
check = json.load(open(PATH, encoding='utf-8'))
kmap = {e['id']: e for e in check['events']}
assert kmap['US_JOBLESS_CLAIMS_20261112']['actual'] == 20.0
assert kmap['US_EXISTING_HOME_20261112']['actual'] == 375
assert kmap['UK_GDP_20261112']['actual'] == 0.2
assert 'actual' not in kmap['CN_M2_20261112'] or kmap['CN_M2_20261112'].get('actual') is None
rel = sum(1 for e in check['events'] if e.get('status') == 'released' or (e.get('actual') is not None))
print('backfill OK. Released(with actuals):', rel, '/ total', len(check['events']))
