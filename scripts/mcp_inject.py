#!/usr/bin/env python3
"""
MCP 数据注入器 v1.1 — 替代 ForexFactory 的数据采集方案

v1.1 (2026-09-04): 修复指标口径错配 bug
- 根因: 同日期同国家多个候选 item 按 score 选优，变体指标因多出公共词
  (如"私营企业非农就业人数"多"人数"、"U6失业率") 反超整体指标，
  导致 US_NFP 被注入私营非农(3万)、失业率被注入U6(7.9)。
- 修复: 新增 EXCLUDE_TOKENS 排除词(私营/U6/四周均值/续请/挑战者/初请)，
  MCP 指标名含排除词且 calendar 指标名不含该词时 score 直接降为负分淘汰。
- 影响: 就业系列(非农/失业率/初请) 与衍生变体指标的注入准确性。

从 westock MCP data_macro 获取的 JSON 文件中提取 actual/forecast/previous 值，
注入到 calendar.json 的对应事件中。

数据文件（位于 data/mcp/）：
- calendar_future.json  → 未来事件日历
- macro_us_employment.json, macro_us_inflation.json, ...
- macro_eu_inflation.json, macro_eu_employment.json, ...
- macro_jp_inflation.json, macro_jp_employment.json, ...
- macro_cpi_ppi.json, macro_pmi.json, macro_gdp.json, ...

工作流（由自动化 prompt 编排）：
1. MCP 采集 → 保存到 data/mcp/*.json
2. 本脚本 → 注入值到 calendar.json
3. run_daily.py → 重新生成 JS
"""

import json
import os
import re
from datetime import date, datetime


SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MCP_DIR = os.path.join(DATA_DIR, "mcp")
CALENDAR_FILE = os.path.join(DATA_DIR, "calendar.json")


# 指标名模糊匹配映射
# (calendar.json indicator 关键词) → (MCP IndicatorName 关键词)
INDICATOR_MATCH_RULES = [
    # 中国
    ("CPI", "CPI"),
    ("PPI", "PPI"),
    ("GDP", "GDP"),
    ("PMI", "PMI"),
    ("工业增加值", "工业增加值"),
    ("社会消费品零售", "社会消费品零售"),
    ("固定资产投资", "固定资产投资"),
    ("贸易差额", "贸易差额"),
    ("M2", "M2"),
    ("失业率", "失业率"),
    ("社融", "社融"),
    ("新增人民币贷款", "新增人民币贷款"),
    ("规模以上工业", "规模以上工业"),
    # 美国
    ("初请", "初请失业金"),
    ("非农", "非农就业"),
    ("失业率", "失业率"),
    ("CPI", "CPI"),
    ("核心CPI", "核心CPI"),
    ("PPI", "PPI"),
    ("核心PPI", "核心PPI"),
    ("零售销售", "零售销售"),
    ("工业产出", "工业产出"),
    ("产能利用率", "产能利用率"),
    ("营建许可", "营建许可"),
    ("新屋开工", "新屋开工"),
    ("消费者信心", "消费者信心"),
    ("密歇根", "密歇根"),
    ("费城联储", "费城联储"),
    ("纽约联储", "纽约联储"),
    ("联邦基金利率", "联邦基金利率"),
    ("FOMC", "FOMC"),
    ("GDP", "GDP"),
    ("进口价格", "进口价格"),
    ("贸易帐", "贸易帐"),
    ("薪资", "平均时薪"),
    ("JOLTs", "JOLTs"),
    ("ADP", "ADP"),
    # 欧元区
    ("CPI", "调和CPI"),
    ("核心CPI", "核心CPI"),
    ("GDP", "GDP"),
    ("失业率", "失业率"),
    ("工业产出", "工业产出"),
    ("PPI", "PPI"),
    ("ZEW", "ZEW"),
    ("经常帐", "经常帐"),
    # 日本
    ("CPI", "核心CPI"),
    ("GDP", "GDP"),
    ("失业率", "失业率"),
    ("工业产出", "工业产出"),
    ("PPI", "PPI"),
    ("机械订单", "机械订单"),
    # 英国
    ("CPI", "CPI"),
    ("GDP", "GDP"),
    ("失业率", "失业率"),
    ("零售销售", "零售销售"),
]


def date_ymd(val):
    """将 20260717 或 20260717 格式转为 2026-07-17"""
    s = str(int(val))
    if len(s) == 8:
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return s


def match_indicators(cal_indicator, mcp_indicator_name):
    """判断 calendar.json 中的指标名是否与 MCP 指标名匹配"""
    for cal_kw, mcp_kw in INDICATOR_MATCH_RULES:
        if cal_kw.lower() in cal_indicator.lower():
            return mcp_kw.lower() in mcp_indicator_name.lower()
    return False


def load_mcp_file(filename):
    """加载 MCP JSON 文件，提取 items 列表"""
    path = os.path.join(MCP_DIR, filename)
    if not os.path.exists(path):
        return [], None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Try nested MCP structure: {"ok": true, "data": {"macro_xxx": {"items": [...]}}}
    inner = data.get("data", {})
    if inner:
        for key, val in inner.items():
            if isinstance(val, dict) and "items" in val:
                return val["items"], key

    # Try flat structure: {"items": [...], "listCode": "xxx"} (directly saved)
    if "items" in data and isinstance(data["items"], list):
        list_code = data.get("listCode", os.path.basename(path).replace(".json", ""))
        return data["items"], list_code

    return [], None


