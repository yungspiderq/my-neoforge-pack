#!/usr/bin/env python3
"""Pin a compatible FTB XMod Compat version for FTB Library 2101.1.36.

Version 21.1.14 needs a newer FTB Library; avoid mixing APIs.
"""
import hashlib
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "21.1.11"
FILENAME = "ftb-xmod-compat-neoforge-" + VERSION + ".jar"
URL = (
    "https://maven.ftb.dev/releases/dev/ftb/mods/"
    "ftb-xmod-compat-neoforge/" + VERSION + "/" + FILENAME
)
OUT = ROOT / "mods/ftb-xmod-compat.pw.toml"

def get(url):
    with urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "MyNeoForgePack/0.3"}),
        timeout=90,
    ) as resp:
        return resp.read()

try:
    checksum = get(URL + ".sha1").decode("ascii", "replace").strip().split()[0]
except Exception:
    checksum = ""
if not re.fullmatch(r"[0-9a-fA-F]{40}", checksum):
    checksum = hashlib.sha1(get(URL)).hexdigest()
new = f"""name = "FTB XMod Compat"
filename = "{FILENAME}"
side = "both"

[download]
url = "{URL}"
hash-format = "sha1"
hash = "{checksum.lower()}"
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
if not OUT.exists() or OUT.read_text(encoding="utf-8") != new:
    OUT.write_text(new, encoding="utf-8")
print("Pinned FTB XMod Compat", VERSION, checksum.lower())
