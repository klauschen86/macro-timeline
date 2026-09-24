# -*- coding: utf-8 -*-
"""2026-09-24 回填：
1) 9/23 EU PMI 初值三项（新华财经+格隆汇+IBKR/Reuters+Econoday 4源✅）
2) 9/23 美 S&P PMI 初值（S&P官方+TradingEconomics+TheStreet Pro+Econoday 4源✅）
3) 9/24 美 初请/新屋销售 fc+prev 预填（investing/helious/OneRoyal+Econoday/彭博多源）
"""
import json, io, sys

PATH = "data/calendar.json"
raw = open(PATH, encoding="utf-8").read()
data = json.loads(raw)
events = data["events"] if isinstance(data, dict) else data

UPDATES = {
    "EU_PMI_MFG_FLASH_20260923": {
        "actual": 52.7, "forecast": 52.7, "previous": 52.7, "status": "released",
        "notes": "9月欧元区制造业PMI初值 52.7（预期52.7/前值8月终值52.7，与8月持平）；制造业产出指数 53.3→53.4（55个月最高）。⚠️ 8月初值52.8、终值下修至52.7。新订单连续第3个月增长（出口拉动）；投入/产出价格涨幅4个月最快（中东能源冲击）。来源：新华财经布鲁塞尔9/23+格隆汇+IBKR(Reuters)+Econoday 4源✅",
    },
    "EU_PMI_SVC_FLASH_20260923": {
        "actual": 53.0, "forecast": 51.4, "previous": 51.6, "status": "released",
        "notes": "9月欧元区服务业PMI初值 53.0（预期51.4/前值8月终值51.6，大超预期），10个月最高。⚠️ 8月初值51.7、终值下修至51.6。服务业扩张为综合PMI创41个月新高（53.1，2023年4月来最快）主驱动；服务业扩招员工、制造商持平；服务业出口需求转弱。来源：新华财经+格隆汇+IBKR/Reuters+Econoday 4源✅",
    },
    "EU_PMI_COMPOSITE_FLASH_20260923": {
        "actual": 53.1, "forecast": 51.7, "previous": 52.0, "status": "released",
        "notes": "9月欧元区综合PMI初值 53.1（预期51.7/前值8月终值52.0，大超预期，路透调查最高预测52.6），41个月最高=2023年4月来最快增速。⚠️ 8月初值52.1、终值下修至52.0。总新订单4年多来最快增长（出口支撑）；就业连续第2个月小幅增加；投入与产出价格以4个月最快速度上涨（能源成本）——Williamson：通胀压力回升不意外，增长韧性好于担忧；ECB 9月已年内第2次加息，PMI超预期加大再加息难度。来源：新华财经+格隆汇+Reuters/KuwaitTimes+Econoday 4源✅",
    },
    "US_PMI_FLASH_20260923": {
        "actual": 58.4, "forecast": 54.9, "previous": 56.0, "status": "released",
        "notes": "9月美S&P综合PMI初值 58.4（预期54.9/前值56.0，大超预期），2021年7月来最高（54-62个月新高口径），连续4个月加速。制造业 57.0（预期53.6-53.7/前53.9，52个月最高）、服务业 58.7（预期55.9-56.0/前56.5，59个月最高）。制造业产出+3.6pt至56.7（2022年4月来最快）；就业2022年6月来最高；积压订单2022年5月来最大增幅；投入成本2022年10月来最高（燃油+运输，工资压力亦升）——通胀信号强化，S&P：Q3年化增速信号约4%。来源：S&P Global官网+TradingEconomics+TheStreet Pro+Econoday/quodd 4源✅",
    },
    "US_JOBLESS_CLAIMS_20260924": {
        "forecast": 20.2, "previous": 19.6, "status": "upcoming",
        "notes": "今晚20:30 BJS发布（至9/19当周）。预期分歧：investing.com 20.1万/helious 20.3万/OneRoyal 20.2万，取20.2万；前值19.6万（9/17当周，7月中来最低，低于预期20.8万）、四周均值20.6万。初请今夏持续处于19-21万历史低位，若持续升破22-23万才是裁员加速信号。",
    },
    "US_NEW_HOME_SALES_20260924": {
        "forecast": 61.8, "previous": 60.7, "status": "upcoming",
        "notes": "今晚22:00 BJS发布（8月数据，Census）。Econoday共识61.8万（区间60.0-64.0万）/彭博调查61.6万/OneRoyal 62.0万，取61.8万；前值7月60.7万（环比-10.5%大跌后预期回升；仍远低于2025年8月69.8万）。背景：NAHB建筑商信心9月回落至32（一年低点）、房贷利率8月初升后月底回落9月反弹、7月成屋销售已连降。",
    },
}

changed = []
for e in events:
    eid = e.get("id")
    if eid in UPDATES:
        u = UPDATES[eid]
        for k, v in u.items():
            if k == "notes":
                e[k] = v
            else:
                e[k] = v
        changed.append(eid)

assert len(changed) == len(UPDATES), f"缺失事件: {set(UPDATES)-set(changed)}"

out = json.dumps(data, ensure_ascii=False, indent=1)
open(PATH, "w", encoding="utf-8", newline="\n").write(out)

# 回读核验
data2 = json.loads(open(PATH, encoding="utf-8").read())
ev2 = {e["id"]: e for e in (data2["events"] if isinstance(data2, dict) else data2)}
for eid in UPDATES:
    e = ev2[eid]
    print(f"{eid}: actual={e.get('actual')} fc={e.get('forecast')} prev={e.get('previous')} status={e.get('status')}")
print("OK, updated", len(changed))
