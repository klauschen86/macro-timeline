#!/usr/bin/env python3
"""
保存 MCP 数据：读取 _call3_raw.json + 其他已有文件，确保所有指标文件完整。
"""
import json, os, sys

MCP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mcp')
os.makedirs(MCP_DIR, exist_ok=True)

def save_indicator(data_block, filename):
    """保存单个指标到 MCP 文件"""
    fpath = os.path.join(MCP_DIR, filename)
    if isinstance(data_block, dict) and 'items' in data_block:
        out = {'ok': True, 'data': {filename.replace('.json', ''): data_block}}
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False)
        return len(data_block.get('items', []))
    return 0

# 1. 处理 _call3_raw.json（macro_eu_eco_growth + macro_eu_employment）
call3_path = os.path.join(MCP_DIR, '_call3_raw.json')
if os.path.exists(call3_path):
    with open(call3_path, 'r', encoding='utf-8') as f:
        call3 = json.load(f)
    for key, val in call3.get('data', {}).items():
        n = save_indicator(val, f'{key}.json')
        print(f'  [_call3] {key}.json: {n} items')
    # 删除临时文件
    os.remove(call3_path)
    print('  [cleanup] Removed _call3_raw.json')

# 2. 列出所有文件
all_files = sorted([f for f in os.listdir(MCP_DIR) if f.endswith('.json') and not f.startswith('_')])
print(f'\nTotal MCP data files: {len(all_files)}')
for f in all_files:
    size = os.path.getsize(os.path.join(MCP_DIR, f))
    print(f'  {f}: {size:,} bytes')

print('\nDone.')
