#!/usr/bin/env python3
"""
每日自动更新脚本
- 基于规律重新推算日历（回溯6个月 + 未来2个月）
- 保留所有已有实际数据（永不覆盖）
- 尝试在线抓取最新结果
- 生成 calendar_data.js 供 Dashboard 加载
- 历史数据永不删除，持续累积
"""

import json
import os
import sys
import subprocess
from datetime import date, datetime, timedelta

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
CALENDAR_FILE = os.path.join(DATA_DIR, "calendar.json")
JS_FILE = os.path.join(DATA_DIR, "calendar_data.js")

sys.path.insert(0, SCRIPTS_DIR)
from generate_calendar import generate_calendar, merge_calendars


def load_calendar():
    if os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"events": [], "meta": {}}


def save_calendar(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_js(data):
    """生成 calendar_data.js 供 HTML 直接加载"""
    js = f"// Auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js += f"window.CALENDAR_DATA = {json.dumps(data, ensure_ascii=False)};"
    with open(JS_FILE, "w", encoding="utf-8") as f:
        f.write(js)


def update_status(events):
    today_str = date.today().strftime("%Y-%m-%d")
    for e in events:
        rd = e.get("release_date", "")
        if e.get("actual") is not None:
            e["status"] = "released"
        elif rd < today_str:
            e["status"] = "pending"
        else:
            e["status"] = "upcoming"
    return events


def main():
    print("=" * 50)
    print("Macro Timeline - Daily Update")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)

    # 1. 推算新日历
    print("\n[1/4] Generating calendar (6mo lookback + 2mo forward)...")
    new_events = generate_calendar(num_months=2, lookback_months=6)
    print(f"  Pattern-generated: {len(new_events)} events")

    # 2. 合并已有数据（永不覆盖）
    print("[2/4] Merging with existing data...")
    existing = load_calendar()
    existing_events = existing.get("events", [])
    merged = merge_calendars(existing_events, new_events)
    print(f"  Merged: {len(merged)} events (preserved all historical data)")

    # 3. 更新状态
    print("[3/4] Updating status...")
    merged = update_status(merged)

    # 统计
    today_str = date.today().strftime("%Y-%m-%d")
    released = [e for e in merged if e.get("status") == "released"]
    upcoming = [e for e in merged if e["release_date"] >= today_str]
    pending = [e for e in merged if e.get("status") == "pending"]
    past_all = [e for e in merged if e["release_date"] < today_str]
    with_forecast = [e for e in upcoming if e.get("forecast") is not None]

    by_country = {}
    for e in merged:
        cn = e.get("country_name", "??")
        by_country[cn] = by_country.get(cn, 0) + 1

    output = {
        "meta": {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_by": "run_daily.py",
            "timezone": "BJS (UTC+8)",
            "total_events": len(merged),
            "upcoming_events": len(upcoming),
            "released_events": len(released),
            "pending_events": len(pending),
            "upcoming_with_forecast": len(with_forecast),
            "historical_events": len(past_all),
            "data_from": min(e["release_date"] for e in merged) if merged else today_str,
            "data_to": max(e["release_date"] for e in merged) if merged else today_str,
            "by_country": by_country,
        },
        "events": merged,
    }

    save_calendar(output)

    # 3.5 模糊匹配注入历史数据（如果修复脚本存在）
    fix_history = os.path.join(SCRIPTS_DIR, "fix_history.py")
    if os.path.exists(fix_history):
        try:
            subprocess.run([sys.executable, fix_history], capture_output=True, timeout=30)
        except Exception:
            pass

    # 重新加载（修复脚本可能更新了数据）
    output = load_calendar()
    generate_js(output)

    print(f"\n{'='*50}")
    print(f"Update Complete!")
    print(f"  Total: {len(merged)} events")
    print(f"  Released (with actuals): {len(released)}")
    print(f"  Historical range: {min(e['release_date'] for e in merged) if merged else 'N/A'} ~ {today_str}")
    print(f"  Upcoming: {len(upcoming)} ({len(with_forecast)} with forecasts)")
    print(f"  Pending: {len(pending)} (past events without data)")
    print(f"  By country: {by_country}")
    print(f"  Data file: {CALENDAR_FILE}")
    print(f"  JS file:   {JS_FILE}")
    print(f"{'='*50}")

    # 今日事件
    today_events = [e for e in merged if e["release_date"] == today_str]
    if today_events:
        print(f"\n[Today] {today_str} releases:")
        for e in today_events:
            stars = "*" * e.get("importance", 1)
            a = f" actual={e['actual']}" if e.get("actual") is not None else ""
            print(f"  {stars} [{e['country_name']}] {e['indicator']}{a}")

    # 明天预告
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    tmr = [e for e in merged if e["release_date"] == tomorrow and e["importance"] >= 2]
    if tmr:
        print(f"\n[Tomorrow] {tomorrow} important releases:")
        for e in tmr[:5]:
            fc = f" forecast={e['forecast']}" if e.get("forecast") is not None else ""
            print(f"  [{e['country_name']}] {e['indicator']}{fc}")

    print("\nDone.")


if __name__ == "__main__":
    main()
