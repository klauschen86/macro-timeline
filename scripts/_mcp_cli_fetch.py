#!/usr/bin/env python3
"""
MCP 数据采集替代通道 v1.0 — 通过 westockdata CLI (--raw) 获取宏观数据
按自动化 v2.1 任务 5 组调用要求采集，包装为 mcp_inject.py 兼容格式保存到 data/mcp/。

调用映射（MCP listCode -> CLI 短名）：
  1. macro_calendar_future           -> cn_calendar_future --date <D>
  2. macro_us_inflation/employment   -> us_inflation,us_employment --date <D>
  3. macro_eu_inflation/employment/eco_growth -> eu_inflation,eu_employment,eu_eco_growth --date <D>
  4. macro_jp_inflation/employment   -> jp_inflation,jp_employment --date <D>
  5. macro_cpi_ppi/pmi/gdp/forecast  -> cn_cpi_ppi,cn_pmi,cn_gdp --year <Y>
"""
import json
import os
import subprocess
import sys
from datetime import date

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
MCP_DIR = os.path.join(PROJECT_DIR, "data", "mcp")
os.makedirs(MCP_DIR, exist_ok=True)

TODAY = date.today().strftime("%Y-%m-%d")
YEAR = date.today().year

# (listCode, CLI 短名列表, 参数)
CALLS = [
    ("macro_calendar_future", "cn_calendar_future", ["--date", TODAY]),
    ("macro_us_inflation,macro_us_employment", "us_inflation,us_employment", ["--date", TODAY]),
    ("macro_eu_inflation,macro_eu_employment,macro_eu_eco_growth", "eu_inflation,eu_employment,eu_eco_growth", ["--date", TODAY]),
    ("macro_jp_inflation,macro_jp_employment", "jp_inflation,jp_employment", ["--date", TODAY]),
    ("macro_cpi_ppi,macro_pmi,macro_gdp,macro_forecast", "cn_cpi_ppi,cn_pmi,cn_gdp", ["--year", str(YEAR)]),
]

def run_cli(short_names, args):
    npx_bin = "npx.cmd" if os.name == "nt" else "npx"
    cmd = [npx_bin, "-y", "westock-data-skillhub@1.0.5", "macro", "indicator", short_names, "--raw"] + args
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=240, shell=False)
    if r.returncode != 0:
        raise RuntimeError(f"CLI failed ({r.returncode}): {r.stderr[-500:]}")
    out = r.stdout.strip()
    data = json.loads(out)
    # 多指标调用返回 {"sections": [[...],[...]]}，展平为单列表
    if isinstance(data, dict) and "sections" in data:
        flat = []
        for sec in data["sections"]:
            if isinstance(sec, list):
                flat.extend(sec)
        return flat
    return data

def save_group(list_code_str, short_names, args):
    """执行一次 CLI 调用，把返回数组按 listCode 拆分保存"""
    raw = run_cli(short_names, args)
    if not isinstance(raw, list):
        print(f"  !! {short_names}: 非数组输出: {str(raw)[:200]}")
        return 0
    # 尝试拆分: 按 IndicatorName 前缀或直接整组保存
    codes = list_code_str.split(",")
    if len(codes) == 1:
        _save_one(codes[0], raw)
        return len(raw)
    # 多指标：CLI 无法区分每个指标的 items，整组保存到每个 code（inject 按 IndicatorName 匹配，无副作用）
    for c in codes:
        _save_one(c, raw)
    return len(raw)

def _save_one(list_code, items):
    payload = {
        "ok": True,
        "data": {
            list_code: {
                "date": TODAY,
                "items": items,
                "listCode": list_code,
            }
        },
    }
    fpath = os.path.join(MCP_DIR, f"{list_code}.json")
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"  saved {list_code}.json ({len(items)} items)")

def main():
    print(f"MCP CLI fetch: {TODAY}")
    total = 0
    for list_code_str, short_names, args in CALLS:
        print(f"[call] {short_names} {args}")
        try:
            n = save_group(list_code_str, short_names, args)
            total += n
            print(f"  -> {n} items")
        except Exception as e:
            print(f"  !! FAILED: {e}")
    print(f"\nTotal items: {total}")

if __name__ == "__main__":
    main()
