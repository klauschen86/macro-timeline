#!/usr/bin/env python3
"""
2026-09-02 人工补录脚本（自动化 v2.1 步骤 a2 兜底）
依据联网核实的权威数据（标普全球/ISM/欧盟统计局/美国劳工部/金十汇总）：
1. 回填 9/1 已发布事件实际值（财新制造业PMI 51.5 / ISM制造业PMI 54.6 / JOLTS 727.1万）
2. 回填 8/31 欧元区 CPI 初值 3.3%
3. 新增 9/2 发布事件（澳Q2 GDP已发 / 新西兰决议已发 / 韩国CPI / 美国ADP 20:15 / 加央行21:45 / 美国工厂订单22:00）
"""
import json

CAL = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\calendar.json"
data = json.load(open(CAL, encoding="utf-8"))
events = data["events"]
by_id = {e["id"]: e for e in events}

# ---------- 1. 更新已有事件实际值 ----------
updates = {
    "CN_CAIXIN_PMI_20260901": {
        "actual": 51.5, "forecast": 51.0, "previous": 50.9,
        "status": "released",
        "notes": "8月财新制造业PMI 51.5（预期51.0/前值50.9，环比升0.6pct，连续第9个月扩张；标普全球9/1发布）",
        "source_url": "https://www.caixin.com",
    },
    "US_ISM_MFG_20260901": {
        "actual": 54.6, "forecast": 55.2, "previous": 55.6,
        "status": "released",
        "notes": "8月ISM制造业PMI 54.6（预期55.2/前值55.6，回落1点但连续第8个月扩张；价格分项71.1高企）",
        "source_url": "https://www.ismworld.org",
    },
    "EU_CPI_FLASH_20260831": {
        "actual": 3.3, "forecast": 3.1, "previous": 2.9,
        "status": "released",
        "notes": "欧元区8月CPI初值同比3.3%（预期3.1%/前值2.9%，2023年9月以来最高；能源+14.3%，核心2.4%；实际发布9/1 17:00 BJS）",
        "source_url": "https://ec.europa.eu/eurostat",
    },
}
# JOLTS：calendar 中无 9/1 条目，单独新增（见下）

# ---------- 2. 新增 9/2 事件 ----------
new_events = [
    {
        "id": "US_JOLTS_20260901",
        "country": "US", "country_name": "美国",
        "indicator": "JOLTs 职位空缺", "indicator_en": "JOLTS Job Openings",
        "frequency": "月度", "importance": 3,
        "release_date": "2026-09-01", "release_time": "22:00", "timezone": "BJS",
        "period": "2026-07", "source": "美国劳工部", "source_url": "https://www.bls.gov/jlt/",
        "unit": "万", "actual": 727.1, "forecast": 730.0, "previous": 718.2,
        "status": "released",
        "notes": "7月JOLTS职位空缺727.1万（预期730/6月下修至718.2万，2025年以来最大负面下修；9/1 22:00 BJS发布）",
    },
    {
        "id": "AU_GDP_Q2_20260902",
        "country": "AU", "country_name": "澳大利亚",
        "indicator": "GDP（环比）", "indicator_en": "GDP QoQ",
        "frequency": "季度", "importance": 3,
        "release_date": "2026-09-02", "release_time": "09:30", "timezone": "BJS",
        "period": "2026-Q2", "source": "澳大利亚统计局", "source_url": "",
        "unit": "%", "actual": 0.3, "forecast": 0.2, "previous": None,
        "status": "released",
        "notes": "Q2 GDP环比+0.3%（预期+0.2%，金十9/2 09:30发布）",
    },
    {
        "id": "NZ_RBNZ_20260902",
        "country": "NZ", "country_name": "新西兰",
        "indicator": "联储利率决议", "indicator_en": "RBNZ Rate Decision",
        "frequency": "会议", "importance": 3,
        "release_date": "2026-09-02", "release_time": "10:00", "timezone": "BJS",
        "period": "2026-09", "source": "新西兰联储", "source_url": "",
        "unit": "%", "actual": None, "forecast": None, "previous": 2.25,
        "status": "pending",
        "notes": "MPS会议决议已发布（10:00 BJS）；表态逐步撤回货币刺激合适，2027-12 OCR预期3.15%；OCR具体值待权威确认",
    },
    {
        "id": "KR_CPI_20260902",
        "country": "KR", "country_name": "韩国",
        "indicator": "CPI（同比）", "indicator_en": "CPI YoY",
        "frequency": "月度", "importance": 2,
        "release_date": "2026-09-02", "release_time": "07:00", "timezone": "BJS",
        "period": "2026-08", "source": "韩国统计厅", "source_url": "",
        "unit": "%", "actual": None, "forecast": None, "previous": None,
        "status": "pending",
        "notes": "8月CPI已发布（金十列为今日关注），数值待权威源补录",
    },
    {
        "id": "US_ADP_20260902",
        "country": "US", "country_name": "美国",
        "indicator": "ADP 就业人数", "indicator_en": "ADP Employment Change",
        "frequency": "月度", "importance": 3,
        "release_date": "2026-09-02", "release_time": "20:15", "timezone": "BJS",
        "period": "2026-08", "source": "ADP", "source_url": "https://adpemploymentreport.com/",
        "unit": "万", "actual": None, "forecast": None, "previous": 4.4,
        "status": "upcoming",
        "notes": "8月ADP就业（20:15 BJS发布，非农前哨；7月为4.4万）",
    },
    {
        "id": "CA_BOC_20260902",
        "country": "CA", "country_name": "加拿大",
        "indicator": "央行利率决议", "indicator_en": "BoC Rate Decision",
        "frequency": "会议", "importance": 3,
        "release_date": "2026-09-02", "release_time": "21:45", "timezone": "BJS",
        "period": "2026-09", "source": "加拿大央行", "source_url": "",
        "unit": "%", "actual": None, "forecast": None, "previous": 2.25,
        "status": "upcoming",
        "notes": "9月利率决议（21:45 BJS，会后新闻发布会22:30；连续6次按兵不动后关注是否变动，油价飙升+贸易战背景）",
    },
    {
        "id": "US_FACTORY_ORDERS_20260902",
        "country": "US", "country_name": "美国",
        "indicator": "工厂订单（月率）", "indicator_en": "Factory Orders MoM",
        "frequency": "月度", "importance": 2,
        "release_date": "2026-09-02", "release_time": "22:00", "timezone": "BJS",
        "period": "2026-07", "source": "美国商务部", "source_url": "https://www.census.gov/manufacturing/m3/",
        "unit": "%", "actual": None, "forecast": None, "previous": None,
        "status": "upcoming",
        "notes": "7月工厂订单（22:00 BJS发布）",
    },
]

n_upd = n_new = 0
for eid, patch in updates.items():
    if eid in by_id:
        by_id[eid].update(patch)
        n_upd += 1
    else:
        print(f"  !! 未找到 {eid}")

for ne in new_events:
    if ne["id"] in by_id:
        print(f"  !! 已存在 {ne['id']}，跳过")
        continue
    events.append(ne)
    n_new += 1

data["events"] = events
json.dump(data, open(CAL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"更新 {n_upd} 个事件实际值，新增 {n_new} 个事件；总计 {len(events)} 事件")
