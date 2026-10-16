# -*- coding: utf-8 -*-
"""2026-10-16 回填 10/14-10/15 发布数据 + 日期根治（多源官方核实）

日期根治（generate_calendar.py DATE_OVERRIDES 已同步加 4 条防回滚）：
  - CN_M2/CN_SOCIAL_FINANCING/CN_NEW_LOANS 2026-10 → 2026-10-14
    （央行 10/14 官网披露前三季度金融统计数据报告，新华财经/央广网/中新网 3 源一致，
     早于 10/12 批次暂按的 10/15）
  - US_RETAIL 2026-10 → 2026-10-15（Census 10/15 20:30 BJS 与 PPI 同日发布，21财经/财闻；
     原模式日期 10/16 错位）

回填值与来源：
  1) 中国 9 月金融数据（央行官方报告，新华财经/央广网/中新网多源一致 ✅）：
     - M2 同比 7.2%（fc 7.5 未达/prev 7.5；余额 359.63 万亿；M1 +3.2%、M0 +10.6%）
     - 新增社融 35500 亿（fc 36000 接近/prev 16600，环比 +1.89 万亿咬合 ✅；
       存量 468.17 万亿 +7.1%，增速环比 -0.1pct；前三季度增量 27.46 万亿同比少 2.63 万亿）
     - 新增人民币贷款 10800 亿（fc 12000 未达/prev 600，环比 +1.02 万亿咬合 ✅；同比少增 2100 亿）
  2) 美国 9 月 PPI 同比 6.3%（BLS，新华社/央视/人民网多源 ✅；预期 5.3 大超 ⚠️；
     环比 +1.3% 为 2022 年 3 月来最大；核心同比 5.0%/环比 0.7%；能源贡献商品涨幅 80%+）
  3) 美国初请 19.9 万（至 10/11 当周，21财经/财闻；预期 20.0；前值 19.7 修正为 19.8）
  4) 英国 8 月 GDP 环比 +0.1%（ONS 官网 + 新华网 ✅；fc -0.1 大超 ✅；7 月 0.4% 未修正；
     3 个月 +0.7%；分项生产 +0.8%/服务业 0.0%/建筑 -0.2%）
  5) 美国 9 月零售环比 +0.8%（预期 0.3 大超 ✅；21财经/财闻；8 月 1.2% 经 Census 官网核实保留）
"""
import json

CAL = 'data/calendar.json'
cal = json.load(open(CAL, encoding='utf-8'))
events = cal['events']

# ── 1. 日期根治 + id 改名（rsplit 铁律：id 含多个下划线）──────────────────
renames = {
    'CN_M2_20261015': ('2026-10-14', 'CN_M2_20261014'),
    'CN_SOCIAL_FINANCING_20261015': ('2026-10-14', 'CN_SOCIAL_FINANCING_20261014'),
    'CN_NEW_LOANS_20261015': ('2026-10-14', 'CN_NEW_LOANS_20261014'),
    'US_RETAIL_20261016': ('2026-10-15', 'US_RETAIL_20261015'),
}
by_id = {e['id']: e for e in events}
for old_id, (new_date, new_id) in renames.items():
    e = by_id.get(old_id)
    if e is None:
        print(f'!! rename target missing: {old_id}')
        continue
    assert new_id not in by_id, f'duplicate target id exists: {new_id}'
    e['release_date'] = new_date
    e['id'] = new_id
    e['status'] = 'pending' if e.get('actual') is None else e['status']
    print(f'renamed {old_id} -> {new_id} @ {new_date}')
    by_id[new_id] = e
    del by_id[old_id]

