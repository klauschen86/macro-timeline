#!/usr/bin/env python3
"""2026-09-22 二次修复：id↔release_date 同步 + 去重 + 补回被 rerun 覆盖的值"""
import json
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(PROJECT, "data", "calendar.json")

cal = json.load(open(CAL, encoding="utf-8"))
events = cal["events"]
log = []

# 1. 去重：同 id 保留信息最全的（actual/notes 优先）
best = {}
order = []
for e in events:
    eid = e["id"]
    if eid not in best:
        best[eid] = e
        order.append(eid)
    else:
        cur = best[eid]
        def score(x):
            return (x.get("actual") is not None, bool(x.get("notes")), x.get("status") == "released")
        if score(e) > score(cur):
            best[eid] = e
        log.append(f"DEDUP remove one copy of {eid}")
events = [best[k] for k in order]

# 2. release_date 与 id 后缀同步（仅模式类 id：KEY_YYYYMMDD）
import re
for e in events:
    m = re.match(r"^(.+)_(\d{8})$", e["id"])
    if m:
        d = f"{m.group(2)[:4]}-{m.group(2)[4:6]}-{m.group(2)[6:]}"
        if e.get("release_date") != d:
            log.append(f"RDATE sync {e['id']}: {e.get('release_date')} -> {d}")
            e["release_date"] = d

def refill(eid, **fields):
    e = best.get(eid)
    if not e:
        log.append(f"MISS refill {eid}")
        return
    changed = False
    for k, v in fields.items():
        if k == "notes_append":
            if v not in (e.get("notes") or ""):
                e["notes"] = (e.get("notes") or "") + v
                changed = True
        else:
            if e.get(k) != v:
                e[k] = v
                changed = True
    if changed:
        log.append(f"REFILL {eid}")

# 3. 补回被 rerun 覆盖的值（官方源）
refill("CN_PMI_MFG_20260331", actual=50.4, previous=49.0, status="released",
       notes_append="2026-03 制造业PMI 50.4（NBS 英文月报表 2源✅，2026-09-22 审计回填）。")
refill("CN_PMI_MFG_20260630", actual=50.3, previous=50.0, status="released",
       notes_append="2026-06 制造业PMI 50.3 重返扩张（+0.3pp；NBS 解读页 t20260630_1964033+新华网+央视网+gov.cn 4源✅）。")
refill("CN_PMI_NONMFG_20260630", actual=50.2, previous=50.1, status="released",
       notes_append="2026-06 非制造业 50.2（+0.1pp；NBS 解读页+新华网 4源✅）。")

cal["events"] = events
json.dump(cal, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(log) if log else "NO CHANGES")
print(f"Total events: {len(events)}")