def extract_indicator_values(items):
    """
    从 MCP items 中提取 (country, date, indicator_name) → {actual, forecast, previous}
    自动推断国家
    """
    values = []
    for item in items:
        indicator_name = item.get("IndicatorName", "")
        occur_date = item.get("OccurDate", "")
        actual = item.get("ActualValue")
        forecast = item.get("ForecastValue")
        previous = item.get("FormerValue")

        if not indicator_name or not occur_date:
            continue

        # 跳过未公布
        if actual == "未公布":
            actual = None

        # 推断国家
        country = None
        if "中国" in indicator_name or "规模以上" in indicator_name or "城镇" in indicator_name:
            country = "中国"
        elif "美国" in indicator_name:
            country = "美国"
        elif "欧元区" in indicator_name:
            country = "欧元区"
        elif "日本" in indicator_name:
            country = "日本"
        elif "英国" in indicator_name:
            country = "英国"

        release_date = date_ymd(occur_date)

        values.append({
            "country": country,
            "indicator_name": indicator_name,
            "release_date": release_date,
            "actual": actual,
            "forecast": forecast,
            "previous": previous,
        })

    return values


def inject_values(calendar_events, mcp_values):
    """将 MCP 指标值注入到 calendar 事件中"""
    # 变体/衍生指标排除词（v1.1 修复口径错配）:
    # MCP 指标名含这些词且 calendar 指标名不含时，直接淘汰，防止
    # "私营企业非农"(多"人数"词)顶替整体非农、"U6失业率"顶替整体失业率等。
    EXCLUDE_TOKENS = ("私营", "U6", "四周均值", "续请", "挑战者", "初请")
    updated = 0

    for ev in calendar_events:
        ev_country = ev.get("country_name", "")
        ev_indicator = ev.get("indicator", "")
        ev_date = ev.get("release_date", "")

        best_match = None
        best_score = 0

        for mv in mcp_values:
            if mv["release_date"] != ev_date:
                continue
            if mv["country"] and mv["country"] != ev_country:
                continue

            # 计算匹配分数
            score = 0
            if match_indicators(ev_indicator, mv["indicator_name"]):
                score += 5
            # 变体排除: 命中排除词且事件指标名不含该词 → 淘汰
            for tok in EXCLUDE_TOKENS:
                if tok in mv["indicator_name"] and tok not in ev_indicator:
                    score = -100
                    break
            # 字符串相似度加分
            ev_words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', ev_indicator.lower()))
            mv_words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', mv["indicator_name"].lower()))
            common = ev_words & mv_words
            score += len(common)

            if score > best_score:
                best_score = score
                best_match = mv

        # 最低匹配分数阈值
        if best_match and best_score >= 5:
            changed = False
            for field in ["actual", "forecast", "previous"]:
                if best_match[field] is not None:
                    val = str(best_match[field])
                    if ev.get(field) != val:
                        ev[field] = val
                        changed = True
            if changed:
                ev["source"] = "WeStock-MCP"
                if ev.get("actual"):
                    ev["status"] = "released"
                updated += 1

    return updated


def main():
    print("=" * 60)
    print("MCP Data Injector v1.0")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # 加载 calendar.json
    if not os.path.exists(CALENDAR_FILE):
        print("[ERROR] calendar.json not found")
        return

    with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
        calendar = json.load(f)

    events = calendar.get("events", [])
    print(f"Loaded {len(events)} events")

    # 扫描 MCP 数据文件
    mcp_files = []
    if os.path.exists(MCP_DIR):
        mcp_files = [f for f in os.listdir(MCP_DIR) if f.endswith(".json")]
    print(f"Found {len(mcp_files)} MCP data files")

    # 收集所有指标值
    all_values = []
    for fname in mcp_files:
        items, list_code = load_mcp_file(fname)
        if not items:
            continue
        vals = extract_indicator_values(items)
        print(f"  {fname}: {len(vals)} indicators")
        all_values.extend(vals)

    print(f"Total MCP indicator values: {len(all_values)}")

    # 注入
    updated = inject_values(events, all_values)
    print(f"Updated: {updated} events")

    # 重算统计
    today_str = date.today().strftime("%Y-%m-%d")
    released = [e for e in events if e.get("actual") is not None]
    upcoming = [e for e in events if e["release_date"] >= today_str]
    pending = [e for e in events if e.get("status") == "pending"]
    with_forecast = [e for e in upcoming if e.get("forecast") is not None]

    by_country = {}
    for e in events:
        cn = e.get("country_name", "??")
        by_country[cn] = by_country.get(cn, 0) + 1

    calendar["meta"].update({
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_events": len(events),
        "upcoming_events": len(upcoming),
        "released_events": len(released),
        "pending_events": len(pending),
        "upcoming_with_forecast": len(with_forecast),
        "by_country": by_country,
    })
    calendar["events"] = events

    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(calendar, f, ensure_ascii=False, indent=2)

    print(f"\nUpdated calendar.json: {len(events)} events, {updated} with MCP values")
    print(f"  Released: {len(released)}, Upcoming: {len(upcoming)}, Pending: {len(pending)}")
    print("Done.")


if __name__ == "__main__":
    main()
