#!/usr/bin/env python3
"""
2026-10-06 修复补丁：
1. 删除幻影 US_FOMC_2026-12-17（10-02 会话删除操作踩 delete() 未写回 bug 从未落盘，
   git log -S 证实该 id 自 v1.01 起一直在文件里；官方 2026 日程 12 月会议 12/8-9，
   BJS 决议日 12/10 已在库。本次删除后带断言验证）
2. 财新服务业 8 月值纠错：CN_CAIXIN_SERVICES_PMI_20260903 actual 50.7 -> 51.4
   （Investing/AAstocks/新浪/联合早报/tdx 5源一致；50.7 为 10-05 补丁误录）
3. 财新服务业 9 月值回填：_20261005 事件改造为 _20260930（提前发布，国庆惯例双年实证）
   actual=51.6 / fc=51.3 / prev=51.4
4. 新建 CN_CAIXIN_PMI_20260930：财新制造业 9 月=52.1（fc=51.7/prev=51.5，9/30 同日提前发布）
5. ISM 非制造业 9 月回填：US_ISM_SERVICES_20261005 actual=54.9（证券之星+TE 2源），
   并同步 US_ISM_SERVICES_20261103 prev 链=54.9
6. 重新生成 calendar_data.js
幂等：带 marker 检查，重复运行无副作用。
"""
import json
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(PROJ, "data", "calendar.json")
JS = os.path.join(PROJ, "data", "calendar_data.js")

with open(CAL, encoding="utf-8") as f:
    data = json.load(f)

events = data["events"]
by_id = {e["id"]: e for e in events}
changes = []

def fnum(v):
    return None if v is None else float(v)

def notes_append(eid, marker, text):
    e = by_id.get(eid)
    if e is None:
        print(f"  !! 事件不存在: {eid}")
        return
    notes = e.get("notes") or ""
    if marker in notes or text[:15] in notes:
        return
    e["notes"] = (notes + ("；" if notes and not notes.endswith("；") else "") + text) if notes else text
    changes.append(f"{eid}.notes += [{marker}]")

# ---- 1. 删除幻影 FOMC 12/17 ----
if "US_FOMC_2026-12-17" in by_id:
    events[:] = [e for e in events if e["id"] != "US_FOMC_2026-12-17"]
    changes.append("删除幻影事件 US_FOMC_2026-12-17（10-02 删除未落盘，本次补执行）")
    by_id.pop("US_FOMC_2026-12-17", None)
else:
    print("  幻影 12/17 已不存在（幂等命中）")

# ---- 2. 财新服务业 8 月值纠错 50.7 -> 51.4 ----
e = by_id.get("CN_CAIXIN_SERVICES_PMI_20260903")
if e is not None and fnum(e.get("actual")) != 51.4:
    old = e.get("actual")
    e["actual"] = 51.4
    e["status"] = "released"
    changes.append(f"CN_CAIXIN_SERVICES_PMI_20260903.actual: {old} -> 51.4（5源纠错）")
    notes_append("CN_CAIXIN_SERVICES_PMI_20260903", "M:20261006fix",
        "⚠️2026-10-06 纠错：8月actual 50.7系误录，Investing/AAstocks/新浪/联合早报/tdx 5源一致为51.4（fc50.6/7月50.4），已修正")
else:
    print("  财新服务业 9/3 已为 51.4（幂等命中）")

# ---- 3. 财新服务业 9 月：_20261005 -> _20260930 改造回填 ----
old_e = by_id.get("CN_CAIXIN_SERVICES_PMI_20261005")
new_e = by_id.get("CN_CAIXIN_SERVICES_PMI_20260930")
if old_e is not None and new_e is None:
    old_e["id"] = "CN_CAIXIN_SERVICES_PMI_20260930"
    old_e["release_date"] = "2026-09-30"
    old_e["status"] = "released"
    old_e["actual"] = 51.6
    old_e["forecast"] = 51.3
    old_e["previous"] = 51.4
    old_e["notes"] = ("财新服务业PMI 9/30 09:45 提前发布（国庆假期惯例，2025年同例9/30发布9月值52.9）；"
        "9月51.6高于共识51.3/前值51.4，3个月最快但仍温和；新订单增速6月来最快、新出口订单3个月首次加速"
        "（连续5个月增长，2024年后最长）；销售价格4个月来首次下降且降幅为2022年4月来最快（价格战信号）；"
        "就业连续5个月增长；综合产出52.4（前52.1）；AAstocks/橙新闻/信报/Lloyds/dailydigest 5源✅；"
        "⚠️10-05补丁曾误记8月值50.7，实为51.4已修正")
    changes.append("CN_CAIXIN_SERVICES_PMI_20261005 -> _20260930 改造回填 51.6/51.3/51.4")
    by_id["CN_CAIXIN_SERVICES_PMI_20260930"] = old_e
    by_id.pop("CN_CAIXIN_SERVICES_PMI_20261005", None)
elif new_e is not None:
    print("  财新服务业 _20260930 已在（幂等命中）")
