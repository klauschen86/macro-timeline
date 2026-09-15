# -*- coding: utf-8 -*-
"""2026-09-15 晨间修复：
1) 回填 9/14 中国8月金融数据 actual（央行 9/14 发布，5源：央视网/澎湃/经济参考报/中新经纬/央广网）
   - M2 同比 +7.5%（前值7.7%；M1 4.1%）
   - 社融当月新增 1.66万亿（低于C50中值1.94万亿；余额同比7.2%，前7.4%）
   - 新增人民币贷款 600亿（低于C50中值1100亿；住户-2029亿/企业+2600亿含票据+1000亿）
2) 9/15 四个经济事件补 forecast/previous（三源：中金研报/一财首席调研/RTTNews-dpaAFX）
   - 7月前值：工业4.5 / 社零0.6 / 固投-6.7 / 失业率5.2
   - 8月预期：工业4.7 / 社零0.8 / 固投-7.0 / 失业率5.2
   注：东财财富号前瞻(5.2/3.0/3.5/5.0)与三源系统性矛盾，判定低质弃用
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'data/calendar.json'
cal = json.load(open(PATH, encoding='utf-8'))
events = cal['events'] if isinstance(cal, dict) else cal
by_id = {e['id']: e for e in events}

def patch(eid, **kw):
    e = by_id.get(eid)
    if not e:
        print(f'!! MISS {eid}'); return
    for k, v in kw.items():
        e[k] = v
    print(f'OK {eid}: ' + ', '.join(f'{k}={v}' for k, v in kw.items() if k != "notes"))

# ---- 1) 9/14 金融数据回填（央行官方，5源一致 ✅） ----
patch('CN_M2_20260914', actual=7.5, status='released',
      notes=by_id['CN_M2_20260914'].get('notes','') + ' | 2026-09-15回填✅: 央行9/14发布, M2同比+7.5%(余额356.81万亿,前值7.7%,落预期区间下沿), M1+4.1%/M0+11.2%; 5源(央视网/澎湃/经济参考报/中新经纬/央广网)一致; 高于名义GDP增速')

patch('CN_SOCIAL_FINANCING_20260914', actual=16600, status='released',
      notes=by_id['CN_SOCIAL_FINANCING_20260914'].get('notes','') + ' | 2026-09-15回填✅: 8月社融新增1.66万亿(低于C50中值1.94万亿及浙商2.13/国联2.36万亿), 余额同比7.2%(前7.4%); 前8月累计23.91万亿, 同比少2.64万亿; 结构: 债券+股票直接融资增量占比超50%首超贷款(温彬:直接融资12.03万亿占50.31%), 政府债券前8月净融资8.77万亿同比少1.5万亿为企业债(2.79万亿多1.23万亿)让位; 5源一致')

patch('CN_NEW_LOANS_20260914', actual=600, status='released',
      notes=by_id['CN_NEW_LOANS_20260914'].get('notes','') + ' | 2026-09-15回填✅: 8月新增人民币贷款600亿(低于C50中值1100亿及浙商1000亿), 贷款余额282.35万亿同比+4.9%; 结构: 住户-2029亿(连续2月负,短贷-1219/中长贷-822), 企业+2600亿(短贷-1600/中长贷+3200/票据+1000), 非银-436亿; 新发放企业贷款利率<3%/房贷约3.1%均历史低位; 5源一致')

# ---- 2) 9/15 经济数据 forecast/previous（中金研报+一财调研+RTTNews 三源 ✅） ----
SRC = '2026-09-15补预期✅(三源:中金研报/一财首席调研/RTTNews-dpaAFX): '
patch('CN_INDUSTRIAL_20260915', forecast=4.7, previous=4.5,
      notes=SRC + '8月工业增加值预期4.7%(一财均值,区间4.4-5.4;中金4.6/RTT 4.8), 7月前值4.5%; 8月制造业PMI 49.8低位修复(7月49.2), 新订单50.6>生产50.4需求自3月后再度超生产; 注: 东财财富号前瞻5.2%与三源矛盾弃用')
patch('CN_RETAIL_20260915', forecast=0.8, previous=0.6,
      notes=SRC + '8月社零预期0.8%(中金/RTT一致), 7月前值0.6%; 暑期出行回暖(地铁/航班降幅收窄)但乘用车零售同比-22%拖累走阔; 东财财富号3.0%弃用')
patch('CN_FAI_20260915', forecast=-7.0, previous=-6.7,
      notes=SRC + '8月固投累计同比预期-7.0%(一财均值/RTT一致), 7月前值-6.7%; 单月降幅或由-12.8%收窄至-12.5%, 制造业-4.0%/地产-26.0%/基建-10.0%均略收窄(中金); 东财财富号+3.5%与三源系统性矛盾弃用')
patch('CN_UNEMPLOYMENT_20260915', forecast=5.2, previous=5.2,
      notes=SRC + '8月城镇调查失业率预期5.2%持平(RTT), 7月前值5.2%; 高校毕业生就业压力渐缓')

json.dump(cal, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('saved', PATH, '| total events:', len(events))
