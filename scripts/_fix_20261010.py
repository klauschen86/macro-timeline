# -*- coding: utf-8 -*-
"""_fix_20261010.py — 2026-10-10 周六补录 10/9 晚发布 2 项 + 密歇根 10 月终值预填
1. CA_EMPLOYMENT_20261009  加拿大9月就业 -6.83万（预期+0.92万，远逊；新华财经+CBC+BNN Bloomberg 5源✅）
2. CA_UNEMPLOYMENT_20261009 加拿大9月失业率 6.5%（+0.1pp）
3. US_MICHIGAN_SENTIMENT_20261009 密歇根10月初值 46.3（现况44.7历史最低；UMich官网+TheStreet Pro+智通 多源✅）
4. US_MICHIGAN_SENTIMENT_20261023 终值 pending prev=46.3（UMich官网确认 10/23 10am ET）
幂等：存在同 id 则跳过新增；回读 assert 校验。
"""
import json, io, sys

CAL = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\calendar.json"

with io.open(CAL, encoding="utf-8") as f:
    data = json.load(f)
events = data["events"] if isinstance(data, dict) else data

NEW = [
    {
        "id": "CA_EMPLOYMENT_20261009", "country": "CA", "country_name": "加拿大",
        "indicator": "就业人数变动", "indicator_en": "Net Change in Employment",
        "release_date": "2026-10-09", "release_time": "20:30", "timezone": "BJS",
        "importance": 3,
        "actual": -6.83, "forecast": 0.92, "previous": -4.17,
        "unit": "万人", "status": "released",
        "source": "加拿大统计局", "source_url": "",
        "period": "2026-09",
        "notes": "9月就业 -6.83万（预期+0.92万，远逊；BNN Bloomberg 68,300精确口径）连续第二个月下滑（8月-4.17万），4-7月+18.1万回暖被两个月抹去大半；全职-3.5万/兼职-3.3万；公共部门-7.0万连续第4个月下滑（教育板块为主，教育服务-3.5万/医疗社会救助-2.3万/制造-1.3万），私营持平；青年15-24岁-4.8万、核心女性25-54岁-2.8万；魁省-4.9万/BC-2.0万/阿尔伯塔+2.3万；时薪同比2.3%（前2.0%）回升至37.64加元；参与率64.8%创除疫情外29年最低（老龄化+移民放缓）；失业再就业率30.6%低于历史均值36.5%；关税冲击首份完整报告月，美向行业流失未显著偏高；BOC 10/28决议前最后一份就业报告，市场预计10月按兵不动、12月或加息25bp；加元盘中-0.44%至1.4287、2Y债收益率-9.5bp至2.410%。来源：新华财经10/9×2+CBC+The Hub+BNN Bloomberg 5源✅",
    },
    {
        "id": "CA_UNEMPLOYMENT_20261009", "country": "CA", "country_name": "加拿大",
        "indicator": "失业率", "indicator_en": "Unemployment Rate",
        "release_date": "2026-10-09", "release_time": "20:30", "timezone": "BJS",
        "importance": 3,
        "actual": 6.5, "forecast": 6.5, "previous": 6.4,
        "unit": "%", "status": "released",
        "source": "加拿大统计局", "source_url": "",
        "period": "2026-09",
        "notes": "9月失业率 6.5%（+0.1pp，符合预期），回到1月水平（4月峰值6.9%后回落、7-8月稳定6.4%）；青年失业率13.0%基本持平，核心女性5.3%（+0.3pp）、核心男性5.8%（-0.2pp）；安省7.0%为大都省最高。来源：新华财经+CBC+The Hub 多源✅",
    },
    {
        "id": "US_MICHIGAN_SENTIMENT_20261009",
        "release_date": "2026-10-09", "period": "2026-10",
        "country": "US", "name": "密歇根大学消费者信心指数（初值）",
        "indicator": None, "release_time": "22:00", "timezone": "BJS",
        "forecast": 47.6, "previous": 48.1, "actual": 46.3,
        "status": "released", "unit": "",
        "notes": "10月初值 46.3（预期47.6/前值48.1，UMich官网+TheStreet Pro+智通财经/网易+ActiveInvestor引Newsquawk 多源✅），环比-3.7%，5月来最低、距5月历史低点44.8仅1.5点；现况指数44.7环比-12.2%创有记录以来最低（前50.9），耐用品购买条件历史最低（46%归因高物价为2022年8月来最多）；预期指数47.3环比+2.2%为7月来首次回升（前46.3）；1年通胀预期4.6%→4.7%、5-10年3.4%→3.5%均连续第2个月升至5月来最高（伊朗冲突前2月仅3.4%）；调查期9/22-10/5；低收入与小股票持仓群体信心降幅最陡；Hsu：各政治派别一致认为经济前景较年初恶化。注：TE10/9快照prev列48.1为9月终值口径。初值后续可能上修（11月前关注）。",
    },
    {
        "id": "US_MICHIGAN_SENTIMENT_20261023",
        "release_date": "2026-10-23", "period": "2026-10",
        "country": "US", "name": "密歇根大学消费者信心指数（终值）",
        "indicator": None, "release_time": "22:00", "timezone": "BJS",
        "forecast": None, "previous": 46.3, "actual": None,
        "status": "pending", "unit": "",
        "notes": "10月终值（UMich官网确认 10/23 10am ET=22:00 BJS）；prev=初值46.3，终值共识待发布前更新；9月初值47.8→终值48.1上修0.3的先例",
    },
]

