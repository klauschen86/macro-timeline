# -*- coding: utf-8 -*-
"""
_fix_20261013.py — 2026-10-13 三项工作

背景：
  ① UK GDP 9/11 错误回填纠正（重大）：多源核实 GOV.UK官方引用+新华社英文9/11电+investingLive+GB News
     一致确认 7月GDP=+0.4%（大超预期0.0），6月+0.3%/5月0.0——日历中 actual=0.0/prev=0.4 系错误数据
     （旧 4 源内容与 ONS 官方矛盾，疑误读其他数据，现以官方多源纠正）。
  ② UK_GDP 日期根治：ONS 官方 release 页确认 8月数据 10/15 07:00 BST（14:00 BJS）发布，
     9月数据 11/12 07:00 GMT（15:00 BJS，Gate.io 单源待 ONS 核实）；
     原 UK_GDP_20261013/20261113 系模式错位事件，删除（DATE_OVERRIDES 已防回滚）。
  ③ 预填：今晚美成屋销售 fc=3.96M（22:00 BJS）；明晨美 CPI/核心CPI 共识（10/14 20:30 BJS）；
     PPI/零售 prev 链机械预填。

配套：generate_calendar.py DATE_OVERRIDES 已加 ("UK_GDP","2026-10"):"2026-10-15"、
     ("UK_GDP","2026-11"):"2026-11-12"（防 run_daily 回滚）。
"""
import json
import sys

CAL = "data/calendar.json"
MARK = "2026-10-13"

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

by_id = {e.get("id"): e for e in events}
log = []

# ---------- 1) 删除模式错位旧事件（upcoming 无数据，安全） ----------
for stale in ("UK_GDP_20261013", "UK_GDP_20261113"):
    e = by_id.get(stale)
    if e is None:
        log.append(f"SKIP {stale}(已删除)")
        continue
    if e.get("actual") is not None:
        log.append(f"REFUSE {stale} 含 actual，禁止删除"); continue
    events.remove(e)
    log.append(f"DELETE {stale} (模式错位,ONS官方10/15与11/12替代)")

# ---------- 2) UK_GDP_20260911 错误回填纠正 ----------
uk911 = by_id.get("UK_GDP_20260911")
if uk911 is not None:
    uk911["actual"] = 0.4
    uk911["previous"] = 0.3
    # forecast 0.0 保留（共识确为 0.0，实际大超）
    uk911["notes"] = (
        "| 2026-10-13数据纠正⚠️: 本事件 9/11 原回填 0.0%系错误数据,经 GOV.UK官方引用(建筑材料月报引ONS)"
        "+新华社英文9/11电+investingLive+GB News 4源核实纠正——英国7月GDP环比+0.4%(大超预期0.0),"
        "6月+0.3%/5月0.0%; 分项: 服务业+0.4%/生产+0.2%/建筑+0.1%; 3个月(5-7月)+0.4%(vs 2-4月),"
        "3个月服务业+0.6%/生产-0.5%/建筑-0.5%; 同比+1.6%(预期+1.0); AI/计算机编程为最大贡献"
        "(ONS统计总监Liz McKeown); 热浪+FIFA世界杯扰动分行业。原notes中'6月+0.4%/生产-0.9%'等均系误读,已废弃。"
        "| period=2026-07(发布月-2,ONS滞后约6周); 发布时点07:00伦敦时间(BST)=14:00 BJS。"
    )
    log.append("FIX UK_GDP_20260911 actual 0.0->0.4, previous 0.4->0.3 (数据纠正)")

# ---------- 3) UK_GDP_20261015 预填（ONS 官方 10/15 发布 8月数据） ----------
uk1015 = by_id.get("UK_GDP_20261015")
if uk1015 is not None:
    uk1015["forecast"] = -0.1
    uk1015["previous"] = 0.4
    append_notes(uk1015,
        "2026-10-13日期根治+预填: ONS官方release页(ons.gov.uk/releases/gdpmonthlyestimateukaugust2026timeseries)"
        "确认8月GDP于10/15 07:00 BST(14:00 BJS)发布,页面明示'not yet published'——原10/13系模式错位已删"
        "(DATE_OVERRIDES已根治)。共识: 环比-0.1%(siften/FXStreet市场前瞻,7月+0.4%后回落); "
        "⚠️10/15同日ONS将随Blue Book 2026年度国民账户修订重开全时间序列修订(Q2已从0.4%上修至0.5%),"
        "历史月度值或有调整。发布前复核共识。")
    log.append("FILL UK_GDP_20261015 fc=-0.1 prev=0.4")

# ---------- 4) UK_GDP_20261112 标注 ----------
uk1112 = by_id.get("UK_GDP_20261112")
if uk1112 is not None:
    append_notes(uk1112,
        "2026-10-13日期修正: 9月数据预计11/12 07:00 GMT(15:00 BJS)发布——Gate.io日历单源(⚠️待ONS官方核实),"
        "与ONS'滞后约6周+周四发布'惯例吻合; 原11/13系模式日期已删(DATE_OVERRIDES已预置)。发布前以ONS官方日历复核。")
    log.append("NOTE UK_GDP_20261112 (Gate单源,待ONS核实)")

