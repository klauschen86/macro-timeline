#!/usr/bin/env python3
"""
中国宏观数据采集器
数据源：东方财富经济日历 + 金十数据
自动获取中国宏观数据发布日历和实际结果
"""

import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests


# ============================================================
# 数据源1: 东方财富经济日历 API
# ============================================================

def fetch_eastmoney_calendar(start_date=None, end_date=None):
    """
    从东方财富获取中国经济日历
    东方财富数据接口
    """
    if start_date is None:
        start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")

    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
    
    params = {
        "reportName": "RPT_ECONOMY_CALENDAR",
        "columns": "ALL",
        "sortColumns": "PUBLISHDATE",
        "sortTypes": "1",
        "pageNumber": "1",
        "pageSize": "500",
        "source": "WEB",
        "client": "WEB",
        "filter": f'(PUBLISHDATE>=\'{start_date}\')(PUBLISHDATE<=\'{end_date}\')(COUNTRY=\'中国\')',
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://data.eastmoney.com/",
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        data = resp.json()
        if data.get("success") and data.get("result") and data["result"].get("data"):
            return parse_eastmoney_data(data["result"]["data"])
    except Exception as e:
        print(f"  [东方财富API] 请求失败: {e}")
    
    return []


def parse_eastmoney_data(rows):
    """解析东方财富经济日历数据"""
    events = []
    # 东方财富字段映射（可能因API版本变化而不同）
    field_map = {
        "PUBLISHDATE": "release_date",
        "COUNTRY": "country", 
        "INDICATORNAME": "indicator",
        "ACTUALVALUE": "actual",
        "FORECASTVALUE": "forecast",
        "PREVVALUE": "previous",
        "IMPORTANCE": "importance",
        "FREQUENCY": "frequency",
        "UNIT": "unit",
        "PUBLISHTIME": "release_time",
        "DATADATE": "period",
        "INDICATORID": "indicator_id",
    }
    
    for row in rows:
        event = {}
        for api_field, our_field in field_map.items():
            val = row.get(api_field)
            if val is not None and val != "" and val != "-":
                event[our_field] = val
        
        if not event.get("release_date"):
            continue
        
        # 标准化
        event["country"] = "CN"
        event["country_name"] = "中国"
        event["source"] = "东方财富"
        event["source_url"] = "https://data.eastmoney.com/"
        event["timezone"] = "BJS"
        
        # 格式化日期
        rd = event["release_date"]
        if len(str(rd)) == 8:
            event["release_date"] = f"{str(rd)[:4]}-{str(rd)[4:6]}-{str(rd)[6:8]}"
        
        # 重要性
        imp = event.get("importance", "")
        if imp:
            event["importance"] = int(imp) if str(imp).isdigit() else 2
        else:
            event["importance"] = 2
        
        # ID
        indicator_id = event.get("indicator_id", event.get("indicator", ""))
        rd_clean = event["release_date"].replace("-", "")
        event["id"] = f"CN_{indicator_id}_{rd_clean}"
        
        events.append(event)
    
    return events


# ============================================================
# 数据源2: 金十数据
# ============================================================

def fetch_jin10_calendar():
    """从金十数据获取财经日历"""
    url = "https://cdn-rili.jin10.com/web_data/latest/daily/zh/calendar.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://rili.jin10.com",
        "Referer": "https://rili.jin10.com/",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        return parse_jin10_data(data)
    except Exception as e:
        print(f"  [金十数据] 请求失败: {e}")
    
    return []


def parse_jin10_data(data):
    """解析金十数据日历"""
    events = []
    if not isinstance(data, dict):
        return events
    
    days = data.get("data", {})
    for date_str, day_data in days.items():
        if not isinstance(day_data, dict):
            continue
        items = day_data.get("list", day_data.get("indicators", []))
        if not items:
            items = day_data if isinstance(day_data, list) else []
        
        for item in items:
            if not isinstance(item, dict):
                continue
            
            country = item.get("country", "")
            if country != "中国" and country != "China":
                continue
            
            event = {
                "id": f"CN_JIN10_{item.get('id', date_str)}_{date_str}",
                "country": "CN",
                "country_name": "中国",
                "indicator": item.get("title", item.get("name", "")),
                "indicator_en": item.get("title_en", ""),
                "release_date": date_str,
                "release_time": item.get("time", ""),
                "timezone": "BJS",
                "importance": item.get("star", item.get("importance", 2)),
                "frequency": item.get("frequency", ""),
                "period": item.get("period", ""),
                "actual": item.get("actual", item.get("actual_state", "")),
                "forecast": item.get("forecast", item.get("consensus", "")),
                "previous": item.get("previous", item.get("revised_previous", "")),
                "unit": item.get("unit", ""),
                "source": "金十数据",
                "source_url": "https://rili.jin10.com/",
                "status": "released" if item.get("actual") else "upcoming",
            }
            events.append(event)
    
    return events


# ============================================================
# 数据源3: 国家统计局发布日程
# ============================================================

def fetch_stats_gov_calendar():
    """从国家统计局获取发布日程表"""
    # 国家统计局通常在每个季度初发布下季度的数据发布日程
    # 尝试获取当前季度的发布日程
    today = date.today()
    quarter = (today.month - 1) // 3 + 1
    
    url = "https://www.stats.gov.cn/sj/tjgb/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    events = []
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        # 尝试从页面中提取发布日程
        html = resp.text
        # 简单正则匹配日期格式 YYYY-MM-DD 和相关指标
        date_pattern = r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})[日]?'
        indicator_keywords = [
            ("CPI", "居民消费价格指数"),
            ("PPI", "工业生产者出厂价格"),
            ("PMI", "采购经理指数"),
            ("GDP", "国内生产总值"),
            ("工业增加值", "规模以上工业增加值"),
            ("消费品零售", "社会消费品零售总额"),
            ("固定资产投资", "固定资产投资"),
            ("贸易", "进出口"),
            ("金融", "社会融资规模"),
        ]
        
        for match in re.finditer(date_pattern, html):
            y, m, d = match.group(1), match.group(2).zfill(2), match.group(3).zfill(2)
            date_str = f"{y}-{m}-{d}"
            context = html[match.start()-50:match.end()+50]
            
            for keyword, indicator in indicator_keywords:
                if keyword in context:
                    events.append({
                        "id": f"CN_STATS_{indicator.replace(' ', '_')}_{date_str}",
                        "country": "CN", "country_name": "中国",
                        "indicator": indicator,
                        "release_date": date_str,
                        "source": "国家统计局",
                        "source_url": "https://www.stats.gov.cn/",
                        "importance": 3 if indicator in ("CPI", "GDP", "PMI") else 2,
                    })
                    break
    except Exception as e:
        print(f"  [国家统计局] 请求失败: {e}")
    
    return events


