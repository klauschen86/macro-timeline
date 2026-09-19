# -*- coding: utf-8 -*-
"""_fix_20260919.py — 回填 2026-09-18 两项 pending（周六晨执行）
1) JP_BOJ_20260918 日央行决议：加息25bp 1.00%→1.25%（上海证券报 9/19 + 财联社 9/18 + 光大证券研报 + FX168 4源✅）
   - 7-2 投票（浅田统一郎/佐藤绫野反对）；1995年来最高利率、1990年来最快紧缩节奏（3个月内第二次）
   - 声明前瞻指引与7月变化有限、未更鹰派 → 日元反贬，美元/日元一度破158；
     日央行深夜"汇率询价"(rate check)后日元反弹至156后半区间（日经/FX168）
   - 植田：不排除任何政策选项；市场预计2027年3月底1.5%、2027Q2 1.75%
2) US_INDUSTRIAL_PRODUCTION_20260918 美8月工业产出：环比 0.0% 持平（fc 0.3 不及预期）
   - 制造业产出 -0.3%（结束连续7个月增长，fc +0.2）；公用事业+1.8%、矿业小升
   - 产能利用率 76.3% 持平（工厂利用率75.7%五个月低点）
   - 来源：新华财经纽约电 + 新浪财经 + FRED G.17 + The Edge(彭博) 4源✅
"""
import json

CAL = 'data/calendar.json'
cal = json.load(open(CAL, encoding='utf-8'))

UPDATES = {
    'JP_BOJ_20260918': {
        'actual': 1.25,
        'notes': '9/18午间决议：加息25bp 1.00%→1.25%（符合预期，1995年来最高；1990年来最快紧缩节奏，距上次仅3个月）。7-2投票（浅田统一郎/佐藤绫野反对，市场解读为后续加息阻力信号）。声明前瞻指引与7月变化有限、未释放更鹰派信号→"买预期卖事实"，美元/日元一度破158；日央行深夜"汇率询价"(rate check)后日元反弹至156后半区间。植田：不排除任何政策选项；调查预计2027年3月底1.5%、2027Q2 1.75%。日央行/美联储/欧央行首次同月加息。来源：上海证券报9/19+财联社9/18+光大证券研报+FX168 4源✅',
    },
    'US_INDUSTRIAL_PRODUCTION_20260918': {
        'actual': 0.0,
        'notes': '8月工业产出环比0.0%持平（低于fc 0.3，预测区间持平~+0.8%；7月+0.2%未修正）。制造业产出-0.3%结束连续7个月增长（fc +0.2），商业设备-0.5%、汽车-1.2%；公用事业+1.8%（电力需求回升）、矿业小升。产能利用率76.3%与7月持平（工厂利用率75.7%五个月低点）。制造业降温与美联储周内加息形成反差，10月再加息概率约55%。来源：新华财经纽约电+新浪财经+FRED G.17+The Edge(彭博) 4源✅',
    },
}

n = 0
for e in cal['events']:
    u = UPDATES.get(e.get('id'))
    if u:
        if e.get('actual') is None:
            e['actual'] = u['actual']
        e['status'] = 'released'
        old_notes = e.get('notes', '')
        e['notes'] = (old_notes + ' | ' + u['notes']) if old_notes else u['notes']
        n += 1

json.dump(cal, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'updated {n} events')
rel = sum(1 for e in cal['events'] if e.get('status') == 'released')
pend = sum(1 for e in cal['events'] if e.get('status') == 'pending')
print(f'Released: {rel}, Pending: {pend}, total {len(cal["events"])}')
