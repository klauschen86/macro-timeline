#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_20260927.py — 2026-09-27（周日）补录与根治
背景：[Today] 为空（周日真无发布，ALFRED+汇通网双源核实），按"为空≠空转"先例修补日历缺漏。

内容：
1. 删除幽灵事件 US_ADP_20261007（9月ADP实际9/30发布=非农10/2前周三；
   10月首个周三10/7晚于非农，模式"每月首个周三"错位；DATE_OVERRIDES 已根治生成端，
   本脚本删除历史残留 id——pattern 不再生成该 id，删除稳定）
2. US_ADP_20260930 填 prev=3.8（8月ADP，9/2发布）
3. 新建 US_DALLAS_FED_20260928（9月达拉斯联储制造业，22:30 BJS，prev 11.6，FXStreet）
4. 新建 US_JOLTS_20260929（8月JOLTS，22:00 BJS，prev 727.1=7月actual，BLS）
5. 新建 US_GDP_FINAL_20260930（Q2 GDP终值，20:30 BJS，prev 1.5=二次估算，BEA官网）
   ⚠️ 同日启动2026年度国民账户更新（BEA官网：annual updates begin Sep 30），终值或含历史修订
6. 新建 US_PCE_20260930 / US_PCE_CORE_20260930（8月PCE，20:30 BJS与GDP终值同刻，
   prev 3.7/3.3=7月值，BEA官方PDF pi0726.pdf；8月CPI同比3.4/核心2.4为前瞻参考）
7. 新建 US_PENDING_HOME_SALES_20260917（released：8月成屋签约指数71.2，环比+0.3%
   低于预期+0.4；7月下修至71.0/-2.6%；同比-4.7%；Econoday+TE双源✅；9/17 22:00 BJS发布）
8. 新建 US_PENDING_HOME_SALES_20261020（9月数据，TE日历10/20 14:00 GMT=22:00 BJS，prev 71.2）
9. US_JOLTS_20260901 prev 735.9→718.2（6月大幅下修值，etnet/华尔街见闻双源）

