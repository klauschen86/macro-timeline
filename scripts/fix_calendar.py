#!/usr/bin/env python3
"""
修复 generate_calendar.py 中的关键函数
—— 扩展历史、永不覆盖数据、保留所有旧事件
"""
import sys, os, re

filepath = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\scripts\generate_calendar.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------
# Fix 1: 扩展历史回溯从 30 天 → 180 天
# -------------------------------------------------------
old_cutoff = "cutoff = today - timedelta(days=30)"
new_cutoff = "cutoff = today - timedelta(days=180)"
content = content.replace(old_cutoff, new_cutoff)

# -------------------------------------------------------
# Fix 2: 重写 merge_calendars — 保留所有旧事件 + 永不覆盖数据
# -------------------------------------------------------
old_merge = '''def merge_calendars(existing_events, new_events):
    """合并日历：保留已有事件的状态（特别是手动更新过的结果）"""
    existing_map = {e["id"]: e for e in existing_events}
    merged = []
    for new_event in new_events:
        eid = new_event["id"]
        if eid in existing_map:
            # 保留已有状态
            old = existing_map[eid]
            new_event["status"] = old.get("status", "upcoming")
            new_event["forecast"] = old.get("forecast")
            new_event["previous"] = old.get("previous")
            new_event["actual"] = old.get("actual")
            new_event["notes"] = old.get("notes", "")
        else:
            new_event["status"] = "upcoming"
        merged.append(new_event)
    return merged'''

new_merge = '''def merge_calendars(existing_events, new_events):
    """合并日历：保留已有事件的所有数据，永不覆盖 actual/forecast/previous"""
    existing_map = {e["id"]: e for e in existing_events}
    merged_ids = set()
    merged = []

    # 第一步：处理新事件（基于规则生成的），保留已有数据
    for new_event in new_events:
        eid = new_event["id"]
        merged_ids.add(eid)
        if eid in existing_map:
            old = existing_map[eid]
            # 核心铁律：如果 old 有 actual/forecast/previous，绝不能覆盖
            for field in ("actual", "forecast", "previous"):
                old_val = old.get(field)
                if old_val is not None and old_val != "":
                    new_event[field] = old_val
            # 状态：保留旧状态（released > pending > upcoming）
            old_status = old.get("status", "")
            if old_status in ("released", "pending"):
                new_event["status"] = old_status
            elif new_event.get("actual") is not None:
                new_event["status"] = "released"
            else:
                new_event["status"] = old_status if old_status else "upcoming"
            # 保留备注
            new_event["notes"] = old.get("notes", "")
        else:
            # 新事件，设为 upcoming
            new_event["status"] = "upcoming"
        merged.append(new_event)

    # 第二步：保留旧日历中不在新日历的事件（它们是已经收集的历史数据）
    for eid, old_event in existing_map.items():
        if eid not in merged_ids:
            merged.append(old_event)

    # 按日期排序
    merged.sort(key=lambda e: e.get("release_date", ""))

    return merged'''

content = content.replace(old_merge, new_merge)

# -------------------------------------------------------
# Fix 3: generate_calendar 也要生成历史月份的事件
# -------------------------------------------------------
old_gen = '''def generate_calendar(num_months=3):
    """生成未来N个月的宏观数据日历"""
    today = date.today()
    events = []

    # 计算需要覆盖的月份范围
    start_month = today.replace(day=1)
    end_month = (today.replace(day=28) + timedelta(days=4 * 31)).replace(day=1)
    end_month = (end_month.replace(day=28) + timedelta(days=(num_months - 3) * 31)).replace(day=1)'''

new_gen = '''def generate_calendar(num_months=3, lookback_months=6):
    """生成未来N个月 + 回顾lookback_months个月的宏观数据日历"""
    today = date.today()
    events = []

    # 计算需要覆盖的月份范围：从 lookback_months 个月前开始
    start_month = today.replace(day=1)
    for _ in range(lookback_months):
        start_month = (start_month.replace(day=1) - timedelta(days=1)).replace(day=1)
    end_month = (today.replace(day=28) + timedelta(days=4 * 31)).replace(day=1)
    end_month = (end_month.replace(day=28) + timedelta(days=(num_months - 3) * 31)).replace(day=1)'''

content = content.replace(old_gen, new_gen)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("generate_calendar.py 已修复:")
print("  1. 历史回溯: 30天 → 180天")
print("  2. merge_calendars: 保留所有旧事件 + 永不覆盖数据")
print("  3. generate_calendar: 支持 lookback_months 参数")
