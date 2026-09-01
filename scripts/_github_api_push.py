# -*- coding: utf-8 -*-
"""Git Data API 推送：将本地变更文件推送到 GitHub main 分支（github.com 不可达时使用）。"""
import ctypes, json, urllib.request, urllib.error, os, sys
from ctypes import wintypes

REPO = "klauschen86/macro-timeline"
BRANCH = "main"

# 变更文件（相对仓库根路径）— 2026-08-31 批次（18 文件，与本地 commit b17e359 一致）
CHANGED = [
    "data/calendar.json",
    "data/calendar_data.js",
    "data/mcp/macro_calendar_future.json",
    "data/mcp/macro_us_inflation,macro_us_employment.json",
    "data/mcp/macro_eu_inflation,macro_eu_employment,macro_eu_eco_growth.json",
    "data/mcp/macro_jp_inflation,macro_jp_employment.json",
    "data/mcp/macro_cpi_ppi,macro_pmi,macro_gdp,macro_forecast.json",
    "data/mcp/macro_us_employment.json",
    "data/mcp/macro_us_inflation.json",
    "data/mcp/macro_eu_eco_growth.json",
    "data/mcp/macro_eu_employment.json",
    "data/mcp/macro_eu_inflation.json",
    "data/mcp/macro_jp_employment.json",
    "data/mcp/macro_jp_inflation.json",
    "data/mcp/macro_cpi_ppi.json",
    "data/mcp/macro_pmi.json",
    "data/mcp/macro_gdp.json",
    "data/mcp/macro_forecast.json",
]

BASE_DIR = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"

# ---- 读取 token ----
class CREDENTIAL_ATTRIBUTE(ctypes.Structure):
    _fields_ = [("Keyword", ctypes.c_wchar_p), ("Flags", wintypes.DWORD),
                ("ValueSize", wintypes.DWORD), ("Value", ctypes.POINTER(ctypes.c_byte))]

class CREDENTIAL(ctypes.Structure):
    _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                ("TargetName", ctypes.c_wchar_p), ("Comment", ctypes.c_wchar_p),
                ("LastWritten", ctypes.c_ulonglong), ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)), ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.POINTER(CREDENTIAL_ATTRIBUTE)),
                ("TargetAlias", ctypes.c_wchar_p), ("UserName", ctypes.c_wchar_p)]

advapi32 = ctypes.windll.advapi32
advapi32.CredReadW.argtypes = [ctypes.c_wchar_p, wintypes.DWORD, wintypes.DWORD,
                               ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
advapi32.CredReadW.restype = wintypes.BOOL
advapi32.CredFree.argtypes = [ctypes.c_void_p]

pcred = ctypes.POINTER(CREDENTIAL)()
if not advapi32.CredReadW("git:https://github.com", 1, 0, ctypes.byref(pcred)):
    print("CredRead FAILED"); sys.exit(1)
cred = pcred.contents
TOKEN = ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize).decode("utf-16-le", errors="ignore")
advapi32.CredFree(ctypes.cast(pcred, ctypes.c_void_p))


def api(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "token " + TOKEN,
        "User-Agent": "macro-timeline-bot",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    })
    try:
        r = urllib.request.urlopen(req, timeout=30)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {method} {url}")
        print(e.read().decode("utf-8", errors="ignore")[:500])
        raise


# 1. 获取远程 HEAD
ref = api("GET", f"https://api.github.com/repos/{REPO}/git/ref/heads/{BRANCH}")
old_commit_sha = ref["object"]["sha"]
print(f"远程 HEAD commit: {old_commit_sha}")

old_commit = api("GET", f"https://api.github.com/repos/{REPO}/git/commits/{old_commit_sha}")
old_tree_sha = old_commit["tree"]["sha"]
print(f"远程 tree: {old_tree_sha}")

# 2. 为每个变更文件创建 blob
tree_entries = []
for path in CHANGED:
    full = os.path.join(BASE_DIR, path.replace("/", os.sep))
    with open(full, "r", encoding="utf-8") as f:
        content = f.read()
    blob = api("POST", f"https://api.github.com/repos/{REPO}/git/blobs",
               {"content": content, "encoding": "utf-8"})
    tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    print(f"  blob {path}: {len(content)} bytes -> {blob['sha'][:7]}")

# 3. 创建新 tree（基于远程 tree）
new_tree = api("POST", f"https://api.github.com/repos/{REPO}/git/trees",
               {"base_tree": old_tree_sha, "tree": tree_entries})
new_tree_sha = new_tree["sha"]
print(f"新 tree: {new_tree_sha}")

# 4. 创建 commit
msg = "数据更新: 2026-08-31 (中国8月官方PMI 49.8/49.0 + 日本7月工业产出+0.1% MCP采集+双源验证)"
new_commit = api("POST", f"https://api.github.com/repos/{REPO}/git/commits",
                 {"message": msg, "tree": new_tree_sha, "parents": [old_commit_sha]})
new_commit_sha = new_commit["sha"]
print(f"新 commit: {new_commit_sha} ({msg})")

# 5. 更新 ref
upd = api("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}",
          {"sha": new_commit_sha, "force": True})
print(f"ref 更新成功: {upd['object']['sha'][:7]}")
print("PUSH DONE.")
