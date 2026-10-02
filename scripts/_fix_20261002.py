# -*- coding: utf-8 -*-
"""2026-10-02 修复脚本：回填 10/1 晚美国 2 项 + 今晚 3 项预填 + FOMC 日期修复 + 10/29 BEA 双事件新建"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
data = json.load(open(PATH, encoding='utf-8'))
evs = data['events'] if isinstance(data, dict) else data

def notes_append(e, txt):
    old = e.get('notes') or ''
    marker = txt.split('；')[0]
    base = old.lstrip('；')
    if marker in base:
        return
    e['notes'] = (base + ('；' if base and not base.endswith('；') else '') + txt)

changes = []

def patch(eid, **kw):
    for e in evs:
        if e.get('id') == eid:
            for k, v in kw.items():
                if k == 'notes_append':
                    notes_append(e, v)
                else:
                    e[k] = v
            changes.append(eid)
            return True
    print(f'!! NOT FOUND: {eid}')
    return False

def delete(eid):
    global evs
    n = len(evs)
    evs = [e for e in evs if e.get('id') != eid]
    if len(evs) < n:
        changes.append(f'-{eid}')
        return True
    print(f'!! DELETE NOT FOUND: {eid}')
    return False

def add(ev):
    if any(e.get('id') == ev['id'] for e in evs):
        print(f'!! ADD SKIP (exists): {ev["id"]}')
        return False
    evs.append(ev)
    changes.append(f'+{ev["id"]}')
    return True

# ============ ① 回填：9月ISM制造业PMI 54.5（预期55/前值54.6）——华尔街见闻+金十+新浪7x24+智通财经 4源✅ ============
patch('US_ISM_MFG_20261001', actual=54.5, status='released',
      notes_append='2026-10-02 回填 actual=54.5（华尔街见闻+金十+新浪7x24+智通财经 4源✅）：低于预期55，连续第2个月下滑但仍连续第9个月扩张（2022年来最长连续扩张纪录）；分项：物价支付77.9（预期72.3/前值71.1，5月来最高=4个月最高）、就业52.7（前值51.2，连续第3个月增长）、新订单55.3（前值53.7）、未完成订单2月来最高；12个行业报告增长（电气设备/初级金属/机械领领涨），印刷/纺织收缩；中东冲突能源价格+航运干扰推升成本；市场反应：标普高开转跌、30Y美债跌幅居前；同日标普全球美国9月制造业PMI终值55.9（8月终值57.0，金十）')

# ============ ② 回填：初请（至9/26当周）19.7万（预期20.0/前值19.7上修19.8）——DOL官网一手+金十+第一财经+腾讯 4源✅ ============
patch('US_JOBLESS_CLAIMS_20261001', actual=19.7, forecast=20.0, previous=19.8, status='released',
      notes_append='2026-10-02 回填 actual=19.7万（DOL官网原文+金十+第一财经+腾讯 4源✅）：预期20.0万（Econoday/金十），减少1000人至57年低位附近；⚠️前值19.7万上修至19.8万（previous已同步）；四周均值20.0万（-2500，7周低点）；续请170.1万（-1.1万，2023年3月来最低）；⚠️识别弃用：Investing.com解析199K与DOL官网197K矛盾，以DOL一手为准；Challenger 9月计划裁员43281（环比-18%/同比-20%），招聘计划90787（同比-23%，2011年来9月最低）；初请不在9月非农统计窗口内；背景：9/16 FOMC加息25bp至3.75-4.00%、伊朗战事推高能源价格')
# 初请前值链同步：9/24发布（至9/19当周）的previous按DOL口径上修（9/12周196→198）
patch('US_JOBLESS_CLAIMS_20260924', previous=19.8,
      notes_append='⚠️前值(9/12周)按DOL 9/24报告上修196→198（previous已同步）')

# ============ ③ 今晚预填：非农+失业率（10/2 20:30 BJS）+ 欧元区CPI初值（17:00 BJS） ============
patch('US_NFP_20261002', forecast=9.0, previous=16.2,
      notes_append='今晚20:30 BJS发布（8:30 AM ET，9月报告）；共识9.0万（东财援引经济学家调查+金十预期9万；⚠️10/1早间共识曾为8.4万，走弱）；前值16.2万（8月）；失业率预期4.1%连续第3个月（风险偏上行）；背景：9月ADP+9.0万大超、初请19.7万近57年低位但Challenger招聘计划同比-23%（不裁也不招）；初请不在统计窗口内')
patch('US_UNEMPLOYMENT_20261002', forecast=4.1, previous=4.1,
      notes_append='今晚20:30 BJS发布；预期4.1%连续第3个月持平（风险偏上行，东财调查+金十）；前值4.1%')
patch('EU_CPI_FLASH_20261002', forecast=3.7, previous=3.2,
      notes_append='今晚17:00 BJS发布（11:00 CET）；共识3.6~3.7（investing/SG 3.7、BigGo 3.6，部分预期3.7创三年新高）；前值8月终值3.2%（⚠️flash 3.3下修0.1，previous已按终值口径）；核心预期2.5~2.6（8月2.4）；能源主推——四大国9月HICP初值全超预期：德3.3（前2.9）/法3.4（前2.6）/意4.1（前3.2）/西5.0（前4.6），法国服务+食品同升、德国核心持平2.4%（二轮效应未现）；ECB 9/10已加息25bp至存款利率2.50%，10/29会议加息概率约1/3（市场降温中）；8月分项：能源14.3%/服务3.0%/核心2.4%')

# ============ ④ 10月中旬CPI前值预填 ============
patch('US_CPI_20261014', previous=3.4,
      notes_append='prev=8月CPI同比3.4%（9/11发布，引自本日历9/30 PCE事件记录）')

# ============ ⑤ FOMC 日期错误修复：删除 11/5 与 5/7 幻影事件（generate_calendar.py FOMC_2026 列表已同步修正） ============
delete('US_FOMC_2026-11-05')
delete('US_FOMC_2026-05-07')
# 官方2026日程（美联储官网）：10月27-28会议 → 决议10/28 14:00 ET = 10/29 02:00 BJS
add({
    "id": "US_FOMC_2026-10-29",
    "country": "US", "country_name": "美国",
    "indicator": "美联储利率决议（FOMC）", "indicator_en": "FOMC Rate Decision",
    "frequency": "每年8次", "importance": 3,
    "release_date": "2026-10-29", "release_time": "02:00", "timezone": "BJS",
    "period": "2026-10", "source": "Federal Reserve",
    "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "unit": "%", "actual": None, "forecast": None, "previous": 4.0,
    "status": "upcoming",
    "notes": "FOMC会议10/27-28（美联储官网2026日程+官网10月日历双重确认），决议10/28 14:00 ET=10/29 02:00 BJS，记者会10/28 14:30 ET；现行利率3.75-4.00%（9/16加息25bp，3年来首次）；9/30 PCE同比3.4%/核心3.0%均低于预期后，CME 10月按兵不动概率52.9%、加息押注降至约9bp；但9月ISM物价支付77.9（4个月最高）+10Y美债5.34%（2002来新高）显示通胀压力仍在；会议纪要10/7 14:00 ET（10/8 02:00 BJS）；⚠️原日历误排2026-11-05（模式生成错误），2026-10-02经美联储官网核实修正"
})
# 官方2026日程：4月28-29会议 → 决议4/29 14:00 ET = 4/30 02:00 BJS（原误排5/7已删除）
add({
    "id": "US_FOMC_2026-04-30",
    "country": "US", "country_name": "美国",
    "indicator": "美联储利率决议（FOMC）", "indicator_en": "FOMC Rate Decision",
    "frequency": "每年8次", "importance": 3,
    "release_date": "2026-04-30", "release_time": "02:00", "timezone": "BJS",
    "period": "2026-04", "source": "Federal Reserve",
    "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "unit": "%", "actual": None, "forecast": None, "previous": None,
    "status": "pending",
    "notes": "官方2026日程：会议4/28-29，决议4/29 14:00 ET=4/30 02:00 BJS；决议内容待补（历史pending）；⚠️原日历误排2026-05-07（模式生成错误），2026-10-02修正"
})

# ============ ⑥ 新建 10/29 BEA 双事件（Q3 GDP初值 + 9月PCE，BEA惯例同刻发布） ============
add({
    "id": "US_GDP_ADV_20261029",
    "country": "US", "country_name": "美国",
    "indicator": "GDP初值（年化环比）", "indicator_en": "GDP Advance Estimate QoQ SAAR",
    "frequency": "季度", "importance": 3,
    "release_date": "2026-10-29", "release_time": "20:30", "timezone": "BJS",
    "period": "2026-Q3", "source": "BEA", "source_url": "https://www.bea.gov/",
    "unit": "%", "actual": None, "forecast": None, "previous": 2.2,
    "status": "upcoming",
    "notes": "Q3 GDP初值 10/29 20:30 BJS（8:30 AM ET，BEA官方日程/ fedratecalc核对版）；prev=Q2终值2.2%（9/30发布，二次估算1.5%大幅上修0.7pp；年度国民账户修订后Q1=2.5%）；与9月PCE同刻发布（BEA惯例，同9/30组合）"
})
add({
    "id": "US_PCE_20261029",
    "country": "US", "country_name": "美国",
    "indicator": "PCE物价指数（同比）", "indicator_en": "PCE Price Index YoY",
    "frequency": "月度", "importance": 3,
    "release_date": "2026-10-29", "release_time": "20:30", "timezone": "BJS",
    "period": "2026-09", "source": "BEA", "source_url": "https://www.bea.gov/",
    "unit": "%", "actual": None, "forecast": None, "previous": 3.4,
    "status": "upcoming",
    "notes": "9月PCE 10/29 20:30 BJS（8:30 AM ET）；prev=8月3.4%（年度方法论修订后口径，7月3.7→3.4下修；⚠️BEA年度修订历史链1-7月衔接待审计）；与Q3 GDP初值同刻发布（BEA惯例）；FOMC决议（10/29 02:00 BJS）后次日发布"
})
add({
    "id": "US_PCE_CORE_20261029",
    "country": "US", "country_name": "美国",
    "indicator": "核心PCE物价指数（同比）", "indicator_en": "Core PCE Price Index YoY",
    "frequency": "月度", "importance": 3,
    "release_date": "2026-10-29", "release_time": "20:30", "timezone": "BJS",
    "period": "2026-09", "source": "BEA", "source_url": "https://www.bea.gov/",
    "unit": "%", "actual": None, "forecast": None, "previous": 3.0,
    "status": "upcoming",
    "notes": "9月核心PCE 10/29 20:30 BJS；prev=8月3.0%（年度方法论修订后口径，创2月来新低；7月3.3→3.0下修；BEA修订投资组合管理/软件/法律服务三法回溯2021）；FOMC决议后次日发布——美联储最看重的通胀指标，9月ISM物价支付77.9走高背景下关注是否续降"
})

# 回读校验（关键：delete/add 重新绑定列表后必须写回 data['events']）
data['events'] = evs
json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
data2 = json.load(open(PATH, encoding='utf-8'))
evs2 = data2['events'] if isinstance(data2, dict) else data2
ok = True
expect = {
    'US_ISM_MFG_20261001': (54.5, 54.6, 'released'),
    'US_JOBLESS_CLAIMS_20261001': (19.7, 19.8, 'released'),
    'US_JOBLESS_CLAIMS_20260924': (None, 19.8, 'released'),
    'US_NFP_20261002': (None, 16.2, 'upcoming'),
    'US_UNEMPLOYMENT_20261002': (None, 4.1, 'upcoming'),
    'EU_CPI_FLASH_20261002': (None, 3.2, 'upcoming'),
    'US_CPI_20261014': (None, 3.4, 'upcoming'),
    'US_FOMC_2026-10-29': (None, 4.0, 'upcoming'),
    'US_FOMC_2026-04-30': (None, None, 'pending'),
    'US_GDP_ADV_20261029': (None, 2.2, 'upcoming'),
    'US_PCE_20261029': (None, 3.4, 'upcoming'),
    'US_PCE_CORE_20261029': (None, 3.0, 'upcoming'),
}
for e in evs2:
    eid = e.get('id')
    if eid in expect:
        a, p, s = expect[eid]
        if a is not None and e.get('actual') != a:
            print(f'MISMATCH {eid} actual={e.get("actual")} expect {a}'); ok = False
        if p is not None and e.get('previous') != p:
            print(f'MISMATCH {eid} previous={e.get("previous")} expect {p}'); ok = False
        if e.get('status') != s:
            print(f'MISMATCH {eid} status={e.get("status")} expect {s}'); ok = False
        if e.get('forecast') is None and eid in ('US_NFP_20261002','US_UNEMPLOYMENT_20261002','EU_CPI_FLASH_20261002'):
            print(f'MISMATCH {eid} forecast empty'); ok = False
    if eid in ('US_FOMC_2026-11-05', 'US_FOMC_2026-05-07'):
        print(f'MISMATCH {eid} still present!'); ok = False
print('PATCHED:', changes)
print('TOTAL EVENTS:', len(evs2))
print('ALL OK' if ok else 'FAIL')
