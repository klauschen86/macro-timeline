# -*- coding: utf-8 -*-
"""Git Data API 推送 v3：将本地 commit 869c014 的变更推送到 GitHub main（git push 网络不可达时使用）。
按原 _github_api_push.py 方案：逐文件创建 blob -> 基于远程 tree 建新 tree -> 创建 commit -> 更新 ref。
变更文件列表由 git diff --name-status 3ac9f2d..869c014 动态获取。
"""
import ctypes, json, subprocess, urllib.request, urllib.error, os, sys
from ctypes import wintypes

REPO = "klauschen86/macro-timeline"
BRANCH = "main"
BASE_DIR = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"
OLD_SHA = "3ac9f2d07fe507fdaad7e54f39a380a3822b4063"   # 远程 HEAD（基线）
NEW_SHA = "869c014512227ed2813b4222b473fd65f3ea47cd"   # 本地待推送 commit
MSG = "数据更新: 2026-09-01 (财新PMI/ISM制造业PMI待发布, MCP CLI采集+双源验证, 合并远程Actions基线)"

# ---- 读取 Windows 凭据中的 GitHub token ----
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


# 0. 动态获取变更文件列表（相对远程基线）
r = subprocess.run(["git", "diff", "--name-status", OLD_SHA, NEW_SHA],
                   capture_output=True, text=True, cwd=BASE_DIR)
CHANGED = []
for line in r.stdout.strip().splitlines():
    parts = line.split("\t")
    if len(parts) >= 2:
        status = parts[0][0]  # A/M/D
        path = parts[-1]
        CHANGED.append((status, path))
print(f"变更文件: {len(CHANGED)}")
for s, p in CHANGED:
    print(f"  [{s}] {p}")

# 1. 获取远程 HEAD 与 tree
ref = api("GET", f"https://api.github.com/repos/{REPO}/git/ref/heads/{BRANCH}")
remote_head = ref["object"]["sha"]
print(f"\n远程 HEAD: {remote_head}")
assert remote_head == OLD_SHA, f"远程 HEAD 与预期不符: {remote_head}"

old_commit = api("GET", f"https://api.github.com/repos/{REPO}/git/commits/{remote_head}")
old_tree_sha = old_commit["tree"]["sha"]
print(f"远程 tree: {old_tree_sha}")

# 2. 为每个变更文件创建 blob / 记录删除
tree_entries = []
for status, path in CHANGED:
    full = os.path.join(BASE_DIR, path.replace("/", os.sep))
    if status == "D" or not os.path.exists(full):
        tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
        print(f"  [D] {path}")
        continue
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
print(f"\n新 tree: {new_tree_sha}")

# 4. 创建 commit
new_commit = api("POST", f"https://api.github.com/repos/{REPO}/git/commits",
                 {"message": MSG, "tree": new_tree_sha, "parents": [old_tree_sha and remote_head]})
new_commit_sha = new_commit["sha"]
print(f"新 commit: {new_commit_sha} ({MSG})")

# 5. 更新 ref
upd = api("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}",
          {"sha": new_commit_sha, "force": False})
print(f"ref 更新成功: {upd['object']['sha'][:7]}")
print("PUSH DONE.")
