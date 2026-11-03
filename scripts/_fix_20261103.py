# -*- coding: utf-8 -*-
"""
_fix_20261103.py — 2026-11-03 回填脚本（幂等）
回填 11-2 发布的两项（昨日已发布，本批次补录）：
①中国10月财新制造业PMI（RatingDog/标普全球，11-2 09:45 BJS）
②美国10月ISM制造业PMI（11-2 23:00 BJS）
数据来源：网络双源交叉验证。
注意：不运行 run_daily merge（避免耐用品/新屋日期重置复现），直接 generate_js。
今日 11-3 ISM 非制造业PMI 今晚 23:00 BJS 发布，留待 11-4 批次回填。
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
        "id": "CN_CAIXIN_PMI_20261102",
        "actual": "52.0",
        "forecast": "51.6",
        "previous": "52.1",
        "notes_append": " | 2026-11-03回填: 10月RatingDog(财新)制造业PMI 52.0, 较9月52.1微降0.1pct, 连续11个月站上荣枯线(2021年中以来最长扩张周期); 产出增速创六个月新高且为今年4月以来最快, 增长连续3个月覆盖全部子行业(投资品领先); 新订单连续17个月扩张; 新出口订单连续4个月增长但增速放缓至3个月低点; 出厂价格三个月内第二次下调, 出口价格近一年来首次回落, 原材料购进价格连续16个月上涨(涨幅收窄); 供应商交货周期2月以来首次缩短; 企业信心降至九个月低位; 与官方制造业PMI 49.3(收缩)口径分歧明显(官方看大企业/民口看中小出口导向企业); 双源✅腾讯新闻引标普全球/RatingDog 11-2 + 格隆汇11-2(另工商时报/香港经济日报同口径)"
    },
    {
        "id": "US_ISM_MFG_20261102",
        "actual": "55.5",
        "forecast": "54.5",
        "previous": "54.5",
        "notes_append": " | 2026-11-03回填: 美国10月ISM制造业PMI 55.5, 超预期(预估54.5-54.6/前值54.5), 为逾四年来第二高水平, 连续10个月扩张; 生产指数59(较9月56.7升2.3pct, 2021年底以来最高); 新订单55.5(9月55.3, 7月以来最高); 就业52.4(9月52.7, 仍扩张, 工厂就业连续4个月增加为2022年初以来最长); 价格指数75.2(9月77.9, 高位回落仍高企, 通胀压力支撑加息预期); 12个行业扩张(电气设备/机械/计算机电子), 印刷/造纸/非金属矿物3行业萎缩; 同日标普全球制造业PMI终值54.9(预期56/前值56), 方向一致; 注意: ISM主席为Susan Spence, 提及通胀压力+原材料供应受限; 双源✅财联社11-2 23:00 + 新华财经11-3"
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
