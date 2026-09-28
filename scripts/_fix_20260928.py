#!/usr/bin/env python3
"""
2026-09-28 修复脚本（幂等，可重复执行）
1. JP_INDUSTRIAL 全系列日期根治：原模式"最后周一"错位，改为 METI 真实规律
   "次月最后营业日"（investing.com 全表 + FXBlue + Econoday 三源核实）。
   旧 id 改名 → 新 id（值全保留），并回填 6 月速报值、清洗 FF 抓取的 HTML 垃圾。
2. US_DALLAS_FED / US_DALLAS_FED_SERVICES 系列补值（模式已于同日加入 generate_calendar.py，
   首跑时新事件尚未生成会跳过，run_daily 生成后再跑一遍即落地）。
"""
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
CAL_FILE = os.path.join(PROJECT_DIR, "data", "calendar.json")

# ---------- 1) JP_INDUSTRIAL 改名 + 值更新 ----------
# (旧id, 新id, 字段更新)
JP_RENAMES = [
    ("JP_INDUSTRIAL_20251229", "JP_INDUSTRIAL_20251226", {
        "release_date": "2025-12-26"}),
    ("JP_INDUSTRIAL_20260126", "JP_INDUSTRIAL_20260130", {
        "release_date": "2026-01-30"}),
    ("JP_INDUSTRIAL_20260223", "JP_INDUSTRIAL_20260227", {
        "release_date": "2026-02-27"}),
    ("JP_INDUSTRIAL_20260330", "JP_INDUSTRIAL_20260331", {
        "release_date": "2026-03-31"}),
    ("JP_INDUSTRIAL_20260427", "JP_INDUSTRIAL_20260430", {
        "release_date": "2026-04-30"}),
    ("JP_INDUSTRIAL_20260525", "JP_INDUSTRIAL_20260529", {
        "release_date": "2026-05-29"}),
    ("JP_INDUSTRIAL_20260629", "JP_INDUSTRIAL_20260630", {
        "release_date": "2026-06-30",
        "actual": 0.5, "forecast": 0.6, "previous": 0.5, "status": "released",
        "notes": "2026-09-28 日期根治+数值清洗：5月速报 m/m +0.5%（fc 0.6/prev 0.5，investing.com）；"
                 "日期由 6/29 根治为 6/30（METI 次月末营业日规律）；prev 字段原混入 ForexFactory 抓取 HTML 垃圾已清除"}),
    ("JP_INDUSTRIAL_20260727", "JP_INDUSTRIAL_20260731", {
        "release_date": "2026-07-31",
        "actual": 1.3, "forecast": 1.0, "previous": 0.1, "status": "released",
        "notes": "2026-09-28 回填：6月速报 m/m +1.3%（fc 1.0/prev 0.1=5月修正值；y/y +4.2%）；"
                 "来源 investing.com 历史表 + FXBlue 双源✅；日期由 7/27 根治为 7/31"}),
    ("JP_INDUSTRIAL_20260928", "JP_INDUSTRIAL_20260930", {
        "release_date": "2026-09-30",
        "previous": -0.2, "status": "upcoming",
        "notes": "8月速报 9/30 08:50 JST 发布（原 9/28 系模式错位，2026-09-28 根治："
                 "investing / Econoday 9-29 19:50 ET=9-30 08:50 JST / FXBlue 三源）；"
                 "prev=7月修正值 -0.2（7月初值 0.1，9/14 修正，investing 9/14 行）；"
                 "y/y 参考 7月修正 3.9%；fc 共识未获取"}),
    ("JP_INDUSTRIAL_20261026", "JP_INDUSTRIAL_20261030", {
        "release_date": "2026-10-30"}),
]

