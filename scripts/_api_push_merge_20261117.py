#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API 合并式推送 2026-11-10：远程 HEAD, github-actions 自动更新)为父，
推送本地完整树（数据严格超集，15 处 actual 差异以本地多源核实值为准）。"""
import json, subprocess, urllib.request, urllib.error, base64, sys

REPO = "klauschen86/macro-timeline"
BRANCH = "main"

# ---- token ----
r = subprocess.run(["git", "credential", "fill"],
                   input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True)
TOKEN = [l for l in r.stdout.splitlines() if l.startswith("password=")][0].split("=", 1)[1]
H = {"Authorization": "token " + TOKEN, "User-Agent": "macro-timeline-bot",
     "Content-Type": "application/json", "Accept": "application/vnd.github+json"}

def api(method, url, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=H)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {method} {url}\n" + e.read().decode(errors="ignore")[:300])
        raise

# 1. 本地完整树
ls = subprocess.run(["git", "ls-tree", "-r", "HEAD"], capture_output=True, text=True).stdout
local_files = {}
for line in ls.strip().splitlines():
    meta, path = line.split("\t", 1)
    mode, otype, sha = meta.split()
    local_files[path] = (mode, sha)
print(f"本地文件数: {len(local_files)}")

# 2. 远程 HEAD 与树
commit = api("GET", f"https://api.github.com/repos/{REPO}/commits/{BRANCH}")
REMOTE_HEAD = commit["sha"]
print(f"远程 HEAD: {REMOTE_HEAD[:10]} {commit['commit']['message'][:40]}")
base_tree_sha = commit["commit"]["tree"]["sha"]
rtree = api("GET", f"https://api.github.com/repos/{REPO}/git/trees/{base_tree_sha}?recursive=1")
remote_blobs = {t["path"]: t["sha"] for t in rtree["tree"] if t["type"] == "blob"}

# 远程独有路径（保留，由 base_tree 自动处理）
remote_only = sorted(set(remote_blobs) - set(local_files))
print(f"远程独有路径(保留): {remote_only}")

# 3. 上传本地新增/变更 blob
need_upload = [p for p, (m, s) in local_files.items() if remote_blobs.get(p) != s]
print(f"需上传 blob: {len(need_upload)}")
for p in need_upload:
    mode, sha = local_files[p]
    raw = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True).stdout
    b = api("POST", f"https://api.github.com/repos/{REPO}/git/blobs",
            {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
    assert b["sha"] == sha, f"blob sha mismatch for {p}: {b['sha']} != {sha}"

# 4. 创建树（完整覆盖本地所有文件，base_tree 保留远程独有）
entries = [{"path": p, "mode": (m if m in ("100644", "100755") else "100644"),
            "type": "blob", "sha": s} for p, (m, s) in local_files.items()]
new_tree = api("POST", f"https://api.github.com/repos/{REPO}/git/trees",
               {"base_tree": base_tree_sha, "tree": entries})
print(f"新树: {new_tree['sha'][:10]}")

# 5. 创建提交（父=远程 HEAD）
MSG = subprocess.run(["git", "log", "-1", "--format=%s"], capture_output=True, text=True).stdout.strip()
new_commit = api("POST", f"https://api.github.com/repos/{REPO}/git/commits",
                 {"message": MSG + " [API合并式推送: 以远程lineage为父, 本地数据为严格超集]",
                  "tree": new_tree["sha"], "parents": [REMOTE_HEAD]})
print(f"新提交: {new_commit['sha'][:10]}")

# 6. 更新 ref（fast-forward）
res = api("PATCH", f"https://api.github.com/repos/{REPO}/git/refs/heads/{BRANCH}",
          {"sha": new_commit["sha"], "force": False})
print(f"ref 更新: {res['object']['sha'][:10]}")

# 7. 验证远程 calendar.json blob = 本地
verify = api("GET", f"https://api.github.com/repos/{REPO}/git/trees/{new_commit['sha']}?recursive=1")
vmap = {t["path"]: t["sha"] for t in verify["tree"] if t["type"] == "blob"}
ok, bad = 0, []
for p, (m, s) in local_files.items():
    if vmap.get(p) == s:
        ok += 1
    else:
        bad.append(p)
print(f"blob 核验: {ok}/{len(local_files)} 一致; 不一致: {bad}")
sys.exit(0 if not bad else 2)
