# -*- coding: utf-8 -*-
"""2026-10-29 一次性后处理（回填 5 项已发布实际值，幂等：actual 已存在则跳过）：
1) 耐用品订单 9月初值（10-27 20:30 BJS）：+1.8%（预期口径1.4~1.9差异存注，前值上修至0.1%）
2) 新屋销售 9月（10-27 22:00 BJS）：67.6万户（预期65.0/65.1，前值68.4→68修正）
3) 谘商会消费者信心 10月（10-27 22:00 BJS）：91.7（预期80.4/81，9月修订84.2，6月以来新高）
4) 达拉斯联储服务业 10月（10-27 22:30 BJS）：4.0（市场原预期-2.9，9月-1.8转正）
5) FOMC 利率决议（10-29 02:00 BJS）：维持3.75%-4.00%不变（10:2投票，库克/哈马克主张加息25bp）
今晚 20:30 初请/GDP初值/PCE 未发布，留待明日回填。
"""
import json
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')

cal = json.load(open(CAL, encoding='utf-8'))
n = 0
for e in cal['events']:
    eid = e.get('id', '')
    # 1) 耐用品订单 9月初值
    if eid == 'US_DURABLE_GOODS_20261026' and e.get('actual') is None and e.get('release_date') == '2026-10-27':
        e['actual'] = 1.8
        e['previous'] = 0.1
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-29回填: 9月初值+1.8%(五个月最大增幅, 新订单3454亿美元), 前值上修至0.1%; '
            '预期口径分歧1.4~1.9%(新华财经1.4/腾讯1.9)存注; 商用飞机订单+28.4%, 核心资本品订单+0.5%(预期0.7), '
            '核心资本品出货+1.2%利多Q3 GDP; 双源✅新华财经10-27/10-28 + 格隆汇10-27(腾讯网)')
        n += 1
    # 2) 新屋销售 9月
    elif eid == 'US_NEW_HOME_SALES_20261026' and e.get('actual') is None and e.get('release_date') == '2026-10-27':
        e['actual'] = 67.6
        e['previous'] = 68.0
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-29回填: 9月67.6万户超预期(预期65.0~65.1), 环比-0.6%, 前值68.4修正为68; '
            '中位售价40.04万美元(同比-3.9%); 双源✅财联社10-27 + 新华财经10-27 + 每经10-27')
        n += 1
    # 3) 谘商会消费者信心 10月
    elif eid == 'US_CONSUMER_CONF_20261027' and e.get('actual') is None:
        e['actual'] = 91.7
        e['forecast'] = 80.4
        e['previous'] = 84.2
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-29回填: 10月91.7大超预期(预期80.4, 东财口径81), 现状指数120.4/预期指数72.6, '
            '9月修订值84.2(原值81.9), 6月以来新高+7.5点; 油价回落驱动; 双源✅新华财经10-27 + 中新社/光明网10-27')
        n += 1
    # 4) 达拉斯联储服务业 10月
    elif eid == 'US_DALLAS_FED_SERVICES_20261027' and e.get('actual') is None:
        e['actual'] = 4.0
        e['forecast'] = -2.9
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-29回填: 10月4.0转正(市场原预期-2.9/前值-1.8), 收入指数4.4(前值-0.9); '
            '双源✅新浪7x24快讯 + AASTOCKS/Yahoo财经10-27')
        n += 1
    # 5) FOMC 利率决议
    elif eid == 'US_FOMC_2026-10-29' and e.get('actual') is None:
        e['actual'] = '3.75%-4.00%（维持不变）'
        e['forecast'] = '维持不变'
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-29回填: 维持3.75%-4.00%不变(符合预期, 会前CME维持概率92.8%), 10:2投票, '
            '库克/哈马克主张加息25bp(库克2022年来首次反对); 声明: 通胀高位+支出韧性+就业同步; '
            '沃什拒绝前瞻指引; 12月加息25bp概率~78-90%(CME 77.7%前值/ING有把握下注); '
            '多源✅新华社10-29快讯 + 中新社10-28 + 新华财经10-28 + 人民网')
        n += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

output = load_calendar()
generate_js(output)
print(f'20261029 fix: backfilled={n}; JS regenerated')
