# -*- coding: utf-8 -*-
"""2026-10-06c: 11月 US CPI/PPI 日期核实修正 + 12月事件补建（遗留清单项）。

BLS 官方日程（bls.gov/schedule/news_release/cpi.htm 与 ppi.htm，2026-10-22:00 抓取，一手来源）：
  CPI: 2026年10月数据 → 2026-11-10 08:30 ET；2026年11月数据 → 2026-12-10 08:30 ET
  PPI: 2026年10月数据 → 2026-11-13 08:30 ET；2026年11月数据 → 2026-12-15 08:30 ET

修正（原记录日期未经官方核实，均有误）：
  US_CPI_20261112     11-12 → 11-10（id 同步改）
  US_CORE_CPI_20261112 11-12 → 11-10（id 同步改）
  US_PPI_20261116     11-16 → 11-13（id 同步改）
新建（12月事件此前缺失）：
  US_CPI_20261210 / US_CORE_CPI_20261210 / US_PPI_20261215
铁律：写回后回读断言落盘，"已修改"不验证就是假完成。
"""
import json, copy

CAL = "data/calendar.json"
JS = "data/calendar_data.js"
MARK = "_fix_20261006c"

with open(CAL, encoding="utf-8") as f:
    data = json.load(f)
events = data["events"]
by_id = {e["id"]: e for e in events}

# ---------- 1) 修正 11 月三个事件（release_date + id + 时区） ----------
renames = [
    ("US_CPI_20261112",     "US_CPI_20261110",     "2026-11-10"),
    ("US_CORE_CPI_20261112","US_CORE_CPI_20261110","2026-11-10"),
    ("US_PPI_20261116",     "US_PPI_20261113",     "2026-11-13"),
]
changes = []
for old_id, new_id, new_date in renames:
    e = by_id.get(old_id)
    assert e is not None, f"{old_id} 不存在，中止"
    if e["release_date"] != new_date or e["id"] != new_id:
        old_date = e["release_date"]
        e["release_date"] = new_date
        e["id"] = new_id
        e["timezone"] = "EST"  # 11/1 夏令时已结束
        e["notes"] = (e.get("notes") or "") + (
            f"；BLS官方日历✅(2026-10-06核实): 10月CPI 11/10、10月PPI 11/13 08:30 ET发布，"
            f"原日期{old_date}未经官方核实有误，id {old_id}->{new_id} [{MARK}]")
        changes.append(f"{old_id}: {old_date}->{new_date} (id->{new_id})")

by_id = {e["id"]: e for e in events}

# ---------- 2) 新建 12 月事件 ----------
def make(id_, indicator, indicator_en, importance, date):
    return {
        "id": id_, "country": "US", "country_name": "美国",
        "indicator": indicator, "indicator_en": indicator_en,
        "frequency": "月度", "importance": importance,
        "release_date": date, "release_time": "08:30", "timezone": "EST",
        "period": "2026-11", "source": "Bureau of Labor Statistics",
        "source_url": "", "unit": "%", "status": "upcoming",
        "notes": ("BLS官方日历✅(2026-10-06核实): 11月CPI 2026-12-10、11月PPI 2026-12-15 08:30 ET发布；"
                  "prev=10月值（11/10、11/13发布后回填） [" + MARK + "]"),
    }

new_defs = [
    ("US_CPI_20261210",      "CPI 消费者物价指数（同比）", "CPI YoY", 3, "2026-12-10"),
    ("US_CORE_CPI_20261210", "核心CPI（同比）",            "Core CPI YoY", 3, "2026-12-10"),
    ("US_PPI_20261215",      "PPI 生产者物价指数（同比）", "PPI YoY", 2, "2026-12-15"),
]
for id_, ind, ind_en, imp, date in new_defs:
    if id_ not in by_id:
        ne = make(id_, ind, ind_en, imp, date)
        events.append(ne)
        by_id[id_] = ne
        changes.append(f"ADD {id_} ({date})")
    else:
        print(f"[SKIP] {id_} 已存在")

# ---------- 3) 写回 + 回读断言 ----------
if changes:
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(JS, "w", encoding="utf-8") as f:
        f.write(f"window.CALENDAR_DATA = {json.dumps(data, ensure_ascii=False)};")
    print(f"共 {len(changes)} 处修改已写回（calendar.json + calendar_data.js）")
    for c in changes:
        print("  -", c)
else:
    print("无修改（幂等命中）")

with open(CAL, encoding="utf-8") as f:
    rd = {e["id"]: e for e in json.load(f)["events"]}
for old_id, new_id, new_date in renames:
    assert old_id not in rd, f"断言失败: {old_id} 仍存在"
    assert new_id in rd, f"断言失败: {new_id} 未落盘"
    assert rd[new_id]["release_date"] == new_date, f"断言失败: {new_id} 日期错"
for id_, _, _, _, date in new_defs:
    assert rd[id_]["release_date"] == date, f"断言失败: {id_} 日期错"
with open(JS, encoding="utf-8") as f:
    jstxt = f.read()
assert MARK in jstxt, "断言失败: calendar_data.js 未更新"
assert "US_CPI_20261210" in jstxt and "US_PPI_20261113" in jstxt
print("回读验证 ALL OK")

n = len(rd)
st = {}
for e in rd.values():
    st[e.get("status", "?")] = st.get(e.get("status", "?"), 0) + 1
print(f"总事件数 {n}；状态分布 {st}")
