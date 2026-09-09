# -*- coding: utf-8 -*-
"""2026-09-09 回填脚本
1. 9/8 贸易三事件 actual 回填（海关总署官方，财联社+中国经济网多源）
2. 9/9 CPI/PPI actual 回填（统计局官网+新华财经+FXStreet 多源）
3. 7月 CPI/PPI 补回填（westock CLI + FXStreet 双源）
4. CN_TRADE_20260910 重复事件标注（8月贸易实际 9/8 已发布）
"""
import json

PATH = 'data/calendar.json'
cal = json.load(open(PATH, encoding='utf-8'))
evs = cal['events']

UPD = {
    # --- 9/8 贸易（美元计价，海关总署 9/8 11:00 发布，财联社+中经网多源✅）---
    'CN_EXPORTS_20260908': dict(actual=25.0, status='released',
        notes='8月出口同比+25.0%美元计价,符合预期(fc 25); 人民币计价+18.6%; AI算力产品(服务器/光模块/电子元器件)出口两位数增长; 前8月出口20.17万亿+14.6%; 来源: 海关总署(财联社/中国经济网/经济日报多源✅)'),
    'CN_IMPORTS_20260908': dict(actual=28.2, status='released',
        notes='8月进口同比+28.2%美元计价,低于预期(fc 30); 人民币计价+21.7%,进口增速连续6个月超出口; 前8月进口14.61万亿+22%; 来源: 海关总署(财联社/中国经济网多源✅)'),
    'CN_TRADE_BALANCE_20260908': dict(actual=1190.9, status='released',
        notes='8月贸易顺差1190.9亿美元,接近预期(fc 1190/Econoday共识1233); 来源: 海关总署(财联社+中国经济网多源✅); 前8月进出口34.78万亿元+17.6%'),
    # --- 7月 CPI/PPI 补回填（westock CLI + FXStreet 双源✅）---
    'CN_CPI_20260810': dict(actual=0.5, status='released',
        notes='7月CPI同比+0.5%; 来源: westock CLI(CPI_END_DATE 20260731) + FXStreet(0.5% in July) 双源✅; 与8月官方解读"比上月扩大0.3个百分点"自洽'),
    'CN_PPI_20260810': dict(actual=3.5, status='released',
        notes='7月PPI同比+3.5%(购进+5.5%); 来源: westock CLI + FXStreet(following a 3.5% increase in July) 双源✅'),
    # --- 9/9 CPI/PPI（统计局官网 09:30 发布，官网+新华财经+FXStreet 多源✅）---
    'CN_CPI_20260909': dict(actual=0.8, forecast=0.8, previous=0.5, status='released',
        notes='8月CPI同比+0.8%(符合路透40家中值0.8/FXStreet consensus 0.8); 环比+0.4%(由降转涨,高于预期0.3); 核心CPI同比+1.0%回升; 能源价格同比4.1%为主要拉动(汽油+9.3%),食品环比+0.4%; 1-8月平均+0.9%; 来源: 统计局官网+新华财经+FXStreet 多源✅'),
    'CN_PPI_20260909': dict(actual=3.8, forecast=3.6, previous=3.5, status='released',
        notes='8月PPI同比+3.8%(高于路透中值3.6/FXStreet共识3.7),环比+0.4%(由降转涨); 购进价格同比+5.8%; 生产资料+5.0%(采掘+17.8%),生活资料-0.5%; 油价输入性+AI算力需求(存储/PCB)支撑; 1-8月平均+2.0%; 来源: 统计局官网+新华财经+FXStreet 多源✅'),
    # --- 重复事件标注 ---
    'CN_TRADE_20260910': dict(
        notes='⚠️ 重复事件(模式日期错位): 中国8月贸易数据已于2026-09-08 11:00 发布(见CN_EXPORTS/IMPORTS/TRADE_BALANCE_20260908),本事件禁止回填; 中国贸易数据实际规律为每月8日左右发布上月数据'),
}

n = 0
for e in evs:
    u = UPD.get(e.get('id'))
    if not u:
        continue
    for k, v in u.items():
        e[k] = v
    e.setdefault('source', e.get('source') or '国家统计局/海关总署')
    n += 1
    print(f"OK {e['id']}: actual={e.get('actual')} fc={e.get('forecast')} prev={e.get('previous')} status={e.get('status')}")

json.dump(cal, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'Updated {n}/{len(UPD)} events')