# ============================================================
# 主函数
# ============================================================

def merge_into_calendar(new_events, calendar_path):
    """将新事件合并到日历JSON中"""
    if not os.path.exists(calendar_path):
        print("  Calendar file not found, creating new one")
        return new_events
    
    with open(calendar_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    existing = {e["id"]: e for e in data.get("events", [])}
    updated = 0
    added = 0
    
    for new_ev in new_events:
        eid = new_ev.get("id")
        if not eid:
            continue
        
        if eid in existing:
            old = existing[eid]
            # 更新实际结果和预期值
            changed = False
            for field in ["actual", "forecast", "previous", "status", "release_date", "release_time"]:
                if new_ev.get(field) is not None and new_ev[field] != old.get(field):
                    old[field] = new_ev[field]
                    changed = True
            if changed:
                updated += 1
        else:
            # 检查是否有相似的（同日同指标）
            found = False
            for _, ev in existing.items():
                if (ev.get("release_date") == new_ev.get("release_date") and
                    ev.get("country") == new_ev.get("country") and
                    (new_ev.get("indicator", "") in ev.get("indicator", "") or
                     ev.get("indicator", "") in new_ev.get("indicator", ""))):
                    # 合并
                    for field in ["actual", "forecast", "previous", "status"]:
                        if new_ev.get(field) is not None:
                            ev[field] = new_ev[field]
                    found = True
                    updated += 1
                    break
            
            if not found:
                existing[eid] = new_ev
                added += 1
    
    data["events"] = list(existing.values())
    data["events"].sort(key=lambda e: e.get("release_date", ""))
    data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["meta"]["total_events"] = len(data["events"])
    
    with open(calendar_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return updated, added


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    calendar_path = os.path.join(project_dir, "data", "calendar.json")
    
    all_new_events = []
    
    # 1. 尝试东方财富
    print("[1/3] 东方财富经济日历...")
    em_events = fetch_eastmoney_calendar()
    print(f"     获取 {len(em_events)} 条")
    all_new_events.extend(em_events)
    
    # 2. 尝试金十数据
    print("[2/3] 金十数据日历...")
    j10_events = fetch_jin10_calendar()
    print(f"     获取 {len(j10_events)} 条")
    all_new_events.extend(j10_events)
    
    # 3. 尝试国家统计局
    print("[3/3] 国家统计局...")
    stats_events = fetch_stats_gov_calendar()
    print(f"     获取 {len(stats_events)} 条")
    all_new_events.extend(stats_events)
    
    # 合并到日历
    if all_new_events:
        updated, added = merge_into_calendar(all_new_events, calendar_path)
        print(f"\n结果: 更新 {updated} 条, 新增 {added} 条")
    else:
        print("\n无新数据（所有数据源均未返回结果）")
        print("提示: 可能是网络原因或API变更，日历将保持基于规律推算的版本")


if __name__ == "__main__":
    main()
