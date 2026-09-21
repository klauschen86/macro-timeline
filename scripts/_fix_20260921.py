#!/usr/bin/env python3
"""
_fix_20260921.py — LPR 全系列根治（2026-09-21）
1. 删除陈旧 CN_LPR_*_20260921 事件（模式按周末顺延误排，实际 9/20 周日发布，5源核实）
2. 回填 CN_LPR_*_20260920 actual/forecast/prev（1Y 3.0 / 5Y+ 3.5，连续16个月不变）
3. 历史日期修正：20260622→20260620（6/20 周六照发）、20251222→20251220（12/20 周六）
4. 历史链污染修正：2026-01~05 actual 3.1/3.6 → 3.0/3.5
   （多源确认：LPR 上次调整为 2025-05 各下调10bp，即 3.10→3.00 / 3.60→3.50，
     此后连续16个月不变至 2026-09；3.1/3.6 为降息前旧值误录）
5. 2026-10/11 prev 链咬合 + 全系列 release_time 统一 09:00
   （PBOC 官网 2024-07-22 公告：发布时间 9:15→9:00）
"""
import json
import os

CAL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "calendar.json")

with open(CAL, encoding="utf-8") as f:
    cal = json.load(f)
events = cal["events"] if isinstance(cal, dict) else cal

NOTES_920 = ("2026年9月LPR：1年期3.0%、5年期以上3.5%，连续16个月不变（上次调整为2025-05各下调10bp）。"
             "符合市场预期（定价锚7天逆回购1.40%稳定；Q2末商业银行净息差1.41%仍处低位，报价行压缩加点动力不足）。"
             "实际发布日9/20（周日）09:00——LPR每月20日发布，遇法定节假日顺延、周末不顺延"
             "（PBOC官网2024-07-22公告：发布时间由9:15调整为9:00）。"
             "来源：央广网9/20+中国经济网+新浪财经/环球网+东财债市早参+forexhsn 5源✅（均引央行授权全国银行间同业拆借中心）。"
             "交叉验证：MCP宏观工具连续第20天未暴露，以多源Web官方口径替代双源✅；westock CLI LPR数据为空值不可用。")

by_id = {e["id"]: e for e in events}

changed = []

# 1) 删除陈旧 20260921 事件
for old in ("CN_LPR_1Y_20260921", "CN_LPR_5Y_20260921"):
    if old in by_id:
        del by_id[old]
        changed.append(f"DEL {old}")

# 2) 回填 20260920
for eid, actual, fc, prev in (
    ("CN_LPR_1Y_20260920", 3.0, 3.0, 3.0),
    ("CN_LPR_5Y_20260920", 3.5, 3.5, 3.5),
):
    e = by_id.get(eid)
    assert e is not None, f"missing {eid}"
    e.update(actual=actual, forecast=fc, previous=prev, status="released",
             release_date="2026-09-20", release_time="09:00", notes=NOTES_920)
    changed.append(f"FILL {eid} actual={actual} fc={fc} prev={prev}")

# 3) 历史日期改名（周末照发规则）
renames = {
    "CN_LPR_1Y_20260622": "CN_LPR_1Y_20260620",
    "CN_LPR_5Y_20260622": "CN_LPR_5Y_20260620",
    "CN_LPR_1Y_20251222": "CN_LPR_1Y_20251220",
    "CN_LPR_5Y_20251222": "CN_LPR_5Y_20251220",
}
for old, new in renames.items():
    if old in by_id:
        assert new not in by_id, f"rename target exists: {new}"
        e = by_id.pop(old)
        e["id"] = new
        e["release_date"] = new.split("_")[-1][:4] + "-" + new.split("_")[-1][4:6] + "-" + new.split("_")[-1][6:]
        e["release_time"] = "09:00"
        by_id[new] = e
        changed.append(f"RENAME {old} -> {new} ({e['release_date']})")

# 4) 历史链污染修正 + 缺口回填（2025-12 ~ 2026-09 全部 3.0/3.5）
chain = [
    ("CN_LPR_1Y_20251220", 3.0), ("CN_LPR_5Y_20251220", 3.5),
    ("CN_LPR_1Y_20260120", 3.0), ("CN_LPR_5Y_20260120", 3.5),
    ("CN_LPR_1Y_20260220", 3.0), ("CN_LPR_5Y_20260220", 3.5),
    ("CN_LPR_1Y_20260320", 3.0), ("CN_LPR_5Y_20260320", 3.5),
    ("CN_LPR_1Y_20260420", 3.0), ("CN_LPR_5Y_20260420", 3.5),
    ("CN_LPR_1Y_20260520", 3.0), ("CN_LPR_5Y_20260520", 3.5),
    ("CN_LPR_1Y_20260620", 3.0), ("CN_LPR_5Y_20260620", 3.5),
    ("CN_LPR_1Y_20260720", 3.0), ("CN_LPR_5Y_20260720", 3.5),
]
for eid, val in chain:
    e = by_id.get(eid)
    if e is None:
        continue
    fixes = []
    if e.get("actual") != val:
        fixes.append(f"actual {e.get('actual')}->{val}")
        e["actual"] = val
    if e.get("previous") != val:
        fixes.append(f"prev {e.get('previous')}->{val}")
        e["previous"] = val
    if e.get("status") != "released":
        fixes.append(f"status {e.get('status')}->released")
        e["status"] = "released"
    if e.get("release_time") != "09:00":
        fixes.append(f"time {e.get('release_time')}->09:00")
        e["release_time"] = "09:00"
    if fixes:
        changed.append(f"FIX {eid}: " + "; ".join(fixes))

# 5) 未来事件 prev 链 + release_time
for eid, prev in (("CN_LPR_1Y_20261020", 3.0), ("CN_LPR_5Y_20261020", 3.5),
                  ("CN_LPR_1Y_20261120", 3.0), ("CN_LPR_5Y_20261120", 3.5)):
    e = by_id.get(eid)
    if e:
        e["previous"] = prev
        e["release_time"] = "09:00"
        changed.append(f"PREV {eid} prev={prev}")

# 12月 override 事件若已被生成器按 DATE_OVERRIDES 产出（12/20 周日）无 prev，补上
for eid, prev in (("CN_LPR_1Y_20261220", 3.0), ("CN_LPR_5Y_20261220", 3.5)):
    e = by_id.get(eid)
    if e and not e.get("previous"):
        e["previous"] = prev
        e["release_time"] = "09:00"
        changed.append(f"PREV {eid} prev={prev}")

cal["events"] = list(by_id.values())
# 按 release_date 排序保持稳定
cal["events"].sort(key=lambda x: (x.get("release_date", ""), x.get("id", "")))
if isinstance(cal, dict) and "generated_at" in cal:
    cal["generated_at"] = cal.get("generated_at")

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

print(f"Total events: {len(cal['events'])}")
for c in changed:
    print(" ", c)
print(f"\n{len(changed)} changes applied.")
