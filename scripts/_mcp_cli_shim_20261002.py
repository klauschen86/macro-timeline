# -*- coding: utf-8 -*-
"""2026-10-02 shim：bash 直调 westock CLI 落盘的 raw JSON -> data/mcp/ mcp_inject 兼容格式
（_mcp_cli_fetch.py 的 subprocess 在沙箱内被 SIGTERM，故拆两步执行）"""
import json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(PROJECT, 'data', 'mcp', '_raw')
MCP = os.path.join(PROJECT, 'data', 'mcp')
TODAY = '2026-10-02'

# (raw文件, listCode逗号串) —— 与 _mcp_cli_fetch.CALLS 一一对应
GROUPS = [
    ('raw1.json', 'macro_calendar_future'),
    ('raw2.json', 'macro_us_inflation,macro_us_employment'),
    ('raw3.json', 'macro_eu_inflation,macro_eu_employment,macro_eu_eco_growth'),
    ('raw4.json', 'macro_jp_inflation,macro_jp_employment'),
    ('raw5.json', 'macro_cpi_ppi,macro_pmi,macro_gdp,macro_forecast'),
]

def load_flat(fname):
    with open(os.path.join(RAW, fname), encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'sections' in data:
        flat = []
        for sec in data['sections']:
            if isinstance(sec, list):
                flat.extend(sec)
        return flat
    if isinstance(data, list):
        return data
    raise ValueError(f'{fname}: 非预期类型 {type(data)}')

def save_one(list_code, items):
    payload = {"ok": True, "data": {list_code: {"date": TODAY, "items": items, "listCode": list_code}}}
    with open(os.path.join(MCP, f'{list_code}.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f'  saved {list_code}.json ({len(items)} items)')

total = 0
for fname, codes in GROUPS:
    items = load_flat(fname)
    total += len(items)
    for c in codes.split(','):
        save_one(c, items)
print(f'Total items: {total}')
