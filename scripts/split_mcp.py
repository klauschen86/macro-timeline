#!/usr/bin/env python3
"""Split combined MCP JSON results into individual indicator files."""
import json, os, sys

MCP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mcp")

def split_combined(filepath):
    """Read a combined MCP JSON (with multiple indicators in data{}) and split into individual files."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    inner = raw.get("data", raw)
    count = 0
    for key, val in inner.items():
        if isinstance(val, dict) and "items" in val:
            out_path = os.path.join(MCP_DIR, f"{key}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(val, f, ensure_ascii=False, indent=2)
            print(f"  -> {key}.json ({len(val.get('items',[]))} items)")
            count += 1
    
    return count

def main():
    combined_dir = os.path.join(MCP_DIR, "_combined")
    if os.path.isdir(combined_dir):
        for fname in sorted(os.listdir(combined_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(combined_dir, fname)
                print(f"Splitting {fname}...")
                split_combined(fpath)
    else:
        print("No _combined directory found, checking for combined files in mcp/...")
        for fname in sorted(os.listdir(MCP_DIR)):
            if fname.startswith("_combined") or "," in fname:
                fpath = os.path.join(MCP_DIR, fname)
                print(f"Splitting {fname}...")
                split_combined(fpath)

if __name__ == "__main__":
    main()
