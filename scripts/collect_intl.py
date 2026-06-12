#!/usr/bin/env python3
"""
国际宏观数据采集器
数据源：Investing.com + ForexFactory + Trading Economics
自动获取美国/欧元区/日本/英国宏观数据发布日历
"""

import json
import os
import re
import sys
from datetime import date, datetime, timedelta

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests


def fetch_investing_calendar(start_date=None, end_date=None, countries=None):
    """
    从 Investing.com 获取经济日历
    默认获取美国、欧元区、日本、英国数据
    """
    if start_date is None:
        start_date = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")
    if countries is None:
        countries = [5, 72, 35, 4]  # US=5, EU=72, JP=35, UK=4
    
    all_events = []
    for country_id in countries:
        events = _fetch_investing_country(country_id, start_date, end_date)
        all_events.extend(events)
        time.sleep(0.5)
    
    return all_events


def _fetch_investing_country(country_id, start_date, end_date):
    """抓取 Investing.com 单个国家的经济日历"""
    country_names = {5: "US", 72: "EU", 35: "JP", 4: "UK"}
    country_cn = {"US": "美国", "EU": "欧元区", "JP": "日本", "UK": "英国"}
    
    url = "https://api.investing.com/api/financialdata/economiccalendar/list"
    
    params = {
        "countryIds": str(country_id),
        "dateFrom": start_date,
        "dateTo": end_date,
        "importance": "1,2,3",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "domain-id": "www",
        "Accept": "application/json",
    }
    
    events = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code != 200:
            # 尝试备用API
            return _fetch_investing_fallback(country_id, start_date, end_date)
        
        data = resp.json()
        items = data.get("data", [])
        
        for item in items:
            country_code = country_names.get(country_id, "??")
            event = {
                "id": f"{country_code}_INV_{item.get('id', '')}_{item.get('date', '')}",
                "country": country_code,
                "country_name": country_cn.get(country_code, ""),
                "indicator": item.get("name", item.get("event", "")),
                "indicator_en": item.get("name", ""),
                "release_date": item.get("date", ""),
                "release_time": item.get("time", ""),
                "timezone": _get_timezone(country_code),
                "importance": item.get("importance", 2),
                "frequency": item.get("frequency", ""),
                "period": item.get("period", ""),
                "actual": item.get("actual"),
                "forecast": item.get("forecast"),
                "previous": item.get("previous"),
                "unit": item.get("unit", ""),
                "source": "Investing.com",
                "source_url": "https://www.investing.com/economic-calendar/",
                "status": "released" if item.get("actual") else "upcoming",
            }
            events.append(event)
    except Exception as e:
        print(f"  [Investing.com-{country_cn.get(country_names.get(country_id, ''), '')}] 请求失败: {e}")
    
    return events


