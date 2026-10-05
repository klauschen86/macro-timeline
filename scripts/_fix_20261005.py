#!/usr/bin/env python3
"""
2026-10-05 修复补丁：
1. 10/2 已发布 3 项 notes 回填（非农 2.9万/失业率 4.2%/欧元区 flash CPI 3.8%，westock 注入 actual 已到位）
2. 今日事件预填：ISM 服务业 fc=55.7/prev=55.4；财新服务业 prev=50.7（今晨未出，国庆月或推迟）
3. prev 链预填：11/6 非农 prev=2.9、11/6 失业率 prev=4.2、11/4 EU flash CPI prev=3.8
4. 近期事件预填：EU_RETAIL_20261006 fc=0.3/prev=-0.6；US_JOBLESS_CLAIMS_20261008 fc=20.0/prev=19.7
5. 10/7 外储/黄金 prev、10/9 中国 CPI/PPI prev 预填
幂等：带 marker 检查，重复运行无副作用。
"""
import json
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAL = os.path.join(PROJ, "data", "calendar.json")

with open(CAL, encoding="utf-8") as f:
    data = json.load(f)

events = {e["id"]: e for e in data["events"]}
changes = []

def set_field(eid, field, value, label=""):
    e = events.get(eid)
    if e is None:
        print(f"  !! 事件不存在: {eid}")
        return
    old = e.get(field)
    if old == value:
        return
    e[field] = value
    changes.append(f"{eid}.{field}: {old} -> {value} {label}")

def notes_append(eid, marker, text):
    e = events.get(eid)
    if e is None:
        print(f"  !! 事件不存在: {eid}")
        return
    notes = e.get("notes") or ""
    # 幂等：marker 或文本前 15 字符任一命中即跳过（防 marker 未落地的历史脏追加）
    if marker in notes or text[:15] in notes:
        return
    e["notes"] = (notes + ("；" if notes and not notes.endswith("；") else "") + text) if notes else text
    changes.append(f"{eid}.notes += [{marker}]")

# ---- 1. 10/2 已发布 notes ----
notes_append("US_NFP_20261002", "M:20261005nfp",
    "9月非农仅+2.9万（预期9.0，华尔街口径8.4），大幅低于预期；⚠️8月16.2万下修至13.3万、7+8月合计净下修6万（prev已同步修正口径）；时薪环比+0.1%（预期0.3）/同比3.0%（预期3.1），工资增速或低于通胀；分项：医疗+1.7万放缓/建筑+1.1万/制造+0.9万，金融-0.7万（2025-05以来累计-12.9万），政府部门/信息业/专业商服为主要拖累；经济学家认为主因季节性调整失真而非实质转向（初请仍在57年低位、无大规模裁员）；市场：CME 10月按兵不动概率77.3%→84%、2Y收益率-6bp至4.73%、金上4227；BLS官方+中新社/光明网+财联社+证券时报 5源✅")
notes_append("US_UNEMPLOYMENT_20261002", "M:20261005unemp",
    "失业率4.2%（预期4.1/前值4.1，+0.1pp；3月以来区间4.1-4.3；黑人失业率升至7.0%；劳动参与率61.8%持平；BLS官方+中新社+财联社 多源✅）")
notes_append("EU_CPI_FLASH_20261002", "M:20261005eucpi",
    "欧元区9月flash CPI 3.8%（高于共识3.6/前值3.2，2023年9月来最高、连续3月加速；核心2.5%符合预期/前2.4%；能源18.8%（前14.3）主拉动、服务3.2%、食品烟酒1.4%、非能源工业品1.1%放缓；环比+0.6%（前0.4）；四大国：德3.3/法3.4/意4.1/西5.0；ECB 12月再加息概率~65%（money.it），ING主张12月保险式加息；Eurostat官方+新华+FXStreet+AMarkets 4源✅")

# ---- 2. 今日事件预填 ----
set_field("US_ISM_SERVICES_20261005", "forecast", 55.7, "ISM 9月共识")
set_field("US_ISM_SERVICES_20261005", "previous", 55.4, "8月actual")
notes_append("US_ISM_SERVICES_20261005", "M:20261005ism",
    "ISM 9月非制造业PMI共识55.7（FXEM+CMC+helious 3源一致；investingLive偏55.1已标注分歧；OneRoyal 55.0且8月值54.4错误弃用）；今晚22:00发布，关注物价支付分项（制造业9月77.9四个月高位的传导）")
