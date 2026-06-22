#!/usr/bin/env python3
"""
中国宏观数据采集器 v2.0
数据源：ForexFactory HTML 解析（主力，含CNY数据）+ 东方财富API（备用）+ 金十数据（备用）
自动获取中国宏观数据发布日历和实际结果

v2.0 变更（2026-06-14）:
- 新增: ForexFactory HTML 解析（已验证可用，含CNY数据）
- 东方财富: RPT_ECONOMY_CALENDAR 报表名已失效（"报表配置不存在"），标记为备用
- 金十数据: SSL EOF 错误（CDN配置问题，持续时间未知），标记为备用
- 国家统计局: 页面变为 JS 渲染 SPA（不可直接抓取），标记为备用
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
# 数据源1: ForexFactory HTML 解析 — CNY 数据（主力）
# ============================================================

def fetch_forexfactory_china():
    """
    从 ForexFactory 首页解析中国(CNY)经济日历
    ForexFactory 包含中国市场主要数据发布
    """
    url = "https://www.forexfactory.com/calendar"

    # 使用 Session 保持 Cookie（CloudFlare 防护需要）
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })

    try:
        # 先访问首页获取 Cookie
        session.get("https://www.forexfactory.com/", timeout=15)
        time.sleep(1)
        # 再获取日历
        resp = session.get(url, timeout=20)
        if resp.status_code != 200:
            print(f"  [ForexFactory] HTTP {resp.status_code}")
            return []
        html = resp.text
    except Exception as e:
        print(f"  [ForexFactory] 请求失败: {e}")
        return []

    rows = re.findall(r'<tr[^>]*calendar__row[^>]*>(.*?)</tr>', html, re.DOTALL)
    if not rows:
        print("  [ForexFactory] 未找到日历行")
        return []

    month_map = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    events = []
    current_date = None

    for row in rows:
        # 检测日期头行
        # 日期行特征: 短行 (< 300 字符) + 包含 "Mon Jun 15" 格式的月日
        dm = re.search(r'([A-Z][a-z]{2})\s+(\d+)', row)
        if dm and len(row) < 300:
            m_str, d_str = dm.group(1), dm.group(2)
            if m_str in month_map and d_str.isdigit():
                m = month_map[m_str]
                d = d_str.zfill(2)
                current_date = f"2026-{m}-{d}"
            continue

        if not current_date:
            continue

        # 只提取 CNY
        curr_match = re.search(r'calendar__currency[^>]*>\s*CNY\s*<', row)
        if not curr_match:
            continue

        # 事件名称
        ev_match = re.search(r'calendar__event-title\"[^>]*>(.*?)</span>', row)
        if not ev_match:
            continue
        event_name = ev_match.group(1).strip()
        if not event_name or event_name == 'Bank Holiday':
            continue

        # 时间
        time_match = re.search(r'calendar__time[^>]*>(.*?)</td>', row)
        time_str = ""
        if time_match:
            raw_time = re.sub(r'<[^>]+>', '', time_match.group(1)).strip()
            if raw_time and not raw_time.startswith('<'):
                time_str = raw_time

        # 影响等级
        impact = 2  # 中国数据默认 important
        if 'icon--ff-impact-red' in row:
            impact = 4
        elif 'icon--ff-impact-ora' in row:
            impact = 3
        elif 'icon--ff-impact-yel' in row:
            impact = 2

        # 提取 actual / forecast / previous
        actual = forecast = previous = None
        vals = re.findall(
            r'class="[^"]*calendar__(actual|forecast|previous)[^"]*">\s*<span[^>]*>(.*?)</span>',
            row
        )
        for field, val in vals:
            val = val.strip()
            if val and val != '&nbsp;':
                if field == 'actual':
                    actual = val
                elif field == 'forecast':
                    forecast = val
                elif field == 'previous':
                    previous = val

        # 事件名翻译映射
        cn_name_map = {
            'Industrial Production y/y': '规模以上工业增加值（同比）',
            'Fixed Asset Investment ytd/y': '固定资产投资（累计同比）',
            'Retail Sales y/y': '社会消费品零售总额（同比）',
            'Unemployment Rate': '城镇调查失业率',
            'New Home Prices m/m': '新建住宅价格（环比）',
            'NBS Press Conference': '国家统计局新闻发布会',
            'Caixin Manufacturing PMI': '财新制造业PMI',
            'Caixin Services PMI': '财新服务业PMI',
            'Manufacturing PMI': '官方制造业PMI',
            'Non-Manufacturing PMI': '官方非制造业PMI',
            'Trade Balance': '贸易差额',
            'CPI y/y': 'CPI 居民消费价格指数（同比）',
            'PPI y/y': 'PPI 工业生产者出厂价格（同比）',
            'GDP y/y': 'GDP 国内生产总值（同比）',
            'M2 Money Supply y/y': 'M2 货币供应量（同比）',
            'New Loans': '新增人民币贷款',
        }
        cn_name = cn_name_map.get(event_name, event_name)

        date_clean = current_date.replace("-", "")
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', event_name)[:40]
        event_id = f"CN_FF_{safe_name}_{date_clean}"

        events.append({
            "id": event_id,
            "country": "CN",
            "country_name": "中国",
            "indicator": cn_name,
            "indicator_en": event_name,
            "release_date": current_date,
            "release_time": time_str,
            "timezone": "BJS",
            "importance": impact,
            "actual": actual,
            "forecast": forecast,
            "previous": previous,
            "unit": "",
            "source": "ForexFactory",
            "source_url": "https://www.forexfactory.com/calendar",
            "status": "released" if actual else "upcoming",
        })

    return events


# ============================================================
# 数据源2: 东方财富（备用 — 报表名已失效 2026-06）
# ============================================================

def fetch_eastmoney_calendar(start_date=None, end_date=None):
    """
    东方财富：RPT_ECONOMY_CALENDAR 报表名已失效（返回 "报表配置不存在"）
    保留此函数等 API 恢复
    """
    return []


# ============================================================
# 数据源3: 金十数据（备用 — SSL CDN 问题 2026-06）
# ============================================================

def fetch_jin10_calendar():
    """
    金十数据：SSL UNEXPECTED_EOF_WHILE_READING
    HTTP 返回 502，网站可访问但 API CDN 不可用
    保留此函数等 CDN 恢复
    """
    return []


# ============================================================
# 数据源4: 国家统计局（备用 — JS SPA 2026-06）
# ============================================================

def fetch_stats_gov_calendar():
    """
    国家统计局：页面变为 JS 渲染 SPA（414 字节 shell HTML）
    需要 headless browser 才能抓取
    保留此函数以便将来集成浏览器抓取
    """
    return []


# ============================================================
# 合并
# ============================================================

def merge_into_calendar(new_events, calendar_path):
    if not os.path.exists(calendar_path):
        print("  Calendar file not found")
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

    # 主力: ForexFactory CNY
    print("[1/1] ForexFactory CNY 数据...")
    ff_events = fetch_forexfactory_china()
    print(f"     获取 {len(ff_events)} 条")
    all_new_events.extend(ff_events)

    if all_new_events:
        for e in all_new_events:
            fc = f" forecast={e['forecast']}" if e.get('forecast') else ''
            pv = f" previous={e['previous']}" if e.get('previous') else ''
            a = f" actual={e['actual']}" if e.get('actual') else ''
            print(f"     [{e['release_date']}] {e['indicator']}{fc}{pv}{a}")

        updated, added = merge_into_calendar(all_new_events, calendar_path)
        print(f"\n结果: 更新 {updated} 条, 新增 {added} 条")
    else:
        print("\n无新数据 — ForexFactory CNY 解析可能因页面变更而失败")
        print("提示: 日历将保持基于规律推算的版本")


if __name__ == "__main__":
    main()
