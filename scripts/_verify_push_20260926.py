# -*- coding: utf-8 -*-
"""_verify_push_20260926.py — 推送后核验：远程 blob SHA vs 本地 git hash-object + Pages 状态"""
import sys, io, json, ctypes, subprocess, urllib.request
from ctypes import wintypes
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class CREDENTIAL_ATTRIBUTE(ctypes.Structure):
    _fields_ = [("Keyword", ctypes.c_wchar_p), ("Flags", wintypes.DWORD),
                ("ValueSize", wintypes.DWORD), ("Value", ctypes.POINTER(ctypes.c_byte))]
class CREDENTIAL(ctypes.Structure):
    _fields_ = [("Flags", ctypes.c_uint32), ("Type", ctypes.c_uint32),
                ("TargetName", ctypes.c_wchar_p), ("Comment", ctypes.c_wchar_p),
                ("LastWritten", ctypes.c_uint64), ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)), ("Persist", ctypes.c_uint32),
                ("AttributeCount", ctypes.c_uint32), ("Attributes", ctypes.POINTER(CREDENTIAL_ATTRIBUTE)),
                ("TargetAlias", ctypes.c_wchar_p), ("UserName", ctypes.c_wchar_p)]
adv = ctypes.windll.advapi32
adv.CredReadW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
adv.CredReadW.restype = ctypes.c_int
adv.CredFree.argtypes = [ctypes.c_void_p]
p = ctypes.POINTER(CREDENTIAL)()
assert adv.CredReadW("git:https://github.com", 1, 0, ctypes.byref(p)), "cred read fail"
blob = ctypes.string_at(p.contents.CredentialBlob, p.contents.CredentialBlobSize)
token = blob.decode('utf-16-le').strip()
adv.CredFree(p)

HDR = {'Authorization': f'token {token}', 'User-Agent': 'verify'}
REPO = 'klauschen86/macro-timeline'
OK = True
for f in ('data/calendar.json', 'data/calendar_data.js'):
    local = subprocess.run(['git', 'hash-object', f], capture_output=True, text=True).stdout.strip()
    url = f'https://api.github.com/repos/{REPO}/contents/{f}?ref=main'
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        remote = json.load(r)['sha']
    ok = local == remote
    OK = OK and ok
    print(f"{f}: local={local[:8]} remote={remote[:8]} {'MISMATCH!' if not ok else 'MATCH ✅'}")

try:
    req = urllib.request.Request('https://klauschen86.github.io/macro-timeline/', headers={'User-Agent': 'verify'})
    with urllib.request.urlopen(req, timeout=20) as r:
        print('Pages HTTP', r.status, '✅' if r.status == 200 else '')
except Exception as e:
    print('Pages check failed:', e)

head = urllib.request.Request(f'https://api.github.com/repos/{REPO}/commits/main', headers=HDR)
with urllib.request.urlopen(head, timeout=30) as r:
    c = json.load(r)
print('Remote HEAD:', c['sha'][:7], '-', c['commit']['message'].splitlines()[0])
print('ALL OK' if OK else 'VERIFY FAILED')