existing = {e.get("id") for e in events}
added, skipped = [], []
for ev in NEW:
    if ev["id"] in existing:
        skipped.append(ev["id"])
        continue
    events.append(ev)
    added.append(ev["id"])

# 写盘
if added:
    with io.open(CAL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"已写盘 {len(added)} 条")

# 回读 assert
with io.open(CAL, encoding="utf-8") as f:
    data2 = json.load(f)
events2 = data2["events"] if isinstance(data2, dict) else data2
by_id = {e.get("id"): e for e in events2}

checks = [
    ("CA_EMPLOYMENT_20261009", -6.83, 0.92, -4.17),
    ("CA_UNEMPLOYMENT_20261009", 6.5, 6.5, 6.4),
    ("US_MICHIGAN_SENTIMENT_20261009", 46.3, 47.6, 48.1),
    ("US_MICHIGAN_SENTIMENT_20261023", None, None, 46.3),
]
ok = True
for eid, act, fc, prev in checks:
    e = by_id.get(eid)
    if not e:
        print(f"FAIL: {eid} 缺失"); ok = False; continue
    if (e.get("actual"), e.get("forecast"), e.get("previous")) != (act, fc, prev):
        print(f"FAIL: {eid} 字段不匹配 {(e.get('actual'), e.get('forecast'), e.get('previous'))}"); ok = False
    else:
        print(f"OK: {eid} actual={act} fc={fc} prev={prev} status={e.get('status')}")
# prev 链咬合
assert by_id["CA_EMPLOYMENT_20261009"]["previous"] == by_id["CA_EMPLOYMENT_20260904"]["actual"], "CA就业 prev链断裂"
assert by_id["CA_UNEMPLOYMENT_20261009"]["previous"] == by_id["CA_UNEMPLOYMENT_20260904"]["actual"], "CA失业率 prev链断裂"
assert by_id["US_MICHIGAN_SENTIMENT_20261009"]["previous"] == by_id["US_MICHIGAN_SENTIMENT_20260925"]["actual"], "密歇根 prev链断裂"
print("prev链咬合 assert 全部通过")
print(f"新增 {len(added)}: {added}")
if skipped: print(f"跳过(已存在): {skipped}")
print("ALL OK" if ok else "HAS FAILURES")
