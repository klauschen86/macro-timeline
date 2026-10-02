# -*- coding: utf-8 -*-
"""2026-09-29 推送核验：远程 blob SHA vs 本地 git hash-object + Pages 状态
仅用 Windows 凭据管理器读 token（git credential fill 本会话挂起老坑）"""
import ctypes, ctypes.wintypes as wintypes, json, subprocess, urllib.request, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

adv = ctypes.windll.advapi32
class CREDENTIAL(ctypes.Structure):
    _fields_ = [('Flags', ctypes.c_uint32), ('Type', ctypes.c_uint32),
                ('TargetName', ctypes.c_wchar_p), ('Comment', ctypes.c_wchar_p),
                ('LastWritten', ctypes.c_uint64), ('CredentialBlobSize', wintypes.DWORD),
                ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)), ('Persist', ctypes.c_uint32),
                ('AttributeCount', ctypes.c_uint32), ('Attributes', ctypes.c_void_p),
                ('TargetAlias', ctypes.c_wchar_p), ('UserName', ctypes.c_wchar_p)]
adv.CredReadW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
adv.CredReadW.restype = ctypes.c_int
adv.CredFree.argtypes = [ctypes.c_void_p]

def token():
    p = ctypes.POINTER(CREDENTIAL)()
    assert adv.CredReadW('git:https://github.com', 1, 0, ctypes.byref(p)), 'cred read fail'
    blob = ctypes.string_at(p.contents.CredentialBlob, p.contents.CredentialBlobSize)
    t = blob.decode('utf-16-le').strip()
    adv.CredFree(p)
    assert t.isascii(), 'token has non-ascii chars'
    return t

tok = token()
h = {'Authorization': 'token ' + tok, 'Accept': 'application/vnd.github+json'}
# ref 支持命令行参数（默认取本地 main 的 parent-free HEAD；硬编码 ref 为历史遗留）
import io as _io
if len(sys.argv) > 1:
    REMOTE_SHA = sys.argv[1]
else:
    REMOTE_SHA = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
req = urllib.request.Request(f'https://api.github.com/repos/klauschen86/macro-timeline/git/trees/{REMOTE_SHA}?recursive=1', headers=h)
tree = json.load(urllib.request.urlopen(req, timeout=30))
remote = {t['path']: t['sha'] for t in tree.get('tree', [])}
allok = True
for f in ('data/calendar.json', 'data/calendar_data.js'):
    local = subprocess.run(['git', 'hash-object', f], capture_output=True, text=True).stdout.strip()
    r = remote.get(f)
    ok = local == r
    if not ok:
        allok = False
    print(('MATCH ' if ok else 'MISMATCH ') + f + ' local=' + local[:8] + ' remote=' + (r or 'MISSING')[:8])
try:
    resp = urllib.request.urlopen('https://klauschen86.github.io/macro-timeline/', timeout=20)
    print('Pages:', resp.status)
except Exception as ex:
    print('Pages: FAIL', ex)
    allok = False
print('VERIFY ' + ('OK' if allok else 'FAILED'))
