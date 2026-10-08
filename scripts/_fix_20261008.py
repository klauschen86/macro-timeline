#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-08 修复脚本（automation-1781242407195）
1. 回填 10/7 中国 9 月末外储 34002.51 亿美元 + 黄金储备 7747 万盎司（官方多源）
2. FOMC 9/15-16 会议纪要要点回填 notes（10/8 02:00 BJS 发布，无数值 actual）
3. CN_CPI/CN_PPI 10 月迭代改名 10/9→10/14（澎湃引统计局：国庆月推迟）+ 共识预填
幂等：marker 或文本前 15 字符双条件；改名前查目标 id 是否已存在。
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CAL = 'data/calendar.json'
data = json.load(open(CAL, encoding='utf-8'))
events = data['events'] if isinstance(data, dict) else data
by_id = {e['id']: e for e in events}
changes = []

# ---------- 1. 回填 9 月末外储 ----------
e = by_id.get('CN_FX_RESERVES_20261007')
assert e, 'CN_FX_RESERVES_20261007 不存在'
if not e.get('actual'):
    e['actual'] = 34002.51
    e['status'] = 'released'
    note = ("9月末外储34002.51亿美元, 较8月末-380.74亿/-1.11% (10/7发布; SAFE官方/中新经纬+证券时报+央行数据 多源✅); "
            "美元指数上涨+全球主要金融资产价格总体下跌, 汇率折算与资产价格变化负向; 8月末34383 咬合✅(34002.51+380.74); "
            "官方强调规模基本稳定; ⚠️ Tradays显示3.441万亿与官方矛盾已弃用")
    marker = '【fix20261008】'
    if marker not in (e.get('notes') or '') and note[:15] not in (e.get('notes') or ''):
        e['notes'] = (e.get('notes') or '') + note
        changes.append('CN_FX_RESERVES_20261007 回填')
else:
    changes.append('CN_FX_RESERVES_20261007 已回填, 跳过')

# ---------- 2. 回填 9 月末黄金储备 ----------
e = by_id.get('CN_GOLD_RESERVES_20261007')
assert e, 'CN_GOLD_RESERVES_20261007 不存在'
if not e.get('actual'):
    e['actual'] = 7747
    e['status'] = 'released'
    note = ("9月末黄金储备7747万盎司, 环比+74万盎司创本轮周期单月新高(超8月+65), 连续第23个月增持 "
            "(10/7发布; 中新社/证券时报/央广网/南方+/中新经纬 5源✅); 8月末7673 咬合✅(7673+74); "
            "10/7 现货黄金一度失守4150美元/盎司")
    marker = '【fix20261008】'
    if marker not in (e.get('notes') or '') and note[:15] not in (e.get('notes') or ''):
        e['notes'] = (e.get('notes') or '') + note
        changes.append('CN_GOLD_RESERVES_20261007 回填')
else:
    changes.append('CN_GOLD_RESERVES_20261007 已回填, 跳过')

# ---------- 3. FOMC 纪要要点（无数值, 仅 notes） ----------
e = by_id.get('US_FOMC_MINUTES_20261008')
assert e, 'US_FOMC_MINUTES_20261008 不存在'
note = ("9/15-16会议纪要(10/8 02:00 BJS发布): 19名官员一致支持9月加息25bp至3.75%-4.00%(2023年7月来首次); "
        "多数与会者认为年底前再加息一次可能合适但未指明具体会议; 部分官员认为加息防能源等价格冲击, 更鹰派主张防需求驱动型通胀; "
        "几名官员称经济内在动能增强; 市场反应: 美元指数+0.42%报102.25, CME 10月加息概率19.4%(一周前约38%)/12月83%; "
        "沃什发布会鹰派 vs 杰斐逊/威廉姆斯偏耐心; 美债收益率处2002年来高位 (财联社+智通财经+新浪外盘头条 多源✅)")
marker = '【fix20261008】'
if marker not in (e.get('notes') or '') and note[:15] not in (e.get('notes') or ''):
    e['notes'] = (e.get('notes') or '') + note
    changes.append('US_FOMC_MINUTES_20261008 notes')
else:
    changes.append('US_FOMC_MINUTES_20261008 已有 notes, 跳过')

