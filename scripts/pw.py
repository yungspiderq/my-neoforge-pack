#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pw.py — универсальный инструмент для ведения модпака в формате packwiz.

Работает на Python 3.8+ без сторонних зависимостей (только стандартная библиотека).
Официальный `packwiz` (Go) при этом остаётся «истиной в последней инстанции»:
CI на GitHub Actions прогоняет `packwiz refresh` / `packwiz modrinth export`
перед каждой публикацией, так что даже если этот скрипт где-то разойдётся
с packwiz — опубликованный пак всё равно будет корректным.

Команды:
  add MOD [MOD ...]      добавить мод(ы) с Modrinth (slug или ID)
  add-url NAME URL       добавить файл по прямой ссылке
  remove MOD [MOD ...]   удалить мод(ы)
  update [MOD ...|--all] обновить версии модов с Modrinth
  list                   показать список модов
  refresh                пересобрать index.toml
  check                  проверить целостность пака
  set-url URL            записать адрес пака в packsync/pack-url.txt
  show-url               показать текущий адрес пака
  versions               показать версии MC / NeoForge из pack.toml
  site [--out DIR]       собрать payload для GitHub Pages
  mrpack [--out FILE]    собрать .mrpack (Modrinth / AstralRinth)
  inject-packsync FILE   доложить packsync/* внутрь готового .mrpack
  instance [--out FILE]  собрать zip-инстанс для Prism / Freesm
  serve [--port N]       локальный HTTP-сервер для теста (http://localhost:8080/pack.toml)
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import socketserver
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from http.server import SimpleHTTPRequestHandler

# --------------------------------------------------------------------------- #
#  Пути
# --------------------------------------------------------------------------- #

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)

PACK_TOML = os.path.join(ROOT, "pack.toml")
INDEX_TOML = os.path.join(ROOT, "index.toml")
PACKWIZIGNORE = os.path.join(ROOT, ".packwizignore")
MODS_DIR = os.path.join(ROOT, "mods")
PACKSYNC_DIR = os.path.join(ROOT, "packsync")
PACK_URL_FILE = os.path.join(PACKSYNC_DIR, "pack-url.txt")
INSTANCE_TEMPLATE = os.path.join(ROOT, "instance-template")

USER_AGENT = "packwiz-modpack-tool/1.0 (https://github.com/packwiz/packwiz)"
MODRINTH_API = "https://api.modrinth.com/v2/"

IGNORE_DEFAULTS = [
    ".git/**",
    ".gitattributes",
    ".gitignore",
    ".DS_Store",
    "/*.zip",
    "*.mrpack",
    "packwiz.exe",
    "packwiz",
]


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print("\033[31mОШИБКА:\033[0m " + msg, file=sys.stderr)
    raise SystemExit(1)


def info(msg: str) -> None:
    print("\033[36m::\033[0m " + msg)


def ok(msg: str) -> None:
    print("\033[32m OK\033[0m " + msg)


# --------------------------------------------------------------------------- #
#  Мини-парсер TOML (подмножество, достаточное для packwiz-файлов)
# --------------------------------------------------------------------------- #

def _parse_value(raw: str, lines: list, idx: int):
    """Возвращает (значение, новый_idx)."""
    raw = raw.strip()
    if raw.startswith("["):
        # массив; может быть многострочным
        buf = raw
        while buf.count("[") > buf.count("]") and idx + 1 < len(lines):
            idx += 1
            buf += " " + lines[idx].strip()
        inner = buf.strip()[1:-1]
        items = [x.strip() for x in re.split(r",(?![^\[]*\])", inner) if x.strip()]
        return [_unquote(i) for i in items], idx
    return _unquote(raw), idx


def _unquote(tok: str):
    tok = tok.strip()
    if tok.startswith('"""') or tok.startswith("'''"):
        return tok[3:-3]
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "\"'":
        return tok[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if tok in ("true", "false"):
        return tok == "true"
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(tok)
    except ValueError:
        pass
    return tok


def read_toml(path: str) -> dict:
    """Очень маленький парсер TOML: таблицы, строки, bool, числа, массивы строк."""
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    root: dict = {}
    cur = root
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        i += 1
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("["):
            name = stripped.strip("[]").strip()
            cur = root
            for part in name.split("."):
                part = part.strip().strip('"')
                cur = cur.setdefault(part, {})
            continue
        m = re.match(r'^([A-Za-z0-9_\-."]+)\s*=\s*(.*)$', stripped)
        if not m:
            continue
        key = m.group(1).strip().strip('"')
        value, i = _parse_value(m.group(2), lines, i - 1)
        i += 1
        cur[key] = value
    return root


# --------------------------------------------------------------------------- #
#  .packwizignore (подмножество gitignore-синтаксиса)
# --------------------------------------------------------------------------- #

class Ignore:
    def __init__(self, patterns):
        self.rules = []
        for pat in patterns:
            pat = pat.strip()
            if not pat or pat.startswith("#"):
                continue
            negate = pat.startswith("!")
            if negate:
                pat = pat[1:]
            anchored = pat.startswith("/")
            pat = pat.lstrip("/")
            dir_only = pat.endswith("/")
            if dir_only:
                pat = pat.rstrip("/")
            self.rules.append((negate, anchored, dir_only, pat))

    @staticmethod
    def _match(pattern: str, path: str) -> bool:
        """Сопоставление по правилам gitignore.

        Важно: `*` НЕ пересекает `/` (в отличие от fnmatch, где `*` -> `.*`).
        Иначе паттерн `/*.zip` (только корень) ловил бы и
        `resourcepacks/MyPack.zip`, а ресурспаки перестали бы попадать в пак.
        """
        if "**" in pattern:
            tmp = (pattern.replace("**/", "\x01")
                          .replace("/**", "\x02")
                          .replace("**", "\x03"))
            rx = re.escape(tmp)
            rx = (rx.replace(re.escape("\x01"), "(?:.*/)?")
                    .replace(re.escape("\x02"), "(?:/.*)?")
                    .replace(re.escape("\x03"), ".*"))
            rx = rx.replace(re.escape("*"), "[^/]*").replace(re.escape("?"), "[^/]")
            return re.fullmatch(rx, path) is not None
        rx = re.escape(pattern).replace(re.escape("*"), "[^/]*") \
                              .replace(re.escape("?"), "[^/]")
        return re.fullmatch(rx, path) is not None

    @staticmethod
    def _is_rooted(pat: str) -> bool:
        """Паттерн привязан к корню, если слэш встречается в начале или в
        СЕРЕДИНЕ (gitignore-семантика). `quests/**` -> только /quests/**,
        но НЕ config/ftbquests/quests/**. `README.md` и `*.zip` (слэша нет)
        -> совпадают на любом уровне.

        Раньше здесь перебирались все суффиксы пути, из-за чего `quests/**`
        молча вырезал config/ftbquests/quests/ — квесты не попадали в пак.
        """
        return "/" in pat.rstrip("/")

    def ignored(self, relpath: str, is_dir: bool = False) -> bool:
        result = False
        for negate, anchored, dir_only, pat in self.rules:
            if dir_only and not is_dir and not relpath.startswith(pat + "/"):
                continue
            if anchored or self._is_rooted(pat):
                matched = self._match(pat, relpath)
            else:
                # без слэша — совпадает с именем на любом уровне
                matched = self._match(pat, relpath) or any(
                    self._match(pat, part) for part in relpath.split("/")
                )
            if matched:
                result = not negate
        return result


