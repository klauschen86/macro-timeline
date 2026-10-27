# -*- coding: utf-8 -*-
"""2026-10-27 一次性后处理：
1) 回填 actual：堪萨斯联储制造业指数(10-22, 16)、达拉斯联储制造业指数(10-26, 13.4)
2) 日期修正：耐用品订单/新屋销售 9月值 实际发布日为 10-27（官方日程+TE确证），模式日期 10-26 有偏差
注意：run_daily 的 merge_calendars 会用模式日期重置 release_date，本脚本须在 run_daily 之后运行并重新生成 JS；
回填部分幂等（actual 已存在则跳过），日期修正部分每次 run_daily 后需重跑（同 UK CPI 模式）。
"""
import json
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')

cal = json.load(open(CAL, encoding='utf-8'))
n_backfill = 0
n_date = 0
for e in cal['events']:
    eid = e.get('id', '')
    # 1) 回填：堪萨斯联储制造业指数 10月
    if eid == 'US_KC_FED_20261022' and e.get('actual') is None:
        e['actual'] = 16
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-27回填: 10月制造业指数16(前值20回落), 综合指数11(前值14); '
            '双源✅新浪速报10-22 23:02 + PChome 10-23(newsquawk同口径)')
        n_backfill += 1
    # 1) 回填：达拉斯联储制造业指数 10月
    elif eid == 'US_DALLAS_FED_20261026' and e.get('actual') is None:
        e['actual'] = 13.4
        e['forecast'] = 8.8
        e['status'] = 'released'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-27回填: 13.4超预期(预期8.8/前值9.8), 生产分项回落约14点; '
            '双源✅财联社10-26 + 东方财富国际金融要情10-27; fx678报预期7.0口径差异存注')
        n_backfill += 1
    # 2) 日期修正：耐用品订单 9月值 → 10-27 20:30 BJS
    elif eid == 'US_DURABLE_GOODS_20261026' and e.get('release_date') != '2026-10-27':
        e['release_date'] = '2026-10-27'
        e['previous'] = -0.1
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-27后处理: 日期修正至10-27 20:30 BJS(东财一周前瞻/新浪/腾讯三日历一致确证, '
            '8月前值下修为-0.1%); 共识1.5~1.8%(东财1.5/新浪1.7/腾讯1.8), tonight发布明日回填')
        n_date += 1
    # 2) 日期修正：新屋销售 9月值 → 10-27 22:00 BJS
    elif eid == 'US_NEW_HOME_SALES_20261026' and e.get('release_date') != '2026-10-27':
        e['release_date'] = '2026-10-27'
        e['notes'] = (e.get('notes', '') +
            ' | 2026-10-27后处理: 日期修正至10-27 22:00 BJS(TradingEconomics官方日历确证2026-10-27 14:00 GMT); '
            '共识65.0万户(-5%)/前值68.4万户与TE一致✅, tonight发布明日回填')
        n_date += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# 重新生成 JS（与 run_daily 同一入口）
output = load_calendar()
generate_js(output)
print(f'20261027 fix: backfilled={n_backfill}, date_fixed={n_date}; JS regenerated')