# ---------- 4. CPI/PPI 改名 10/9→10/14 + 共识预填 ----------
def rename_and_fill(old_id, new_id, fc, note):
    e_old = by_id.get(old_id)
    e_new = by_id.get(new_id)
    assert e_old or e_new, f'{old_id} 与 {new_id} 均不存在'
    if e_new:
        # 已改名/重生成版本存在: 确保 fc/notes 落地
        if not e_new.get('forecast') and fc is not None:
            e_new['forecast'] = fc
        marker = '【fix20261008】'
        if marker not in (e_new.get('notes') or '') and note[:15] not in (e_new.get('notes') or ''):
            e_new['notes'] = (e_new.get('notes') or '') + note
        changes.append(f'{old_id}→{new_id} 目标已存在, 补字段')
        return
    e_old['id'] = new_id
    _d = new_id.rsplit('_', 1)[1]  # ⚠️ 必须 rsplit：CN_CPI_20261014 含两个下划线，split('_',1) 会取到 'CPI_20261014'
    e_old['release_date'] = _d[:4] + '-' + _d[4:6] + '-' + _d[6:8]
    if fc is not None and not e_old.get('forecast'):
        e_old['forecast'] = fc
    marker = '【fix20261008】'
    if marker not in (e_old.get('notes') or '') and note[:15] not in (e_old.get('notes') or ''):
        e_old['notes'] = (e_old.get('notes') or '') + note
    by_id.pop(old_id, None)
    by_id[new_id] = e_old
    changes.append(f'{old_id} 改名→{new_id}')

rename_and_fill('CN_CPI_20261009', 'CN_CPI_20261014', 1.0,
    ("【fix20261008】发布日修正: 统计局10/14 9:30发布9月物价数据(澎湃新闻10/7, 国庆月惯例推迟; 原10/9系模式日期偏差, 已加 DATE_OVERRIDES 根治); "
     "机构预测CPI同比1.0%左右: 中金/浙商/东方金诚1.0, 西部/北大1.1; 食品季节性上涨+猪肉低基数降幅收窄(20.9%→16.9%), 仍处偏低水平"))
rename_and_fill('CN_PPI_20261009', 'CN_PPI_20261014', 4.5,
    ("【fix20261008】发布日修正: 统计局10/14 9:30发布(澎湃新闻10/7); 机构预测PPI同比4.5%左右: 中金/浙商/西部4.5, 北大4.3, 东方金诚4.1, 或再迎高点; "
     "9月布伦特均价回升至100美元/桶附近+煤炭走强, PMI购进价格60.8/出厂价格54.0 隐含环比~0.7%"))

# ---------- 写回 ----------
if isinstance(data, dict):
    data['events'] = events
else:
    data = events
json.dump(data, open(CAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('变更项:')
for c in changes:
    print(' -', c)

# ---------- 回读 assert ----------
d2 = json.load(open(CAL, encoding='utf-8'))
ev2 = {e['id']: e for e in (d2['events'] if isinstance(d2, dict) else d2)}
fx = ev2['CN_FX_RESERVES_20261007']
gold = ev2['CN_GOLD_RESERVES_20261007']
assert abs(fx['actual'] - 34002.51) < 0.01, '外储 actual 回读失败'
assert fx['previous'] == 34383, '外储 prev 咬合失败'
assert gold['actual'] == 7747 and gold['previous'] == 7673, '黄金回读/咬合失败'
assert '34002.51' in (fx['notes'] or ''), '外储 notes 回读失败'
assert '7747' in (gold['notes'] or ''), '黄金 notes 回读失败'
assert '19.4%' in (ev2['US_FOMC_MINUTES_20261008']['notes'] or ''), 'FOMC notes 回读失败'
cpi = ev2.get('CN_CPI_20261014')
ppi = ev2.get('CN_PPI_20261014')
assert cpi and cpi['release_date'] == '2026-10-14' and cpi.get('forecast') == 1.0, 'CPI 改名/预填失败'
assert ppi and ppi['release_date'] == '2026-10-14' and ppi.get('forecast') == 4.5, 'PPI 改名/预填失败'
assert 'CN_CPI_20261009' not in ev2 and 'CN_PPI_20261009' not in ev2, '旧 id 残留'
assert cpi['previous'] == 0.8 and ppi['previous'] == 3.8, 'CPI/PPI prev 丢失'
print('回读 assert ALL OK')
