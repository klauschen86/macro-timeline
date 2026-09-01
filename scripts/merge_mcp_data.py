#!/usr/bin/env python3
"""
MCP 数据合并器 v1.0
从 westock MCP 获取的宏观经济数据合并到 calendar.json 中。

数据来源：
- calendar_future: 未来宏观经济事件日历（中/美/欧/日/英等）
- calendar_hist:   历史宏观经济事件
- 各国指标: us_inflation, us_employment, eu_inflation, jp_inflation 等

数据文件：
- data/mcp_calendar_future.json  → 来自 data_macro(macro_calendar_future)
- data/mcp_calendar_hist.json     → 来自 data_macro(macro_calendar_hist)
- data/mcp_{region}_{type}.json   → 来自各国指标 data_macro
- data/calendar.json              → 输出目标

工作流：
1. 读取所有 MCP 数据文件
2. 提取事件和指标值
3. 与现有 calendar.json 合并
4. 去重、更新 actual/forecast/previous
5. 生成 calendar_data.js
"""

import json
import os
import re
import sys
from datetime import date, datetime


SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MCP_DIR = os.path.join(DATA_DIR, "mcp")
CALENDAR_FILE = os.path.join(DATA_DIR, "calendar.json")

# ============================================================
# 区域 → 国家映射
# ============================================================
AREA_COUNTRY_MAP = {
    "中国":   ("CN", "中国"),
    "美国":   ("US", "美国"),
    "欧元区": ("EU", "欧元区"),
    "德国":   ("EU", "欧元区"),
    "法国":   ("EU", "欧元区"),
    "意大利": ("EU", "欧元区"),
    "西班牙": ("EU", "欧元区"),
    "英国":   ("UK", "英国"),
    "日本":   ("JP", "日本"),
}

# 区域指标 → MCP listCode 映射
REGION_INDICATORS = {
    "US": ["us_inflation", "us_employment", "us_monetary", "us_energy",
           "us_confidence", "us_fiscal", "us_realestate", "us_eco_growth"],
    "EU": ["eu_inflation", "eu_employment", "eu_monetary", "eu_confidence",
           "eu_eco_growth", "eu_export_reserve"],
    "JP": ["jp_inflation", "jp_employment", "jp_monetary", "jp_confidence",
           "jp_eco_growth", "jp_export_reserve"],
    "UK": [],  # 英国数据在 calendar_future 中
    "CN": ["cpi_ppi", "pmi", "gdp", "financing", "fundquantity", "export",
           "consumption", "investment", "valueadded", "forecast"],
}


def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def date_ymd(occur_date):
    """将 20260717 格式转为 2026-07-17"""
    s = str(occur_date)
    if len(s) == 8:
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return s


# ============================================================
# Step 1: 从 calendar_future/calendar_hist 提取事件
# ============================================================

def extract_calendar_events(mcp_data, source_label="future"):
    """
    从 calendar_future 或 calendar_hist 提取事件列表
    返回: [(country_code, country_name, indicator, release_date, release_time, importance), ...]
    """
    events = []
    if not mcp_data or "items" not in mcp_data:
        return events

    for item in mcp_data["items"]:
        area = item.get("AreaName", "")
        event_text = item.get("Event", "")
        occur_date = item.get("OccurDate", "")
        occur_time = item.get("OccurTime", "")

        if not area or not event_text or not occur_date:
            continue

        # 映射区域 → 国家代码
        country_info = AREA_COUNTRY_MAP.get(area)
        if not country_info:
            # 跳过非五大经济体的事件（但要保留——以后可能扩展）
            continue

        country_code, country_name = country_info
        release_date = date_ymd(occur_date)

        # 生成指标名（截取前80字）
        indicator = event_text[:80]

        # 重要性：根据事件关键词判断
        importance = 1
        high_impact_keywords = ["利率决议", "CPI", "PPI", "GDP", "PMI", "非农",
                                "FOMC", "货币政策", "失业率", "通胀", "利率"]
        medium_impact_keywords = ["讲话", "发布会", "零售", "工业产出", "贸易",
                                  "消费者信心", "营建许可", "新屋开工", "褐皮书"]
        for kw in high_impact_keywords:
            if kw in event_text:
                importance = 3
                break
        if importance == 1:
            for kw in medium_impact_keywords:
                if kw in event_text:
                    importance = 2
                    break

        events.append({
            "country": country_code,
            "country_name": country_name,
            "indicator": indicator,
            "release_date": release_date,
            "release_time": occur_time,
            "importance": importance,
            "source": "WeStock-MCP",
            "source_label": source_label,
        })

    return events


# ============================================================
# Step 2: 从各国指标中提取 actual/forecast/previous
# ============================================================

