# -*- coding: utf-8 -*-
"""合并式 API 推送 v5（分叉场景）：
远程 main 在本地分叉点 b8d4d6b 之后新增了 Actions commit (064a1ef -> e136c79, 仅改 calendar_data.js/update.log)。
本地 HEAD 683a55f 基于 b8d4d6b。本脚本以远程 HEAD tree 为 base_tree，
上传本地变更文件(calendar.json/calendar_data.js/scripts/_fix_20260905.py)，
保留远程 Actions 对 update.log 的追加，生成 parent=远程 HEAD 的新 commit 并更新 ref。
"""
import ctypes, json, subprocess, urllib.request, urllib.error, os, sys
from ctypes import wintypes

REPO = "klauschen86/macro-timeline"
BRANCH = "main"
BASE_DIR = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"
REMOTE_HEAD = "e136c79a235fb0192fecf0b9c44688e1b5f6d239"  # 远程当前 HEAD

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
pcred = ctypes.POINTER(CREDENTIAL)()
if not advapi32.CredReadW("git:https://github.com", 1, 0, ctypes.byref(pcred)):
    print("CredRead FAILED"); sys.exit(1)
cred = pcred.contents
TOKEN = ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize).decode("utf-16-le", errors="ignore")
advapi32.CredFree(ctypes.cast(pcred, ctypes.c_void_p))

def api(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "token " + TOKEN, "User-Agent": "macro-timeline-bot",
        "Content-Type": "application/json", "Accept": "application/vnd.github+json"})
    try:
        r = urllib.request.urlopen(req, timeout=40)
        return json.loads(r.read()) if r.read else {}
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {method} {url}")
        print(e.read().decode("utf-8", errors="ignore")[:800])
        raise

def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=BASE_DIR)
    return r.stdout.strip()

# 0. 复核远程 HEAD
ref = api("GET", f"https://api.github.com/repos/{REPO}/git/ref/heads/{BRANCH}")
cur_remote = ref["object"]["sha"]
print(f"当前远程 HEAD: {cur_remote[:10]}")
if cur_remote != REMOTE_HEAD:
    print("!! 远程 HEAD 已变化，请复核后重跑")
    sys.exit(1)

NEW_SHA = git("rev-parse", "HEAD")
MSG = git("log", "-1", "--format=%s")
print(f"本地 HEAD: {NEW_SHA[:10]}  {MSG}")

# 1. 远程 tree 作 base
old_commit = api("GET", f"https://api.github.com/repos/{REPO}/git/commits/{cur_remote}")
old_tree_sha = old_commit["tree"]["sha"]
print(f"远程 tree: {old_tree_sha}")

# 2. 上传本地变更文件 blob（覆盖式）
FILES_TO_PUSH = [
    "data/calendar.json",
    "data/calendar_data.js",
    "scripts/_fix_20260905.py",
]
tree_entries = []
for path in FILES_TO_PUSH:
    full = os.path.join(BASE_DIR, path.replace("/", os.sep))
    if not os.path.exists(full):
        print(f"  !! 本地缺失: {path}"); sys.exit(1)
    with open(full, "r", encoding="utf-8") as f:
        content = f.read()
    blob = api("POST", f"https://api.github.com/repos/{REPO}/git/blobs",
               {"content": content, "encoding": "utf-8"})
    tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    print(f"  blob {path}: {len(content)} bytes -> {blob['sha'][:7]}")

# 3. 新 tree (base=远程 tree, 仅覆盖变更文件, update.log 保留远程 Actions 追加)
new_tree = api("POST", f"https://api.github.com/repos/{REPO}/git/trees",
               {"base_tree": old_tree_sha, "tree": tree_entries})
print(f"新 tree: {new_tree['sha']}")

# 4. commit (parent = 远程 HEAD)
new_commit = api("POST", f"https://api.github.com/repos/{REPO}/git/commits",
                 {"message": MSG, "tree": new_tree["sha"], "parents": [cur_remote]})
print(f"新 commit: {new_commit['sha']}")

# 5. 更新 ref
upd = api("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}",
          {"sha": new_commit["sha"], "force": False})
print(f"ref 更新成功: {upd['object']['sha'][:10]}")
print("PUSH DONE (merge-style).")
