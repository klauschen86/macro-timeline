#!/usr/bin/env python3
"""拆分 MCP 超大返回的临时文件 -> data/mcp/{listCode}.json

用法: python scripts/_split_mcp.py <临时文件路径>
将临时文件中的 {"data": {"xxx": {...}, "yyy": {...}}} 拆分为多个文件，
每个 key 保存为 data/mcp/{key}.json（保持 {"ok":true,"data":{key:{...}}} 结构）。
"""
import json
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
MCP_DIR = os.path.join(PROJECT_DIR, "data", "mcp")

def main():
    if len(sys.argv) < 2:
        print("usage: python _split_mcp.py <tempfile>")
        return
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)

    data = d.get("data", {})
    if not data:
        print("no data key")
        return

    os.makedirs(MCP_DIR, exist_ok=True)
    for key, val in data.items():
        out = {"ok": True, "data": {key: val}}
        out_path = os.path.join(MCP_DIR, f"{key}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        items = val.get("items", []) if isinstance(val, dict) else []
        print(f"  saved {key}.json (items={len(items)})")

if __name__ == "__main__":
    main()