set_field("CN_CAIXIN_SERVICES_PMI_20261005", "previous", 50.7, "8月actual")
notes_append("CN_CAIXIN_SERVICES_PMI_20261005", "M:20261005cxsvc",
    "9月财新服务业PMI原定今晨09:45发布，执行时（09:45+）未见报道；国庆月惯例常推迟至假期后（9/3记录：约10/9），日期需核对；无共识预填")

# ---- 3. 下月 prev 链预填 ----
set_field("US_NFP_20261106", "previous", 2.9, "9月actual")
set_field("US_UNEMPLOYMENT_20261106", "previous", 4.2, "9月actual")
set_field("EU_CPI_FLASH_20261104", "previous", 3.8, "9月flash actual")

# ---- 4. 近期事件预填 ----
set_field("EU_RETAIL_20261006", "forecast", 0.3, "investingLive共识")
set_field("EU_RETAIL_20261006", "previous", -0.6, "7月actual（9/8回填）")
notes_append("EU_RETAIL_20261006", "M:20261005euretail",
    "欧元区8月零售销售共识环比+0.3%（investingLive，前值-0.6%；明晚17:00发布）")
set_field("US_JOBLESS_CLAIMS_20261008", "forecast", 20.0, "investingLive共识")
set_field("US_JOBLESS_CLAIMS_20261008", "previous", 19.7, "10/1发布值")
notes_append("US_JOBLESS_CLAIMS_20261008", "M:20261005claims",
    "初请共识20.0万（investingLive；FXEM偏19.7万与前值持平口径已标注分歧；前值19.7）")

# ---- 5. 10/7 外储/黄金、10/9 中国 CPI/PPI prev ----
set_field("CN_FX_RESERVES_20261007", "previous", 34383, "8月末官方值")
set_field("CN_GOLD_RESERVES_20261007", "previous", 7673, "8月末官方值（万盎司）")
set_field("CN_CPI_20261009", "previous", 0.8, "8月actual")
set_field("CN_PPI_20261009", "previous", 3.8, "8月actual")

# ---- 校验 prev 链咬合（actual/previous 可能为字符串型，统一 float 比较）----
def fnum(v):
    return None if v is None else float(v)

assert fnum(events["US_NFP_20261002"]["actual"]) == 2.9, "非农 actual 异常"
assert fnum(events["US_NFP_20261002"]["previous"]) == 13.3, "非农 prev 应为8月修正值13.3"
assert fnum(events["US_UNEMPLOYMENT_20261002"]["actual"]) == 4.2
assert fnum(events["EU_CPI_FLASH_20261002"]["actual"]) == 3.8
assert fnum(events["US_ISM_SERVICES_20261005"]["previous"]) == 55.4 == fnum(events["US_ISM_SERVICES_20260903"]["actual"]), "ISM prev 链断裂"
assert fnum(events["CN_CAIXIN_SERVICES_PMI_20261005"]["previous"]) == 50.7 == fnum(events["CN_CAIXIN_SERVICES_PMI_20260903"]["actual"]), "财新服务业 prev 链断裂"
# previous 字段数值类型归一（历史字符串型隐患）
for eid in ("US_NFP_20261106", "US_UNEMPLOYMENT_20261106", "EU_CPI_FLASH_20261104",
            "EU_RETAIL_20261006", "US_JOBLESS_CLAIMS_20261008"):
    v = events[eid].get("previous")
    if isinstance(v, str) and v.replace(".", "").replace("-", "").isdigit():
        events[eid]["previous"] = float(v)
        changes.append(f"{eid}.previous 字符串归一 float")

if changes:
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"共 {len(changes)} 处修改已写回")
    for c in changes:
        print("  -", c)
else:
    print("无修改（幂等命中）")

# 回读验证
with open(CAL, encoding="utf-8") as f:
    rd = {e["id"]: e for e in json.load(f)["events"]}
assert fnum(rd["US_ISM_SERVICES_20261005"]["forecast"]) == 55.7
assert fnum(rd["US_NFP_20261106"]["previous"]) == 2.9
assert "9月非农仅+2.9万" in (rd["US_NFP_20261002"]["notes"] or "")
assert "flash CPI 3.8%" in (rd["EU_CPI_FLASH_20261002"]["notes"] or "")
print("回读验证 ALL OK")