def _fetch_investing_fallback(country_id, start_date, end_date):
    """备用方式：从 Investing.com 移动端API获取"""
    url = "https://m.investing.com/economic-calendar/Service/getEconomicCalendarData"
    params = {
        "country[]": str(country_id),
        "dateFrom": start_date,
        "dateTo": end_date,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
        "X-Requested-With": "XMLHttpRequest",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        # 尝试解析返回数据
        return []
    except:
        return []


def _get_timezone(country_code):
    tz_map = {"US": "EST", "EU": "CET", "JP": "JST", "UK": "BST"}
    return tz_map.get(country_code, "UTC")


# ============================================================
# 数据源2: ForexFactory (外汇工厂)
# ============================================================

def fetch_forexfactory_week():
    """从 ForexFactory 获取本周财经日历"""
    url = "https://www.forexfactory.com/calendar"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        html = resp.text
        
        # 从HTML中提取日历数据（简单正则解析）
        # ForexFactory 的数据在 script 标签中
        events = []
        script_pattern = r'calendarData\s*=\s*(\[.*?\]);'
        match = re.search(script_pattern, html, re.DOTALL)
        
        if match:
            raw = match.group(1)
            try:
                data = json.loads(raw)
                for item in data:
                    country = item.get("country", "")
                    country_map = {"USD": "US", "EUR": "EU", "JPY": "JP", "GBP": "UK"}
                    cc = country_map.get(country, "")
                    if not cc:
                        continue
                    
                    cn_map = {"US": "美国", "EU": "欧元区", "JP": "日本", "UK": "英国"}
                    events.append({
                        "id": f"{cc}_FF_{item.get('id', '')}_{item.get('date', '')}",
                        "country": cc,
                        "country_name": cn_map.get(cc, country),
                        "indicator": item.get("title", item.get("name", "")),
                        "indicator_en": item.get("title", ""),
                        "release_date": item.get("date", ""),
                        "release_time": item.get("time", ""),
                        "timezone": _get_timezone(cc),
                        "importance": _ff_importance(item.get("impact", "")),
                        "actual": item.get("actual"),
                        "forecast": item.get("forecast"),
                        "previous": item.get("previous"),
                        "unit": "",
                        "source": "ForexFactory",
                        "source_url": "https://www.forexfactory.com/calendar",
                        "status": "released" if item.get("actual") else "upcoming",
                    })
            except json.JSONDecodeError:
                pass
        
        return events
    except Exception as e:
        print(f"  [ForexFactory] 请求失败: {e}")
    
    return []


def _ff_importance(impact):
    """ForexFactory 影响等级映射"""
    m = {"high": 3, "medium": 2, "low": 1}
    return m.get(str(impact).lower(), 2)


# ============================================================
# 数据源3: Trading Economics
# ============================================================

def fetch_trading_economics(country_code="united-states"):
    """从 Trading Economics 获取经济日历（需要API key但可尝试免费端点）"""
    # Trading Economics 有免费API，但可能需要注册
    # 这里提供一个基本的抓取框架
    url = f"https://api.tradingeconomics.com/calendar/country/{country_code}"
    
    # 免费演示API key（每天有限额）
    params = {"c": "guest:guest", "f": "json"}
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return parse_te_data(data, country_code)
    except Exception as e:
        print(f"  [TradingEconomics] 请求失败: {e}")
    
    return []


def parse_te_data(data, country_code):
    """解析 Trading Economics 数据"""
    country_map = {
        "united-states": ("US", "美国"),
        "euro-area": ("EU", "欧元区"),
        "japan": ("JP", "日本"),
        "united-kingdom": ("UK", "英国"),
    }
    cc, cn = country_map.get(country_code, ("??", country_code))
    
    events = []
    for item in data:
        events.append({
            "id": f"{cc}_TE_{item.get('CalendarId', '')}_{item.get('Date', '')}",
            "country": cc,
            "country_name": cn,
            "indicator": item.get("Event", item.get("Category", "")),
            "indicator_en": item.get("Event", ""),
            "release_date": str(item.get("Date", ""))[:10],
            "release_time": "",
            "timezone": _get_timezone(cc),
            "importance": item.get("Importance", 2),
            "actual": item.get("Actual"),
            "forecast": item.get("Forecast"),
            "previous": item.get("Previous"),
            "unit": item.get("Unit", ""),
            "source": "Trading Economics",
            "source_url": "https://tradingeconomics.com/",
            "status": "released" if item.get("Actual") else "upcoming",
        })
    return events


# ============================================================
# 合并
# ============================================================

def merge_into_calendar(new_events, calendar_path):
    if not os.path.exists(calendar_path):
        return 0, 0
    
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
            changed = False
            for field in ["actual", "forecast", "previous", "status"]:
                if new_ev.get(field) is not None and new_ev[field] != old.get(field):
                    old[field] = new_ev[field]
                    changed = True
            if changed:
                updated += 1
        else:
            existing[eid] = new_ev
            added += 1
    
    data["events"] = list(existing.values())
    data["events"].sort(key=lambda e: e.get("release_date", ""))
    data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["meta"]["total_events"] = len(data["events"])
    
    # 更新国家统计
    by_country = {}
    for e in data["events"]:
        cn = e.get("country_name", "")
        by_country[cn] = by_country.get(cn, 0) + 1
    data["meta"]["by_country"] = by_country
    
    with open(calendar_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return updated, added


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    calendar_path = os.path.join(project_dir, "data", "calendar.json")
    
    all_events = []
    
    # 1. Investing.com
    print("[1/3] Investing.com...")
    inv_events = fetch_investing_calendar()
    print(f"     获取 {len(inv_events)} 条")
    all_events.extend(inv_events)
    
    # 2. ForexFactory
    print("[2/3] ForexFactory...")
    ff_events = fetch_forexfactory_week()
    print(f"     获取 {len(ff_events)} 条")
    all_events.extend(ff_events)
    
    # 3. Trading Economics
    print("[3/3] Trading Economics...")
    for cc in ["united-states", "euro-area", "japan", "united-kingdom"]:
        te_events = fetch_trading_economics(cc)
        all_events.extend(te_events)
        time.sleep(0.5)
    print(f"     获取 {len(all_events)} 条 (合计)")
    
    if all_events:
        updated, added = merge_into_calendar(all_events, calendar_path)
        print(f"\n结果: 更新 {updated} 条, 新增 {added} 条")
    else:
        print("\n无新数据（在线数据源可能因网络或API限制无法访问）")
        print("日历保持基于规律推算的版本 + 已有数据")


if __name__ == "__main__":
    main()
