#!/usr/bin/env python3
"""Save MCP Call 5 results.
The raw data is too large for inline, so we use a cached JSON file approach.
Actually, let's just use this as a validator to check if all 12 MCP files have proper data."""
import json, os, sys

mcp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mcp")
expected = {
    'macro_calendar_future.json': 15,
    'macro_us_inflation.json': 250,
    'macro_us_employment.json': 396,
    'macro_eu_inflation.json': 126,
    'macro_eu_employment.json': 12,
    'macro_eu_eco_growth.json': 24,
    'macro_jp_inflation.json': 35,
    'macro_jp_employment.json': 36,
    'macro_cpi_ppi.json': 18,
    'macro_pmi.json': 6,
    'macro_gdp.json': 2,
    'macro_forecast.json': 12,
}

all_ok = True
for fn, expected_items in expected.items():
    fp = os.path.join(mcp_dir, fn)
    if not os.path.exists(fp):
        print(f"MISSING: {fn}")
        all_ok = False
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    items = d.get('items', [])
    if len(items) != expected_items:
        print(f"WRONG: {fn} has {len(items)} items, expected {expected_items}")
        all_ok = False
    else:
        print(f"OK: {fn} ({len(items)} items)")

if all_ok:
    print("\nAll 12 MCP files validated successfully!")
    sys.exit(0)
else:
    print("\nSome files are missing or have wrong counts!")
    sys.exit(1)