else:
    print("  !! 找不到 CN_CAIXIN_SERVICES_PMI_20261005，需人工检查")

# ---- 4. 新建财新制造业 9/30 ----
if "CN_CAIXIN_PMI_20260930" not in by_id:
    ev = {
        "id": "CN_CAIXIN_PMI_20260930",
        "country": "CN", "country_name": "中国",
        "indicator": "财新制造业PMI", "indicator_en": "Caixin Manufacturing PMI",
        "frequency": "月度", "importance": 2,
        "release_date": "2026-09-30", "release_time": "09:45", "timezone": "BJS",
        "period": "2026-09",
        "source": "财新/S&P Global", "source_url": "",
        "unit": "", "status": "released",
        "actual": 52.1, "forecast": 51.7, "previous": 51.5,
        "notes": ("财新制造业PMI 9/30 09:45 与服务业同日提前发布（国庆惯例）；52.1高于共识51.7/前值51.5，"
            "5个月新高、连续10个月扩张；新订单连续16个月增长（部分企业积累安全库存）、产出连续10个月增长；"
            "就业4个月内第三次增长；供应商交付连续7个月延长；出厂价格重新上调；"
            "AAstocks/橙新闻/信报 3源✅（2026-10-06 补建，此前库内缺失该事件）"),
    }
    events.append(ev)
    by_id[ev["id"]] = ev
    changes.append("新建 CN_CAIXIN_PMI_20260930 52.1/51.7/51.5")
else:
    print("  财新制造业 _20260930 已在（幂等命中）")

# ---- 5. ISM 非制造业 9 月回填 ----
e = by_id.get("US_ISM_SERVICES_20261005")
if e is not None and fnum(e.get("actual")) != 54.9:
    e["actual"] = 54.9
    e["status"] = "released"
    changes.append(f"US_ISM_SERVICES_20261005.actual: {e.get('actual')} -> 54.9")
    notes_append("US_ISM_SERVICES_20261005", "M:20261006ismfill",
        "10/5 22:00 BJS 发布：54.9低于预期55（TE/媒体口径，预填共识55.7亦未达）/前值55.4，27个月连续扩张；"
        "分项：商业活动56.5（前61.7）明显放缓、新订单59.8、就业50.1两月收缩后重返扩张、"
        "物价支付74为2022年7月来最高（预期73.3，投入成本继续攀升）、积压56.6为2022年7月来最高、"
        "供应商交付53.2、出口订单8个月首次跌破50；证券之星金吾财讯+TradingEconomics 2源✅")
else:
    print("  ISM 服务业 10/5 已回填（幂等命中）")

# ---- 6. ISM prev 链同步 ----
e = by_id.get("US_ISM_SERVICES_20261103")
if e is not None and fnum(e.get("previous")) != 54.9:
    old = e.get("previous")
    e["previous"] = 54.9
    changes.append(f"US_ISM_SERVICES_20261103.previous: {old} -> 54.9（prev链咬合）")

# ---- 排序 + 校验 ----
events.sort(key=lambda x: x.get("release_date", ""))

assert "US_FOMC_2026-12-17" not in by_id, "幻影 12/17 删除失败"
assert "US_FOMC_2026-12-10" in by_id, "12/10 正确事件不得被误删"
assert fnum(by_id["CN_CAIXIN_SERVICES_PMI_20260903"]["actual"]) == 51.4
assert fnum(by_id["CN_CAIXIN_SERVICES_PMI_20260930"]["actual"]) == 51.6
assert fnum(by_id["CN_CAIXIN_PMI_20260930"]["actual"]) == 52.1
assert fnum(by_id["US_ISM_SERVICES_20261005"]["actual"]) == 54.9
assert fnum(by_id["US_ISM_SERVICES_20261005"]["previous"]) == 55.4
assert fnum(by_id["US_ISM_SERVICES_20261103"]["previous"]) == 54.9

if changes:
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 重新生成 JS（与 run_daily.generate_js 同格式）
    from datetime import datetime
    js = f"// Auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js += f"window.CALENDAR_DATA = {json.dumps(data, ensure_ascii=False)};"
    with open(JS, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"共 {len(changes)} 处修改已写回（calendar.json + calendar_data.js）")
    for c in changes:
        print("  -", c)
else:
    print("无修改（幂等命中）")

# 回读验证
with open(CAL, encoding="utf-8") as f:
    rd = {e["id"]: e for e in json.load(f)["events"]}
assert "US_FOMC_2026-12-17" not in rd
assert fnum(rd["US_ISM_SERVICES_20261005"]["actual"]) == 54.9
assert fnum(rd["CN_CAIXIN_SERVICES_PMI_20260930"]["actual"]) == 51.6
with open(JS, encoding="utf-8") as f:
    jstxt = f.read()
assert '"US_FOMC_2026-12-17"' not in jstxt, "JS 中仍含幻影"
assert "54.9" in jstxt
print("回读验证 ALL OK")
