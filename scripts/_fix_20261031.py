# -*- coding: utf-8 -*-
"""
_fix_20261031.py — 2026-10-31 回填脚本（幂等）
回填 10-31 09:30 BJS 发布的中国官方 PMI 两项（统计局/中物联官方发布）
数据来源：网络多源交叉验证（中物联官方公众号×3篇 + 腾讯自选股/大河财立方引国家统计局）
WeStock CLI 数据库10月值未更新（最新至9月），故走网络双源采集。
注意：不运行 run_daily merge（避免耐用品/新屋日期第6次重置），直接用 generate_js 再生成 JS。
"""
import json
import sys
import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)
from run_daily import generate_js, load_calendar

CAL = os.path.join(SCRIPTS_DIR, '..', 'data', 'calendar.json')

FIXES = [
    {
        "id": "CN_PMI_MFG_20261031",
        "actual": "49.3",
        "forecast": "50.0",
        "previous": "50.1",
        "notes_append": " | 2026-10-31回填: 10月官方制造业PMI 49.3%大幅低于预期(路透调查中值50.0/前值50.1, 降0.8pct重回收缩区间); 大型50.2(-0.4)仍扩张/中型48.4(-1.3)/小型47.5(-1.4); 生产49.8(-1.9)/新订单49.4(-1.1)/新出口订单48.7(-1.3)/购进价格56.8(-4.0高位回落)/出厂价格51.7(-2.3); 高技术制造业51.3/装备制造业50.6延续扩张; 统计局解读: 假期前需求提前释放+国际环境复杂, 需求不足问题仍在发展; 双源✅中物联官方公众号10-31 + 腾讯自选股(大河财立方引统计局)10-31 09:32"
    },
    {
        "id": "CN_PMI_NONMFG_20261031",
        "actual": "49.7",
        "previous": "50.2",
        "notes_append": " | 2026-10-31回填: 10月官方非制造业商务活动指数49.7%(降0.5pct, 时隔数月降至收缩区间); 建筑业48.0(-2.3, 开工进度偏慢主拖累)/服务业50.0(-0.2, 临界点持稳); 非制造业新订单44.4(-2.1)/业务预期54.7(-0.8); 节日消费托底: 铁路运输60+/航空54+/邮政55+/文体娱乐53+; 综合PMI产出指数49.7(-1.0, 三大指数全线回落); 双源✅中物联官方公众号10-31 + 腾讯自选股(大河财立方引统计局)10-31"
    },
]


def main():
    with open(CAL, encoding="utf-8") as f:
        cal = json.load(f)
    events = cal["events"] if isinstance(cal, dict) else cal

    backfilled = 0
    for fx in FIXES:
        ev = next((e for e in events if e.get("id") == fx["id"]), None)
        if ev is None:
            print(f"[MISS] {fx['id']} not found")
            continue
        if ev.get("actual") is not None:
            print(f"[SKIP] {fx['id']} already has actual={ev['actual']}")
            continue
        ev["actual"] = fx["actual"]
        if fx.get("forecast"):
            ev["forecast"] = fx["forecast"]
        if fx.get("previous"):
            ev["previous"] = fx["previous"]
        ev["status"] = "released"
        base = ev.get("notes", "") or ""
        if fx["notes_append"] not in base:
            ev["notes"] = (base + fx["notes_append"]).strip(" |")
        backfilled += 1
        print(f"[OK] {fx['id']}: actual={ev['actual']} fc={ev.get('forecast')} prev={ev.get('previous')}")

    released = sum(1 for e in events if e.get("status") == "released")
    pending = sum(1 for e in events if e.get("status") == "pending")
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(cal, f, ensure_ascii=False, indent=2)

    # 重新生成 JS（与 run_daily 同一入口，不跑 merge 避免日期重置）
    output = load_calendar()
    generate_js(output)
    print(f"Done. backfilled={backfilled} | total={len(events)} released={released} pending={pending}; JS regenerated")


if __name__ == "__main__":
    main()