运行：python scripts/_fix_20260927.py
"""
import json
import sys
from pathlib import Path

CAL = Path(__file__).resolve().parent.parent / "data" / "calendar.json"


def make_event(**kw):
    base = {
        "id": "", "country": "US", "country_name": "美国",
        "indicator": "", "indicator_en": "", "frequency": "月度", "importance": 3,
        "release_date": "", "release_time": "", "timezone": "BJS", "period": "",
        "source": "", "source_url": "", "unit": "",
        "actual": None, "forecast": None, "previous": None,
        "status": "upcoming", "notes": "",
    }
    base.update(kw)
    return base


def main():
    with open(CAL, encoding="utf-8") as f:
        data = json.load(f)
    events = data["events"]
    by_id = {e["id"]: e for e in events}
    changed = []

    # 1. 删除幽灵事件 US_ADP_20261007
    if "US_ADP_20261007" in by_id:
        events[:] = [e for e in events if e["id"] != "US_ADP_20261007"]
        changed.append("删除幽灵事件 US_ADP_20261007")
        by_id.pop("US_ADP_20261007")

    # 2. US_ADP_20260930 填 prev/notes
    e = by_id.get("US_ADP_20260930")
    if e:
        e["previous"] = 3.8
        e["period"] = "2026-09"
        e["notes"] = ("9月ADP就业 9/30 20:15 BJS 发布（10/2周五非农前最后一个周三；"
                      "prev=8月ADP 3.8万，9/2发布）。DATE_OVERRIDES 根治：模式'每月首个周三'"
                      "在10月错位（10/7晚于10/2非农），override改写为9/30。来源：Homebuyer日历+ADP惯例")
        changed.append("US_ADP_20260930 填 prev=3.8")

    # 3-8. 新建事件
    new_events = [
        make_event(
            id="US_DALLAS_FED_20260928", indicator="达拉斯联储制造业指数",
            indicator_en="Dallas Fed Manufacturing Business Index",
            release_date="2026-09-28", release_time="22:30", timezone="BJS",
            period="2026-09", source="Dallas Fed",
            source_url="https://www.dallasfed.org/research/survey/tmos", unit="",
            previous=11.6,
            notes=("9月达拉斯联储制造业展望调查（Texas Manufacturing Outlook Survey），"
                   "22:30 BJS（14:30 ET）发布；prev=8月 11.6（FXStreet）。"
                   "2026-09-27 补录：日历原缺整个达拉斯联储系列（下周要点多日提示'日历可能缺'）"),
        ),
        make_event(
            id="US_JOLTS_20260929", indicator="JOLTs 职位空缺",
            indicator_en="JOLTS Job Openings",
            release_date="2026-09-29", release_time="22:00", timezone="BJS",
            period="2026-08", source="BLS",
            source_url="https://www.bls.gov/jlt/", unit="万",
            previous=727.1,
            notes=("8月JOLTS职位空缺 9/29 22:00 BJS（10:00 ET，BLS官方fedratecalc双源）；"
                   "prev=7月727.1万（9/1发布，低于预期730-731.3万；6月大幅下修至718.2万）。"
                   "7月特征：'低招聘低解雇'——招聘505.4万(-27.8万)/裁员166.6万(-11.9万，1月来最低)/"
                   "主动离职305.6万(-15.7万)；制造业空缺2023年12月来最高。"
                   "⚠️JOLTS调查回应率从疫情前58%降至约30%，权重不宜过高（金十引）"),
        ),
        make_event(
            id="US_GDP_FINAL_20260930", indicator="GDP（环比年化终值）",
            indicator_en="GDP QoQ Final Estimate",
            release_date="2026-09-30", release_time="20:30", timezone="BJS",
            period="2026-Q2", source="BEA",
            source_url="https://www.bea.gov/", unit="%",
            previous=1.5,
            notes=("美国Q2 GDP终值（第三次估算）9/30 20:30 BJS（8:30 AM EDT）发布，"
                   "与8月PCE同刻。BEA官网Upcoming Releases确认（for-journalists页）。"
                   "prev=Q2二次估算+1.5%（8/26发布，与初值持平；Q1 +2.1%）。"
                   "⚠️2026年度国民账户更新同日启动（BEA官网：annual updates begin Sep 30, 2026，"
                   "GDP/GDI/个人收入等历史数据首次同日修订）——终值可能含年度修订，波动或超常规。"
                   "支持项：个人消费/企业投资/州地方政府支出；拖累项：净出口/库存/联邦政府支出"),
        ),
        make_event(
            id="US_PCE_20260930", indicator="PCE物价指数（同比）",
            indicator_en="PCE Price Index YoY",
            release_date="2026-09-30", release_time="20:30", timezone="BJS",
            period="2026-08", source="BEA",
            source_url="https://www.bea.gov/", unit="%",
            previous=3.7,
            notes=("8月PCE物价同比 9/30 20:30 BJS（8:30 AM EDT）发布（BEA官网PDF pi0726.pdf"
                   "'Next release: September 30, 2026'直接确认）；与Q2 GDP终值同刻。"
                   "prev=7月3.7%（7月环比+0.2%；收入+0.4%翻倍但实际PCE停滞0.0%，服务+862亿/"
                   "商品-499亿分化）。8月CPI同比3.4%（9/11发布）为PCE前瞻参考。"
                   "9/16 FOMC（加息25bp至3.75-4.00%）后首个PCE——10/28-29 FOMC 前核心通胀证据。"
                   "⚠️年度国民账户更新同日启动，历史序列或有修订"),
        ),
        make_event(
            id="US_PCE_CORE_20260930", indicator="核心PCE物价指数（同比）",
            indicator_en="Core PCE Price Index YoY",
            release_date="2026-09-30", release_time="20:30", timezone="BJS",
            period="2026-08", source="BEA",
            source_url="https://www.bea.gov/", unit="%",
            previous=3.3,
            notes=("8月核心PCE同比 9/30 20:30 BJS 发布（与PCE/GDP终值同刻）。"
                   "prev=7月3.3%（连续2月持平：6月3.3/7月3.3，BEA官方PDF；环比+0.2%）。"
                   "通胀距2%目标仍远：1-7月链=3.1/3.0/3.3/3.4/3.5/3.3/3.3（BEA月表）。"
                   "8月核心CPI 2.4%为前瞻参考；美联储官方通胀目标口径，"
                   "10/28-29 FOMC 关键输入（若粘性≥3.3%强化按兵不动）"),
        ),
        make_event(
            id="US_PENDING_HOME_SALES_20260917", indicator="成屋签约销售指数",
            indicator_en="Pending Home Sales Index",
            release_date="2026-09-17", release_time="22:00", timezone="BJS",
            period="2026-08", source="NAR",
            source_url="https://www.nar.realtor/", unit="",
            actual=71.2, forecast=None, previous=71.0, status="released",
            notes=("8月成屋签约指数71.2，环比+0.3%（预期+0.4%，略低；7月由71.2/-2.3%"
                   "下修至71.0/-2.6%）；同比-4.7%四大区域全降（南+2.3/西+3.0环比回升，"
                   "东北-4.2/中西-1.6）。签约量较疫前2019年低约30%。"
                   "高利率+创纪录房价压制；Yun：8月签约回升预示9月成屋销售环比小幅反弹。"
                   "来源：Econoday(quodd)+TE+NAR官方(GLOBE 8/18为7月值) 3源✅。"
                   "2026-09-27 补录历史：日历原缺整个Pending Home Sales系列。"
                   "⚠️investing.com 7月行显示actual 71.2系初值，已下修至71.0"),
        ),
        make_event(
            id="US_PENDING_HOME_SALES_20261020", indicator="成屋签约销售指数",
            indicator_en="Pending Home Sales Index",
            release_date="2026-10-20", release_time="22:00", timezone="BJS",
            period="2026-09", source="NAR",
            source_url="https://www.nar.realtor/", unit="",
            previous=71.2,
            notes=("9月成屋签约指数 10/20 22:00 BJS（14:00 GMT，TE日历确认）；"
                   "prev=8月71.2。NAR惯例每月约20日发布上月数据（investing历史：8/18/7/16/6/17），"
                   "模式化待后续；2026-09-27 补录"),
        ),
    ]
    added = []
    for ne in new_events:
        if ne["id"] not in by_id:
            events.append(ne)
            by_id[ne["id"]] = ne
            added.append(ne["id"])
            changed.append(f"新建 {ne['id']}")
        else:
            changed.append(f"跳过（已存在）{ne['id']}")

    # 9. US_JOLTS_20260901 prev 修正 735.9→718.2
    e = by_id.get("US_JOLTS_20260901")
    if e and float(e.get("previous") or 0) == 735.9:
        e["previous"] = 718.2
        e["notes"] = ("7月JOLTS职位空缺727.1万（预期730/6月大幅下修至718.2万——2025年以来"
                      "最大负面下修，初值735.9；9/1 22:00 BJS发布）。"
                      "prev字段2026-09-27由初值735.9修正为下修值718.2（etnet+华尔街见闻双源）")
        changed.append("US_JOLTS_20260901 prev 735.9→718.2")

    # 排序并保存（按 release_date, id 保持稳定）
    events.sort(key=lambda x: (x.get("release_date", ""), x.get("id", "")))
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n".join(changed))
    print(f"\nTotal events: {len(events)}")

    # 回读核验（9/22 踩坑：改名/修改后必须逐项回读）
    with open(CAL, encoding="utf-8") as f:
        data2 = json.load(f)
    ids2 = {e["id"] for e in data2["events"]}
    assert "US_ADP_20261007" not in ids2, "幽灵事件未删除！"
    for rid in added:
        assert rid in ids2, f"{rid} 未写入！"
    chk = {e["id"]: e for e in data2["events"]}
    assert chk["US_ADP_20260930"]["previous"] == 3.8
    assert chk["US_JOLTS_20260929"]["previous"] == 727.1
    assert chk["US_GDP_FINAL_20260930"]["previous"] == 1.5
    assert chk["US_PCE_20260930"]["previous"] == 3.7
    assert chk["US_PCE_CORE_20260930"]["previous"] == 3.3
    assert chk["US_PENDING_HOME_SALES_20260917"]["actual"] == 71.2
    assert chk["US_JOLTS_20260901"]["previous"] == 718.2
    # prev 链咬合：8月JOLTS prev == 7月JOLTS actual
    assert chk["US_JOLTS_20260929"]["previous"] == float(chk["US_JOLTS_20260901"]["actual"]), "JOLTS prev链断裂"
    print("\n回读核验全部通过 ✅")


if __name__ == "__main__":
    sys.exit(main())
