#!/usr/bin/env python3
"""
2026-09-23 修复脚本
1. US_RICHMOND_FED_20260922 回填 actual=-2（6个月首次负值；财联社+Morningstar/WSJ+TE+forexcalendar+TickerSpark 5源✅）
2. EU_PMI_MFG_FLASH 7月/8月日期根治：7/23→7/24、8/24→8/21（wealthbranch+investing HK 双源），
   回填 7月 flash 52.0（fc51.5/prev51.4）、8月 flash 52.8（fc51.8/prev52.0）
3. EU_PMI_MFG_FLASH_20260923 补 fc 52.7（Econoday）/ prev 52.8（8月flash）
4. 新增模式生成的 EU_PMI_SVC_FLASH / EU_PMI_COMPOSITE_FLASH：回填 8月（svc 51.7 / composite 52.1）、
   补 9/23 fc/prev
5. 补录 EU_CONS_CONF_20260922（EC 消费者信心初值 -16.5，fc -16 / prev -15.5，TE 快讯）
6. US_PMI_FLASH_20260923 notes 补分量共识（Econoday：制造 53.8 / 服务 56.0）
7. 同 id 去重（改名目标已被 pattern 生成时合并，防 9/22 踩坑②复现）+ 回读核验
"""
import json
import sys
from datetime import date

