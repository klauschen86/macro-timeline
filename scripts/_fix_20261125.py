# -*- coding: utf-8 -*-
"""2026-11-25 数据层修正（不改脚本代码）：
1) 感恩节顺延日期纠正【复修】：run_daily.py 合并再次回滚 11-24 b 轮修正（已固化教训：
   日期修正必须在每次 run_daily 之后落地）——
   - US_DURABLE_GOODS_20261126 → 2026-11-25（感恩节顺延，21:30 BJS 同刻组合）
   - US_JOBLESS_CLAIMS_20261126 → 2026-11-25（同上）
2) US_CONSUMER_CONF_20261124 回填：11月谘商会消费者信心指数 actual=103.3（11-24 10:00 ET
   = 23:00 BJS 发布，2026-11-25 晨采）。前值：官方口径 10 月修正值 91.9（calendar 原 prev=91.7
   为修正前值，按官方发布稿更新为 91.9 并在 notes 记录修订）。
   来源 5 源✅：The Conference Board 官网（primary）+ AP + jkn.co.kr(韩联社中文) +
   uanalyze.com.tw + sedaily(首尔经济)。consensus 92.2（道琼斯统计），大超预期 11.1 点，
   2025-01 以来最高；现状指数 132.8(+13.7)、预期指数 83.6(+9.9)。
   westock CLI us_confidence 数据源尚无 11-24 值（feed 最新至 11-20 密歇根终值 51.5）。
"""
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')
MARK = '【2026-11-25'

cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events']
by = {e.get('id'): e for e in events}
log = []


def notes_of(e):
    return e.get('notes', '') or ''


def append_notes(e, text):
    e['notes'] = (notes_of(e) + ' | ' + text).strip(' |')


# ---------- 1) 感恩节顺延日期复修（run_daily 回滚复发） ----------
e = by['US_DURABLE_GOODS_20261126']
e['release_date'] = '2026-11-25'
append_notes(e, MARK + '日期复修】run_daily合并再次回滚11-24顺延修正（复发第2次），重新落地11-25 21:30 BJS发布；共识fc环比+0.5%/核心+0.7%不变')
log.append('RE-FIX US_DURABLE_GOODS_20261126 -> 2026-11-25')

e = by['US_JOBLESS_CLAIMS_20261126']
e['release_date'] = '2026-11-25'
append_notes(e, MARK + '日期复修】run_daily合并再次回滚11-24顺延修正（复发第2次），重新落地11-25 21:30 BJS发布；fc 20.1万/prev 20.3万不变')
log.append('RE-FIX US_JOBLESS_CLAIMS_20261126 -> 2026-11-25')

# ---------- 2) 谘商会消费者信心 11 月回填 ----------
e = by['US_CONSUMER_CONF_20261124']
e['actual'] = '103.3'
e['forecast'] = '92.2'
e['previous'] = '91.9'
e['status'] = 'released'
append_notes(e, MARK + '回填】11月谘商会消费者信心103.3，大超共识92.2达11.1点，2025-01以来最高；前值按官方修正口径91.9（原91.7为修正前）；现状132.8(+13.7)/预期83.6(+9.9，重回衰退信号80上方)；驱动=中期选举不确定性消除+汽油价格回落+就业认知改善；The Conference Board官网+AP+韩联社中文+优分析+首尔经济 5源✅；westock CLI feed缺该值（最新至11-20密歇根终值51.5）')
log.append('BACKFILL US_CONSUMER_CONF_20261124 -> 103.3 (fc 92.2 / prev 91.9)')

# ---------- 校验 PCE 组合事件完好 ----------
for eid in ('US_PCE_20261125', 'US_PCE_CORE_20261125', 'US_GDP_2ND_20261125'):
    ev = by[eid]
    assert ev['release_date'] == '2026-11-25', f'{eid} date broken: {ev["release_date"]}'
    assert ev['status'] == 'upcoming', f'{eid} status broken: {ev["status"]}'
log.append('ASSERT PCE/核心PCE/GDP二估 11-25 21:30 upcoming 完好 ✅')

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------- 重新生成 JS ----------
data = json.load(open(CAL, encoding='utf-8'))
generate_js(data)

for line in log:
    print(line)
print('calendar.json + calendar_data.js regenerated.')
