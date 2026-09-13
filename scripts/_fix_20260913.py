# -*- coding: utf-8 -*-
"""
_fix_20260913.py — 2026-09-13（周日）数据质量补课（今日无新发布）
1) 美CPI 2026 全年历史链审计修正（多源：东方证券研报/国联民生研报分项表/证券时报/央广网/新华财经/JEC）：
   - 2月(3/11发布) CPI 2.4/核心2.5；1月 CPI 2.4/核心2.5（JEC 2.39/2.50）
   - 3月 CPI 3.3/核心2.6；4月 CPI 3.8/核心2.8（环比0.6曾被误录为actual）；5月 CPI 4.2/核心2.9；6月 CPI 3.5/核心2.6（原缺失）
   - 2月事件日期 3/12→3/11（3源确认）+ id 改名
2) 中国金融数据回填：
   - 7月（8/14发布，金融时报+智汇研Wind双源）：M2 7.7、社融当月 14017亿、新增贷款 -3400亿 + id 改名 8/12→8/14
   - 6月（7/15发布，央行上半年报告+北大国民经济研究中心+腾讯证券多源）：M2 8.0、社融 33645亿、新增贷款 16100亿
   - 9/14 三事件 prev 预填 + 发布窗口顺延备注
3) 格式污染清理（"8.6%"/"520B" 等）
"""
import json, io, sys

CAL = "data/calendar.json"
data = json.load(open(CAL, encoding="utf-8"))
events = data["events"]
by_id = {e["id"]: e for e in events}

def rename(old, new, new_date):
    e = by_id.get(old)
    if not e:
        print(f"  !! rename 跳过（不存在）: {old}")
        return None
    e["id"] = new
    e["release_date"] = new_date
    by_id.pop(old)
    by_id[new] = e
    print(f"  rename: {old} -> {new} (date={new_date})")
    return e

def upd(eid, **kw):
    e = by_id.get(eid)
    if not e:
        print(f"  !! upd 跳过（不存在）: {eid}")
        return
    notes_add = kw.pop("notes_add", None)
    for k, v in kw.items():
        e[k] = v
    if notes_add:
        e["notes"] = ((e.get("notes") or "") + " | " + notes_add).strip(" |")
    print(f"  upd: {eid} -> {kw}")

print("[1] id 改名 + 日期修正")
rename("US_CPI_20260312", "US_CPI_20260311", "2026-03-11")
rename("US_CORE_CPI_20260312", "US_CORE_CPI_20260311", "2026-03-11")
rename("CN_M2_20260812", "CN_M2_20260814", "2026-08-14")
rename("CN_SOCIAL_FINANCING_20260812", "CN_SOCIAL_FINANCING_20260814", "2026-08-14")
rename("CN_NEW_LOANS_20260812", "CN_NEW_LOANS_20260814", "2026-08-14")

print("[2] 美CPI 2026 历史链修正（多源✅）")
# 1月数据（2/12发布）
upd("US_CPI_20260212", actual=2.4, previous=None, status="released",
    notes_add="2026-09-13审计修正: actual原2.6误录→2.4(JEC 2.39+新华财经'与前月一致'双源)")
upd("US_CORE_CPI_20260212", actual=2.5, previous=None, status="released",
    notes_add="2026-09-13审计修正: actual原3.1误录→2.5(JEC 2.50)")
# 2月数据（3/11发布，改名后）
upd("US_CPI_20260311", actual=2.4, previous=2.4, status="released",
    notes_add="2026-09-13审计修正: 日期3/12→3/11(央广网/新华财经3源)、actual原2.6误录→2.4(5源)")
upd("US_CORE_CPI_20260311", actual=2.5, previous=2.5, status="released",
    notes_add="2026-09-13审计修正: actual原3.0误录→2.5(5源)")
# 3月数据（4/13发布）
upd("US_CPI_20260413", actual=3.3, previous=2.4, status="released",
    notes_add="2026-09-13审计修正: actual原2.5误录→3.3(国联民生研报3.3+东方证券,能源+12.5%拉动)")
upd("US_CORE_CPI_20260413", actual=2.6, previous=2.5, status="released",
    notes_add="2026-09-13审计修正: actual原3.0误录→2.6(国联民生+东方证券双源)")
