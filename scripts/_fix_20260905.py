#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-09-05 补录/修正事件（联网多源核实: 中新社/光明网/新华财经/每经/网易/搜狐/Yonhap/玉山/中行/新浪）
背景: 9/4 晨执行时 9/3-9/4 实际值未出炉, 今日回填; 7月非农遭上修需同步历史链。

数据源与数值（均为官方/权威媒体一致口径）:
1. 美国8月非农 +16.2万 (预期+5.6万, 前值7月 -2.3万→上修+2.1万)  ✅ 多源
2. 美国8月失业率 4.1%  (预期4.1, 前值4.1)  ✅ 多源
3. 美国8月时薪 m/m +0.3% / y/y +3.1%  ✅ 多源
4. 修正: 6月非农 初值+2.0万 → 上修 +3.1万 (9/4随8月报告修正, 两月合计+5.5万)
5. 修正: 7月非农 初值-2.3万 → 上修 +2.1万 (US_NFP_20260807 actual 同步)
6. 加拿大8月就业 -4.17万 (Reuters 41.7K; 预期+1.5万)  ✅ Xinhua/新华财经/格隆汇
7. 加拿大8月失业率 6.4%  ✅ 多源
8. ISM 非制造业PMI 8月 55.4 (预期54.2, 前值54.1) — 9/3 发布漏回填  ✅ 中行/玉山/新浪
9. 6月失业率 4.2 (由 US_UNEMPLOYMENT_20260807 prev=4.2 佐证, 未上修)
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(BASE, "data", "calendar.json")
d = json.load(open(CAL, encoding="utf-8"))
evs = d["events"]
by_id = {e["id"]: e for e in evs}

def upd(eid, **kw):
    if eid not in by_id:
        print(f"  !! NOT FOUND: {eid}")
        return
    e = by_id[eid]
    for k, v in kw.items():
        if e.get(k) != v:
            print(f"  ~ {eid} [{k}]: {e.get(k)!r} -> {v!r}")
            e[k] = v
        else:
            print(f"  = {eid} [{k}] already {v!r}")

# ---- 9/4 美国就业报告 (2026-08 期) actual 回填 ----
upd("US_NFP_20260904", actual="16.2", previous="2.1", status="released",
    notes="8月非农 +16.2万 远超预期+5.6万 (9/4晚发布; 中新社/光明网/每经/网易/Yonhap 多源✅); 7月修正+2.1万")
upd("US_UNEMPLOYMENT_20260904", actual="4.1", status="released",
    notes="8月失业率 4.1% 持平前值 (9/4发布; 多源✅)")
upd("US_FF_Average_Hourly_Earnings_m_m_20260904", actual="0.3%", status="released",
    notes="8月时薪 m/m +0.3% (9/4发布; 每经/搜狐 多源✅)")
upd("US_FF_Average_Hourly_Earnings_y_y_20260904", actual="3.1%", status="released",
    notes="8月时薪 y/y +3.1% (9/4发布; 每经/搜狐 多源✅)")

# ---- 历史上修链: 6月 +2.0→+3.1, 7月 -2.3→+2.1 (prev 链同步) ----
upd("US_NFP_20260703", actual="3.1", status="released",
    notes="6月非农初值+2.0万, 9/4随8月报告上修至+3.1万 (两月合计+5.5万, 劳工部)")
upd("US_NFP_20260807", actual="2.1", previous="3.1", status="released",
    notes="7月非农初值-2.3万, 9/4随8月报告上修至+2.1万 (劳工部)")
upd("US_UNEMPLOYMENT_20260703", actual="4.2", status="released",
    notes="6月失业率 4.2% (由8/7发布7月报告 prev=4.2 佐证, 未上修)")

# ---- 9/4 加拿大就业报告 (2026-08 期) actual 回填 ----
upd("CA_EMPLOYMENT_20260904", actual="-4.17", status="released",
    notes="8月就业 -4.17万 (Reuters 41.7K, 预期+1.5万; Xinhua/新华财经/格隆汇 多源✅); 前值7月+7.51万")
upd("CA_UNEMPLOYMENT_20260904", actual="6.4", status="released",
    notes="8月失业率 6.4% 持平 (9/4发布; Xinhua/新华财经 多源✅)")

# ---- 9/3 ISM 非制造业PMI 55.4 (漏回填) ----
upd("US_ISM_SERVICES_20260903", actual="55.4", status="released",
    notes="8月ISM非制造业PMI 55.4 (预期54.2, 前值54.1; 9/3晚发布; 中行/玉山/新浪 多源✅)")

json.dump(d, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\nDone. total {len(evs)} events")
