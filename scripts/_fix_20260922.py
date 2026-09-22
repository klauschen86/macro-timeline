#!/usr/bin/env python3
"""
2026-09-22 修复脚本
1. CN_PMI 全系列根治：NBS 每月最后一日发布当月 PMI（官方解读页/英文月报逐月核实），
   日期错位事件改名迁移（id=发布日），period 改为"发布月=数据月"，污染值修正：
   4月 50.5→50.3、5月 50.4→50.0（官方 4源：NBS 解读页/英文月报/新华网/央视网/gov.cn）；
   补 7月 49.2（8月报告"+0.6pp"反推，4源✅）；6月 50.3 / 8月 49.8 官方确认值保留。
2. EU_CPI_FLASH：8月 flash 发布日 8/31→9/1（Eurostat 官方日历）；删除 9/28、10/26 幽灵事件
   （9月 flash 实际 10/2 发布，模式已生成 _20261002）。
3. US 新屋销售 9/25→9/24、耐用品订单 9/28→9/25（NY Fed 官方日历）。
4. 新增事件：美 CFNAI（9/21 已发布 -0.04）、里士满联储制造业指数（8/25 已发布 4 + 9/22 今晚待发）、
   S&P Global 美国 PMI 初值（8/21 已发布 + 9/23 待发）——官方源多源交叉核实。
"""
import json
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(PROJECT, "data", "calendar.json")

cal = json.load(open(CAL, encoding="utf-8"))
events = cal["events"]
by_id = {e["id"]: e for e in events}

log = []

def rename(old_id, new_id, **fields):
    e = by_id.get(old_id)
    if not e:
        log.append(f"MISS rename {old_id}")
        return
    e["id"] = new_id
    for k, v in fields.items():
        e[k] = v
    by_id.pop(old_id, None)
    by_id[new_id] = e
    log.append(f"RENAME {old_id} -> {new_id} {fields}")

def patch(eid, **fields):
    e = by_id.get(eid)
    if not e:
        log.append(f"MISS patch {eid}")
        return
    for k, v in fields.items():
        e[k] = v
    log.append(f"PATCH {eid} {fields}")

def delete(eid):
    e = by_id.pop(eid, None)
    if e:
        events.remove(e)
        log.append(f"DELETE {eid} (actual={e.get('actual')})")
    else:
        log.append(f"MISS delete {eid}")

def add(e):
    if e["id"] in by_id:
        log.append(f"SKIP add (exists) {e['id']}")
        return
    events.append(e)
    by_id[e["id"]] = e
    log.append(f"ADD {e['id']}")

# ---------- 1. CN_PMI_MFG 历史链修正（值源：NBS 官方） ----------
CN_SRC = "官方源：国家统计局英文月报 PMI 表(2026年2月/5月报告)+8月解读页+新华网/央视网/gov.cn（2026-09-22 审计回填）"
rename("CN_PMI_MFG_20251229", "CN_PMI_MFG_20251231", period="2025-12", actual=50.1, previous=49.2, status="released",
       notes="2025-12 制造业PMI 50.1（NBS 英文月报表）；发布日按 NBS 规则 12/31（2026-09-22 日期根治）。" + CN_SRC)
rename("CN_PMI_MFG_20260201", "CN_PMI_MFG_20260131", period="2026-01", actual=49.3, previous=50.1, status="released",
       notes="2026-01 制造业PMI 49.3（NBS 英文月报表）；发布日 1/31（周六照发，先例同 8/31）。" + CN_SRC)
rename("CN_PMI_MFG_20260301", "CN_PMI_MFG_20260228", period="2026-02", actual=49.0, previous=49.3, status="released",
       notes="2026-02 制造业PMI 49.0（NBS 英文月报表）；发布日 2/28。" + CN_SRC)
rename("CN_PMI_MFG_20260330", "CN_PMI_MFG_20260331", period="2026-03", actual=50.4, previous=49.0, status="released",
       notes="2026-03 制造业PMI 50.4（NBS 英文月报表）；发布日 3/31。" + CN_SRC)
rename("CN_PMI_MFG_20260501", "CN_PMI_MFG_20260430", period="2026-04", actual=50.3, previous=50.4, status="released",
       notes="2026-04 制造业PMI 50.3（⚠️原库 50.5 系污染值，NBS 英文月报表修正）；发布日 4/30。" + CN_SRC)