def load_ignore() -> Ignore:
    pats = list(IGNORE_DEFAULTS)
    if os.path.isfile(PACKWIZIGNORE):
        with open(PACKWIZIGNORE, "r", encoding="utf-8") as fh:
            pats += fh.read().splitlines()
    return Ignore(pats)


def pack_files():
    """Список (relpath, abs_path, is_dir=False) файлов, входящих в пак."""
    ign = load_ignore()
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
        if rel == ".":
            rel = ""
        dirnames[:] = sorted(
            d for d in dirnames
            if not ign.ignored(posixpath.join(rel, d) if rel else d, is_dir=True)
        )
        for fn in sorted(filenames):
            rp = posixpath.join(rel, fn) if rel else fn
            if rp in ("pack.toml", "index.toml", ".packwizignore"):
                continue
            if ign.ignored(rp):
                continue
            out.append((rp, os.path.join(dirpath, fn)))
    return sorted(out)


# --------------------------------------------------------------------------- #
#  pack.toml
# --------------------------------------------------------------------------- #

def load_pack() -> dict:
    if not os.path.isfile(PACK_TOML):
        fail("pack.toml не найден — запускайте скрипт из корня модпака")
    return read_toml(PACK_TOML)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
#  index.toml
# --------------------------------------------------------------------------- #

def read_index() -> dict:
    """-> {relpath: {'hash':..., 'metafile':bool, 'preserve':bool, 'alias':str}}"""
    data = read_toml(INDEX_TOML)
    out = {}
    for entry in data.get("files", []) if isinstance(data.get("files"), list) else []:
        if isinstance(entry, dict) and "file" in entry:
            out[entry["file"]] = entry
    # read_toml не разбирает [[files]] — делаем это отдельно
    if not out and os.path.isfile(INDEX_TOML):
        out = _read_index_arrays()
    return out


def _read_index_arrays() -> dict:
    with open(INDEX_TOML, "r", encoding="utf-8") as fh:
        text = fh.read()
    entries = {}
    for block in re.split(r"^\s*\[\[files\]\]\s*$", text, flags=re.M)[1:]:
        cur = {}
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("["):
                continue
            m = re.match(r'^([A-Za-z0-9_\-]+)\s*=\s*(.*)$', line)
            if m:
                cur[m.group(1)] = _unquote(m.group(2))
        if cur.get("file"):
            entries[cur["file"]] = cur
    return entries


def write_index(entries: dict) -> None:
    lines = ['hash-format = "sha256"', ""]
    for rel in sorted(entries):
        e = entries[rel]
        lines.append("[[files]]")
        lines.append('file = "%s"' % rel)
        if e.get("hash"):
            lines.append('hash = "%s"' % e["hash"])
        if e.get("hash-format"):
            lines.append('hash-format = "%s"' % e["hash-format"])
        if e.get("alias"):
            lines.append('alias = "%s"' % e["alias"])
        if e.get("metafile"):
            lines.append("metafile = true")
        if e.get("preserve"):
            lines.append("preserve = true")
        lines.append("")
    with open(INDEX_TOML, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines).rstrip("\n") + "\n")
    # хэш индекса в pack.toml
    _update_pack_index_hash()


