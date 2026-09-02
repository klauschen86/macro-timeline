# -*- coding: utf-8 -*-
"""Git Data API 推送 v4（动态版）：将本地 HEAD 与远程 HEAD 之间的差异推送到 GitHub main。
git push 网络不可达时的可靠替代。自动获取 OLD/NEW SHA、diff 文件列表、commit message。
"""
import ctypes, json, subprocess, urllib.request, urllib.error, os, sys
from ctypes import wintypes

REPO = "klauschen86/macro-timeline"
BRANCH = "main"
BASE_DIR = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"

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


def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=BASE_DIR)
    return r.stdout.strip()


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


# 0. 动态获取 OLD(远程)/NEW(本地) SHA 与 commit message
NEW_SHA = git("rev-parse", "HEAD")
MSG = git("log", "-1", "--format=%s")
try:
    ref = api("GET", f"https://api.github.com/repos/{REPO}/git/ref/heads/{BRANCH}")
    OLD_SHA = ref["object"]["sha"]
except Exception as e:
    print(f"获取远程 HEAD 失败: {e}")
    sys.exit(1)

print(f"本地 HEAD: {NEW_SHA}  {MSG}")
print(f"远程 HEAD: {OLD_SHA}")

# 变更文件列表
r = subprocess.run(["git", "diff", "--name-status", OLD_SHA, NEW_SHA],
                   capture_output=True, text=True, cwd=BASE_DIR)
CHANGED = []
for line in r.stdout.strip().splitlines():
    parts = line.split("\t")
    if len(parts) >= 2:
        CHANGED.append((parts[0][0], parts[-1]))
print(f"变更文件: {len(CHANGED)}")
for s, p in CHANGED:
    print(f"  [{s}] {p}")

# 1. 远程 tree
old_commit = api("GET", f"https://api.github.com/repos/{REPO}/git/commits/{OLD_SHA}")
old_tree_sha = old_commit["tree"]["sha"]
print(f"远程 tree: {old_tree_sha}")

# 2. blob
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

# 3. 新 tree
new_tree = api("POST", f"https://api.github.com/repos/{REPO}/git/trees",
               {"base_tree": old_tree_sha, "tree": tree_entries})
print(f"新 tree: {new_tree['sha']}")

# 4. commit（parent = 远程 HEAD）
new_commit = api("POST", f"https://api.github.com/repos/{REPO}/git/commits",
                 {"message": MSG, "tree": new_tree["sha"], "parents": [OLD_SHA]})
print(f"新 commit: {new_commit['sha']}  ({MSG})")

# 5. 更新 ref
upd = api("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}",
          {"sha": new_commit["sha"], "force": False})
print(f"ref 更新成功: {upd['object']['sha'][:7]}")
print("PUSH DONE.")