def extract_indicator_values(mcp_data):
    """
    从区域指标数据提取实际值/预测值/前值
    返回: {(country_code, indicator_name, date): {actual, forecast, previous}}
    """
    values = {}
    if not mcp_data or "items" not in mcp_data:
        return values

    for item in mcp_data["items"]:
        indicator_name = item.get("IndicatorName", "")
        occur_date = item.get("OccurDate", "")
        actual = item.get("ActualValue")
        forecast = item.get("ForecastValue")
        previous = item.get("FormerValue")

        if not indicator_name or not occur_date:
            continue

        release_date = date_ymd(occur_date)

        # 从指标名推断国家
        country_code = "CN"  # 默认中国
        for area_name in ["美国", "欧元区", "日本", "英国"]:
            if area_name in indicator_name:
                for cn, (cc, _) in AREA_COUNTRY_MAP.items():
                    if cn == area_name:
                        country_code = cc
                        break
                break

        # 简化指标名（去掉国家前缀）
        short_name = indicator_name
        for prefix in ["美国", "欧元区", "日本", "英国"]:
            short_name = short_name.replace(prefix, "", 1)

        key = (country_code, short_name, release_date)
        values[key] = {
            "actual": actual if actual and actual != "未公布" else None,
            "forecast": forecast if forecast else None,
            "previous": previous if previous else None,
            "full_name": indicator_name,
        }

    return values


# ============================================================
# Step 3: 匹配事件与指标值
# ============================================================

def match_indicator_to_event(event_indicator, indicator_name):
    """判断事件描述文本是否与指标名匹配（模糊匹配）"""
    # 直接包含
    if indicator_name in event_indicator or event_indicator in indicator_name:
        return True

    # 关键词匹配
    keywords_map = {
        "CPI": ["CPI", "通胀", "消费者价格"],
        "PPI": ["PPI", "生产者价格"],
        "GDP": ["GDP", "国内生产总值"],
        "PMI": ["PMI", "采购经理"],
        "非农": ["非农", "就业"],
        "失业率": ["失业", "就业人数"],
        "零售": ["零售"],
        "工业产出": ["工业产出", "工业增加值"],
        "贸易": ["贸易", "进出口"],
        "利率": ["利率", "FOMC", "联邦基金"],
        "消费者信心": ["消费者信心", "消费者情绪"],
        "营建许可": ["营建许可"],
        "新屋开工": ["新屋开工"],
        "M2": ["M2", "货币供应"],
        "社融": ["社融", "社会融资"],
    }

    for kw, aliases in keywords_map.items():
        if any(a in indicator_name for a in aliases):
            return any(a in event_indicator for a in aliases)

    return False


# ============================================================
# Step 4: 主合并逻辑
# ============================================================

