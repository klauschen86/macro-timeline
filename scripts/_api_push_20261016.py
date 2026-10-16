# -*- coding: utf-8 -*-
"""Git Data API 推送 v5（2026-10-16 批次新生成，禁止跨批复用）。
同 v5 方法：纯 API 递归树比对（远程 tree?recursive=1 vs 本地 git ls-tree -r HEAD，
按 blob SHA 比对），base_tree=远程树仅提交差异文件，commit parent=远程 HEAD。
"""
import ctypes, json, subprocess, urllib.request, urllib.error, os, sys
from ctypes import wintypes

REPO = "klauschen86/macro-timeline"
BRANCH = "main"
BASE_DIR = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"

class CREDENTIAL(ctypes.Structure):
    _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                ("TargetName", ctypes.c_wchar_p), ("Comment", ctypes.c_wchar_p),
                ("LastWritten", ctypes.c_ulonglong), ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)), ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
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
        "Authorization": "token " + TOKEN,
        "User-Agent": "macro-timeline-bot",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    })
    try:
        r = urllib.request.urlopen(req, timeout=60)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {method} {url}")
        print(e.read().decode("utf-8", errors="ignore")[:300])
        raise

def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=BASE_DIR)

NEW_SHA = git("rev-parse", "HEAD").stdout.strip()
MSG = git("log", "-1", "--format=%s").stdout.strip()
print(f"本地 HEAD: {NEW_SHA}  {MSG}")

ref = api("GET", f"https://api.github.com/repos/{REPO}/git/ref/heads/{BRANCH}")
OLD_SHA = ref["object"]["sha"]
print(f"远程 HEAD: {OLD_SHA}")
if OLD_SHA == NEW_SHA:
    print("远程与本地一致，无需推送"); sys.exit(0)

old_commit = api("GET", f"https://api.github.com/repos/{REPO}/git/commits/{OLD_SHA}")
old_tree_sha = old_commit["tree"]["sha"]

remote_tree = api("GET", f"https://api.github.com/repos/{REPO}/git/trees/{old_tree_sha}?recursive=1")
remote_blobs = {t["path"]: t["sha"] for t in remote_tree.get("tree", []) if t["type"] == "blob"}
print(f"远程文件数: {len(remote_blobs)}")

r = git("ls-tree", "-r", "HEAD")
local_blobs = {}
for line in r.stdout.strip().splitlines():
    meta, path = line.split("\t", 1)
    sha = meta.split()[2]
    local_blobs[path] = sha
print(f"本地文件数: {len(local_blobs)}")

changed = [p for p in local_blobs if remote_blobs.get(p) != local_blobs[p]]
deleted = [p for p in remote_blobs if p not in local_blobs]
print(f"变更(内容/新增): {len(changed)}, 删除: {len(deleted)}")
for p in changed[:50]:
    print(f"  [M/A] {p}")
for p in deleted[:20]:
    print(f"  [D] {p}")

entries = []
for p in deleted:
    entries.append({"path": p, "mode": "100644", "type": "blob", "sha": None})
for p in changed:
    if remote_blobs.get(p) == local_blobs[p]:
        continue
    full = os.path.join(BASE_DIR, p.replace("/", os.sep))
    try:
        with open(full, "r", encoding="utf-8") as f:
            content = f.read()
        enc = "utf-8"
    except UnicodeDecodeError:
        import base64
        with open(full, "rb") as f:
            content = base64.b64encode(f.read()).decode("ascii")
        enc = "base64"
    blob = api("POST", f"https://api.github.com/repos/{REPO}/git/blobs",
               {"content": content, "encoding": enc})
    entries.append({"path": p, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    print(f"  blob {p}: {blob['sha'][:7]}")

new_tree = api("POST", f"https://api.github.com/repos/{REPO}/git/trees",
               {"base_tree": old_tree_sha, "tree": entries})
print(f"新 tree: {new_tree['sha']}")

new_commit = api("POST", f"https://api.github.com/repos/{REPO}/git/commits",
                 {"message": MSG, "tree": new_tree["sha"], "parents": [OLD_SHA]})
print(f"新 commit: {new_commit['sha']}")

upd = api("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}",
          {"sha": new_commit["sha"], "force": False})
print(f"ref 更新成功: {upd['object']['sha'][:7]}")
print("PUSH DONE.")