# ---------- 5) US_EXISTING_HOME_20261013 预填 ----------
eh = by_id.get("US_EXISTING_HOME_20261013")
if eh is not None:
    eh["forecast"] = 3.96
    append_notes(eh,
        "2026-10-13预填: 9月成屋销售今晚22:00 BJS(10:00 ET,NAR)发布。共识3.96M SAAR"
        "(Admiral Markets/TradingEconomics 3.96✅,TE模型3.97/OneRoyal引NAR 3.97,分歧已标注),"
        "预期环比约-0.5%(8月3.98M连续3月降、同比约-2.5%); 背景: 成屋签约待售-4%m/m(2014春来最低,Redfin)、"
        "Redfin 14.5%交易取消率、Freddie Mac 30Y利率10/8升至7.40%(2023来最高)——但9月过户多反映7-8月签约"
        "(当时利率6.65-6.70%),10-11月数据才是高利率冲击窗口; 8月库存162万套/4.9个月供应、中位价$429,100(+1.6%y/y)。")
    log.append("FILL US_EXISTING_HOME_20261013 fc=3.96")

# ---------- 6) US_CPI_20261014 / US_CORE_CPI 预填 ----------
cpi = by_id.get("US_CPI_20261014")
if cpi is not None:
    cpi["forecast"] = 3.7
    append_notes(cpi,
        "2026-10-13预填: 9月CPI明晨20:30 BJS(10/14 08:30 ET,BLS)发布,FOMC(10/27-28)前最后一份通胀报告。"
        "共识同比3.6-3.7%(汇通财经/WSJ 3.7,FinancialJuice 3.6,Credit Agricole/DB 3.64,克利夫兰联储Nowcast 3.6,"
        "取区间上沿3.7,分歧已标注); 环比预期0.6%(8月0.4%,汽油+9.6%季节调整后主拉动,能源环比约+5.5%为3月来最大贡献); "
        "市场定价: CME 10月加息概率~19-25%(9月非农2.9万后大降)、12月~68%——核心环比(预期0.2%)比整体更关键,"
        "偏强则重燃10月押注。发布后明晨回填+妙想/tdx双源验证。")
    log.append("FILL US_CPI_20261014 fc=3.7")
core = by_id.get("US_CORE_CPI_20261014")
if core is not None:
    core["forecast"] = 2.5
    core["previous"] = 2.4
    append_notes(core,
        "2026-10-13预填: 核心CPI同比共识2.4-2.5%(FinancialJuice/WSJ 2.5,汇通/hedgwatch 2.4,DB 2.39,"
        "克利夫兰联储2.4,取2.5,分歧已标注); 环比预期0.2%(8月0.3%,8月电话服务方法论变更一次性跳升预计回吐,"
        "DB 0.16); 8月同比2.4%(prev)。")
    log.append("FILL US_CORE_CPI_20261014 fc=2.5 prev=2.4")

# ---------- 7) PPI/零售 prev 链机械预填 ----------
ppi = by_id.get("US_PPI_20261015")
if ppi is not None and ppi.get("previous") is None:
    ppi["previous"] = 5.4
    append_notes(ppi, "2026-10-13预填: prev=5.4(8月PPI同比,9/10官方回填值); 9月共识未成形,发布前补。")
    log.append("FILL US_PPI_20261015 prev=5.4")
ret = by_id.get("US_RETAIL_20261016")
if ret is not None and ret.get("previous") is None:
    ret["previous"] = 1.2
    append_notes(ret, "2026-10-13预填: prev=1.2(8月零售环比+1.2%,Census官方9/16发布,大超预期0.8); 9月共识未成形。")
    log.append("FILL US_RETAIL_20261016 prev=1.2")

# ---------- 8) 写回 ----------
if isinstance(data, dict):
    data["events"] = events
with open(CAL, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# ---------- 9) 回读 assert ----------
with open(CAL, encoding="utf-8") as f:
    data2 = json.load(f)
events2 = data2["events"] if isinstance(data2, dict) else data2
by2 = {e.get("id"): e for e in events2}
ok = True
if "UK_GDP_20261013" in by2 or "UK_GDP_20261113" in by2:
    print("ASSERT FAIL: 旧 UK_GDP 错位事件残留"); ok = False
e = by2.get("UK_GDP_20260911")
if e is None or e.get("actual") != 0.4 or e.get("previous") != 0.3 or "数据纠正" not in notes_of(e):
    print("ASSERT FAIL: UK_GDP_20260911 纠正未落地"); ok = False
for eid, checks in {
    "UK_GDP_20261015": {"forecast": -0.1, "previous": 0.4},
    "US_EXISTING_HOME_20261013": {"forecast": 3.96, "previous": 398},
    "US_CPI_20261014": {"forecast": 3.7, "previous": 3.4},
    "US_CORE_CPI_20261014": {"forecast": 2.5, "previous": 2.4},
    "US_PPI_20261015": {"previous": 5.4},
    "US_RETAIL_20261016": {"previous": 1.2},
}.items():
    e = by2.get(eid)
    if e is None:
        print(f"ASSERT FAIL: {eid} 不存在"); ok = False; continue
    for k, v in checks.items():
        if e.get(k) != v:
            print(f"ASSERT FAIL: {eid}.{k}={e.get(k)} 期望 {v}"); ok = False
    if MARK not in notes_of(e):
        print(f"ASSERT FAIL: {eid} notes 缺 marker"); ok = False

print("\n".join(log))

# ---------- 10) 重生成 JS（不走 generate+merge，防回滚） ----------
if ok:
    import run_daily
    run_daily.generate_js(data2)
    print("generate_js OK")
print("READBACK:", "ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