rename("CN_PMI_MFG_20260601", "CN_PMI_MFG_20260531", period="2026-05", actual=50.0, previous=50.3, status="released",
       notes="2026-05 制造业PMI 50.0（⚠️原库 50.4 系污染值，NBS 英文月报表修正；与6月报告'上升0.3至50.3'咬合）；发布日 5/31。" + CN_SRC)
rename("CN_PMI_MFG_20260629", "CN_PMI_MFG_20260630", period="2026-06", actual=50.3, previous=50.0, status="released",
       notes="2026-06 制造业PMI 50.3 重返扩张（+0.3pp；NBS 解读页 t20260630_1964033+新华网+央视网+gov.cn 4源✅）；发布日 6/30。")
rename("CN_PMI_MFG_20260801", "CN_PMI_MFG_20260731", period="2026-07", actual=49.2, previous=50.3, status="released",
       notes="2026-07 制造业PMI 49.2（由8月官方报告'49.8 比上月上升0.6'反推，NBS 解读页+英文月报+央视+今日头条 4源✅；此前 7 月事件整月缺失）。")
patch("CN_PMI_MFG_20260831", period="2026-08", previous=49.2,
      notes_suffix="；8月官方解读：+0.6pp 回升，生产50.4/新订单50.6（+2.1pp），16/21 行业回升（霍丽慧解读 t20260831_1965155，4源✅）")
delete("CN_PMI_MFG_20260928")
delete("CN_PMI_MFG_20261101")

# ---------- CN_PMI_NONMFG ----------
rename("CN_PMI_NONMFG_20251229", "CN_PMI_NONMFG_20251231", period="2025-12")
rename("CN_PMI_NONMFG_20260201", "CN_PMI_NONMFG_20260131", period="2026-01")
rename("CN_PMI_NONMFG_20260301", "CN_PMI_NONMFG_20260228", period="2026-02")
rename("CN_PMI_NONMFG_20260330", "CN_PMI_NONMFG_20260331", period="2026-03")
rename("CN_PMI_NONMFG_20260501", "CN_PMI_NONMFG_20260430", period="2026-04")
rename("CN_PMI_NONMFG_20260601", "CN_PMI_NONMFG_20260531", period="2026-05", actual=50.1, status="released",
       notes="2026-05 非制造业商务活动指数 50.1（由6月官方报告'50.2 比上月上升0.1'反推；NBS 解读页）。")
rename("CN_PMI_NONMFG_20260629", "CN_PMI_NONMFG_20260630", period="2026-06", actual=50.2, previous=50.1, status="released",
       notes="2026-06 非制造业 50.2（+0.1pp；NBS 解读页+新华网 4源✅）；发布日 6/30。")
rename("CN_PMI_NONMFG_20260801", "CN_PMI_NONMFG_20260731", period="2026-07", actual=49.0, previous=50.2, status="released",
       notes="2026-07 非制造业 49.0（由8月官方报告'49.0 与上月持平'反推，4源✅；建筑业受暴雨台风影响 46.9）。")
patch("CN_PMI_NONMFG_20260831", period="2026-08",
      notes_suffix="；8月官方：49.0 与上月持平，服务业 49.3 持平/建筑业 46.9 -0.1pp（4源✅）")
delete("CN_PMI_NONMFG_20260928")
delete("CN_PMI_NONMFG_20261101")

# notes_suffix 合并处理
for e in events:
    sfx = e.pop("_notes_suffix_", None)
    if sfx:
        e["notes"] = (e.get("notes") or "") + sfx

# ---------- 2. EU_CPI_FLASH ----------
rename("EU_CPI_FLASH_20260831", "EU_CPI_FLASH_20260901", period="2026-08",
       notes="8月欧元区 flash CPI 3.3%（前 2.9%，financecalendar/Eurostat 双源✅）；发布日 9/1 11:00 CEST（Eurostat 官方 euro-indicators 日历确认，2026-09-22 日期根治——欧元区 flash 并非每月末发布，实际多为次月初）。")
delete("EU_CPI_FLASH_20260928")
delete("EU_CPI_FLASH_20261026")

# ---------- 3. US 日期根治 ----------
rename("US_NEW_HOME_SALES_20260925", "US_NEW_HOME_SALES_20260924",
       notes="发布日 9/24 10:00 ET（NY Fed 官方日历 i-sep26print，2026-09-22 根治；8月数据）。")