# 4月数据（5/12发布）
upd("US_CPI_20260512", actual=3.8, previous=3.3, forecast=3.7, status="released",
    notes_add="2026-09-13审计修正: 原0.6/0.9系环比污染→同比3.8(证券时报:预期3.7,环比0.6,能源+17.9%)")
upd("US_CORE_CPI_20260512", actual=2.8, previous=2.6, forecast=2.7, status="released",
    notes_add="2026-09-13审计修正: 原0.6系环比污染→同比2.8(证券时报:预期2.7,创2025-09来新高)")
# 5月数据（6/12发布）
upd("US_CPI_20260612", actual=4.2, previous=3.8, status="released",
    notes_add="2026-09-13审计修正: actual原2.7误录→4.2(东方证券+国联民生双源,能源+23.5%见顶)")
upd("US_CORE_CPI_20260612", actual=2.9, previous=2.8, status="released",
    notes_add="2026-09-13审计修正: actual原3.2误录→2.9(双源)")
# 6月数据（7/13发布，原缺失）
upd("US_CPI_20260713", actual=3.5, previous=4.2, status="released",
    notes_add="2026-09-13审计回填: 6月CPI 3.5%(东方证券+国联民生双源,油价回落后回落)")
upd("US_CORE_CPI_20260713", actual=2.6, previous=2.9, status="released",
    notes_add="2026-09-13审计回填: 核心2.6%(双源)")
# 7月数据 prev 修正
upd("US_CPI_20260812", previous=3.5,
    notes_add="2026-09-13审计: prev原0.2污染→3.5(6月)")
upd("US_CORE_CPI_20260812", previous=2.6,
    notes_add="2026-09-13审计: prev原0.2污染→2.6(6月)")

print("[3] 中国金融数据回填")
# 6月数据（7/15发布）
upd("CN_M2_20260713", actual=8.0, previous=7.2, forecast=8.5, status="released",
    notes_add="2026-09-13回填: 6月末M2同比8.0%(央行上半年报告,中新网/金融新闻网/人民网多源;prev/fc原'8.6%'/'8.5%'格式污染已清理)")
upd("CN_SOCIAL_FINANCING_20260713", actual=33645, previous=None, status="released",
    notes_add="2026-09-13回填: 6月新增社融33645亿(北大国民经济研究中心+腾讯证券双源,与H1累计20.84万亿自洽;1-5月日历链23.05万亿≠官方17.48万亿,历史链审计待办)")
upd("CN_NEW_LOANS_20260713", actual=16100, previous=14800, forecast=19500, status="released",
    notes_add="2026-09-13回填: 6月新增贷款1.61万亿(双源,'逊于预期';prev原'520B'污染已清理)")
# 7月数据（8/14发布）
upd("CN_M2_20260814", actual=7.7, previous=8.0, status="released",
    notes_add="2026-09-13回填: 7月末M2同比7.7%(金融时报8/14+广发9/1研报双源;发布日8/12→8/14已修正)")
upd("CN_SOCIAL_FINANCING_20260814", actual=14017, previous=33645, status="released",
    notes_add="2026-09-13回填: 7月新增社融14017亿(智汇研Wind表+金融时报前7月累计自洽)")
upd("CN_NEW_LOANS_20260814", actual=-3400, previous=16100, status="released",
    notes_add="2026-09-13回填: 7月金融机构新增贷款-3400亿(罕见负增,智汇研Wind表;票据冲量退潮+需求弱)")

print("[4] 9/14 三事件 prev 预填 + 窗口顺延")
upd("CN_M2_20260914", previous=7.7,
    notes_add="2026-09-13: 9/12-13周末未发布(FXStreet预告9/12落空),窗口顺延9/14-9/15;prev=7月7.7%已预填")
upd("CN_SOCIAL_FINANCING_20260914", previous=14017,
    notes_add="2026-09-13: 窗口顺延9/14-9/15;市场预期:社融~1.94-2.36万亿/C50中值1.94万亿,已预填prev=7月14017亿")
upd("CN_NEW_LOANS_20260914", previous=-3400,
    notes_add="2026-09-13: 窗口顺延9/14-9/15;市场预期:新增信贷~0.41-0.75万亿/C50中值0.11万亿,prev=7月-3400亿已预填")

json.dump(data, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nDone. events={len(events)}")
