#!/usr/bin/env python3
"""2026-11-10: 还原 mcp_inject 覆盖的 17 个历史事件（第4次同型污染拦截）。
HEAD 为准，保留 4 条 2027-01 窗口扩展新事件。写盘后回读 assert。"""
import json, subprocess, sys

PROJ = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"
PATH = PROJ + r"\data\calendar.json"

head = json.loads(subprocess.check_output(
    ["git", "show", "HEAD:data/calendar.json"], cwd=PROJ).decode("utf-8"))
head_events = head["events"] if isinstance(head, dict) else head
cur = json.load(open(PATH, encoding="utf-8"))
cur_events = cur["events"] if isinstance(cur, dict) else cur

def key(e):
    return e.get("id") or (e.get("country", "") + e.get("name", ""))

head_by = {key(e): e for e in head_events}
restored = []
changed = False
for i, e in enumerate(cur_events):
    k = key(e)
    he = head_by.get(k)
    if he is not None and e != he:
        cur_events[i] = he
        restored.append(k)
        changed = True

if not changed:
    print("no pollution found, nothing to do")
    sys.exit(0)

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(cur, f, ensure_ascii=False, indent=2)

# 写盘后回读 assert
chk = json.load(open(PATH, encoding="utf-8"))
chk_events = chk["events"] if isinstance(chk, dict) else chk
chk_by = {key(e): e for e in chk_events}
bad = [k for k in restored if chk_by.get(k) != head_by[k]]
assert not bad, f"RESTORE FAILED: {bad}"
print(f"restored {len(restored)} events to HEAD state:")
for k in restored:
    print(" ", k)
# 最终 diff 校验
mods = sum(1 for e in chk_events if key(e) in head_by and e != head_by[key(e)])
news = sum(1 for e in chk_events if key(e) not in head_by)
print(f"final diff vs HEAD: MOD={mods} (must be 0), NEW={news}")
assert mods == 0