rename("US_DURABLE_GOODS_20260928", "US_DURABLE_GOODS_20260925",
       notes="发布日 9/25 08:30 ET（NY Fed 官方日历，2026-09-22 根治；8月耐用品订单初值）。")

# ---------- 4. 新增事件 ----------
add({
    "id": "US_CFNAI_20260921", "country": "US", "country_name": "美国",
    "indicator": "芝加哥联储全国活动指数", "indicator_en": "Chicago Fed National Activity Index (CFNAI)",
    "frequency": "月度", "importance": 1,
    "release_date": "2026-09-21", "release_time": "20:30", "timezone": "BJS",
    "period": "2026-08", "source": "Chicago Fed",
    "unit": "", "actual": -0.04, "forecast": -0.08, "previous": 0.08,
    "status": "released",
    "notes": "8月 CFNAI -0.04（预期 -0.08，低于零=低于历史平均趋势；7月由 -0.08 上修至 +0.08）；3个月移动平均 0.01、扩散指数 0.02；4分项中3项正贡献，生产相关转负-0.07。来源：芝加哥联储/FRED(9/21更新)+Morningstar(道琼斯)+Econoday 3源✅。",
})
add({
    "id": "US_RICHMOND_FED_20260825", "country": "US", "country_name": "美国",
    "indicator": "里士满联储制造业指数", "indicator_en": "Richmond Fed Manufacturing Index",
    "frequency": "月度", "importance": 2,
    "release_date": "2026-08-25", "release_time": "22:00", "timezone": "BJS",
    "period": "2026-08", "source": "Richmond Fed",
    "unit": "", "actual": 4, "forecast": 7, "previous": 5,
    "status": "released",
    "notes": "8月综合 4（预期7/前5，连续第2个月扩张但动能放缓）；出货11(前8)/新订单3(前5)/就业-2(前2)/积压-7(前4)/资本开支-5(前0)；服务业指数 -8（前-3，年内最低）。来源：TradingEconomics(引里士满联储)+MacroMicro+edgeX 3源✅。",
})
add({
    "id": "US_RICHMOND_FED_20260922", "country": "US", "country_name": "美国",
    "indicator": "里士满联储制造业指数", "indicator_en": "Richmond Fed Manufacturing Index",
    "frequency": "月度", "importance": 2,
    "release_date": "2026-09-22", "release_time": "22:00", "timezone": "BJS",
    "period": "2026-09", "source": "Richmond Fed",
    "unit": "", "previous": 4,
    "status": "upcoming",
    "notes": "今晚 10:00 ET（22:00 BJS）发布 9 月值；TE 模型预期 -1；前值 4（8月，预期7 不及预期）。2026 发布日历：每月第三个周二左右（Econoday 官方日程 3源✅）。",
})
add({
    "id": "US_PMI_FLASH_20260821", "country": "US", "country_name": "美国",
    "indicator": "S&P Global 综合PMI 初值", "indicator_en": "S&P Global US Composite PMI Flash",
    "frequency": "月度", "importance": 2,
    "release_date": "2026-08-21", "release_time": "21:45", "timezone": "BJS",
    "period": "2026-08", "source": "S&P Global",
    "unit": "", "actual": 56.0, "previous": 54.5,
    "status": "released",
    "notes": "8月综合 56.0（前54.5，52个月高）；制造业 53.2（预期53.9/前53.9，5个月低）、服务业 56.8（预期54.0/前54.6，20个月高）；Q3 年化增速近 3.0%（前 1.5%）。来源：S&P Global 官方新闻稿+Econoday+edgeX/Sharecast 3源✅。",
})
add({
    "id": "US_PMI_FLASH_20260923", "country": "US", "country_name": "美国",
    "indicator": "S&P Global 综合PMI 初值", "indicator_en": "S&P Global US Composite PMI Flash",
    "frequency": "月度", "importance": 2,
    "release_date": "2026-09-23", "release_time": "21:45", "timezone": "BJS",
    "period": "2026-09", "source": "S&P Global",
    "unit": "", "previous": 56.0,
    "status": "upcoming",
    "notes": "明晚 9/23 21:45 BJS 发布 9 月初值；前值综合 56.0/制造 53.2/服务 56.8；关注制造业降温延续与服务业是否回落。",
})

json.dump(cal, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(log))
print(f"Total events: {len(events)}")
