#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-23 批次数据层操作（不改 run_daily/mcp_inject 逻辑）：
1) EU PMI 初值×3 预填（今晚发布）+ period 2026-11 + 发布时间冬令时 17:00 BJS
2) US_CONSUMER_CONF_20261124 预填 fc 92.1/prev 91.7（双源✅）
3) LPR×2 / JP_CPI_20261120 notes 去重（另一环境回填脚本产生 ×4 重复段）
4) 仅重生成 calendar_data.js，不再跑 run_daily merge"""
import json, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")

cal = json.load(open(CAL, encoding="utf-8"))
events = cal["events"]
by_id = {e["id"]: e for e in events}
n_changed = 0

# ---- 1. EU PMI flash ×3 预填 ----
eu_fixes = {
    "EU_PMI_MFG_FLASH_20261123": ("制造业PMI", 52.4, 52.7,
        "fc 52.4(forexcracked 单源⚠️)/prev 52.7(10月终值, mw801纵横汇海+forexcracked 双源✅; 10月初值52.4已录于EU_PMI_MFG_FLASH_20261023)"),
    "EU_PMI_SVC_FLASH_20261123": ("服务业PMI", 49.9, 51.4,
        "fc 49.9(forexcracked 单源⚠️, 较前值回落明显)/prev 51.4(10月终值双源✅; 10月初值51.7已录10-23事件)"),
    "EU_PMI_COMPOSITE_FLASH_20261123": ("综合PMI", 51.0, 51.7,
        "fc 51.0(forexcracked 单源⚠️)/prev 51.7(10月终值双源✅; 10月初值51.9已录10-23事件)"),
}
TIME_NOTE = ("【2026-11-23日期/时间标注】发布时间口径: S&P Global 伦敦上午发布随冬夏令时切换 BJS(夏16:00/冬17:00)——"
             "10-23批三源定为16:00(夏令时), 本批 mw801(17:00 BJS)+forexcracked(09:00 UTC)双源定为冬令时17:00, 两批自洽; "
             "run_daily 模式每次重置回10:00, 以本标注为准(数据层根治, 锁禁改脚本)。")
for eid, (nm, fc, pv, src) in eu_fixes.items():
    e = by_id[eid]
    e["period"] = "2026-11"
    e["forecast"] = fc
    e["previous"] = pv
    e["release_time"] = "17:00"
    pre = f"【2026-11-23预填】11月{nm}初值今晚发布(BJS 17:00, 口径见日期标注); {src}。| "
    e["notes"] = pre + TIME_NOTE
    n_changed += 1
    print(f"[预填] {eid}: fc={fc} prev={pv} period=2026-11 time=17:00")

# ---- 2. US_CONSUMER_CONF_20261124 预填 ----
e = by_id["US_CONSUMER_CONF_20261124"]
e["forecast"] = 92.1
e["previous"] = 91.7
e["notes"] = ("【2026-11-23预填】明日(11-24)23:00 BJS发布(冬令时 EST 10:00 = 23:00 BJS); "
              "fc 92.1/prev 91.7(中国能源网《环球下周看点》+investing.com 双源✅)。"
              "10月91.7大超预期80.4(已录US_CONSUMER_CONF_20261027, 9月修订值84.2), 高基数下11月共识仅微升。")
n_changed += 1
print(f"[预填] US_CONSUMER_CONF_20261124: fc=92.1 prev=91.7")

# ---- 3. notes 去重（保留首段+预填段, 压缩重复的回填段） ----
def dedupe_notes(notes):
    segs = [s.strip() for s in notes.split(" | ") if s.strip()]
    seen, out = set(), []
    for s in segs:
        key = s[:60]
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return " | ".join(out)

for eid in ["CN_LPR_1Y_20261120", "CN_LPR_5Y_20261120", "JP_CPI_20261120", "US_JOBLESS_CLAIMS_20261119"]:
    e = by_id[eid]
    before = len(e.get("notes") or "")
    e["notes"] = dedupe_notes(e.get("notes") or "")
    after = len(e["notes"])
    if before != after:
        n_changed += 1
    print(f"[去重] {eid}: notes {before} -> {after} chars")

# ---- 保存 + 仅重生成 JS ----
json.dump(cal, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
# 回读校验
chk = json.load(open(CAL, encoding="utf-8"))
assert {e["id"]: e for e in chk["events"]}["EU_PMI_COMPOSITE_FLASH_20261123"]["period"] == "2026-11"
assert {e["id"]: e for e in chk["events"]}["US_CONSUMER_CONF_20261124"]["forecast"] == 92.1

sys.path.insert(0, os.path.join(BASE, "scripts"))
from run_daily import generate_js, load_calendar
generate_js(load_calendar())
print(f"\nDone: {n_changed} events changed; calendar_data.js regenerated (未跑 run_daily merge, 防止 pattern 重置).")