def _update_pack_index_hash() -> None:
    digest = sha256_file(INDEX_TOML)
    with open(PACK_TOML, "r", encoding="utf-8") as fh:
        text = fh.read()
    if re.search(r'^hash\s*=\s*".*"$', text, flags=re.M):
        text = re.sub(r'^hash\s*=\s*".*"$', 'hash = "%s"' % digest, text, count=1, flags=re.M)
    else:
        text = text.replace('hash-format = "sha256"',
                            'hash-format = "sha256"\nhash = "%s"' % digest, 1)
    with open(PACK_TOML, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def cmd_refresh(_args) -> None:
    old = _read_index_arrays() if os.path.isfile(INDEX_TOML) else {}
    entries = {}
    for rel, abspath in pack_files():
        prev = old.get(rel, {})
        entries[rel] = {
            "file": rel,
            "hash": sha256_file(abspath),
            "metafile": rel.endswith(".pw.toml"),
            "preserve": bool(prev.get("preserve")),
            "alias": prev.get("alias", ""),
        }
    write_index(entries)
    ok("index.toml: %d файлов" % len(entries))


def cmd_check(_args) -> None:
    problems = []
    warnings = []
    index = _read_index_arrays() if os.path.isfile(INDEX_TOML) else {}
    disk = {rel: abspath for rel, abspath in pack_files()}
    for rel in sorted(set(index) - set(disk)):
        problems.append("в index.toml есть, на диске нет: " + rel)
    for rel in sorted(set(disk) - set(index)):
        problems.append("на диске есть, в index.toml нет: " + rel)
    for rel, abspath in disk.items():
        if rel in index and index[rel].get("hash") != sha256_file(abspath):
            problems.append("хэш не совпадает: " + rel)
    mods = load_mods()
    for slug, m in mods.items():
        if not m.get("download", {}).get("url"):
            problems.append("нет [download] url: mods/%s.pw.toml" % slug)
        if not any(isinstance(v, dict) and v for v in (m.get("update") or {}).values()):
            # Для модов с Maven или по прямой ссылке [update] пуст — это нормально:
            # packwiz умеет обновлять только modrinth/curseforge, а кастомный
            # [update.maven] уронил бы packwiz с "Update plugin maven not found!".
            warnings.append("нет [update] — обновлять вручную: mods/%s.pw.toml" % slug)
    for w in warnings:
        print("  \033[33m!\033[0m " + w)
    if problems:
        print("\n".join("  - " + p for p in problems))
        fail("найдено проблем: %d (запустите `pw.py refresh`)" % len(problems))
    ok("пак в порядке: %d файлов, %d модов" % (len(index), len(mods)))


# --------------------------------------------------------------------------- #
#  Моды
# --------------------------------------------------------------------------- #

def load_mods() -> dict:
    """-> {slug: {metafile, path, name, filename, side, download{}, update{}}}"""
    out = {}
    if not os.path.isdir(MODS_DIR):
        return out
    for fn in sorted(os.listdir(MODS_DIR)):
        if not fn.endswith(".pw.toml"):
            continue
        path = os.path.join(MODS_DIR, fn)
        out[fn[: -len(".pw.toml")]] = {"path": path, **_parse_mod(path)}
    return out


def _parse_mod(path: str) -> dict:
    data = read_toml(path)
    return {
        "name": data.get("name", ""),
        "filename": data.get("filename", ""),
        "side": data.get("side", "both"),
        "pin": bool(data.get("pin", False)),
        "option": data.get("option", {}) if isinstance(data.get("option"), dict) else {},
        "download": data.get("download", {}) if isinstance(data.get("download"), dict) else {},
        "update": data.get("update", {}) if isinstance(data.get("update"), dict) else {},
    }


def slugify(name: str) -> str:
    """Точная копия core.SlugifyName из packwiz."""
    s = name.lower()
    s = re.sub(r"\(.*\)", "", s)
    s = re.sub(r" - .+", "", s)
    s = re.sub(r"[^a-z\d]", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def write_mod(slug: str, name: str, filename: str, side: str, url: str,
              hash_format: str, hash_value: str, update_block: str,
              optional: bool = False) -> str:
    os.makedirs(MODS_DIR, exist_ok=True)
    path = os.path.join(MODS_DIR, slug + ".pw.toml")
    lines = [
        'name = "%s"' % name.replace('"', '\\"'),
        'filename = "%s"' % filename,
        'side = "%s"' % side,
    ]
    if optional:
        lines += ["", "[option]", "optional = true", "default = false"]
    lines += [
        "",
        "[download]",
        'url = "%s"' % url,
        'hash-format = "%s"' % hash_format,
        'hash = "%s"' % hash_value,
        "",
        "[update]",
        update_block.rstrip(),
        "",
    ]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    return path


# --------------------------------------------------------------------------- #
#  Maven (нужно для FTB-модов: их нет на Modrinth, только на CurseForge и
#  на публичном maven.ftb.dev)
# --------------------------------------------------------------------------- #

MAVEN_DEFAULTS = {
    "ftb": "https://maven.ftb.dev/releases",
}


def _maven_fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def maven_latest(base: str, group: str, artifact: str, prefix: str = "") -> str:
    """Список версий из листинга каталога maven (maven-metadata.xml не у всех есть)."""
    path = "%s/%s/%s/" % (base.rstrip("/"), group.replace(".", "/"), artifact)
    html = _maven_fetch(path).decode("utf-8", "replace")
    vers = re.findall(r'href="\./([^/"]+)/"', html)
    vers = [v for v in vers if re.match(r"^\d", v)]
    if prefix:
        vers = [v for v in vers if v.startswith(prefix)]
    if not vers:
        fail("в %s нет версий%s" % (path, " с префиксом " + prefix if prefix else ""))

    def key(v):
        return [int(x) if x.isdigit() else 0 for x in re.split(r"[.\-+]", v)]
    return sorted(vers, key=key)[-1]


def maven_pom_deps(base: str, group: str, artifact: str, version: str):
    """Зависимости из POM. Возвращает [(group, artifact, version, scope)]."""
    url = "%s/%s/%s/%s/%s-%s.pom" % (base.rstrip("/"), group.replace(".", "/"),
                                     artifact, version, artifact, version)
    try:
        xml = _maven_fetch(url).decode("utf-8", "replace")
    except Exception as e:                              # noqa: BLE001
        warn_pom = "POM недоступен (%s) — зависимости не разрешаются" % e
        info(warn_pom)
        return []
    out = []
    for m in re.finditer(r"<dependency>(.*?)</dependency>", xml, re.S):
        blk = m.group(1)
        if "<exclusion>" in blk:
            # исключение применяется к транзитивным зависимостям самого блока,
            # но сам блок нам всё равно нужен
            pass
        g = re.search(r"<groupId>([^<]+)</groupId>", blk)
        a = re.search(r"<artifactId>([^<]+)</artifactId>", blk)
        v = re.search(r"<version>([^<]+)</version>", blk)
        sc = re.search(r"<scope>([^<]+)</scope>", blk)
        if g and a and v:
            out.append((g.group(1).strip(), a.group(1).strip(),
                        v.group(1).strip(), (sc.group(1).strip() if sc else "compile")))
    return out


def maven_sha1(base: str, group: str, artifact: str, version: str) -> str:
    url = "%s/%s/%s/%s/%s-%s.jar.sha1" % (base.rstrip("/"), group.replace(".", "/"),
                                          artifact, version, artifact, version)
    try:
        return _maven_fetch(url).decode().strip().split()[0]
    except Exception:                                   # noqa: BLE001
        return ""


def maven_jar_url(base: str, group: str, artifact: str, version: str) -> str:
    return "%s/%s/%s/%s/%s-%s.jar" % (base.rstrip("/"), group.replace(".", "/"),
                                      artifact, version, artifact, version)


def _maven_ver_key(v: str):
    return [int(x) if x.isdigit() else 0 for x in re.split(r"[.\-+]", v)]


def _maven_display_name(artifact: str) -> str:
    """ftb-library-neoforge -> 'FTB Library'; kubejs-neoforge -> 'Kubejs'."""
    clean = re.sub(r"-(neoforge|forge|fabric|quilt)$", "", artifact)
    parts = clean.split("-")
    if parts and parts[0].lower() in ("ftb", "jei", "emi", "rei"):
        parts[0] = parts[0].upper()
    return " ".join(w.capitalize() if w.islower() else w for w in parts)


def cmd_add_maven(args) -> None:
    """Добавляет артефакт с Maven и разрешает транзитивные зависимости из POM.

    Конфликты версий (когда разные POM просят разное) разрешаются выбором
    МАКСИМАЛЬНОЙ версии — иначе более старая перезапишет более новую, потому
    что имя файла mods/<slug>.pw.toml от версии не зависит.
    """
    base = MAVEN_DEFAULTS.get(args.repo, args.repo)

    # --- фаза 1: обход графа зависимостей ---
    candidates = {}       # (group, artifact) -> {version: [источники]}
    external = {}         # (group, artifact) -> {version: источник}
    queue = [(args.group, args.artifact, args.version, "запрошен явно")]
    seen = set()
    while queue:
        g, a, v, why = queue.pop(0)
        if (g, a, v) in seen:
            continue
        seen.add((g, a, v))
        if g != args.group:
            external.setdefault((g, a), {}).setdefault(v, why)
            continue
        candidates.setdefault((g, a), {}).setdefault(v, []).append(why)
        if args.no_deps:
            continue
        for dg, da, dv, scope in maven_pom_deps(base, g, a, v):
            if scope not in ("compile", "runtime"):
                continue
            queue.append((dg, da, dv, "зависимость %s:%s" % (g, a)))

    # --- фаза 2: разрешение конфликтов ---
    resolved = []
    for (g, a), versions in sorted(candidates.items()):
        best = sorted(versions, key=_maven_ver_key)[-1]
        if len(versions) > 1:
            info("%s: запрошены версии %s — беру максимальную %s"
                 % (a, ", ".join(sorted(versions, key=_maven_ver_key)), best))
        resolved.append((g, a, best, versions[best]))

    # --- фаза 3: запись ---
    for g, a, v, whys in resolved:
        url = maven_jar_url(base, g, a, v)
        digest = maven_sha1(base, g, a, v)
        if not digest and not args.force:
            fail("не удалось получить sha1 для %s" % url)
        title = args.name if args.name and a == args.artifact else _maven_display_name(a)
        slug = slugify(title) or re.sub(r"[^a-z\d]+", "-", a.lower()).strip("-")
        write_mod(slug, title, "%s-%s.jar" % (a, v), args.side, url,
                  "sha1", digest, "[update]\n", optional=args.optional)
        ok("%-22s %-16s sha1=%s  (%s)" % (title, v, (digest[:16] + "…") if digest else "—",
                                           "; ".join(sorted(set(whys)))))

    if external:
        info("внешние зависимости (другая группа) — добавьте их отдельно:")
        for (g, a), versions in sorted(external.items()):
            need = sorted(versions, key=_maven_ver_key)[-1]
            hint = {"architectury-neoforge": "architectury-api",
                    "architectury-fabric": "architectury-api",
                    "architectury-forge": "architectury-api"}.get(a, a)
            print("      %s:%s  >= %s   ->   pw.py add %s" % (g, a, need, hint))

    cmd_refresh(args)


# --------------------------------------------------------------------------- #
#  Modrinth API
# --------------------------------------------------------------------------- #

def mr(path: str, params=None, retries: int = 4):
    url = MODRINTH_API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (408, 425, 429, 500, 502, 503, 504, 520, 521, 522, 524) and attempt < retries - 1:
                last = e
                time.sleep(2 ** attempt)
                continue
            body = e.read().decode("utf-8", "ignore")[:300]
            fail("Modrinth API %s -> HTTP %s\n%s" % (url, e.code, body))
        except Exception as e:                      # noqa: BLE001 - сеть может отвалиться
            last = e
            if attempt < retries - 1:
                info("Modrinth API недоступен (%s), повтор через %d c..." % (e, 2 ** attempt))
                time.sleep(2 ** attempt)
                continue
    fail("Modrinth API %s недоступен после %d попыток: %s" % (url, retries, last))


def mr_project(ident: str) -> dict:
    return mr("project/" + urllib.parse.quote(ident))


def _as_list(v):
    """Строка -> [строка]. Критично: list('neoforge') дало бы список букв."""
    if not v:
        return []
    if isinstance(v, str):
        return [v]
    return list(v)


def mr_versions(project_id: str, loaders, game_versions):
    params = {}
    ld = _as_list(loaders)
    gv = _as_list(game_versions)
    if ld:
        params["loaders"] = json.dumps(ld)
    if gv:
        params["game_versions"] = json.dumps(gv)
    return mr("project/%s/version" % project_id, params)


def loaders_from_pack(pack: dict):
    v = pack.get("versions", {})
    out = []
    if "quilt" in v:
        out += ["quilt", "fabric"]
    elif "fabric" in v:
        out += ["fabric"]
    if "neoforge" in v:
        out += ["neoforge", "forge"]
    elif "forge" in v:
        out += ["forge"]
    return out


def game_versions_from_pack(pack: dict):
    """Список версий MC для фильтра Modrinth.

    ВАЖНО: основная версия из [versions].minecraft идёт ПЕРВОЙ.
    pick_version() берёт gvs[:1] как «точное совпадение», поэтому порядок
    здесь определяет, под какую версию MC будут подбираться моды.
    (У packwiz список устроен наоборот — mc последним, — но он и «точную»
    версию определяет иначе. Здесь порядок внутренний.)
    """
    v = pack.get("versions", {})
    mc = v.get("minecraft")
    if not mc:
        fail("в pack.toml не указана версия Minecraft")
    acc = pack.get("options", {}).get("acceptable-game-versions", [])
    seen, out = set(), []
    for x in [mc] + list(acc):
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def side_from_env(ver: dict, forced=None) -> str:
    """Определяем side по данным Modrinth.

    API может отдать `environment` либо словарём {"client": "...", "server": "..."},
    либо строкой-перечислением (например "client_or_server_prefers_both").
    """
    if forced:
        return forced
    env = ver.get("environment")
    if isinstance(env, str):
        e = env.lower()
        if "client_only" in e:
            return "client"
        if "server_only" in e:
            return "server"
        return "both"
    if isinstance(env, dict):
        client = str(env.get("client") or "unknown").lower()
        server = str(env.get("server") or "unknown").lower()
        if client in ("required", "optional") and server in ("required", "optional"):
            return "both"
        if client in ("required", "optional"):
            return "client"
        if server in ("required", "optional"):
            return "server"
    return "both"


def primary_loader(pack: dict) -> str:
    v = pack.get("versions", {})
    for key in ("neoforge", "forge", "quilt", "fabric"):
        if key in v:
            return key
    return ""


def pick_version(project_id, loaders, game_versions, primary="", allow_pre=False):
    """Подбираем лучшую версию мода.

    Порядок попыток — от самого точного совпадения к самому свободному:
    сначала только основной загрузчик (neoforge) и точная версия MC, затем
    запасные варианты. Это важно: запрос сразу по [neoforge, forge] может
    вернуть файл, собранный для Forge, который на NeoForge не запустится.

    Внутри каждой попытки предпочтение отдаётся release, затем beta, затем
    alpha — иначе свежайшая бета затрёт стабильную версию.
    Флаг allow_pre снимает это предпочтение (берёт просто самую новую).
    """
    prim = _as_list(primary)
    ld_all = _as_list(loaders)
    gvs = _as_list(game_versions)
    gvs_exact = gvs[:1]

    attempts = []
    if prim:
        attempts += [(prim, gvs_exact), (prim, gvs)]
    if ld_all and ld_all != prim:
        attempts += [(ld_all, gvs_exact), (ld_all, gvs)]
    attempts += [(None, gvs_exact), (None, gvs), (None, None)]

    preference = ("release", "beta", "alpha")
    seen = set()
    for ld, gv in attempts:
        key = (tuple(ld or ()), tuple(gv or ()))
        if key in seen:
            continue
        seen.add(key)
        vs = mr_versions(project_id, ld, gv)
        if not vs:
            continue
        used_prim = bool(ld) and (not prim or set(ld) == set(prim))
        used_exact_mc = bool(gv) and list(gv) == gvs_exact
        picked = None
        newer_pre = None
        if not allow_pre:
            for want in preference:
                cand = [v for v in vs if (v.get("version_type") or "") == want]
                if cand:
                    picked = cand[0]
                    break
        picked = picked or vs[0]
        # vs отсортирован по дате публикации (новые первыми): если самая свежая
        # сборка — не релиз, а мы взяли релиз, честно об этом сообщаем
        if not allow_pre and (picked.get("version_type") or "") == "release":
            top = vs[0]
            if (top.get("version_type") or "") != "release" and top.get("id") != picked.get("id"):
                newer_pre = top
        return picked, {"prim": used_prim, "mc": used_exact_mc, "newer_pre": newer_pre}
    fail("не нашлось ни одной версии для %s" % project_id)


def pick_file(ver: dict, primary: str = ""):
    """Выбираем конкретный .jar внутри версии.

    Modrinth может отдать несколько файлов (forge/neoforge/fabric) в одной версии.
    Сначала берём помеченный primary, но если его имя явно про другой загрузчик —
    ищем файл, подходящий нашему.
    """
    files = ver.get("files") or []
    if not files:
        fail("у версии %s нет файлов" % ver.get("id"))
    prim = next((f for f in files if f.get("primary")), files[0])
    if not primary:
        return prim
    others = {"neoforge": ("forge", "fabric"), "forge": ("neoforge", "fabric"),
              "fabric": ("forge", "neoforge"), "quilt": ("forge", "neoforge")}
    bad = [b for b in others.get(primary, ()) if b != primary]
    name = (prim.get("filename") or "").lower()
    if primary in name:
        return prim
    if any(b in name for b in bad):
        # primary-файл собран под другой загрузчик — ищем правильный
        for f in files:
            if primary in (f.get("filename") or "").lower():
                return f
        for f in files:
            fn = (f.get("filename") or "").lower()
            if not any(b in fn for b in bad):
                return f
    return prim


def cmd_add(args) -> None:
    pack = load_pack()
    prim = args.loader or primary_loader(pack)
    loaders = [prim] if args.loader else loaders_from_pack(pack)
    gvs = [args.mc] if args.mc else game_versions_from_pack(pack)
    queue = list(args.mods)
    done = set()

    while queue:
        ident = queue.pop(0)
        if ident in done:
            continue
        proj = mr_project(ident)
        pid = proj["id"]
        done.add(ident)
        done.add(pid)

        slug = slugify(proj["title"]) or proj["slug"]
        ver, meta = pick_version(pid, loaders, gvs, prim, args.pre_release)
        if not meta["prim"]:
            info("%s: нет сборки под %s — беру ближайшую (loaders=%s, MC=%s)"
                 % (proj["title"], prim or "загрузчик из pack.toml",
                    ver.get("loaders"), ver.get("game_versions")))
        f = pick_file(ver, prim)
        side = side_from_env(ver, args.side)

        update_block = "[update.modrinth]\nmod-id = \"%s\"\nversion = \"%s\"" % (pid, ver["id"])
        path = write_mod(slug, proj["title"], f["filename"], side, f["url"],
                         "sha1", f["hashes"]["sha1"], update_block,
                         optional=args.optional)
        ok("%-38s %s  [%s] -> mods/%s.pw.toml"
           % (proj["title"], ver["version_number"], side, slug))
        if meta.get("newer_pre"):
            np = meta["newer_pre"]
            warn_pre = ("есть более свежая %s: %s (от %s). "
                        "Поставить её:  pw.py add %s --pre-release"
                        % (np.get("version_type"), np.get("version_number"),
                           (np.get("date_published") or "")[:10], ident))
            print("    " + "\033[33m!?\033[0m " + warn_pre)

        if not args.no_deps:
            for dep in ver.get("dependencies", []):
                if dep.get("dependency_type") != "required":
                    continue
                dep_id = dep.get("project_id")
                if dep_id and dep_id not in done:
                    info("  + обязательная зависимость: %s" % dep_id)
                    queue.append(dep_id)

    cmd_refresh(args)


def cmd_add_url(args) -> None:
    slug = slugify(args.name) or re.sub(r"[^a-z\d]+", "-", args.name.lower()).strip("-")
    filename = args.filename or posixpath.basename(urllib.parse.urlparse(args.url).path)
    if not filename:
        fail("не удалось определить имя файла — укажите --filename")
    digest = hashlib.sha1(urllib.request.urlopen(
        urllib.request.Request(args.url, headers={"User-Agent": USER_AGENT}), timeout=120
    ).read()).hexdigest() if args.hash else ""
    write_mod(slug, args.name, filename, args.side, args.url, "sha1", digest,
              "[update]\n", optional=args.optional)
    ok("%s -> mods/%s.pw.toml (side=%s)" % (args.name, slug, args.side))
    cmd_refresh(args)


def cmd_remove(args) -> None:
    mods = load_mods()
    wanted = set(args.mods)
    removed = 0
    for slug, m in list(mods.items()):
        mid = (m.get("update", {}).get("modrinth", {}) or {}).get("mod-id", "")
        if slug in wanted or m["name"].lower() in {w.lower() for w in wanted} or mid in wanted:
            os.remove(m["path"])
            ok("удалён " + slug)
            removed += 1
    if not removed:
        fail("ничего не найдено. Список: " + ", ".join(sorted(mods)) )
    cmd_refresh(args)


def cmd_update(args) -> None:
    pack = load_pack()
    loaders = loaders_from_pack(pack)
    gvs = game_versions_from_pack(pack)
    prim = primary_loader(pack)
    mods = load_mods()
    targets = mods if args.all else {k: v for k, v in mods.items() if k in set(args.mods)}
    if not targets:
        fail("укажите имена модов или --all")
    changed = 0
    for slug, m in sorted(targets.items()):
        mrid = (m.get("update", {}).get("modrinth", {}) or {}).get("mod-id")
        if not mrid:
            info("%s: нет modrinth-метаданных, пропускаю" % slug)
            continue
        if m.get("pin"):
            info("%s: закреплён (pin = true), пропускаю" % slug)
            continue
        ver, _ = pick_version(mrid, loaders, gvs, prim, args.pre_release)
        if ver["id"] == (m.get("update", {}).get("modrinth", {}) or {}).get("version"):
            info("%s: уже последняя (%s)" % (slug, ver["version_number"]))
            continue
        f = pick_file(ver, prim)
        update_block = "[update.modrinth]\nmod-id = \"%s\"\nversion = \"%s\"" % (mrid, ver["id"])
        write_mod(slug, m["name"], f["filename"], m.get("side", "both"), f["url"],
                  "sha1", f["hashes"]["sha1"], update_block,
                  optional=bool(m.get("option", {}).get("optional")))
        ok("%s -> %s" % (slug, ver["version_number"]))
        changed += 1
    cmd_refresh(args)
    ok("обновлено модов: %d" % changed)


def _w(s: str) -> int:
    """Ширина строки с поправкой на wide-символы (эмодзи и т.п.)."""
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def _pad(s: str, width: int) -> str:
    return s + " " * max(0, width - _w(s))


def cmd_list(_args) -> None:
    mods = load_mods()
    if not mods:
        print("Модов пока нет. Добавьте:  python scripts/pw.py add jei")
        return
    print(_pad("МОД", 36) + _pad("SIDE", 8) + _pad("ФЛАГ", 8) + "ФАЙЛ В mods/")
    print("-" * 52)
    for slug, m in sorted(mods.items()):
        flags = []
        if m.get("pin"):
            flags.append("pin")
        if (m.get("option") or {}).get("optional"):
            flags.append("optional")
        print(_pad(m["name"], 36) + _pad(m.get("side", "both"), 8)
              + _pad(",".join(flags) or "-", 8) + m.get("filename", ""))
    print("\nВсего модов: %d" % len(mods))


# --------------------------------------------------------------------------- #
#  URL пака
# --------------------------------------------------------------------------- #

def read_pack_url() -> str:
    if os.path.isfile(PACK_URL_FILE):
        with open(PACK_URL_FILE, "r", encoding="utf-8") as fh:
            u = fh.read().strip()
        if u and "REPLACE_ME" not in u:
            return u
    env = os.environ.get("PACK_URL")
    if env:
        return env.strip()
    fail("адрес пака не задан. Выполните:\n"
         "    python scripts/pw.py set-url https://<user>.github.io/<repo>/pack.toml")


def cmd_set_url(args) -> None:
    os.makedirs(PACKSYNC_DIR, exist_ok=True)
    with open(PACK_URL_FILE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(args.url.strip() + "\n")
    ok("packsync/pack-url.txt = " + args.url.strip())


def cmd_show_url(_args) -> None:
    try:
        print(read_pack_url())
    except SystemExit:
        print("(не задан)")


# --------------------------------------------------------------------------- #
#  Сборка GitHub Pages
# --------------------------------------------------------------------------- #

def cmd_site(args) -> None:
    out = os.path.join(ROOT, args.out) if not os.path.isabs(args.out) else args.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    index = _read_index_arrays()
    if not index:
        cmd_refresh(args)
        index = _read_index_arrays()

    copied = 0
    for rel in sorted(index):
        src = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.isfile(src):
            fail("файл из index.toml отсутствует на диске: " + rel)
        dst = os.path.join(out, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    for extra in ("pack.toml", "index.toml"):
        shutil.copy2(os.path.join(ROOT, extra), os.path.join(out, extra))
    # Статика для игроков: установщик и «проверялка» модов.
    # Кладём в корень сайта, чтобы адреса были короткими:
    #   <base>/install.ps1   <base>/CheckMods.bat   <base>/CheckMods.ps1
    static_dirs = (("installer", (".ps1", ".sh", ".bat")),)
    inst_n = 0
    for dname, exts in static_dirs:
        src = os.path.join(ROOT, dname)
        if not os.path.isdir(src):
            continue
        for fn in sorted(os.listdir(src)):
            if fn.startswith(".") or fn.lower() == "readme.md" or not fn.endswith(exts):
                continue
            shutil.copy2(os.path.join(src, fn), os.path.join(out, fn))
            inst_n += 1
    if inst_n:
        ok("скрипты для игроков: %d файлов (install.* + CheckMods.*)" % inst_n)

    # packsync/ нужен приложению, чтобы создавать инстанс Prism/Freesm прямо на
    # диске (оно качает jar-ы и обёртки с сервера). В индекс пака эти файлы
    # намеренно не входят — иначе packwiz-installer перезаписывал бы jar,
    # который сам же исполняет, и на Windows это упало бы на блокировке файла.
    ps_src = os.path.join(ROOT, "packsync")
    ps_n = 0
    if os.path.isdir(ps_src):
        ps_dst = os.path.join(out, "packsync")
        os.makedirs(ps_dst, exist_ok=True)
        for fn in sorted(os.listdir(ps_src)):
            if _skip_packsync(fn) or not os.path.isfile(os.path.join(ps_src, fn)):
                continue
            shutil.copy2(os.path.join(ps_src, fn), os.path.join(ps_dst, fn))
            ps_n += 1
    if ps_n:
        ok("packsync/: %d файлов (для установки инстанса приложением)" % ps_n)

    # GitHub Pages: отключаем Jekyll, иначе файлы с '_' в имени не публикуются
    open(os.path.join(out, ".nojekyll"), "w").close()
    ok("site/ готово: %d файлов пака + %d установщика + pack.toml + index.toml"
       % (copied, inst_n))
    try:
        print("\nАдрес пака будет:  %s" % read_pack_url())
    except SystemExit:
        print("\n(адрес пака не задан — выполните `pw.py set-url <url>`; в CI он проставляется сам)")


# --------------------------------------------------------------------------- #
#  Сборка .mrpack
# --------------------------------------------------------------------------- #

ALLOWED_HOSTS = {"cdn.modrinth.com", "github.com", "raw.githubusercontent.com", "gitlab.com"}


def cmd_mrpack(args) -> None:
    pack = load_pack()
    index = _read_index_arrays()
    if not index:
        fail("index.toml пуст — сначала `pw.py refresh`")

    versions = pack.get("versions", {})
    deps = {"minecraft": versions.get("minecraft", "")}
    for key in ("neoforge", "forge", "quilt", "fabric"):
        if key in versions:
            deps[{"quilt": "quilt-loader", "fabric": "fabric-loader"}.get(key, key)] = versions[key]

    files = []
    overrides = []
    for rel in sorted(index):
        e = index[rel]
        if e.get("metafile"):
            mod = _parse_mod(os.path.join(ROOT, rel.replace("/", os.sep)))
            mru = (mod.get("update", {}) or {}).get("modrinth", {}) or {}
            dl = mod.get("download", {}) or {}
            host = urllib.parse.urlparse(dl.get("url", "")).netloc
            if not mru.get("mod-id") or host not in ALLOWED_HOSTS:
                fail("мод %s нельзя положить в .mrpack ссылкой (host=%s, modrinth id=%s).\n"
                     "Используйте официальный `packwiz modrinth export` — он вложит .jar внутрь."
                     % (rel, host, mru.get("mod-id")))
            side = mod.get("side", "both")
            env = {
                "both": {"client": "required", "server": "required"},
                "client": {"client": "required", "server": "unsupported"},
                "server": {"client": "unsupported", "server": "required"},
            }.get(side, {"client": "required", "server": "required"})
            dest = posixpath.join(posixpath.dirname(rel), mod.get("filename", ""))
            files.append({
                "path": dest,
                "hashes": {"sha1": dl.get("hash", "")},
                "env": env,
                "downloads": [dl["url"]],
            })
        else:
            overrides.append(rel)

    manifest = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": pack.get("version", "1.0.0"),
        "name": pack.get("name", "modpack"),
        "summary": pack.get("description", ""),
        "files": files,
        "dependencies": deps,
    }

    outdir = os.path.dirname(os.path.abspath(args.out)) or "."
    os.makedirs(outdir, exist_ok=True)
    out = args.out
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(manifest, indent=4))
        z.writestr("overrides/", "")
        for rel in overrides:
            z.write(os.path.join(ROOT, rel.replace("/", os.sep)), "overrides/" + rel)
    inject_packsync(out)
    ok("%s  (%d модов ссылкой, %d файлов в overrides)" % (out, len(files), len(overrides)))


PACKSYNC_SKIP = {"README.md"}


def _skip_packsync(filename: str) -> bool:
    return filename.startswith(".") or filename in PACKSYNC_SKIP


def inject_packsync(mrpack_path: str) -> None:
    """Докладывает packsync/* внутрь .mrpack (в overrides/packsync/)."""
    if not os.path.isdir(PACKSYNC_DIR):
        return
    with zipfile.ZipFile(mrpack_path, "a", zipfile.ZIP_DEFLATED) as z:
        existing = set(z.namelist())
        added = 0
        for fn in sorted(os.listdir(PACKSYNC_DIR)):
            src = os.path.join(PACKSYNC_DIR, fn)
            if _skip_packsync(fn):
                continue
            arc = "overrides/packsync/" + fn
            if arc in existing:
                continue
            z.write(src, arc)
            added += 1
    if added:
        ok("в .mrpack добавлено packsync-файлов: %d" % added)


def cmd_inject(args) -> None:
    inject_packsync(args.mrpack)


# --------------------------------------------------------------------------- #
#  Сборка инстанса для Prism / Freesm
# --------------------------------------------------------------------------- #

def cmd_instance(args) -> None:
    pack = load_pack()
    url = read_pack_url()
    versions = pack.get("versions", {})
    mc = versions.get("minecraft")
    if not mc:
        fail("в pack.toml нет versions.minecraft")

    loader_uid, loader_name, loader_ver = None, None, None
    if "neoforge" in versions:
        loader_uid, loader_name, loader_ver = "net.neoforged", "NeoForge", versions["neoforge"]
    elif "forge" in versions:
        loader_uid, loader_name, loader_ver = "net.minecraftforge", "Forge", versions["forge"]
    elif "fabric" in versions:
        loader_uid, loader_name, loader_ver = "net.fabricmc.fabric-loader", "Fabric Loader", versions["fabric"]
    elif "quilt" in versions:
        loader_uid, loader_name, loader_ver = "org.quiltmc.quilt-loader", "Quilt Loader", versions["quilt"]
    else:
        fail("в pack.toml не указан загрузчик")

    java_major, java_uid = _java_runtime_for(mc)

    prelaunch = (
        '"$INST_JAVA" -jar "$INST_DIR/minecraft/packsync/packwiz-installer-bootstrap.jar" '
        '--bootstrap-no-update '
        '--bootstrap-main-jar "$INST_DIR/minecraft/packsync/packwiz-installer.jar" '
        '--pack-folder "$INST_DIR/minecraft" -g "%s"' % url
    )

    tpl_cfg = os.path.join(INSTANCE_TEMPLATE, "instance.cfg")
    if os.path.isfile(tpl_cfg):
        with open(tpl_cfg, "r", encoding="utf-8") as fh:
            cfg = fh.read()
    else:
        cfg = "[General]\nConfigVersion=1.2\nInstanceType=OneSix\n"
    cfg = cfg.replace("@@NAME@@", pack.get("name", "Modpack"))
    cfg = cfg.replace("@@PRELAUNCH@@", prelaunch)

    mmc_pack = {
        "components": [
            {
                "cachedName": "Minecraft",
                "cachedRequires": [{"equals": str(java_major),
                                    "suggests": "%d.0.1" % java_major,
                                    "uid": java_uid}],
                "cachedVersion": mc,
                "important": True,
                "uid": "net.minecraft",
                "version": mc,
            },
            {
                "cachedName": loader_name,
                "cachedRequires": [{"equals": mc, "uid": "net.minecraft"}],
                "cachedVersion": loader_ver,
                "cachedVolatile": True,
                "important": True,
                "uid": loader_uid,
                "version": loader_ver,
            },
        ],
        "formatVersion": 1,
    }

    outdir = os.path.dirname(os.path.abspath(args.out)) or "."
    os.makedirs(outdir, exist_ok=True)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("instance.cfg", cfg.replace("\r\n", "\n"))
        z.writestr("mmc-pack.json", json.dumps(mmc_pack, indent=4))
        icon = os.path.join(INSTANCE_TEMPLATE, "icon.png")
        if os.path.isfile(icon):
            z.write(icon, "icon.png")
        for fn in sorted(os.listdir(PACKSYNC_DIR)):
            src = os.path.join(PACKSYNC_DIR, fn)
            if os.path.isfile(src) and not _skip_packsync(fn):
                z.write(src, "minecraft/packsync/" + fn)
    ok("%s" % args.out)
    print("   Импорт: Prism/Freesm -> Add instance -> Import from zip")
    print("   URL пака: %s" % url)


def _java_major_for(mc: str) -> int:
    return _java_runtime_for(mc)[0]


def _java_runtime_for(mc: str):
    """(major, component) по данным piston-meta.mojang.com.

    component НЕ функция от версии Java: Mojang переименовал
    java-runtime-beta -> gamma на границе 1.18.2/1.19, поэтому ключ — версия MC.
    (Та же функция есть в app/packlib.py — держите их синхронно.)

        1.12.2-1.16.5  -> Java 8   jre-legacy
        1.17-1.17.1    -> Java 16  java-runtime-alpha
        1.18-1.18.1    -> Java 17  java-runtime-beta
        1.19-1.20.4    -> Java 17  java-runtime-gamma
        1.20.5-1.21.x  -> Java 21  java-runtime-delta
        26.x           -> Java 25  java-runtime-epsilon
    """
    m = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", mc or "")
    if not m:
        return 21, "java-runtime-delta"
    a, b = int(m.group(1)), int(m.group(2))
    c = int(m.group(3) or 0)
    if a >= 26:
        return 25, "java-runtime-epsilon"
    if a == 1:
        if b >= 21:
            return 21, "java-runtime-delta"
        if b == 20:
            return (21, "java-runtime-delta") if c >= 5 else (17, "java-runtime-gamma")
        if b == 19:
            return 17, "java-runtime-gamma"
        if b == 18:
            return 17, "java-runtime-beta"
        if b == 17:
            return 16, "java-runtime-alpha"
        return 8, "jre-legacy"
    return 21, "java-runtime-delta"


def _java_runtime_uid(java_major: int) -> str:
    """Устарело: uid зависит от версии MC, а не от мажора Java. Оставлен
    для совместимости, но возвращает лишь наиболее вероятный компонент."""
    return {8: "jre-legacy", 16: "java-runtime-alpha", 17: "java-runtime-gamma",
            21: "java-runtime-delta", 25: "java-runtime-epsilon"}.get(
        java_major, "java-runtime-delta")


# --------------------------------------------------------------------------- #
#  Локальный сервер для теста
# --------------------------------------------------------------------------- #

def cmd_serve(args) -> None:
    os.chdir(ROOT)
    handler = type("H", (SimpleHTTPRequestHandler,), {"end_headers": _no_cache})
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        info("Тестовый сервер: http://localhost:%d/pack.toml   (Ctrl+C — выход)" % args.port)
        info("В лаунчере временно укажите этот адрес вместо GitHub Pages.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


def _no_cache(self):
    self.send_header("Cache-Control", "no-store, max-age=0")
    self.send_header("Pragma", "no-cache")
    SimpleHTTPRequestHandler.end_headers(self)


# --------------------------------------------------------------------------- #
#  Прочее
# --------------------------------------------------------------------------- #

def cmd_versions(_args) -> None:
    pack = load_pack()
    v = pack.get("versions", {})
    print("Minecraft : %s" % v.get("minecraft", "?"))
    for k in ("neoforge", "forge", "fabric", "quilt"):
        if k in v:
            print("%-10s: %s" % (k.capitalize(), v[k]))
    print("acceptable: %s" % pack.get("options", {}).get("acceptable-game-versions", []))
    print("Java для инстанса: %d" % _java_major_for(v.get("minecraft", "1.21.1")))


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pw.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add", help="добавить мод(ы) с Modrinth")
    s.add_argument("mods", nargs="+")
    s.add_argument("--side", choices=["both", "client", "server"])
    s.add_argument("--loader")
    s.add_argument("--mc")
    s.add_argument("--optional", action="store_true")
    s.add_argument("--no-deps", action="store_true")
    s.add_argument("--pre-release", action="store_true",
                   help="разрешить beta/alpha (по умолчанию prefers release)")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("add-url", help="добавить файл по прямой ссылке")
    s.add_argument("name")
    s.add_argument("url")
    s.add_argument("--filename")
    s.add_argument("--side", default="both", choices=["both", "client", "server"])
    s.add_argument("--optional", action="store_true")
    s.add_argument("--hash", action="store_true", help="скачать файл и посчитать sha1")
    s.set_defaults(func=cmd_add_url)

    s = sub.add_parser("add-maven", help="добавить мод с Maven (нужно для FTB)")
    s.add_argument("artifact", help="artifactId, например ftb-quests-neoforge")
    s.add_argument("--group", default="dev.ftb.mods")
    s.add_argument("--version", help="версия; без неё берётся последняя (--mc-prefix)")
    s.add_argument("--repo", default="ftb", help="имя из MAVEN_DEFAULTS или полный URL")
    s.add_argument("--mc-prefix", default="", help="фильтр версий, например 2101 для MC 1.21.1")
    s.add_argument("--name", help="человеческое имя мода")
    s.add_argument("--side", default="both", choices=["both", "client", "server"])
    s.add_argument("--optional", action="store_true")
    s.add_argument("--no-deps", action="store_true")
    s.add_argument("--force", action="store_true", help="добавить даже без sha1")
    s.set_defaults(func=cmd_add_maven_entry)

    s = sub.add_parser("remove", help="удалить мод(ы)")
    s.add_argument("mods", nargs="+")
    s.set_defaults(func=cmd_remove)

    s = sub.add_parser("update", help="обновить моды")
    s.add_argument("mods", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--pre-release", action="store_true",
                   help="разрешить beta/alpha")
    s.set_defaults(func=cmd_update)

    s = sub.add_parser("list", help="список модов")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("refresh", help="пересобрать index.toml")
    s.set_defaults(func=cmd_refresh)

    s = sub.add_parser("check", help="проверить пак")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("set-url", help="записать адрес пака")
    s.add_argument("url")
    s.set_defaults(func=cmd_set_url)

    s = sub.add_parser("show-url", help="показать адрес пака")
    s.set_defaults(func=cmd_show_url)

    s = sub.add_parser("versions", help="версии MC/загрузчика")
    s.set_defaults(func=cmd_versions)

    s = sub.add_parser("site", help="собрать payload для GitHub Pages")
    s.add_argument("--out", default="site")
    s.set_defaults(func=cmd_site)

    s = sub.add_parser("mrpack", help="собрать .mrpack")
    s.add_argument("--out", default=None)
    s.set_defaults(func=_mrpack_entry)

    s = sub.add_parser("inject-packsync", help="доложить packsync/* в готовый .mrpack")
    s.add_argument("mrpack")
    s.set_defaults(func=cmd_inject)

    s = sub.add_parser("instance", help="собрать zip-инстанс для Prism/Freesm")
    s.add_argument("--out", default=None)
    s.set_defaults(func=_instance_entry)

    s = sub.add_parser("serve", help="локальный HTTP-сервер для теста")
    s.add_argument("--port", type=int, default=8080)
    s.set_defaults(func=cmd_serve)

    return p


def cmd_add_maven_entry(args) -> None:
    base = MAVEN_DEFAULTS.get(args.repo, args.repo)
    version = args.version
    if not version:
        version = maven_latest(base, args.group, args.artifact, args.mc_prefix)
        info("последняя версия%s: %s" % (" с префиксом " + args.mc_prefix if args.mc_prefix else "", version))
    args.version = version
    cmd_add_maven(args)


def _mrpack_entry(args) -> None:
    if args.out is None:
        pack = load_pack()
        name = slugify(pack.get("name", "modpack"))
        args.out = os.path.join(ROOT, "dist", "%s-%s.mrpack" % (name, pack.get("version", "1.0.0")))
    cmd_mrpack(args)


def _instance_entry(args) -> None:
    if args.out is None:
        pack = load_pack()
        name = slugify(pack.get("name", "modpack"))
        args.out = os.path.join(ROOT, "dist", "%s-%s-instance.zip" % (name, pack.get("version", "1.0.0")))
    cmd_instance(args)


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
