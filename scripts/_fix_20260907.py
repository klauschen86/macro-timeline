# -*- coding: utf-8 -*-
"""
2026-09-07 数据补录与修复脚本
数据源：国家外汇管理局官方月度增减链（中经网 2026-08-07 报道）+ SAFE 官方储备资产表
        + 光明网/人民网/中国经济网/央广网 5 源交叉验证（7 月末外储 34188 亿 / 黄金 7608 万盎司）
        + Trading Economics（欧元区 Q2 GDP 终值 9/7 发布，consensus 环比 0.4%）

修复内容：
1. CN_FX_RESERVES 系列：1-3 月 act 值错误（32170/32170/32280 vs 官方 33579/33991/34278）全链修正；
   4-7 月 pending 回填 released；今日 9/7 事件补 previous=34188
2. CN_GOLD_RESERVES 系列（generate_calendar.py 新增模式生成）：2-8 月历史 actual 回填；今日事件补 previous=7608
3. 新增 EU_GDP_20260907（欧元区 Q2 GDP 环比终值，TE 确认今日 11:00 CET 发布）
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAL = ROOT / "data" / "calendar.json"

with open(CAL, encoding="utf-8") as f:
    cal = json.load(f)

events = {ev["id"]: ev for ev in cal["events"]}
changes = []


def set_field(ev, field, value, tag):
    old = ev.get(field)
    if old != value:
        ev[field] = value
        changes.append(f"  [{tag}] {ev['id']}.{field}: {old!r} -> {value!r}")


# ---------- 1. 外汇储备全链修正/回填（官方增减链，单位亿美元，取整） ----------
# 官方链条：2025年12月末=33578.69(推算) -> 1月+412.09 -> 2月+287.29 -> 3月-856.84
#           -> 4月+684.24 -> 5月+316.91 -> 6月-259.76 -> 7月+25.14
# SAFE 表锚点：2026.01=33990.78 / 02=34278.07 / 03=33421.23 / 04=34105.47（与链条逐月验算完全吻合）
fx_chain = {
    "CN_FX_RESERVES_20260107": {"actual": 33579, "prev_src": None},   # 2025-12 月末（推算值）
    "CN_FX_RESERVES_20260209": {"actual": 33991, "previous": 33579},  # 2026-01 月末（SAFE 官方）
    "CN_FX_RESERVES_20260309": {"actual": 34278, "previous": 33991},  # 2026-02 月末（SAFE 官方）
    "CN_FX_RESERVES_20260407": {"actual": 33421, "previous": 34278},  # 2026-03 月末（SAFE 官方）
    "CN_FX_RESERVES_20260507": {"actual": 34105, "previous": 33421},  # 2026-04 月末（SAFE 官方）
    "CN_FX_RESERVES_20260608": {"actual": 34422, "previous": 34105},  # 2026-05 月末（官方增减推算 34422.38）
    "CN_FX_RESERVES_20260707": {"actual": 34163, "previous": 34422},  # 2026-06 月末（中经网官方 34162.62）
    "CN_FX_RESERVES_20260807": {"actual": 34188, "previous": 34163},  # 2026-07 月末（5 源官方 34187.76）
}
for eid, upd in fx_chain.items():
    ev = events.get(eid)
    if not ev:
        changes.append(f"  [MISS] {eid} 不存在，跳过")
        continue
    set_field(ev, "actual", upd["actual"], "FX")
    if upd.get("previous") is not None:
        set_field(ev, "previous", upd["previous"], "FX")
    set_field(ev, "status", "released", "FX")

ev_today_fx = events.get("CN_FX_RESERVES_20260907")
if ev_today_fx:
    set_field(ev_today_fx, "previous", 34188, "FX")
    ev_today_fx["notes"] = "8月末数据，今日16:00 BJS发布，actual待回填；7月末34188亿(5源验证)"

# ---------- 2. 黄金储备系列回填（generate 已按新模式生成事件，此处填值） ----------
GOLD_TEMPLATE = {
    "country": "CN", "country_name": "中国",
    "indicator": "黄金储备（万盎司）", "indicator_en": "Gold Reserves",
    "frequency": "月度", "importance": 2,
    "release_time": "16:00", "timezone": "BJS",
    "source": "中国人民银行", "source_url": "",
    "unit": "万盎司",
}
# generate 的 cutoff=today-180d 过滤了 3/9、2/9 发布日，此处手动补建
gold_missing = {
    "CN_GOLD_RESERVES_20260107": {"release_date": "2026-01-07", "period": "2025-12",
                                   "actual": None, "previous": None, "status": "pending",
                                   "notes": "2025年12月末黄金储备，官方值未采集，留pending"},
    "CN_GOLD_RESERVES_20260209": {"release_date": "2026-02-09", "period": "2026-01",
                                   "actual": 7419, "previous": None, "status": "released",
                                   "notes": "SAFE官方储备资产表 7419万盎司"},
    "CN_GOLD_RESERVES_20260309": {"release_date": "2026-03-09", "period": "2026-02",
                                   "actual": 7422, "previous": 7419, "status": "released",
                                   "notes": "SAFE官方储备资产表 7422万盎司"},
}
for eid, meta in gold_missing.items():
    if eid not in events:
        events[eid] = {"id": eid, **GOLD_TEMPLATE, **meta}
        changes.append(f"  [NEW] {eid} 补建（generate cutoff 边界过滤，act={meta['actual']}）")

gold_chain = {
    "CN_GOLD_RESERVES_20260209": {"actual": 7419},   # 2026-01 月末（SAFE 表 7419 万盎司）
    "CN_GOLD_RESERVES_20260309": {"actual": 7422},   # 2026-02 月末（SAFE 表）
    "CN_GOLD_RESERVES_20260407": {"actual": 7438},   # 2026-03 月末（SAFE 表）
    "CN_GOLD_RESERVES_20260507": {"actual": 7464},   # 2026-04 月末（SAFE 表）
    "CN_GOLD_RESERVES_20260608": {"actual": 7496},   # 2026-05 月末（推算：6月末7544 - 6月增持48）
    "CN_GOLD_RESERVES_20260707": {"actual": 7544},   # 2026-06 月末（中经网官方）
    "CN_GOLD_RESERVES_20260807": {"actual": 7608},   # 2026-07 月末（5 源官方）
}
for eid, upd in gold_chain.items():
    ev = events.get(eid)
    if not ev:
        changes.append(f"  [MISS] {eid} 不存在（generate 未生成？），跳过")
        continue
    set_field(ev, "actual", upd["actual"], "GOLD")
    set_field(ev, "status", "released", "GOLD")

ev_today_gold = events.get("CN_GOLD_RESERVES_20260907")
if ev_today_gold:
    set_field(ev_today_gold, "previous", 7608, "GOLD")
    ev_today_gold["notes"] = "8月末数据，今日16:00 BJS与外储同日发布，actual待回填；7月末7608万盎司(连续21个月增持)"

# ---------- 3. 新增欧元区 Q2 GDP 环比终值事件（TE 确认 9/7 11:00 CET） ----------
if "EU_GDP_20260907" not in events:
    events["EU_GDP_20260907"] = {
        "id": "EU_GDP_20260907",
        "country": "EU", "country_name": "欧元区",
        "indicator": "GDP（环比）终值", "indicator_en": "GDP QoQ Final Estimate",
        "frequency": "季度", "importance": 3,
        "release_date": "2026-09-07", "release_time": "11:00", "timezone": "CET",
        "period": "2026-Q2", "unit": "%",
        "source": "欧盟统计局 EUROSTAT", "source_url": "",
        "forecast": 0.4, "previous": 0.4, "actual": None,
        "status": "upcoming",
        "notes": "7/30初值+0.4%、8/14二次估值+0.4%（年率1.0%，westock+TE双源✅）；终值今日11:00 CET=17:00 BJS发布",
    }
    changes.append("  [NEW] EU_GDP_20260907 新增（环比终值 fc=0.4/prev=0.4，upcoming）")

# ---------- 3b. 新增欧央行利率决议事件（9/6 联网核实：9/10 决议+拉加德记者会，加息25bp预期） ----------
if "EU_ECB_20260910" not in events:
    events["EU_ECB_20260910"] = {
        "id": "EU_ECB_20260910",
        "country": "EU", "country_name": "欧元区",
        "indicator": "欧央行利率决议", "indicator_en": "ECB Interest Rate Decision",
        "frequency": "月度（不定期）", "importance": 3,
        "release_date": "2026-09-10", "release_time": "20:15", "timezone": "BJS",
        "period": "2026-09", "unit": "%",
        "source": "欧洲央行 ECB", "source_url": "",
        "forecast": None, "previous": None, "actual": None,
        "status": "upcoming",
        "notes": "9/6核实：9/10决议(20:15 BJS)+拉加德记者会(20:45 BJS)，市场加息25bp预期；利率水平待发布核实",
    }
    changes.append("  [NEW] EU_ECB_20260910 新增（欧央行利率决议，upcoming）")

cal["events"] = list(events.values())

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cal, f, ensure_ascii=False, indent=2)

print(f"共 {len(changes)} 处变更：")
for c in changes:
    print(c)
print(f"\n总计 {len(cal['events'])} events")
