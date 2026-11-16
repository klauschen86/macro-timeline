#!/usr/bin/env python3
"""2026-11-16 b轮回填：中国10月实际值（统计局官网一手 10:00 BJS 发布）+ US_RETAIL 日期再修正
运行顺序：本脚本在 run_daily.py 之后执行（合并会回滚日期），改完调 run_daily.generate_js 重生成 JS
"""
import json

CAL = "data/calendar.json"
cal = json.load(open(CAL, encoding="utf-8"))
events = {e["id"]: e for e in cal["events"]}

# 中国10月实际值（官方一手，澎湃+新华社+腾讯多源转载一致；westock CLI 后端10月值未更新）
e = events["CN_INDUSTRIAL_20261116"]
e["actual"] = 4.8
e["status"] = "released"
e["notes"] += (
    " | 【10:00官方回填】10月规上工业增加值+4.8%(环比+0.21%),大幅低于机构预期(均值5.3/华泰5.7);9月5.5%;1-10月累计5.3%。"
    "高技术制造业+17.6%/装备制造+10.6%支撑;汽车产量-7.7%/发电量-2.1%/十种有色-1.2%拖累;出口交货值+18.6%。"
    "来源:统计局官网(一手)+澎湃+新华社(腾讯转载) 多源✅;westock CLI 10月值后端未更新,以官方一手为权威"
)

e = events["CN_RETAIL_20261116"]
e["actual"] = 0.4
e["status"] = "released"
e["notes"] += (
    " | 【10:00官方回填】10月社零46463亿元+0.4%(低于机构均值0.9,略高于华泰0);9月1.1%;限额以上-4.9%为主要拖累,"
    "餐饮+0.7%/商品+0.3%;1-10月+1.0%。来源:统计局官网(一手)+澎湃+新华社 多源✅"
)

e = events["CN_FAI_20261116"]
e["actual"] = -8.1
e["status"] = "released"
e["notes"] += (
    " | 【10:00官方回填】1-10月固投364824亿元累计同比-8.1%(降幅深于机构预期-7.0);房地产开发投资57215亿-21.6%;"
    "第二产业-3.6%/第三产业-10.9%;新开工-24.4%/商品房销售额-14.3%。来源:统计局官网(一手)+澎湃 多源✅"
)

e = events["CN_UNEMPLOYMENT_20261116"]
e["actual"] = 5.1
e["status"] = "released"
e["notes"] += (
    " | 【10:00官方回填】10月全国城镇调查失业率5.1%(与上月持平);31个大城市5.1%;1-10月均值5.2%。"
    "来源:统计局官网(一手)+新华社(腾讯转载) 多源✅"
)

# US_RETAIL 日期再修正（run_daily 合并会回滚到11-16，本脚本在合并后重改）
e = events["US_RETAIL_20261116"]
e["release_date"] = "2026-11-17"

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

# 重生成 JS
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import run_daily
run_daily.generate_js(run_daily.load_calendar())
print("回填: CN工业4.8/社零0.4/固投-8.1/失业率5.1 全部released; US_RETAIL→11-17; JS已重生成")