def merge_all():
    print("=" * 60)
    print("MCP Data Merger v1.0")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # 加载现有数据
    existing = load_json(CALENDAR_FILE)
    if not existing:
        print("[ERROR] calendar.json not found")
        return

    existing_events = existing.get("events", [])
    existing_ids = {e["id"]: e for e in existing_events}
    print(f"\nExisting events: {len(existing_events)}")

    # ========================================================
    # Phase 1: 采集 MCP 日历事件
    # ========================================================

    mcp_events = []

    # 1a. calendar_future
    cf = load_json(os.path.join(MCP_DIR, "calendar_future.json"))
    if cf:
        data = cf.get("data", {}).get("macro_calendar_future", {})
        future_events = extract_calendar_events(data, "future")
        print(f"  calendar_future: {len(future_events)} events")
        mcp_events.extend(future_events)

    # 1b. calendar_hist
    ch = load_json(os.path.join(MCP_DIR, "calendar_hist.json"))
    if ch:
        data = ch.get("data", {}).get("macro_calendar_hist", {})
        hist_events = extract_calendar_events(data, "hist")
        print(f"  calendar_hist: {len(hist_events)} events")
        mcp_events.extend(hist_events)

    # ========================================================
    # Phase 2: 采集区域指标实际值
    # ========================================================

    all_values = {}

    for country_code, indicators in REGION_INDICATORS.items():
        for ind in indicators:
            path = os.path.join(MCP_DIR, f"macro_{ind}.json")
            data = load_json(path)
            if not data:
                continue
            mcp_data = data.get("data", {}).get(f"macro_{ind}", {})
            vals = extract_indicator_values(mcp_data)
            all_values.update(vals)

    print(f"  Indicator values extracted: {len(all_values)}")

    # ========================================================
    # Phase 3: 合并 MCP 事件到 calendar.json
    # ========================================================

    updated = 0
    added = 0
    merged_ids = set()

    for mcp_ev in mcp_events:
        country = mcp_ev["country"]
        indicator = mcp_ev["indicator"]
        rel_date = mcp_ev["release_date"]

        # 生成 ID
        date_clean = rel_date.replace("-", "")
        safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', indicator)[:40]
        event_id = f"{country}_MCP_{safe_name}_{date_clean}"

        merged_ids.add(event_id)

        if event_id in existing_ids:
            # 更新现有事件
            old = existing_ids[event_id]
            changed = False
            for field in ["indicator", "release_time", "importance"]:
                if mcp_ev.get(field) and mcp_ev[field] != old.get(field):
                    old[field] = mcp_ev[field]
                    changed = True
            # 搜索匹配的指标值
            for (cc, iname, rdate), vals in all_values.items():
                if cc == country and rdate == rel_date and match_indicator_to_event(indicator, iname):
                    for vf in ["actual", "forecast", "previous"]:
                        if vals.get(vf) is not None and vals[vf] != old.get(vf):
                            old[vf] = vals[vf]
                            changed = True
                    old["source"] = "WeStock-MCP"
                    break
            if changed:
                updated += 1
        else:
            # 新事件
            new_ev = {
                "id": event_id,
                "country": country,
                "country_name": mcp_ev["country_name"],
                "indicator": indicator,
                "indicator_en": indicator,
                "release_date": rel_date,
                "release_time": mcp_ev.get("release_time", ""),
                "timezone": "BJS",
                "importance": mcp_ev.get("importance", 1),
                "actual": None,
                "forecast": None,
                "previous": None,
                "unit": "",
                "source": "WeStock-MCP",
                "source_url": "",
                "status": "upcoming",
            }
            # 尝试匹配指标值
            for (cc, iname, rdate), vals in all_values.items():
                if cc == country and rdate == rel_date and match_indicator_to_event(indicator, iname):
                    new_ev["actual"] = vals.get("actual")
                    new_ev["forecast"] = vals.get("forecast")
                    new_ev["previous"] = vals.get("previous")
                    if new_ev["actual"]:
                        new_ev["status"] = "released"
                    break
            existing_ids[event_id] = new_ev
            added += 1

    # ========================================================
    # Phase 4: 只更新已有事件的 indicator 值（不新增）
    # ========================================================

    # 对 calendar.json 中已有的事件，尝试匹配 MCP 指标值
    for eid, ev in existing_ids.items():
        if eid in merged_ids:
            continue  # already processed

        country = ev.get("country", "")
        indicator = ev.get("indicator", "")
        rel_date = ev.get("release_date", "")

        for (cc, iname, rdate), vals in all_values.items():
            if cc == country and rdate == rel_date and match_indicator_to_event(indicator, iname):
                changed = False
                for vf in ["actual", "forecast", "previous"]:
                    if vals.get(vf) is not None and vals[vf] != ev.get(vf):
                        ev[vf] = vals[vf]
                        changed = True
                if changed:
                    ev["source"] = "WeStock-MCP"
                    if ev.get("actual"):
                        ev["status"] = "released"
                    updated += 1
                break

    # ========================================================
    # Phase 5: 生成输出
    # ========================================================

    # 更新状态
    today_str = date.today().strftime("%Y-%m-%d")
    for ev in existing_ids.values():
        rd = ev.get("release_date", "")
        if ev.get("actual") is not None:
            ev["status"] = "released"
        elif rd < today_str:
            ev["status"] = "pending"
        else:
            ev["status"] = "upcoming"

    events_list = list(existing_ids.values())
    events_list.sort(key=lambda e: e.get("release_date", ""))

    # 统计
    by_country = {}
    for e in events_list:
        cn = e.get("country_name", "??")
        by_country[cn] = by_country.get(cn, 0) + 1

    released = [e for e in events_list if e.get("status") == "released"]
    upcoming = [e for e in events_list if e["release_date"] >= today_str]
    pending = [e for e in events_list if e.get("status") == "pending"]
    with_forecast = [e for e in upcoming if e.get("forecast") is not None]

    output = {
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_by": "merge_mcp_data.py",
            "timezone": "BJS (UTC+8)",
            "total_events": len(events_list),
            "upcoming_events": len(upcoming),
            "released_events": len(released),
            "pending_events": len(pending),
            "upcoming_with_forecast": len(with_forecast),
            "data_from": min(e["release_date"] for e in events_list) if events_list else today_str,
            "data_to": max(e["release_date"] for e in events_list) if events_list else today_str,
            "by_country": by_country,
        },
        "events": events_list,
    }

    save_json(CALENDAR_FILE, output)

    print(f"\n{'='*60}")
    print(f"Merge Complete!")
    print(f"  Total: {len(events_list)} events")
    print(f"  Updated: {updated}, Added: {added}")
    print(f"  Released: {len(released)}")
    print(f"  Upcoming: {len(upcoming)} ({len(with_forecast)} with forecasts)")
    print(f"  Pending: {len(pending)}")
    print(f"  By country: {by_country}")
    print(f"{'='*60}")

    return output


if __name__ == "__main__":
    merge_all()
