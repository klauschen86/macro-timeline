#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_20261012.py — 2026-10-12 中国数据日期根治（9 事件改名 + 12 处字段回填）

背景：run_daily [Today] 显示 10/12 有 4 个中国事件，经三组官方源核实全部系模式日期偏早：
  ① 贸易数据 → 10/14（国新办采访通知，中国网 10/10；统计局发布预告 + 央广财经 10/11 双源）
  ② 金融数据 3 项（M2/社融/贷款）→ 暂按 10/15（无官方预告，窗口 10/13-10/16，
     央广财经 10/11"下周公布" + 2025 年同期 10/15 先例），实际发布后修正
  ③ 经济数据 4 项 + GDP → 10/19 10:00（统计局官网《2026 年主要统计信息发布日程表》官方确证）

配套：generate_calendar.py DATE_OVERRIDES 已加 9 条（防 run_daily 回滚）。
10/12 当日实际无发布（美哥伦布日休市 + 中国 4 事件全部错位），本修复为今日主体工作。
"""
import json
import sys
from datetime import datetime

CAL = "data/calendar.json"
MARK = "2026-10-12日期根治"

with open(CAL, encoding="utf-8") as f:
    data = json.load(f)
events = data["events"] if isinstance(data, dict) else data

def notes_of(e):
    return e.get("notes") or ""

def append_notes(e, text):
    n = notes_of(e)
    if MARK in n and text[:20] in n:
        return False  # 幂等：marker+文本前缀均已存在
    sep = "" if not n else ("\n" if n.endswith((".", "。", "✅", ")")) else "；")
    e["notes"] = (n + sep + text).strip("；")
    return True

# ---------- 1) 改名映射（old_id -> (new_id, release_date, patches, note)） ----------
RENAMES = {
    "CN_TRADE_20261012": ("CN_TRADE_20261014", "2026-10-14",
        {"previous": 1190.9, "forecast": 1270.0},
        "2026-10-12日期根治: 国新办采访通知(中国网10/10)——10/14(周三)10:00海关总署发布会介绍2026年前三季度进出口,统计局官网发布预告+央广财经'下周看点'(10/11)双源✅; 原10/12系模式日期偏早(DATE_OVERRIDES已根治)。etnet前值列: 8月出口+25.0%/进口+28.2%/顺差1190.9亿美元(与9/8官方回填吻合✅)。9月预期(Lundgreen's/Yiyi Capital单源,共识未成形,发布前复核): 出口+30%(8月+25%)/进口+25%(8月+28.2%)/顺差~1270亿美元。"),
    "CN_M2_20261012": ("CN_M2_20261015", "2026-10-15",
        {"previous": 7.5, "forecast": 7.5},
        "2026-10-12日期修正: 央行无官方预告,发布窗口10/13-10/16(央广财经10/11'9月金融数据或将在下周公布';2025年同期9月数据10/15发布先例),暂按10/15,实际发布后按真实日期修正(DATE_OVERRIDES已预置)。机构预测: 中金M2 7.5%(持平8月)/华源7.4%; 政府债发行提速+季末财政支出提速支撑。prev=7.5(8月,央行官方9/14发布)。"),
    "CN_SOCIAL_FINANCING_20261012": ("CN_SOCIAL_FINANCING_20261015", "2026-10-15",
        {"previous": 16600, "forecast": 36000},
        "2026-10-12日期修正: 同M2,窗口10/13-10/16暂按10/15。机构预测9月新增社融: 中金3.6万亿/华源3.45万亿/同花顺汇总券商3.15万亿(fc取中金36000亿,分歧已标注); 社融存量增速预期7.0-7.2%(8月7.2%),政府债净融资~1.5-1.59万亿(同比多增约3100-3500亿,创年内新高)为主要支撑,政策性金融工具9月启动投放。prev=16600亿(8月,央行官方9/14发布)。"),
    "CN_NEW_LOANS_20261012": ("CN_NEW_LOANS_20261015", "2026-10-15",
        {"previous": 600, "forecast": 12000},
        "2026-10-12日期修正: 同M2,窗口10/13-10/16暂按10/15。机构预测9月新增贷款: 中金1.2万亿/华源1.16万亿(fc取中金12000亿); 季末冲量环比改善但实体需求弱于季节性,票据融资或转负,政策性银行投放超千亿(节奏较去年提前约1个月)带动对公中长贷与委托贷款; 居民端地产新政边际提振但仍偏弱。prev=600亿(8月,住户-2029亿连续2月负,央行官方)。"),
    "CN_INDUSTRIAL_20261015": ("CN_INDUSTRIAL_20261019", "2026-10-19",
        {"previous": 5.2},
        "2026-10-12日期根治: 统计局官网《2026年国家统计局主要统计信息发布日程表》+发布预告栏官方确证——10/19(周一)10:00国民经济运行情况发布会(前三季度); 原10/15系模式日期偏早(DATE_OVERRIDES已根治)。etnet前值列8月值5.2%与9/15官方回填逐一吻合✅。"),
    "CN_RETAIL_20261015": ("CN_RETAIL_20261019", "2026-10-19",
        {"previous": 0.4},
        "2026-10-12日期根治: 同工业增加值,统计局官方日程表确证10/19 10:00。etnet前值列8月值0.4%与9/15官方回填吻合✅(限额以上-3.7%拖累,低基数下关注9月边际改善)。"),
    "CN_FAI_20261015": ("CN_FAI_20261019", "2026-10-19",
        {"previous": -7.2},
        "2026-10-12日期根治: 同工业增加值,统计局官方日程表确证10/19 10:00。etnet前值列8月累计-7.2%与9/15官方回填吻合✅(地产开发-19.9%续拖累)。"),
    "CN_UNEMPLOYMENT_20261015": ("CN_UNEMPLOYMENT_20261019", "2026-10-19",
        {"previous": 5.3},
        "2026-10-12日期根治: 同工业增加值,统计局官方日程表确证10/19 10:00。etnet前值列8月值5.3%与9/15官方回填吻合✅; 另: 国新办10/10'开局起步十五五'发布会披露1-9月城镇新增就业1052万人(完成全年目标87.7%)、前8个月调查失业率均值5.2%(gov.cn官方)。"),
    "CN_GDP_20261016": ("CN_GDP_20261019", "2026-10-19",
        {"previous": 4.3},
        "2026-10-12日期根治: 统计局官方日程表确证10/19(周一)10:00国民经济运行情况发布会(含Q3 GDP),10/20 9:30季度行业增加值初核; 原10/16系模式偏早。prev=4.3(Q2同比,etnet 10/19事件前值列;与H1累计4.7%/Q1 5.2%反推自洽✅;同列8月月度值与官方逐一吻合,口径可信)。Q3共识暂未成形,fc留空发布前补。"),
}

by_id = {e.get("id"): e for e in events}
log = []
for old_id, (new_id, new_date, patches, note) in RENAMES.items():
    tgt = by_id.get(old_id)
    if tgt is None:
        if new_id in by_id and MARK in notes_of(by_id[new_id]):
            log.append(f"SKIP(已改名) {old_id} -> {new_id}")
            continue
        log.append(f"MISS {old_id}(不存在且未改名)"); continue
    if new_id in by_id and by_id[new_id] is not tgt:
        log.append(f"CONFLICT 目标id已存在: {new_id}"); continue
    # 改名 + 同步日期（铁律：id↔release_date 必须同步，rsplit 防多下划线）
    assert old_id.rsplit("_", 1)[1] == old_id.split("_")[-1]
    tgt["id"] = new_id
    tgt["release_date"] = new_date
    for k, v in patches.items():
        tgt[k] = v
    append_notes(tgt, note)
    log.append(f"OK {old_id} -> {new_id} @{new_date} patches={list(patches)}")

# ---------- 2) 顺带回填 Q2 GDP（此前一直 pending） ----------
q2 = by_id.get("CN_GDP_20260716")
if q2 is not None and q2.get("actual") is None:
    q2["actual"] = 4.3
    append_notes(q2, "2026-10-12回填: Q2 GDP同比4.3%(etnet 10/19 Q3事件前值列;与H1累计4.7%/Q1 5.2%反推自洽✅,此前pending)。")
    log.append("OK CN_GDP_20260716 actual=4.3 (Q2)")
elif q2 is None:
    log.append("MISS CN_GDP_20260716")

# ---------- 3) 写回 ----------
if isinstance(data, dict):
    data["events"] = events
with open(CAL, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ---------- 4) 回读 assert ----------
with open(CAL, encoding="utf-8") as f:
    data2 = json.load(f)
events2 = data2["events"] if isinstance(data2, dict) else data2
by2 = {e.get("id"): e for e in events2}
ok = True
for old_id, (new_id, new_date, patches, _) in RENAMES.items():
    e = by2.get(new_id)
    if e is None:
        print(f"ASSERT FAIL: {new_id} 不存在"); ok = False; continue
    if e["release_date"] != new_date:
        print(f"ASSERT FAIL: {new_id} date={e['release_date']}"); ok = False
    for k, v in patches.items():
        if e.get(k) != v:
            print(f"ASSERT FAIL: {new_id}.{k}={e.get(k)} 期望 {v}"); ok = False
    if MARK not in notes_of(e):
        print(f"ASSERT FAIL: {new_id} notes 缺 marker"); ok = False
old_left = [i for i in RENAMES if i in by2]
if old_left:
    print(f"ASSERT FAIL: 旧id残留 {old_left}"); ok = False
q2b = by2.get("CN_GDP_20260716")
if q2b is None or q2b.get("actual") != 4.3:
    print("ASSERT FAIL: CN_GDP_20260716 actual"); ok = False

print("\n".join(log))
print("READBACK:", "ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
