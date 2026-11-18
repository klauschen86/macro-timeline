#!/usr/bin/env python3
"""2026-11-18 修复：
①从 HEAD 还原 mcp_inject 错期值覆盖的污染事件（第7次复现，就地 e.clear()+e.update()）
②US_RETAIL_20261116：日期纠正 11-17（合并回滚复发）+ 回填 actual 0.2（财联社+新华财经+东财 3源✅）
③UK_CPI_20261117：日期纠正 → 2026-11-18 15:00 BJS（ONS 2026年10月CPI 实际 11-18 07:00 GMT 发布，
  Econoday 2026日历 + FXStreet/TIOmarkets 双源✅），本批次留 pending 待 11-19 回填
运行顺序：在 mcp_inject 之后、run_daily 之前执行主体；run_daily 后 b 轮再校日期并重生成 JS
"""
import json
import subprocess

CAL = "data/calendar.json"

# ---- ① 还原污染事件 ----
head_raw = subprocess.check_output(["git", "show", "HEAD:data/calendar.json"]).decode("utf-8")
head_events = {e["id"]: e for e in json.loads(head_raw)["events"]}
cur = json.load(open(CAL, encoding="utf-8"))

restored = []
for e in cur["events"]:
    h = head_events.get(e["id"])
    if h is None:
        continue
    if e != h:
        e.clear()
        e.update(h)  # 必须就地改对象，替换引用不生效（2026-11-11 踩坑）
        restored.append(e["id"])

# ---- ② 回填 + 日期纠正 ----
events = {e["id"]: e for e in cur["events"]}

e = events["US_RETAIL_20261116"]
e["release_date"] = "2026-11-17"
e["actual"] = 0.2
e["status"] = "released"
e["notes"] += (
    " | 【11-18回填】美10月零售销售环比+0.2%(7482亿美元,同比+6.8%),较9月0.8%明显放缓;"
    "剔除汽车+0.6%/剔除汽车和汽油+0.5%/控制组+0.6%(8月来最大,均高于预期0.3);"
    "汽车及零部件-1.6%/家具-2.3%(大件耐用品拖累)/非店铺零售+1.2%(同比+11.8%)。"
    "fc0.0系11-16预填共识,实际预期口径0.1-0.2(财联社0.1/东财0.2),偏差<0.2pct。"
    "来源:财联社11-17 + 新华财经 + 东方财富 3源✅"
)

e = events["UK_CPI_20261117"]
e["release_date"] = "2026-11-18"
e["time"] = "15:00"
e["notes"] += (
    " | 【11-18日期纠正】ONS 2026年10月CPI实际于11-18 07:00 GMT=15:00 BJS发布(日历原误标11-17);"
    "来源:Econoday 2026年发布日程表(11/18,For Oct 2026)+FXStreet/TIOmarkets 07:00 GMT 双源✅;"
    "本批次(11-18上午)留pending,待11-19回填actual;fc3.7/prev3.5维持"
)

with open(CAL, "w", encoding="utf-8") as f:
    json.dump(cur, f, ensure_ascii=False, indent=2)

# ---- ③ 写盘后回读 assert ----
chk = {e["id"]: e for e in json.load(open(CAL, encoding="utf-8"))["events"]}
assert chk["US_RETAIL_20261116"]["release_date"] == "2026-11-17"
assert chk["US_RETAIL_20261116"]["actual"] == 0.2
assert chk["US_RETAIL_20261116"]["status"] == "released"
assert chk["UK_CPI_20261117"]["release_date"] == "2026-11-18"
assert chk["UK_CPI_20261117"]["time"] == "15:00"
assert chk["UK_CPI_20261117"]["status"] in ("upcoming", "pending")  # HEAD还原后为upcoming,run_daily重跑后转pending
for eid in restored:
    if eid in ("US_RETAIL_20261116", "UK_CPI_20261117"):  # 二者为有意修正项,不校验与HEAD一致
        continue
    assert chk[eid] == head_events[eid], f"restore failed: {eid}"

print(f"还原污染事件 {len(restored)} 项: {restored}")
print("回填: US_RETAIL 0.2 released(11-17); UK_CPI→11-18 15:00 pending; JS待run_daily后重生成")
