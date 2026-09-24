#!/usr/bin/env python3
"""2026-09-23 推送核验：远程 calendar.json/JS blob SHA 与本地对比 + Pages 状态（ctypes 读凭据，避开 git credential fill 挂起坑）"""
import ctypes
import json
import subprocess
import sys
import urllib.request

BASE = r"D:\WorkBuddy\2026-06-12-13-25-25\macro-timeline"


class CREDENTIAL(ctypes.Structure):
    _fields_ = [("Flags", ctypes.c_uint32), ("Type", ctypes.c_uint32), ("TargetName", ctypes.c_wchar_p),
                ("Comment", ctypes.c_wchar_p), ("LastWritten", ctypes.c_uint64), ("CredentialBlobSize", ctypes.c_uint32),
                ("CredentialBlob", ctypes.c_void_p), ("Persist", ctypes.c_uint32), ("AttributeCount", ctypes.c_uint32),
                ("Attributes", ctypes.c_void_p), ("TargetAlias", ctypes.c_wchar_p), ("UserName", ctypes.c_wchar_p)]


advapi32 = ctypes.windll.advapi32
advapi32.CredReadW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
advapi32.CredReadW.restype = ctypes.c_int
pcred = ctypes.POINTER(CREDENTIAL)()
if not advapi32.CredReadW("git:https://github.com", 1, 0, ctypes.byref(pcred)):
    print("CredRead FAILED"); sys.exit(1)
cred = pcred.contents
TOKEN = ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize).decode("utf-16-le", errors="ignore").strip()
advapi32.CredFree(ctypes.cast(pcred, ctypes.c_void_p))

local = {}
for name, path in [("cal", "data/calendar.json"), ("js", "data/calendar_data.js")]:
    r = subprocess.run(["git", "hash-object", path], capture_output=True, text=True, cwd=BASE)
    local[name] = r.stdout.strip()

hdr = {"Authorization": "token " + TOKEN, "User-Agent": "macro-timeline-check", "Accept": "application/vnd.github+json"}
ok = True
for name, path in [("cal", "data/calendar.json"), ("js", "data/calendar_data.js")]:
    req = urllib.request.Request(f"https://api.github.com/repos/klauschen86/macro-timeline/contents/{path}?ref=main", headers=hdr)
    d = json.load(urllib.request.urlopen(req, timeout=30))
    match = d["sha"] == local[name]
    ok &= match
    print(f"{path}: remote={d['sha'][:8]} local={local[name][:8]} match={match}")

req = urllib.request.Request("https://klauschen86.github.io/macro-timeline/", headers={"User-Agent": "check"})
try:
    r = urllib.request.urlopen(req, timeout=30)
    print("Pages HTTP", r.status)
except Exception as ex:
    print("Pages check:", ex)

print("VERIFY", "PASS" if ok else "FAIL")