# ---------- 2) Dallas 制造/服务补值 ----------
# (id, 字段更新)；notes_append=追加到既有 notes（带幂等标记）
DALLAS_PATCHES = [
    ("US_DALLAS_FED_20260427", {
        "actual": -2.3, "previous": -0.2, "status": "released",
        "notes": "2026-09-28 补值（investing.com 历史表单源，链咬合：5月 prev=-2.3 ✅）"}),
    ("US_DALLAS_FED_20260526", {
        "actual": 0.4, "previous": -2.3, "status": "released",
        "notes": "2026-09-28 补值（investing 单源，链咬合 ✅；Memorial Day 5/25 顺延至 5/26 发布）"}),
    ("US_DALLAS_FED_20260629", {
        "actual": 0.0, "previous": 0.4, "status": "released",
        "notes": "2026-09-28 补值（investing + TE 双源✅）"}),
    ("US_DALLAS_FED_20260727", {
        "actual": 1.3, "forecast": -1.0, "previous": 0.0, "status": "released",
        "notes": "2026-09-28 补值（act/prev investing+TE 双源✅；fc -1=TE 共识）"}),
    ("US_DALLAS_FED_20260831", {
        "actual": 11.6, "forecast": 0.7, "previous": 1.3, "status": "released",
        "notes": "2026-09-28 补值（act/prev investing+TE 双源✅；fc 0.7=TE 共识；8月创 2025-01 来最高）"}),
    ("US_DALLAS_FED_20260928", {
        "notes_append": "9/28 更新：9月共识缺失——FXStreet n/a、investing 无预测、TE 显示截断 '1.x' 不采信；"
                        "Gate.io '7.2' 系发布前不可验证数字弃用。今晚 22:30 BJS 发布后明晨回填"}),
    ("US_DALLAS_FED_SERVICES_20260428", {
        "notes_append": "（日期未核实，模式推算）"}),
    ("US_DALLAS_FED_SERVICES_20260527", {
        "notes": "⚠️ 5月 Memorial Day 特例：mfg 实际 5/26（investing），svc 按 mfg+1 规律推算 5/27，未直接核实"}),
    ("US_DALLAS_FED_SERVICES_20260630", {
        "actual": 2.9, "status": "released",
        "notes": "2026-09-28 补值：act 2.9 系 TE 7月行 prev 反推（单源链）"}),
    ("US_DALLAS_FED_SERVICES_20260728", {
        "actual": 6.6, "forecast": 2.0, "previous": 2.9, "status": "released",
        "notes": "2026-09-28 补值（TE + moomoo 双源✅；fc 2=TE 共识）"}),
    ("US_DALLAS_FED_SERVICES_20260901", {
        "actual": 4.2, "forecast": 5.0, "previous": 6.6, "status": "released",
        "notes": "2026-09-28 补值（TE + moomoo 双源✅；fc 5=TE 共识；8月数据跨月 9/1 发布）"}),
    ("US_DALLAS_FED_SERVICES_20260929", {
        "previous": 4.2,
        "notes": "9月服务业调查 9/29 22:30 BJS（TE 2026-09-29 02:30 PM GMT）；"
                 "prev=8月 4.2（TE+moomoo 双源✅，7月 6.6）；8月分项：revenues 6.6 / company outlook 3.0 / "
                 "投入价格 35.6 / 售价 8.9 / 就业 0.8；发布日=mfg+1 天规律（2026 三点吻合）；2026-09-28 补录"}),
]


# ---------- 3) Memorial Day 幽灵事件删除（模式最后周一 5/25 与 svc 5/26 均非真实发布日）----------
GHOST_DELETES = [
    "US_DALLAS_FED_20260525",
    "US_DALLAS_FED_SERVICES_20260526",
]


def main():
    with open(CAL_FILE, encoding="utf-8") as f:
        data = json.load(f)
    events = data["events"] if isinstance(data, dict) else data
    by_id = {e["id"]: e for e in events}

    n_rename = n_patch = n_skip = n_del = 0

    # 0) 幽灵事件删除
    for gid in GHOST_DELETES:
        if gid in by_id:
            del by_id[gid]
            n_del += 1
            print(f"  delete ghost {gid}")
        else:
            print(f"  skip (absent) {gid}")

    # 1) JP 改名（旧id存在→改名；仅新id存在→已改名跳过）
    for old_id, new_id, fields in JP_RENAMES:
        if old_id in by_id:
            ev = by_id.pop(old_id)
            ev["id"] = new_id
            ev.update(fields)
            by_id[new_id] = ev
            n_rename += 1
            print(f"  rename {old_id} -> {new_id}")
        elif new_id in by_id:
            print(f"  skip (already renamed) {new_id}")
            n_skip += 1
        else:
            print(f"  !! MISSING both {old_id} and {new_id}")
            n_skip += 1

    # 2) Dallas 补值
    for eid, fields in DALLAS_PATCHES:
        ev = by_id.get(eid)
        if ev is None:
            print(f"  skip (not generated yet) {eid}")
            n_skip += 1
            continue
        append = fields.pop("notes_append", None)
        changed = []
        for k, v in fields.items():
            if ev.get(k) != v:
                ev[k] = v
                changed.append(k)
        if append:
            marker = append.lstrip("；").split("；")[0][:24]
            if marker and marker not in (ev.get("notes") or ""):
                ev["notes"] = (ev.get("notes") or "") + "；" + append
                changed.append("notes+")
        if changed:
            n_patch += 1
            print(f"  patch {eid}: {','.join(changed)}")
        else:
            print(f"  skip (no change) {eid}")
            n_skip += 1

    # 回写（保持 dict 结构）+ 去重校验
    out_events = list(by_id.values())
    ids = [e["id"] for e in out_events]
    assert len(ids) == len(set(ids)), "duplicate ids after fix!"
    out_events.sort(key=lambda e: e.get("release_date", ""))
    if isinstance(data, dict):
        data["events"] = out_events
        json.dump(data, open(CAL_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        json.dump(out_events, open(CAL_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    released = sum(1 for e in out_events if e.get("status") == "released")
    print(f"\nDone. renames={n_rename} patches={n_patch} deletes={n_del} skips={n_skip} | total={len(out_events)} released={released}")


if __name__ == "__main__":
    main()