# ── 2. 回填 ──────────────────────────────────────────────────────────────
fixes = {
    'CN_M2_20261014': {
        'actual': 7.2, 'status': 'released',
        'note': '2026-10-16回填: 9月末M2同比7.2%(预期7.5未达⚠️/前值7.5持平持平预期落空),余额359.63万亿元; M1同比3.2%、M0同比10.6%; 央行10/14官网发布前三季度金融统计报告(早于日历10/15,已日期根治),新华财经/央广网/中新网多源一致✅'
    },
    'CN_SOCIAL_FINANCING_20261014': {
        'actual': 35500, 'status': 'released',
        'note': '2026-10-16回填: 9月新增社融3.55万亿(预期3.6万亿基本达标/前值1.66万亿,环比+1.89万亿咬合✅),同比+192亿; 存量468.17万亿+7.1%(增速环比-0.1pct); 前三季度增量27.46万亿同比少2.63万亿; 9月政府债融资1.53万亿占当月43%(温彬:发行提速+政策性金融工具); 债券股票等直接融资占比49.48%连续超贷款,融资结构"降速提质"; 央行官方,新华财经/央广网/中新网多源✅'
    },
    'CN_NEW_LOANS_20261014': {
        'actual': 10800, 'status': 'released',
        'note': '2026-10-16回填: 9月新增人民币贷款1.08万亿(预期1.2万亿未达⚠️/前值600亿,环比+1.02万亿咬合✅),同比少增2100亿; 结构:企(事)业单位+1.29万亿同比多增700亿、住户贷款0(短贷-900亿/中长贷+874亿环比+1696亿,楼市政策组合拳带动按揭边际回升-温彬); 9月末贷款余额283.44万亿+4.8%; 央行官方,新华财经/央广网/中新网多源✅'
    },
    'US_PPI_20261015': {
        'actual': 6.3, 'status': 'released',
        'note': '2026-10-16回填: 9月PPI同比6.3%(预期5.3,大超⚠️创2022年12月来最大;21财经称2026年5月来新高),环比+1.3%(8月0.5%,2022年3月来最大); 核心PPI同比5.0%/环比0.7%(8月4.6%/0.2%); 商品环比+2.6%能源贡献超80%、服务环比+0.8%; ⚠️前值口径分歧:新华社引BLS"8月同比5.6%"vs财闻"前值5.4"(疑初值5.4后上修),previous字段保留原预填5.4待核; 劳工部15日发布,新华社/央视/人民网多源一致✅'
    },
    'US_JOBLESS_CLAIMS_20261015': {
        'actual': 19.9, 'status': 'released',
        'note': '2026-10-16回填: 至10/11当周初请19.9万(预期20.0,略低✅); 前值19.7万修正为19.8万(previous字段保留原报19.7,DOL修正口径环比+1000); "低招聘低裁员"格局延续; 21财经/财闻2源,与PPI/零售同晚发布✅'
    },
    'UK_GDP_20261015': {
        'actual': 0.1, 'status': 'released',
        'note': '2026-10-16回填: 8月GDP环比+0.1%(预期-0.1,大超✅/7月0.4%未修正); 3个月(6-8月)+0.7%(5-7月/4-6月均上修至0.5%); 分项:生产+0.8%、服务业0.0%、建筑-0.2%; ONS统计总监McKeown:服务业6-7月强劲带动3个月增长; BCC:中东冲突推高能源价格挤压企业; ONS官网+新华网2源✅'
    },
    'US_RETAIL_20261015': {
        'actual': 0.8, 'status': 'released',
        'note': '2026-10-16回填: 9月零售环比+0.8%(预期0.3,大超✅/8月1.2%Census官方核实保留); 与PPI同晚发布(原模式日期10/16错位,已日期根治至10/15); 市场:美债收益率集体下挫超13bp(数据强但PPI通胀更吓人?),CME 12月累计加息25bp概率62.2%+50bp概率28.7%,瑞银将第三次加息预测延后至2027年3月; 21财经/财闻多源✅'
    },
}
n = 0
for e in events:
    if e['id'] in fixes:
        f = fixes[e['id']]
        e['actual'] = f['actual']
        e['status'] = f['status']
        e['notes'] = e.get('notes', '') + ' | ' + f['note']
        n += 1
        print(f"backfilled {e['id']} = {f['actual']}")
assert n == len(fixes), f'backfill mismatch: {n}/{len(fixes)}'

# ── 3. prev 链预填 ────────────────────────────────────────────────────────
prefills = {
    'US_JOBLESS_CLAIMS_20261022': 19.9,
    'UK_GDP_20261112': 0.1,
    'CN_M2_20261112': 7.2,
    'CN_SOCIAL_FINANCING_20261112': 35500,
    'CN_NEW_LOANS_20261112': 10800,
    'US_RETAIL_20261116': 0.8,
}
m = 0
for e in events:
    if e['id'] in prefills and e.get('previous') is None:
        e['previous'] = prefills[e['id']]
        m += 1
        print(f"prev-filled {e['id']} prev={prefills[e['id']]}")
assert m == len(prefills), f'prefill mismatch: {m}/{len(prefills)}'

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ── 4. 回读验证 ──────────────────────────────────────────────────────────
cal2 = json.load(open(CAL, encoding='utf-8'))
ev2 = {e['id']: e for e in cal2['events']}
for eid, f in fixes.items():
    e = ev2[eid]
    assert e['actual'] == f['actual'] and e['status'] == 'released', eid
for eid, v in prefills.items():
    assert ev2[eid]['previous'] == v, eid
for old_id, (nd, nid) in renames.items():
    assert old_id not in ev2, f'old id still exists: {old_id}'
    assert ev2[nid]['release_date'] == nd, nid
released = sum(1 for e in cal2['events'] if e.get('status') == 'released')
print(f'READBACK OK: {len(cal2["events"])} events, Released {released}')