sys.path.insert(0, r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\scripts")
from run_daily import generate_js  # noqa: E402

CAL = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\calendar.json"

with open(CAL, encoding="utf-8") as f:
    cal = json.load(f)
events = cal if isinstance(cal, list) else cal.get("events", cal)
print(f"load: {len(events)} events")

by_id = {}
for e in events:
    by_id.setdefault(e["id"], []).append(e)


def get(eid):
    lst = by_id.get(eid, [])
    return lst[0] if lst else None


def rename(old_id, new_id, new_date):
    """改名 + 同步 release_date；若 new_id 已存在（pattern 生成的空版本），把数据合并进后者并删除旧事件"""
    src = get(old_id)
    if src is None:
        print(f"  !! rename: {old_id} 不存在")
        return
    tgt = get(new_id)
    if tgt is not None and tgt is not src:
        # 数据合并：actual/fc/prev/notes/status/time 以有数据的一方为准
        for k in ("actual", "forecast", "previous", "notes", "status", "release_time", "timezone", "unit"):
            sv, tv = src.get(k), tgt.get(k)
            if sv not in (None, "") and (tv in (None, "") or (k in ("actual", "notes") and tv in (None, ""))):
                tgt[k] = sv
        # 事件元字段以源为准补齐缺失
        for k in ("name", "indicator", "country", "country_name", "frequency", "importance", "source"):
            if tgt.get(k) in (None, "") and src.get(k) not in (None, ""):
                tgt[k] = src[k]
        events.remove(src)
        by_id[old_id].remove(src)
        print(f"  rename+merge: {old_id} -> {new_id} (合并数据, 删除旧事件)")
    else:
        src["id"] = new_id
        by_id.setdefault(new_id, []).append(src)
        by_id[old_id].remove(src)
        print(f"  rename: {old_id} -> {new_id}")
    tgt2 = get(new_id)
    tgt2["release_date"] = new_date


# ============ 1. 里士满联储 9/22 回填 ============
e = get("US_RICHMOND_FED_20260922")
if e:
    e["actual"] = -2
    e["forecast"] = 2
    e["status"] = "released"
    e["notes"] = (
        "9月综合 -2（预期2/前4，6个月首次负值、环比-6）；出货 -5（前11）/新订单 -6（前3）/积压 -10（前-7）继续走弱，"
        "就业 7（前-2）转正为最大对冲；未来6个月出货预期 33（前26）/新订单预期 32 仍扩张，但资本开支 -1（前4）、"
        "就业预期 8（前20）明显降温；支付价格涨幅跳升、收取价格温和上行。服务业：营收指数 0（前-8）、需求 2（前3）。"
        "⚠️ 预期分歧大：财联社+forexcalendar 2 / WSJ 4 / TE stream 5，取双源一致的 2。"
        "来源：财联社9/22电+Morningstar(Dow Jones/WSJ调查)+TradingEconomics+forexcalendar.app+TickerSpark 5源✅。"
    )
    print("1. US_RICHMOND_FED_20260922 回填 -2 ✅")
else:
    print("1. !! US_RICHMOND_FED_20260922 缺失")

# ============ 2. EU 制造业 PMI 初值日期根治 + 回填 ============
rename("EU_PMI_MFG_FLASH_20260723", "EU_PMI_MFG_FLASH_20260724", "2026-07-24")
rename("EU_PMI_MFG_FLASH_20260824", "EU_PMI_MFG_FLASH_20260821", "2026-08-21")

e = get("EU_PMI_MFG_FLASH_20260724")
if e:
    e["status"] = "released"
    e["actual"] = 52.0
    e["forecast"] = 51.5
    e["previous"] = 51.4
    e["notes"] = (
        "7月制造业初值 52.0（预期51.5/前值6月终值51.4，连续第4个月扩张）；终值 51.9（8/3发布）。"
        "来源：wealthbranch 日历+investing.com HK 双源✅（2026-09-23 回填）。"
    )
    print("2a. EU_PMI_MFG_FLASH_20260724 回填 52.0 ✅")

e = get("EU_PMI_MFG_FLASH_20260821")
if e:
    e["status"] = "released"
    e["actual"] = 52.8
    e["forecast"] = 51.8
    e["previous"] = 52.0
    e["notes"] = (
        "8月制造业初值 52.8（预期51.8/前值7月初值52.0，超预期+1.0）；终值 52.7（9/1发布）。"
        "来源：wealthbranch 日历+Econoday prior 列 双源✅（investing HK 该行显示 51.8 与两源矛盾，判定为其页面数据错位，弃用）。"
    )
    print("2b. EU_PMI_MFG_FLASH_20260821 回填 52.8 ✅")

# ============ 3. 今日 EU 制造业初值 fc/prev ============
e = get("EU_PMI_MFG_FLASH_20260923")
if e:
    e["forecast"] = 52.7
    e["previous"] = 52.8
    e["notes"] = (
        "今日 16:00 BJS（10:00 CEST）发布 9 月初值；Econoday 共识 52.7（区间51.8-53.0）/ wealthbranch 预期 52.9；"
        "前值 8月初值 52.8（终值 52.7）。今晨执行时未发布，actual 待明晨回填。"
    )
    print("3. EU_PMI_MFG_FLASH_20260923 fc/prev 已填 ✅")

# ============ 4. 新模式事件：svc/composite 回填 + 今日 fc/prev ============
e = get("EU_PMI_SVC_FLASH_20260821")
if e:
    e["status"] = "released"
    e["actual"] = 51.7
    e["previous"] = None
    e["notes"] = "8月服务业初值 51.7（终值 51.6，9/1发布）；前值 7 月初值暂缺待补（本次无来源，禁止编造）。来源：Econoday prior 列（单源，标注⚠️待补第二源）。"
    print("4a. EU_PMI_SVC_FLASH_20260821 回填 51.7 ✅")

e = get("EU_PMI_COMPOSITE_FLASH_20260821")
if e:
    e["status"] = "released"
    e["actual"] = 52.1
    e["forecast"] = 51.7
    e["previous"] = 52.0
    e["notes"] = "8月综合初值 52.1（预期51.7/前值7月初值52.0）；终值 52.0（9/3发布）。来源：investing.com 1491+Econoday prior 列 双源✅。"
    print("4b. EU_PMI_COMPOSITE_FLASH_20260821 回填 52.1 ✅")

e = get("EU_PMI_SVC_FLASH_20260923")
if e:
    e["forecast"] = 51.4
    e["previous"] = 51.7
    e["notes"] = "今日 16:00 BJS 发布 9 月初值；Econoday 共识 51.4（区间51.0-52.0）；前值 8月初值 51.7（终值51.6）。actual 待明晨回填。"
    print("4c. EU_PMI_SVC_FLASH_20260923 fc/prev 已填 ✅")

e = get("EU_PMI_COMPOSITE_FLASH_20260923")
if e:
    e["forecast"] = 51.6
    e["previous"] = 52.1
    e["notes"] = "今日 16:00 BJS 发布 9 月初值；Econoday 共识 51.6（区间51.0-52.5，前值8月终值52.0）；前值字段取 8月初值 52.1。actual 待明晨回填。"
    print("4d. EU_PMI_COMPOSITE_FLASH_20260923 fc/prev 已填 ✅")

# ============ 5. 补录 EC 消费者信心初值 9/22 ============
if get("EU_CONS_CONF_20260922") is None:
    events.append({
        "id": "EU_CONS_CONF_20260922",
        "name": None,
        "country": "EU",
        "country_name": "欧元区",
        "indicator": "消费者信心指数（初值）",
        "indicator_en": "Consumer Confidence Flash",
        "release_date": "2026-09-22",
        "release_time": "16:00",
        "timezone": "CEST",
        "frequency": "月度",
        "importance": 1,
        "source": "European Commission",
        "unit": "",
        "status": "released",
        "actual": -16.5,
        "forecast": -16,
        "previous": -15.5,
        "notes": (
            "9月初值 -16.5（预期-16/前-15.5，差于预期），终结连续4个月改善（8月曾创6个月新高）；"
            "欧盟整体 -15.8（前-15）。官方归因地缘政治不确定性+通胀担忧。"
            "来源：TradingEconomics 快讯（EC flash 口径）单源+发布时点与 TE stream 时序吻合（约22:00 BJS）⚠️建议明日复核第二源。"
        ),
    })
    print("5. EU_CONS_CONF_20260922 补录 -16.5 ✅")
else:
    print("5. EU_CONS_CONF_20260922 已存在")

# ============ 6. 美 PMI 初值今晚分量共识 ============
e = get("US_PMI_FLASH_20260923")
if e:
    e["notes"] = (
        "今晚 21:45 BJS 发布 9 月初值；前值综合 56.0/制造 53.2/服务 56.8（8月初值，8月终值 56.0/53.9/56.5 于 9/3 发布且与共识持平）；"
        "Econoday 分量共识：制造业初值 53.8（区间53.0-54.7）、服务业初值 56.0（区间53.7-56.4），综合未给共识（分量隐含约55.5-56）。"
        "actual 待明晨回填。"
    )
    print("6. US_PMI_FLASH_20260923 notes 已更新 ✅")

# ============ 7. 去重 + 断言 + 回读 ============
seen = {}
dups = []
for ev in events:
    if ev["id"] in seen:
        dups.append(ev["id"])
    seen[ev["id"]] = ev
if dups:
    print(f"!! 仍有重复 id: {dups}")
    raise SystemExit(1)

# prev 链咬合检查：EU mfg flash 7/24 prev(51.4=6月终值) 与 8/21 prev(52.0=7月初值) 语义不同属正常（prev=上月初值）
assert get("EU_PMI_MFG_FLASH_20260821")["previous"] == 52.0
assert get("EU_PMI_MFG_FLASH_20260923")["previous"] == 52.8
assert get("US_RICHMOND_FED_20260922")["actual"] == -2
print("7. 断言通过 ✅")

if isinstance(cal, list):
    out = events
else:
    cal["events"] = events
    out = cal
with open(CAL, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(f"saved calendar.json: {len(events)} events")

generate_js(out)
print("generate_js done")

# 回读核验
with open(CAL, encoding="utf-8") as f:
    chk = json.load(f)
evs2 = chk if isinstance(chk, list) else chk.get("events", chk)
m = {e["id"]: e for e in evs2}
for k in ("US_RICHMOND_FED_20260922", "EU_PMI_MFG_FLASH_20260724", "EU_PMI_MFG_FLASH_20260821",
          "EU_PMI_MFG_FLASH_20260923", "EU_PMI_SVC_FLASH_20260821", "EU_PMI_COMPOSITE_FLASH_20260821",
          "EU_PMI_SVC_FLASH_20260923", "EU_PMI_COMPOSITE_FLASH_20260923", "EU_CONS_CONF_20260922",
          "US_PMI_FLASH_20260923"):
    e = m.get(k)
    print(f"  {k}: status={e['status']} actual={e.get('actual')} fc={e.get('forecast')} prev={e.get('previous')} date={e['release_date']}")
assert "EU_PMI_MFG_FLASH_20260723" not in m and "EU_PMI_MFG_FLASH_20260824" not in m
print("回读核验通过 ✅")
