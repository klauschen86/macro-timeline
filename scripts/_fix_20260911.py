# -*- coding: utf-8 -*-
"""2026-09-11 回填与日期补丁
1. 回填 9/10 actual：美8月PPI 5.4 / 初请 20.6万 / 欧央行加息25bp(存款2.50%)
2. 回填 9/11 今早：英国7月GDP 环比0.0%（ONS 07:00发布）
3. 日期补丁（run_daily 后执行，防覆盖回滚）：
   - US_CPI/US_CORE_CPI 9/14→9/11（今晚20:30 BJS），回填共识 fc
   - UK_GDP 9/14→9/11, period 2026-08→2026-07
4. 历史缺口：US_PPI_20260814（7月PPI）actual=4.8（8月报告上修值）
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_daily

CAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'calendar.json')

with open(CAL, encoding='utf-8') as f:
    data = json.load(f)

by_id = {e['id']: e for e in data['events']}
PATCH = '| 2026-09-11补丁✅'


def patch(eid, **kw):
    e = by_id[eid]
    for k, v in kw.items():
        if k == 'notes_append':
            e['notes'] = (e.get('notes') or '') + v
        else:
            e[k] = v
    print(f"patched {eid}: " + ", ".join(f"{k}={str(v)[:40]}" for k, v in kw.items()))


# 1. 美8月PPI（实际9/10 20:30 BJS发布）
patch('US_PPI_20260914',
      release_date='2026-09-10', status='released',
      actual=5.4, forecast=5.3, previous=4.7,
      notes_append=PATCH + ': 美8月PPI同比+5.4%(预估5.3,前值4.7), 环比+0.4%符合预期; 核心PPI同比4.6%符合预期(7月上修4.3%); 财联社+StoneX+Fidelity三源✅; 7月前值上修至4.8%(StoneX口径); 拉动: 能源商品+1.1%(柴油+24.1%), 运输仓储服务+2.3%; 发布后Fed 9/15-16加息概率58%→64%, 交易员已充分消化10月加息')

# 2. 初请失业金（9/10 20:30 BJS）
patch('US_JOBLESS_CLAIMS_20260910',
      status='released', actual=20.6,
      notes_append=PATCH + ': 初请20.6万(预估20.5,略偏高), 财联社+StoneX双源✅; 上周上修20.7万; 四周均值20.6万回落; 续请177.4万; 劳动力市场韧性延续, 与强非农共振支撑Fed加息叙事')

# 3. 欧央行利率决议（9/10 20:15 BJS）
patch('EU_ECB_20260910',
      status='released', actual='2.50%',
      notes_append=PATCH + ': 加息25bp落地✅(财联社+东方财富21世纪+Lixtus Forex多源✅); 存款利率2.25%→2.50%/主要再融资2.40%→2.65%/边际借贷2.65%→2.90%; 同日发布最新经济预测, 通胀预测上调0.2-0.3pp; 关注12月是否再加息(市场分歧); 能源冲击(欧元区8月通胀3.3%)为加息主因')

# 4. 英国7月GDP（今早9/11 07:00 BJS发布）
patch('UK_GDP_20260914',
      release_date='2026-09-11', period='2026-07',
      status='released', actual=0.0, forecast=0.0, previous=0.4,
      notes_append=PATCH + ': 英国7月GDP环比0.0%(零增长,符合预期), 6月+0.4%; 3个月环比+0.2%(前值0.3%); 生产端-0.9%(制造业-1.3%)拖累, 服务业+0.1%/建筑业+0.2%; ONS 07:00发布✅; Financial Reporter+BritBrief+UK Business Reporter+Sharecast 4源✅; 预算不确定性与涨薪税负担抑制企业信心')

# 5. 美8月CPI（今晚9/11 20:30 BJS）日期修正+共识回填
patch('US_CPI_20260914',
      release_date='2026-09-11', forecast=3.4,
      notes_append=PATCH + ': 共识同比3.4%(与7月持平), 环比0.4%; 财联社周报+Juno+StoneX多源✅; 9/16 FOMC前最后一份通胀读数, PPI超预期(5.4%)后若CPI再超预期则9月加息几乎确定; 发布后明早回填actual')

patch('US_CORE_CPI_20260914',
      release_date='2026-09-11', forecast=2.5,
      notes_append=PATCH + ': 共识同比2.5%(财联社/Juno), StoneX偏2.4%, 区间2.4-2.5; 环比共识0.2%——沃勒阈值: 核心环比≤0.2%倾向按兵不动, ≥0.3%考虑加息, 为全周最关键观察值')

# 6. 历史缺口：7月PPI（8/14发布，此前pending）
patch('US_PPI_20260814',
      status='released', actual=4.8,
      notes_append=PATCH + ': 7月PPI同比初值4.7%, 在8月PPI报告中上修至4.8%(StoneX); 补回填历史缺口')

with open(CAL, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 重新加载并生成 JS（不跑 generate+merge，防止覆盖回滚）
output = run_daily.load_calendar()
run_daily.generate_js(output)

rel = sum(1 for e in output if e.get('status') == 'released')
print(f"\nDone. Total: {len(output)}, Released: {rel}")
