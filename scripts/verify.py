#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — проверка, что автосинхронизация реально работает.

Прогоняет РОВНО ту же цепочку, что и packwiz-installer при каждом запуске игры,
но без Minecraft и без лаунчера. Отвечает на вопрос «а моды-то скачаются?»
однозначно, за ~10 секунд.

Что проверяется:
  1. pack.toml          доступен по HTTP
  2. index.toml         скачан, его sha256 совпадает с заявленным в pack.toml
                        (это защита от подмены/рассинхрона индекса)
  3. каждый mods/*.pw.toml  доступен и содержит [download]
  4. каждый .jar мода   реально скачивается и его sha1 совпадает с заявленным
  5. latest/instance.zip и latest/pack.mrpack  доступны, и внутри них
     packsync/pack-url.txt указывает на этот же пак
  6. (опционально) всё раскладывается в папку как при настоящей установке

Использование:
  python scripts/verify.py                       # полная проверка с закачкой jar-ов
  python scripts/verify.py --fast                # только HTTP-заголовки, без закачки
  python scripts/verify.py --dest /tmp/mc        # симулировать установку в папку
  python scripts/verify.py --side server         # проверить серверную сторону
  python scripts/verify.py --url https://...     # проверить другой адрес пака
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import posixpath
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

UA = "modpack-verify/1.0"
TIMEOUT = 60

GREEN = "\033[32m"; RED = "\033[31m"; YELLOW = "\033[33m"
CYAN = "\033[36m"; DIM = "\033[2m"; BOLD = "\033[1m"; RST = "\033[0m"

FAILURES = []


def ok(msg):    print("   %s OK %s  %s" % (GREEN, RST, msg))
def bad(msg):   print("   %s XX %s  %s" % (RED, RST, msg)); FAILURES.append(msg)
def warn(msg):  print("   %s !! %s  %s" % (YELLOW, RST, msg))
def note(msg):  print("   %s..%s   %s" % (DIM, RST, msg))
def head(msg):  print("\n%s%s%s" % (BOLD, msg, RST))


# --------------------------------------------------------------------------- #
#  HTTP
# --------------------------------------------------------------------------- #

def fetch(url: str, binary=False, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504, 520, 524) and i < retries - 1:
                time.sleep(2 ** i); last = e; continue
            raise
        except Exception as e:
            last = e
            if i < retries - 1:
                time.sleep(2 ** i); continue
            raise
    raise last


def head_only(url: str):
    """Возвращает (status, content_length) без скачивания тела."""
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            cl = r.headers.get("Content-Length")
            return r.status, (int(cl) if cl else None)
    except urllib.error.HTTPError as e:
        # некоторые CDN не любят HEAD — пробуем GET с обрывом
        if e.code == 405:
            req2 = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req2, timeout=TIMEOUT) as r:
                cl = r.headers.get("Content-Length")
                return r.status, (int(cl) if cl else None)
        return e.code, None


# --------------------------------------------------------------------------- #
#  Мини-парсер TOML (то же подмножество, что в pw.py)
# --------------------------------------------------------------------------- #

def parse_toml(text: str) -> dict:
    root, cur = {}, {}
    tables = {}
    cur_name = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\[\[(.+)\]\]$", line)
        if m:
            cur_name = m.group(1).strip()
            tables.setdefault(cur_name, []).append({})
            cur = tables[cur_name][-1]
            continue
        m = re.match(r"^\[(.+)\]$", line)
        if m:
            cur_name = m.group(1).strip()
            cur = root
            for part in cur_name.split("."):
                cur = cur.setdefault(part.strip(), {})
            continue
        m = re.match(r'^([A-Za-z0-9_\-]+)\s*=\s*(.*)$', line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if v.startswith("["):
            items = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            cur[k] = [i.strip('"') for i in items]
        elif v.startswith('"'):
            cur[k] = v.strip('"')
        elif v in ("true", "false"):
            cur[k] = (v == "true")
        else:
            cur[k] = v
    for name, lst in tables.items():
        root.setdefault(name, []).extend(lst)
    return root


# --------------------------------------------------------------------------- #
#  Проверки
# --------------------------------------------------------------------------- #

def check_pack_toml(base: str):
    head("1. pack.toml")
    url = base + "/pack.toml"
    try:
        text = fetch(url)
    except Exception as e:
        bad("не удалось получить %s: %s" % (url, e))
        bad("GitHub Pages не опубликован или адрес неверен")
        return None
    ok("%s  (%d байт)" % (url, len(text.encode())))
    p = parse_toml(text)
    for k in ("name", "version"):
        if p.get(k):
            note("%-16s %s" % (k + ":", p[k]))
    v = p.get("versions", {})
    note("%-16s %s" % ("minecraft:", v.get("minecraft", "?")))
    for ldr in ("neoforge", "forge", "fabric", "quilt"):
        if ldr in v:
            note("%-16s %s" % (ldr + ":", v[ldr]))
    idx = p.get("index", {})
    if not idx.get("file"):
        bad("в pack.toml нет [index].file")
        return None
    return p


def check_index(base: str, pack: dict):
    head("2. index.toml + цепочка целостности")
    idx = pack["index"]
    url = base + "/" + idx["file"]
    try:
        raw = fetch(url, binary=True)
    except Exception as e:
        bad("не удалось получить %s: %s" % (url, e))
        return {}
    ok("%s  (%d байт)" % (url, len(raw)))

    declared = idx.get("hash", "")
    fmt = idx.get("hash-format", "sha256")
    actual = hashlib.new(fmt, raw).hexdigest() if fmt in hashlib.algorithms_available else ""
    note("заявленный %s : %s" % (fmt, declared[:32] + ("…" if len(declared) > 32 else "")))
    note("фактический %s : %s" % (fmt, actual[:32] + ("…" if len(actual) > 32 else "")))
    if declared and declared == actual:
        ok("цепочка целостности pack.toml -> index.toml сходится")
    elif declared:
        bad("ХЭШ INDEX.TOML НЕ СХОДИТСЯ — пак рассинхронизирован, "
            "packwiz-installer откажется его ставить")
    else:
        warn("в pack.toml пустой hash — packwiz-installer пропустит проверку")

    entries = parse_toml(raw.decode("utf-8", "replace")).get("files", [])
    ok("в индексе файлов: %d" % len(entries))
    return {e["file"]: e for e in entries if isinstance(e, dict) and e.get("file")}


def check_metafiles(base: str, index: dict):
    head("3. Метаданные модов (mods/*.pw.toml)")
    metas = {k: v for k, v in index.items() if k.endswith(".pw.toml")}
    if not metas:
        warn("в паке НЕТ НИ ОДНОГО МОДА — проверять скачивание нечего")
        warn("добавьте моды:  python scripts/pw.py add jei")
        return []
    out = []
    for rel in sorted(metas):
        e = metas[rel]
        url = base + "/" + rel
        try:
            text = fetch(url)
        except Exception as ex:
            bad("%s недоступен: %s" % (rel, ex))
            continue
        declared = e.get("hash", "")
        actual = hashlib.sha256(text.encode()).hexdigest()
        if declared and declared != actual:
            bad("%s: sha256 в index.toml не совпадает с файлом" % rel)
            continue
        m = parse_toml(text)
        dl = m.get("download", {})
        if not dl.get("url"):
            bad("%s: нет [download].url" % rel)
            continue
        out.append({
            "meta": rel, "name": m.get("name", rel), "filename": m.get("filename", ""),
            "side": m.get("side", "both"), "url": dl["url"],
            "hash": dl.get("hash", ""), "hash_format": dl.get("hash-format", "sha1"),
        })
        ok("%-30s %s" % (rel, m.get("name", "")))
    return out


def check_downloads(mods, side_filter, fast, dest):
    head("4. Скачивание jar-ов модов")
    if not mods:
        note("проверять нечего")
        return
    wanted = [m for m in mods if m["side"] in ("both", side_filter)]
    skipped = [m for m in mods if m not in wanted]
    note("сторона '%s': %d модов к установке, %d пропускаем (другая сторона)"
         % (side_filter, len(wanted), len(skipped)))
    for m in skipped:
        note("   пропущен %-28s side=%s" % (m["name"][:28], m["side"]))

    total = 0
    print()
    for m in wanted:
        label = "%-26s" % m["name"][:26]
        if fast:
            st, size = head_only(m["url"])
            if st == 200:
                total += size or 0
                ok("%s %s  (%s)" % (label, "доступен",
                                    ("%.1f МБ" % (size / 1048576)) if size else "размер неизвестен"))
            else:
                bad("%s HTTP %s" % (label, st))
            continue
        try:
            t0 = time.time()
            data = fetch(m["url"], binary=True)
            dt = time.time() - t0
        except Exception as e:
            bad("%s не скачался: %s" % (label, e))
            continue
        total += len(data)
        hf = m["hash_format"]
        actual = hashlib.new(hf, data).hexdigest() if hf in hashlib.algorithms_available else ""
        if m["hash"] and actual != m["hash"]:
            bad("%s %s НЕ СОВПАЛ (ожидали %s, получили %s)"
                % (label, hf, m["hash"][:12], actual[:12]))
            continue
        speed = (len(data) / 1048576 / dt) if dt > 0 else 0
        ok("%s %.2f МБ  %s=%s…  %.1f МБ/с"
           % (label, len(data) / 1048576, hf, actual[:10], speed))
        if dest:
            sub = "mods" if m["filename"].endswith(".jar") else ""
            d = os.path.join(dest, sub) if sub else dest
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, m["filename"]), "wb") as fh:
                fh.write(data)
    print()
    ok("итого к скачиванию: %.2f МБ (%d файлов)" % (total / 1048576, len(wanted)))


def check_artifacts(base: str):
    head("5. Установочные артефакты на Pages")
    for name, kind in (("latest/instance.zip", "Prism/Freesm"),
                       ("latest/pack.mrpack", "AstralRinth/Modrinth")):
        url = base + "/" + name
        try:
            data = fetch(url, binary=True)
        except Exception as e:
            warn("%s недоступен (%s) — артефакты появятся после первого успешного pages.yml"
                 % (name, e))
            continue
        ok("%s  (%.2f МБ)" % (name, len(data) / 1048576))
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
        except Exception as e:
            bad("%s не является валидным zip: %s" % (name, e))
            continue
        names = z.namelist()
        hits = [n for n in names if n.endswith("packsync/pack-url.txt")]
        if not hits:
            bad("%s: внутри нет packsync/pack-url.txt — автосинк не заработает" % name)
            continue
        inner = z.read(hits[0]).decode("utf-8", "replace").strip()
        expected = base + "/pack.toml"
        if inner == expected:
            ok("   %s -> %s" % (hits[0], inner))
        else:
            bad("   %s указывает на %s, ожидали %s" % (hits[0], inner, expected))
        if kind == "Prism/Freesm":
            cfg = [n for n in names if n.endswith("instance.cfg")]
            if cfg:
                txt = z.read(cfg[0]).decode("utf-8", "replace")
                m = re.search(r"^PreLaunchCommand=(.*)$", txt, re.M)
                if not m:
                    bad("   instance.cfg: нет PreLaunchCommand — автосинка не будет")
                else:
                    cmd = m.group(1)
                    for need in ("packwiz-installer-bootstrap.jar", "--bootstrap-no-update",
                                 "--pack-folder", "-g", expected):
                        if need not in cmd:
                            bad("   PreLaunchCommand: отсутствует %r" % need)
                    if all(n in cmd for n in ("packwiz-installer-bootstrap.jar",
                                              "--bootstrap-no-update", "--pack-folder",
                                              "-g", expected)):
                        ok("   instance.cfg: PreLaunchCommand корректна")
                    moc = re.search(r"^OverrideCommands=(.*)$", txt, re.M)
                    if not moc or moc.group(1).strip() != "true":
                        bad("   instance.cfg: OverrideCommands не true — Prism проигнорирует команду")
                    else:
                        ok("   instance.cfg: OverrideCommands=true")
                    mjson = [n for n in names if n.endswith("mmc-pack.json")]
                    if mjson:
                        comp = json.loads(z.read(mjson[0]).decode("utf-8")).get("components", [])
                        uids = [(c.get("uid"), c.get("version")) for c in comp]
                        ok("   mmc-pack.json: %s" % ", ".join("%s=%s" % u for u in uids))
        else:
            mj = [n for n in names if n.endswith("modrinth.index.json")]
            if mj:
                man = json.loads(z.read(mj[0]).decode("utf-8"))
                ok("   modrinth.index.json: %d модов, deps=%s"
                   % (len(man.get("files", [])), man.get("dependencies")))
                if not man.get("files"):
                    warn("   в .mrpack нет модов — они придут только через hook (packwiz-installer)")


def write_report(base: str, mods, dest):
    head("6. Итог")
    if FAILURES:
        print("   %sПРОВАЛОВ: %d%s" % (RED, len(FAILURES), RST))
        for f in FAILURES:
            print("     - " + f)
        return 1
    print("   %sВСЁ РАБОТАЕТ%s — именно это и сделает packwiz-installer при запуске игры." % (GREEN, RST))
    print()
    print("   Адрес пака      : %s/pack.toml" % base)
    print("   Модов в паке    : %d" % len(mods))
    if dest:
        print("   Разложено в     : %s" % dest)
        print("   (сравните с тем, что появится в .minecraft/mods после запуска)")
    return 0


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(prog="verify.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    default = None
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pf = os.path.join(here, "packsync", "pack-url.txt")
    if os.path.isfile(pf):
        u = open(pf, encoding="utf-8").read().strip()
        if u and "REPLACE_ME" not in u:
            default = u.rsplit("/pack.toml", 1)[0]
    ap.add_argument("--url", default=default, help="базовый адрес пака (без /pack.toml)")
    ap.add_argument("--fast", action="store_true", help="не скачивать jar-ы, только HEAD")
    ap.add_argument("--dest", help="куда разложить скачанное (симуляция установки)")
    ap.add_argument("--side", default="client", choices=["client", "server", "both"])
    args = ap.parse_args()

    if not args.url:
        print("не задан адрес пака. Укажите --url https://<user>.github.io/<repo>",
              file=sys.stderr)
        return 2
    base = args.url.rstrip("/")

    print("%s%s Проверяю автосинхронизацию модпака %s" % (BOLD, CYAN, RST))
    print("   адрес: %s" % base)
    print("   режим: %s, сторона: %s" % ("быстрый (без закачки)" if args.fast else "полный",
                                         args.side))
    if args.dest:
        os.makedirs(args.dest, exist_ok=True)

    pack = check_pack_toml(base)
    if not pack:
        return write_report(base, [], args.dest)
    index = check_index(base, pack)
    mods = check_metafiles(base, index)
    check_downloads(mods, args.side, args.fast, args.dest)
    check_artifacts(base)
    return write_report(base, mods, args.dest)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nпрервано")
        sys.exit(130)
