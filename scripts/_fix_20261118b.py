#!/usr/bin/env python3
"""2026-11-18 b轮：run_daily 合并回滚日期后重改（不改脚本代码的既定流程）
US_RETAIL→11-17；UK_CPI→11-18 15:00 BJS（ONS 官方发布日程）
改完调 run_daily.generate_js 重生成 JS
"""
import json
import sys, os

CAL = "data/calendar.json"
cal = json.load(open(CAL, encoding="utf-8"))
events = {e["id"]: e for e in cal["events"]}

e = events["US_RETAIL_20261116"]
e["release_date"] = "2026-11-17"

e = events["UK_CPI_20261117"]
e["release_date"] = "2026-11-18"
e["time"] = "15:00"
if "11-18日期纠正" not in str(e.get("notes", "")):
    e["notes"] += (
        " | 【11-18日期纠正】ONS 2026年10月CPI实际于11-18 07:00 GMT=15:00 BJS发布(日历原误标11-17);"
        "来源:Econoday 2026年发布日程表(11/18,For Oct 2026)+FXStreet/TIOmarkets 07:00 GMT 双源✅;"
        "本批次(11-18上午)留pending,待11-19回填actual;fc3.7/prev3.5维持"
    )

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

chk = {e["id"]: e for e in json.load(open(CAL, encoding="utf-8"))["events"]}
assert chk["US_RETAIL_20261116"]["release_date"] == "2026-11-17"
assert chk["US_RETAIL_20261116"]["actual"] == 0.2
assert chk["UK_CPI_20261117"]["release_date"] == "2026-11-18"
assert chk["UK_CPI_20261117"]["time"] == "15:00"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_daily
run_daily.generate_js(run_daily.load_calendar())
print("b轮: US_RETAIL→11-17(0.2 released保留); UK_CPI→11-18 15:00 pending; JS已重生成")
