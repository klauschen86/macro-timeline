#!/usr/bin/env python3
"""Save Call 5 MCP results that are too large for inline writing"""
import json, os

mcp_data = {}

# Use the raw data from MCP call results saved in previous turn
raw_dir = r"C:\Users\chen8\.workbuddy\projects\d-WorkBuddy-2026-06-12-13-25-25-macro-timeline\596f102e-4ec3-49ac-bea9-8a6c27d708b2\tool-results"

# The call5 result was returned inline, let's write it from a temp approach
# Instead, use scripts/mcp_inject.py which reads data/mcp/*.json and processes it

# For now, just verify what files exist
mcp_dir = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline\data\mcp"
files = sorted(os.listdir(mcp_dir))
for f in files:
    fp = os.path.join(mcp_dir, f)
    with open(fp, 'r', encoding='utf-8') as fh:
        d = json.load(fh)
    print(f"{f}: {d.get('totalItems', 'N/A')} items, {len(json.dumps(d))} chars")

# Now check what's missing vs expected
expected = [
    'macro_calendar_future', 'macro_us_inflation', 'macro_us_employment',
    'macro_eu_inflation', 'macro_eu_employment', 'macro_eu_eco_growth',
    'macro_jp_inflation', 'macro_jp_employment',
    'macro_cpi_ppi', 'macro_pmi', 'macro_gdp', 'macro_forecast'
]
missing = [e for e in expected if f"{e}.json" not in files]
print(f"\nMissing: {missing}")
