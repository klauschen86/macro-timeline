#!/usr/bin/env python3
"""
国际宏观数据采集器 v2.0
数据源：ForexFactory HTML 解析（主力）+ Investing.com API（备用）+ Trading Economics（备用）
自动获取美国/欧元区/日本/英国宏观数据发布日历

v2.0 变更（2026-06-14）:
- ForexFactory: 从失效的 JS 注入改为 HTML DOM 解析，已验证可用
- Investing.com: 标记为备用（403 需要认证，永久性不可用）
- Trading Economics: 标记为备用（guest 账户已停用，永久性不可用）
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
# 数据源1: ForexFactory HTML 解析（主力）
# ============================================================

def fetch_forexfactory():
    """
    从 ForexFactory 首页解析经济日历 HTML
    页面结构（2026-06）: 传统 HTML 表格，非 SPA
    - 日历行: <tr class="calendar__row">
    - 日期头: <td><span>Mon Jun 15</span></td>
    - 货币: <td class="calendar__currency">USD</td>
    - 影响: <span class="icon icon--ff-impact-{yel|ora|red}"></span>
    - 事件: <span class="calendar__event-title">Event Name</span>
    - 值: <td class="calendar__actual|forecast|previous"> <span>VALUE</span> </td>
    """
    url = "https://www.forexfactory.com/calendar"

    # 使用 Session 保持 Cookie（CloudFlare 防护需要）
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
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

    # 提取所有日历行
    rows = re.findall(r'<tr[^>]*calendar__row[^>]*>(.*?)</tr>', html, re.DOTALL)
    if not rows:
        print("  [ForexFactory] 未找到日历行（页面结构可能已变更）")
        return []

    # 月份映射
    month_map = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    # 货币→国家映射（只关注四大经济体）
    currency_country = {
        'USD': ('US', '美国'),
        'EUR': ('EU', '欧元区'),
        'JPY': ('JP', '日本'),
        'GBP': ('UK', '英国'),
    }

    timezone_map = {'US': 'EST', 'EU': 'CET', 'JP': 'JST', 'UK': 'BST'}

    # 英文→中文翻译表（覆盖 ForexFactory 所有常见指标）
    indicator_cn = {
        # === 美国 ===
        'Empire State Manufacturing Index': '纽约联储制造业指数',
        'Capacity Utilization Rate': '产能利用率',
        'Industrial Production m/m': '工业产出（环比）',
        'NAHB Housing Market Index': 'NAHB 房产市场指数',
        'ADP Weekly Employment Change': 'ADP 就业人数变化',
        'Building Permits': '营建许可',
        'Housing Starts': '新屋开工',
        'Import Prices m/m': '进口价格指数（环比）',
        'API Weekly Statistical Bulletin': 'API 原油库存报告',
        'Core Retail Sales m/m': '核心零售销售（环比）',
        'Retail Sales m/m': '零售销售（环比）',
        'Business Inventories m/m': '商业库存（环比）',
        'Pending Home Sales m/m': '成屋签约销售（环比）',
        'Crude Oil Inventories': '原油库存',
        'Federal Funds Rate': '联邦基金利率',
        'FOMC Economic Projections': 'FOMC 经济预测',
        'FOMC Statement': 'FOMC 声明',
        'FOMC Press Conference': 'FOMC 新闻发布会',
        'Philly Fed Manufacturing Index': '费城联储制造业指数',
        'Unemployment Claims': '初请失业金人数',
        'CB Leading Index m/m': '谘商会领先指标（环比）',
        'Natural Gas Storage': '天然气库存',
        'TIC Long-Term Purchases': 'TIC 长期资本净流入',
        'Bank Holiday': '银行假日',

        # === 欧元区 ===
        'German WPI m/m': '德国批发物价指数（环比）',
        'German Buba President Nagel Speaks': '德国央行行长纳格尔讲话',
        'ECB President Lagarde Speaks': '欧央行行长拉加德讲话',
        'Italian Trade Balance': '意大利贸易帐',
        'Trade Balance': '贸易帐',
        'German ZEW Economic Sentiment': '德国 ZEW 经济景气指数',
        'ZEW Economic Sentiment': '欧元区 ZEW 经济景气指数',
        'Final Core CPI y/y': '核心 CPI 终值（同比）',
        'Final CPI y/y': 'CPI 终值（同比）',
        'Current Account': '经常帐',
        'Spanish 10-y Bond Auction': '西班牙 10 年期国债拍卖',
        'German Buba Monthly Report': '德国央行月度报告',
        'German PPI m/m': '德国 PPI（环比）',

        # === 英国 ===
        'Rightmove HPI m/m': 'Rightmove 房价指数（环比）',
        '10-y Bond Auction': '10 年期国债拍卖',
        'CPI y/y': 'CPI（同比）',
        'Core CPI y/y': '核心 CPI（同比）',
        'PPI Input m/m': 'PPI 投入物价（环比）',
        'PPI Output m/m': 'PPI 产出物价（环比）',
        'RPI y/y': '零售物价指数（同比）',
        'HPI y/y': '房价指数（同比）',
        'Claimant Count Change': '失业金申请人数变化',
        'Average Earnings Index 3m/y': '平均薪资指数（3个月/同比）',
        'Unemployment Rate': '失业率',
        'Monetary Policy Summary': '货币政策摘要',
        'MPC Official Bank Rate Votes': 'MPC 利率投票结果',
        'Official Bank Rate': '央行基准利率',
        'GfK Consumer Confidence': 'GfK 消费者信心指数',
        'Retail Sales m/m': '零售销售（环比）',
        'Public Sector Net Borrowing': '公共部门净借款',
        'GDP m/m': 'GDP（环比）',
        'GDP q/q': 'GDP（环比）',

        # === 日本 ===
        'Tertiary Industry Activity m/m': '第三产业活动指数（环比）',
        'BOJ Policy Rate': '日本央行政策利率',
        'Monetary Policy Statement': '货币政策声明',
        'BOJ Press Conference': '日本央行新闻发布会',
        'Core Machinery Orders m/m': '核心机械订单（环比）',
        'National Core CPI y/y': '全国核心 CPI（同比）',
        'Monetary Policy Meeting Minutes': '货币政策会议纪要',
    }

    events = []
    current_date = None

    for row in rows:
        # 检测日期头行
        # 日期行特征: 短行 (< 300 字符) + 包含 "Mon Jun 15" 格式的月日
        # 三种格式:
        #   <td colspan="10" class="calendar__cell">Sun <span>Jun 14</span></td>
        #   <td class="calendar__cell calendar__date" rowspan="18"><span class="date">Mon <span>Jun 15</span></span></td>
        #   <td class="calendar__cell calendar__date"> <span class="date">Sun <span>Jun 14</span></span> </td>
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

        # 提取货币代码
        curr_match = re.search(r'calendar__currency[^>]*>\s*(\w+)\s*<', row)
        if not curr_match:
            continue
        currency = curr_match.group(1)

        if currency not in currency_country:
            continue

        country_code, country_name = currency_country[currency]

        # 提取事件名称
        ev_match = re.search(r'calendar__event-title\"[^>]*>(.*?)</span>', row)
        if not ev_match:
            continue
        event_name = ev_match.group(1).strip()
        if not event_name:
            continue

        # 翻译为中文
        cn_name = indicator_cn.get(event_name, event_name)

        # 提取时间
        time_match = re.search(r'calendar__time[^>]*>(.*?)</td>', row)
        time_str = ""
        if time_match:
            raw_time = re.sub(r'<[^>]+>', '', time_match.group(1)).strip()
            # 过滤掉非时间内容
            if raw_time and not raw_time.startswith('<'):
                time_str = raw_time

        # 提取影响等级
        impact = 1
        if 'icon--ff-impact-red' in row:
            impact = 4
        elif 'icon--ff-impact-ora' in row:
            impact = 3
        elif 'icon--ff-impact-yel' in row:
            impact = 2

        # 提取 actual / forecast / previous 值
        # 注意: previous 单元格可能在 <span> 前有空格
        actual = forecast = previous = None

        # 方案A: 匹配 <td class="...calendar__actual|forecast|previous...">\s*<span>VALUE</span>\s*</td>
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

        # 生成唯一 ID
        date_clean = current_date.replace("-", "")
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', event_name)[:40]
        event_id = f"{country_code}_FF_{safe_name}_{date_clean}"

        events.append({
            "id": event_id,
            "country": country_code,
            "country_name": country_name,
            "indicator": cn_name,
            "indicator_en": event_name,
            "release_date": current_date,
            "release_time": time_str,
            "timezone": timezone_map.get(country_code, "UTC"),
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
# 数据源2: Investing.com API（备用 — 目前 403）
# ============================================================

def fetch_investing_calendar(start_date=None, end_date=None, countries=None):
    """
    从 Investing.com API 获取经济日历
    目前返回 403 Forbidden — Investing.com 已限制 API 访问
    保留此函数以便将来 API 恢复或使用替代方案
    """
    # 跳过：已知永久性不可用
    return []


# ============================================================
# 数据源3: Trading Economics API（备用 — 目前 410）
# ============================================================

def fetch_trading_economics(country_code="united-states"):
    """
    Trading Economics API
    目前返回 410 Gone — guest 账户已停用，需要付费计划
    保留此函数以便将来使用
    """
    # 跳过：已知永久性不可用
    return []


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
            # 模糊匹配：同日同国 + 相似指标名 → 更新值而非新增
            found = False
            new_ind = new_ev.get("indicator", "")
            new_en = new_ev.get("indicator_en", "")
            new_date = new_ev.get("release_date", "")
            new_country = new_ev.get("country", "")
            for _, ev in existing.items():
                if ev.get("release_date") != new_date or ev.get("country") != new_country:
                    continue
                old_ind = ev.get("indicator", "")
                old_en = ev.get("indicator_en", "")
                # 中英文交叉匹配
                if (new_ind and new_ind in old_ind) or (old_ind and old_ind in new_ind) or \
                   (new_en and new_en in old_en) or (old_en and old_en in new_en) or \
                   (new_en and old_ind and _indicator_similar(new_en, old_ind)):
                    for field in ["actual", "forecast", "previous", "status"]:
                        if new_ev.get(field) is not None:
                            ev[field] = new_ev[field]
                    # 如果现有事件是英文且有中文翻译，更新为中文
                    if not re.search(r'[\u4e00-\u9fff]', ev.get("indicator", "")) and re.search(r'[\u4e00-\u9fff]', new_ind):
                        ev["indicator"] = new_ind
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

    # 更新国家统计
    by_country = {}
    for e in data["events"]:
        cn = e.get("country_name", "")
        by_country[cn] = by_country.get(cn, 0) + 1
    data["meta"]["by_country"] = by_country

    with open(calendar_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return updated, added


def _indicator_similar(en_name, cn_indicator):
    """判断英文指标名是否与中文指标描述同一事件"""
    pairs = [
        ("CPI", "CPI"),
        ("PPI", "PPI"),
        ("GDP", "GDP"),
        ("PMI", "PMI"),
        ("Unemployment", "失业"),
        ("Industrial Production", "工业"),
        ("Retail Sales", "零售"),
        ("Trade Balance", "贸易"),
        ("FOMC", "FOMC"),
        ("Federal Funds", "联邦基金"),
        ("Housing Starts", "新屋开工"),
        ("Building Permits", "营建许可"),
        ("Consumer Confidence", "消费者信心"),
        ("Current Account", "经常帐"),
        ("Monetary Policy", "货币"),
        ("M2", "M2"),
        ("Money Supply", "货币供应"),
    ]
    for en_key, cn_key in pairs:
        if en_key.lower() in en_name.lower() and cn_key in cn_indicator:
            return True
    return False


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    calendar_path = os.path.join(project_dir, "data", "calendar.json")

    all_events = []

    # 主力: ForexFactory HTML 解析
    print("[1/1] ForexFactory HTML 解析...")
    ff_events = fetch_forexfactory()
    print(f"     获取 {len(ff_events)} 条（US/EU/JP/UK）")
    all_events.extend(ff_events)

    # 统计
    if all_events:
        by_country = {}
        for e in all_events:
            cn = e.get("country_name", "??")
            by_country[cn] = by_country.get(cn, 0) + 1
        for cn, cnt in sorted(by_country.items()):
            print(f"     {cn}: {cnt} 条")

        updated, added = merge_into_calendar(all_events, calendar_path)
        print(f"\n结果: 更新 {updated} 条, 新增 {added} 条")
    else:
        print("\n无新数据 — ForexFactory 解析可能因页面变更而失败")
        print("日历保持基于规律推算的版本 + 已有数据")


if __name__ == "__main__":
    main()
