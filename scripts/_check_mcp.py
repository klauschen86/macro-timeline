#!/usr/bin/env python3
"""Save MCP Call 5 results from original tool output to data/mcp/"""
import json, os

mcp_dir = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\mcp"

# Read data from a temp file that has the full call 5 result
# For now, we'll save the available data via direct MCP re-call
# through the inject script which will handle missing files gracefully

print("Checking existing MCP files...")
for f in sorted(os.listdir(mcp_dir)):
    fp = os.path.join(mcp_dir, f)
    with open(fp, 'r', encoding='utf-8') as fh:
        d = json.load(fh)
    print(f"  {f}: {d.get('totalItems', 'N/A')} items")

# Check what call 5 files are missing
need = ['macro_cpi_ppi', 'macro_pmi', 'macro_gdp', 'macro_forecast']
for n in need:
    fp = os.path.join(mcp_dir, f'{n}.json')
    if not os.path.exists(fp):
        print(f"  MISSING: {n}.json")
