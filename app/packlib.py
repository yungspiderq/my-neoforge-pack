#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
packlib — ядро Modpack Manager: чтение пака, сверка с диском, синхронизация.

GUI здесь нет намеренно: всё, что делает приложение, живёт в этом модуле,
поэтому его можно тестировать headless и использовать из CLI/CI.

Ключевые решения:
  • синхронизация собственная, на urllib — Java НЕ нужна (в отличие от
    packwiz-installer, которого дёргала PowerShell-версия);
  • скачиваем во временный файл, сверяем хэш и только потом подменяем —
    оборвавшаяся закачка не оставит вместо мода огрызок;
  • заменяемый файл уходит в .modpack-backup;
  • preserve=true из index.toml уважаем: такие файлы не перезаписываются,
    чтобы не затирать личные настройки игрока;
  • чистая переустановка (clean_reinstall): папки mods/, config/, kubejs/ и
    остальные управляемые паком каталоги ЦЕЛИКОМ уезжают в
    .modpack-backup/clean-<время>/, затем всё скачивается заново. Это
    единственный способ убрать устаревшие файлы — лаунчеры вроде
    AstralRinth/Modrinth App при импорте .mrpack ничего не удаляют, и
    выпущенный из пака мод остаётся лежать в mods/ (реальный краш
    crash-2026-10-04_10.28.53-client.txt: certain_questing_additions
    дожил до v1.3.1 именно так).
"""

from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

UA = "ModpackManager/3.1 (+https://github.com/packwiz/packwiz)"
TIMEOUT = 60
BACKUP_DIR = ".modpack-backup"
PACKSYNC_REMOTE = "packsync"

# --------------------------------------------------------------------------- #
#  Статусы
# --------------------------------------------------------------------------- #

OK = "НА МЕСТЕ"
MISSING = "ОТСУТСТВУЕТ"
MISMATCH = "НЕ СОВПАДАЕТ"
DISABLED = "ОТКЛЮЧЁН"
PRESERVED = "НЕТ (preserve)"
OTHER_SIDE = "ДРУГАЯ СТОРОНА"
EXTRA = "ЛИШНИЙ"
BROKEN_REMOTE = "НЕТ НА СЕРВЕРЕ"

BAD_STATUSES = (MISSING, MISMATCH, BROKEN_REMOTE)

CATEGORIES = ("Моды", "Конфиги", "Ресурспаки", "Шейдеры", "Прочее", "Лишние")


# --------------------------------------------------------------------------- #
#  Мини-парсер TOML (подмножество packwiz)
# --------------------------------------------------------------------------- #

def parse_toml(text: str) -> dict:
    """Очень маленький парсер: таблицы, [[массивы таблиц]], строки, bool, числа."""
    root: dict = {}
    cur = root
    arrays: dict = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\[\[(.+)\]\]$", line)
        if m:
            name = m.group(1).strip()
            entry: dict = {}
            arrays.setdefault(name, []).append(entry)
            cur = entry
            continue
        m = re.match(r"^\[(.+)\]$", line)
        if m:
            cur = root
            for part in m.group(1).strip().split("."):
                cur = cur.setdefault(part.strip(), {})
            continue
        m = re.match(r'^([A-Za-z0-9_\-]+)\s*=\s*(.*)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("["):
            items = [i.strip().strip('"') for i in val[1:-1].split(",")]
            cur[key] = [i for i in items if i]
        elif val.startswith('"'):
            cur[key] = val.strip('"')
        elif val in ("true", "false"):
            cur[key] = val == "true"
        else:
            cur[key] = val
    for name, lst in arrays.items():
        root.setdefault(name, []).extend(lst)
    return root


# --------------------------------------------------------------------------- #
#  HTTP
# --------------------------------------------------------------------------- #

RETRYABLE = (408, 425, 429, 500, 502, 503, 504, 520, 521, 522, 524)


def http_get(url: str, binary: bool = False, retries: int = 3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in RETRYABLE and i < retries - 1:
                last = e
                time.sleep(1.5 ** i)
                continue
            raise
        except Exception as e:                              # noqa: BLE001
            last = e
            if i < retries - 1:
                time.sleep(1.5 ** i)
                continue
            raise
    raise last


def http_size(url: str):
    """Размер файла без скачивания. HEAD, с откатом на GET-Range."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA}, method="HEAD")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            cl = r.headers.get("Content-Length")
            return int(cl) if cl else None
    except Exception:                                       # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
#  Модель пака
# --------------------------------------------------------------------------- #

@dataclass
class PackItem:
    kind: str            # 'mod' | 'file'
    category: str
    name: str
    rel: str             # путь в индексе пака
    dest_rel: str        # путь относительно папки игры
    url: str
    hash_fmt: str
    hash_value: str
    side: str = "both"
    preserve: bool = False


@dataclass
class PackModel:
    base_url: str
    name: str = ""
    version: str = ""
    mc: str = ""
    loader: str = ""
    loader_version: str = ""
    integrity: str = "не задан"
    items: list = field(default_factory=list)

    @property
    def summary(self) -> str:
        return "%s %s · Minecraft %s · %s %s · файлов: %d · index.toml: %s" % (
            self.name or "?", self.version or "?", self.mc or "?",
            self.loader or "?", self.loader_version or "",
            len(self.items), self.integrity)


@dataclass
class Row:
    item: object          # PackItem или None для «лишних»
    category: str
    name: str
    dest_rel: str
    path: str
    status: str
    detail: str = ""
    size: int = 0

    @property
    def actionable(self) -> bool:
        return self.status in BAD_STATUSES

    @property
    def removable(self) -> bool:
        return self.status == EXTRA


def hash_algo(fmt: str) -> str:
    return {
        "sha1": "sha1", "sha256": "sha256", "sha512": "sha512",
        "md5": "md5", "sha-1": "sha1", "sha-256": "sha256",
    }.get((fmt or "sha1").lower(), "sha1")


def file_hash(path: str, fmt: str) -> str:
    alg = hash_algo(fmt)
    if alg not in hashlib.algorithms_available:
        return ""
    h = hashlib.new(alg)
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def categorize(rel: str) -> str:
    first = rel.split("/")[0].lower()
    if first in ("config", "defaultconfigs", "kubejs"):
        return "Конфиги"
    if first == "resourcepacks":
        return "Ресурспаки"
    if first == "shaderpacks":
        return "Шейдеры"
    return "Прочее"


def load_pack(base_url: str, progress=None) -> PackModel:
    """Читает pack.toml -> index.toml -> mods/*.pw.toml и строит модель."""
    base = base_url.rstrip("/")
    base = re.sub(r"/pack\.toml$", "", base)

    def rep(pct, msg):
        if progress:
            progress(pct, msg)

    rep(5, "Читаю pack.toml")
    pack = parse_toml(http_get(base + "/pack.toml"))
    versions = pack.get("versions", {}) or {}
    index_sec = pack.get("index", {}) or {}
    idx_name = index_sec.get("file") or "index.toml"

    rep(15, "Читаю " + idx_name)
    idx_text = http_get(base + "/" + idx_name)

    integrity = "не задан"
    declared = index_sec.get("hash", "")
    if declared:
        fmt = index_sec.get("hash-format", "sha256")
        actual = hashlib.new(hash_algo(fmt), idx_text.encode("utf-8")).hexdigest()
        integrity = "OK" if actual == declared.lower() else "РАССИНХРОН"

    idx = parse_toml(idx_text)
    files = [f for f in (idx.get("files") or []) if isinstance(f, dict) and f.get("file")]

    model = PackModel(
        base_url=base,
        name=pack.get("name", ""),
        version=pack.get("version", ""),
        mc=versions.get("minecraft", ""),
        integrity=integrity,
    )
    for key in ("neoforge", "forge", "fabric", "quilt"):
        if versions.get(key):
            model.loader, model.loader_version = key, versions[key]

    n = len(files)
    for i, entry in enumerate(files):
        rel = entry["file"]
        rep(20 + int(60 * i / max(1, n)), "Метаданные: %d / %d" % (i + 1, n))
        if rel.endswith(".pw.toml"):
            try:
                m = parse_toml(http_get(base + "/" + rel))
            except Exception:                               # noqa: BLE001
                continue
            dl = m.get("download", {}) or {}
            if not dl.get("url"):
                continue
            parent = posixpath.dirname(rel)
            fname = m.get("filename") or posixpath.basename(dl["url"])
            dest = posixpath.join(parent, fname) if parent else ("mods/" + fname)
            model.items.append(PackItem(
                kind="mod", category="Моды", name=m.get("name") or fname,
                rel=rel, dest_rel=dest, url=dl["url"],
                hash_fmt=dl.get("hash-format", "sha1"), hash_value=dl.get("hash", ""),
                side=m.get("side") or "both", preserve=False))
        else:
            model.items.append(PackItem(
                kind="file", category=categorize(rel), name=rel,
                rel=rel, dest_rel=rel, url=base + "/" + rel,
                hash_fmt=entry.get("hash-format") or "sha256",
                hash_value=entry.get("hash", ""),
                side="both", preserve=bool(entry.get("preserve"))))
    rep(100, "Пак прочитан: %d записей" % len(model.items))
    return model


# --------------------------------------------------------------------------- #
#  Сверка с диском
# --------------------------------------------------------------------------- #

SCAN_DIRS = ("mods", "config", "defaultconfigs", "resourcepacks",
             "shaderpacks", "kubejs")

# Каталоги, которые пак полностью контролирует: при «чистой починке» они
# уезжают в бэкап ЦЕЛИКОМ. packsync/ сюда намеренно не входит (это сам
# синхронизатор), как и saves/, local/, journeymap/, options.txt, logs/ —
# личный прогресс игрока не трогается.
CLEAN_DIRS = ("mods", "config", "defaultconfigs", "kubejs",
              "resourcepacks", "shaderpacks")

# Поддеревья, где «лишние» файлы ищутся РЕКУРСИВНО, а не только на первом
# уровне. config/ целиком сканировать вглубь нельзя — после первого запуска
# mods-конфиги (sodium, jade, fml.toml…) засыпали бы вкладку «Лишние» сотнями
# строк. А вот эти каталоги принадлежат паку полностью: всё, что лежит здесь
# и не значится в index.toml, — устаревший мусор (например, главы квестов
# старой версии книги: config/ftbquests/quests/chapters/start.snbt).
DEEP_SCAN_SUBTREES = ("config/ftbquests", "defaultconfigs",
                      "kubejs/startup_scripts", "kubejs/server_scripts",
                      "kubejs/assets")


def scan_local(game_dir: str, model: PackModel, side: str = "client",
               progress=None) -> list:
    """Сравнивает содержимое папки игры с моделью пака."""
    def rep(pct, msg):
        if progress:
            progress(pct, msg)

    rows = []
    items = model.items
    n = len(items)
    for i, it in enumerate(items):
        rep(int(90 * i / max(1, n)), "Сверяю: %d / %d" % (i + 1, n))
        rel = it.dest_rel.replace("/", os.sep)
        path = os.path.join(game_dir, rel)
        row = Row(item=it, category=it.category, name=it.name,
                  dest_rel=it.dest_rel, path=path, status="")

        if side != "both" and it.side not in ("both", side):
            row.status = OTHER_SIDE
            row.detail = "side=%s, выбрана сторона %s" % (it.side, side)
            rows.append(row)
            continue

        if not os.path.isfile(path):
            if os.path.isfile(path + ".disabled"):
                row.status = DISABLED
                row.detail = "лежит как .disabled — мод выключен вручную"
            elif it.preserve:
                row.status = PRESERVED
                row.detail = "preserve=true: файл намеренно не перезаписывается"
            else:
                row.status = MISSING
                row.detail = "будет скачан"
            rows.append(row)
            continue

        try:
            row.size = os.path.getsize(path)
        except OSError:
            row.size = 0
        actual = file_hash(path, it.hash_fmt)
        if it.hash_value and actual and actual != it.hash_value.lower():
            row.status = MISMATCH
            row.detail = "%s: ждём %s…, файл %s…" % (
                it.hash_fmt, it.hash_value[:10], actual[:10])
        elif not actual:
            row.status = MISMATCH
            row.detail = "не удалось посчитать хэш"
        else:
            row.status = OK
            row.detail = "%s верен, %.2f МБ" % (it.hash_fmt, row.size / 1048576)
        rows.append(row)

    # --- лишние файлы (первый уровень управляемых каталогов) ---
    expected = {it.dest_rel.replace("/", os.sep).lower() for it in items}
    expected_posix = {it.dest_rel.lower() for it in items}
    for sub in SCAN_DIRS:
        d = os.path.join(game_dir, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            fp = os.path.join(d, fn)
            if not os.path.isfile(fp):
                continue
            rel = os.path.join(sub, fn).lower()
            if rel in expected:
                continue
            if any((k + ".disabled") == rel for k in expected):
                continue          # отключённый мод из пака — не мусор
            rows.append(Row(
                item=None, category="Лишние", name=fn,
                dest_rel="%s/%s" % (sub, fn), path=fp, status=EXTRA,
                detail="%.2f МБ, в паке не значится" % (os.path.getsize(fp) / 1048576),
                size=os.path.getsize(fp)))

    # --- лишние файлы ВГЛУБЬ полностью подконтрольных паку каталогов ---
    # Здесь прячется то, что поверхностный скан не видит: старые главы квестов
    # (config/ftbquests/quests/chapters/*.snbt), удалённые скрипты KubeJS и т.п.
    for sub in DEEP_SCAN_SUBTREES:
        root = os.path.join(game_dir, sub.replace("/", os.sep))
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in sorted(filenames):
                fp = os.path.join(dirpath, fn)
                rel = os.path.relpath(fp, game_dir).replace(os.sep, "/")
                if rel.lower() in expected_posix:
                    continue
                try:
                    size = os.path.getsize(fp)
                except OSError:
                    size = 0
                rows.append(Row(
                    item=None, category="Лишние", name=fn,
                    dest_rel=rel, path=fp, status=EXTRA,
                    detail="устаревший файл внутри %s/, в паке не значится" % sub,
                    size=size))
    rep(100, "Сверка завершена")
    return rows


def summarize(rows) -> dict:
    out = {}
    for r in rows:
        out[r.status] = out.get(r.status, 0) + 1
    return out


# --------------------------------------------------------------------------- #
#  Синхронизация (собственная, без Java)
# --------------------------------------------------------------------------- #

@dataclass
class SyncResult:
    downloaded: int = 0
    replaced: int = 0
    failed: int = 0
    bytes: int = 0
    errors: list = field(default_factory=list)


def _backup(game_dir: str, dest_rel: str, on_log=None) -> None:
    src = os.path.join(game_dir, dest_rel.replace("/", os.sep))
    if not os.path.isfile(src):
        return
    bak_root = os.path.join(game_dir, BACKUP_DIR)
    os.makedirs(bak_root, exist_ok=True)
    name = dest_rel.replace("/", "_").replace("\\", "_").replace(":", "_")
    try:
        shutil.copy2(src, os.path.join(bak_root, name))
    except OSError as e:
        if on_log:
            on_log("не удалось сделать бэкап %s: %s" % (dest_rel, e))


def sync_rows(game_dir: str, rows, progress=None, on_log=None) -> SyncResult:
    """Качает отсутствующее и заменяет несовпавшее. Хэш проверяется ДО подмены."""
    res = SyncResult()
    todo = [r for r in rows if r.actionable]
    n = len(todo)
    for i, r in enumerate(todo):
        if progress:
            progress(int(100 * i / max(1, n)), "Скачиваю %d/%d: %s" % (i + 1, n, r.name))
        dest = r.path
        tmp = dest + ".download"
        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            data = http_get(r.item.url, binary=True)
            with open(tmp, "wb") as fh:
                fh.write(data)
            alg = hash_algo(r.item.hash_fmt)
            if r.item.hash_value and alg in hashlib.algorithms_available:
                actual = hashlib.new(alg, data).hexdigest()
                if actual != r.item.hash_value.lower():
                    raise RuntimeError("хэш скачанного не совпал: ждём %s, получили %s"
                                       % (r.item.hash_value[:12], actual[:12]))
            existed = os.path.isfile(dest)
            if existed:
                _backup(game_dir, r.dest_rel, on_log)
            os.replace(tmp, dest)
            res.bytes += len(data)
            if existed:
                res.replaced += 1
            else:
                res.downloaded += 1
            if on_log:
                on_log("%s %s (%.2f МБ)" % (
                    "заменён" if existed else "скачан", r.dest_rel, len(data) / 1048576))
        except Exception as e:                              # noqa: BLE001
            res.failed += 1
            res.errors.append("%s: %s" % (r.dest_rel, e))
            if on_log:
                on_log("ОШИБКА %s: %s" % (r.dest_rel, e))
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                pass
    if progress:
        progress(100, "Готово: %d скачано, %d заменено, %d ошибок"
                 % (res.downloaded, res.replaced, res.failed))
    return res


def remove_extras(game_dir: str, rows, on_log=None) -> int:
    """Переносит лишние файлы в .modpack-backup (не удаляет навсегда)."""
    bak = os.path.join(game_dir, BACKUP_DIR)
    moved = 0
    for r in rows:
        if not r.removable:
            continue
        try:
            os.makedirs(bak, exist_ok=True)
            name = r.dest_rel.replace("/", "_").replace("\\", "_")
            shutil.move(r.path, os.path.join(bak, name))
            moved += 1
            if on_log:
                on_log("убран лишний: " + r.dest_rel)
        except OSError as e:
            if on_log:
                on_log("не удалось убрать %s: %s" % (r.dest_rel, e))
    return moved


# --------------------------------------------------------------------------- #
#  Чистая переустановка (кнопка «Починить всё»)
# --------------------------------------------------------------------------- #

@dataclass
class WipeResult:
    backup_dir: str = ""
    moved_dirs: list = field(default_factory=list)
    files: int = 0
    bytes: int = 0
    errors: list = field(default_factory=list)


def _count_tree(path: str):
    """(число файлов, суммарный размер) — для отчёта перед переносом."""
    n, b = 0, 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for fn in filenames:
            try:
                b += os.path.getsize(os.path.join(dirpath, fn))
                n += 1
            except OSError:
                pass
    return n, b


def wipe_managed(game_dir: str, on_log=None) -> WipeResult:
    """Уносит управляемые паком каталоги ЦЕЛИКОМ в .modpack-backup/clean-<время>/.

    Зачем: обычный фикс только докачивает и заменяет файлы из индекса, а
    устаревшее (мод, исключённый из пака; главы квестов прошлой версии книги)
    остаётся на диске. Лаунчеры Theseus-семейства (AstralRinth, Modrinth App)
    при импорте .mrpack тоже ничего не удаляют — так в инстансе доживал
    certain-questing-additions после v1.3.1 и ронял клиент при открытии книги.

    Файлы НЕ удаляются навсегда — вся папка переезжает в бэкап, откуда её
    можно достать. Не трогаем: saves/, local/ (прогресс квестов), journeymap/,
    options.txt, logs/, crash-reports/, packsync/, packwiz.json.
    """
    res = WipeResult()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bak = os.path.join(game_dir, BACKUP_DIR, "clean-" + stamp)
    res.backup_dir = bak
    for sub in CLEAN_DIRS:
        src = os.path.join(game_dir, sub)
        if not os.path.isdir(src):
            continue
        n, b = _count_tree(src)
        try:
            os.makedirs(bak, exist_ok=True)
            shutil.move(src, os.path.join(bak, sub))
            res.moved_dirs.append(sub)
            res.files += n
            res.bytes += b
            if on_log:
                on_log("в бэкап: %s/ — %d файлов, %.1f МБ" % (sub, n, b / 1048576))
        except OSError as e:
            # Почти всегда — запущенная игра держит jar-ы открытыми.
            res.errors.append("%s/: %s" % (sub, e))
            if on_log:
                on_log("ОШИБКА: не удалось унести %s/: %s "
                       "(игра запущена?)" % (sub, e))
    return res


def restore_preserved(game_dir: str, wipe: WipeResult, items, on_log=None) -> int:
    """Возвращает из бэкапа файлы с preserve=true — их нельзя затирать."""
    if not wipe.backup_dir or not wipe.moved_dirs:
        return 0
    n = 0
    for it in items:
        if not it.preserve:
            continue
        rel = it.dest_rel.replace("/", os.sep)
        src = os.path.join(wipe.backup_dir, rel)
        dst = os.path.join(game_dir, rel)
        if not os.path.isfile(src) or os.path.isfile(dst):
            continue
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            n += 1
            if on_log:
                on_log("сохранён личный файл (preserve): " + it.dest_rel)
        except OSError as e:
            if on_log:
                on_log("не удалось вернуть %s: %s" % (it.dest_rel, e))
    return n


@dataclass
class CleanResult:
    wipe: WipeResult = field(default_factory=WipeResult)
    sync: SyncResult = field(default_factory=SyncResult)
    preserved: int = 0

    @property
    def ok(self) -> bool:
        return not self.wipe.errors and not self.sync.failed


def clean_reinstall(game_dir: str, model: PackModel, side: str = "client",
                    progress=None, on_log=None) -> CleanResult:
    """Полная переустановка: стереть управляемые каталоги -> скачать всё заново.

    Если очистка каталогов не удалась (файлы держит запущенная игра),
    прерываемся ДО скачивания: полуснесённая папка mods + докачка оставила бы
    инстанс в ещё более странном состоянии.
    """
    def rep(pct, msg):
        if progress:
            progress(pct, msg)

    out = CleanResult()
    rep(2, "Уношу старые файлы в бэкап…")
    out.wipe = wipe_managed(game_dir, on_log)
    if out.wipe.errors:
        rep(100, "Прервано: не удалось очистить папки")
        return out
    out.preserved = restore_preserved(game_dir, out.wipe, model.items, on_log)

    rep(8, "Сверяю очищенную папку с паком…")
    rows = scan_local(game_dir, model, side,
                      progress=lambda p, m: rep(8 + int(7 * p / 100), m))
    todo = [r for r in rows if r.actionable]
    rep(15, "Скачиваю заново: %d файлов" % len(todo))
    out.sync = sync_rows(game_dir, todo,
                         progress=lambda p, m: rep(15 + int(85 * p / 100), m),
                         on_log=on_log)
    return out


# --------------------------------------------------------------------------- #
#  Поиск папок сборки
# --------------------------------------------------------------------------- #

def _appdata(sub: str) -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, sub)


def _localappdata(sub: str) -> str:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, sub)


def _xdg(sub: str) -> str:
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, sub)


LAUNCHER_LAYOUTS = [
    ("AstralRinth",  [_appdata("AstralRinthApp/profiles"), _xdg("AstralRinthApp/profiles")], False),
    ("Modrinth App", [_appdata("ModrinthApp/profiles"), _xdg("ModrinthApp/profiles")], False),
    ("Freesm",       [_appdata("FreesmLauncher/instances"), _localappdata("FreesmLauncher/instances"),
                      _xdg("freesmlauncher/instances")], True),
    ("Prism",        [_appdata("PrismLauncher/instances"), _localappdata("PrismLauncher/instances"),
                      _xdg("PrismLauncher/instances")], True),
    ("MultiMC",      [_appdata("MultiMC/instances"), _xdg("MultiMC/instances")], True),
]


@dataclass
class FoundDir:
    label: str
    path: str
    has_packsync: bool
    has_mods: bool


def detect_game_dirs() -> list:
    """Ищем папки сборки всех известных лаунчеров.

    Разница принципиальная: у Theseus-лаунчеров (AstralRinth, Modrinth App)
    папка профиля И ЕСТЬ папка игры, а у Prism-семейства игра лежит в
    <instance>/.minecraft.
    """
    out, seen = [], set()
    for label, bases, nested in LAUNCHER_LAYOUTS:
        for base in bases:
            if not os.path.isdir(base):
                continue
            try:
                entries = sorted(os.listdir(base))
            except OSError:
                continue
            for name in entries:
                inst = os.path.join(base, name)
                if not os.path.isdir(inst):
                    continue
                gd = inst
                if nested:
                    for sub in (".minecraft", "minecraft"):
                        cand = os.path.join(inst, sub)
                        if os.path.isdir(cand):
                            gd = cand
                            break
                key = os.path.normcase(os.path.abspath(gd))
                if key in seen:
                    continue
                seen.add(key)
                has_ps = os.path.isdir(os.path.join(gd, "packsync"))
                has_md = os.path.isdir(os.path.join(gd, "mods"))
                tag = "" if has_ps else (" — нет packsync" if has_md else " — пустой инстанс")
                out.append(FoundDir("%s: %s%s" % (label, name, tag), gd, has_ps, has_md))
    for cand in (_appdata(".minecraft"), os.path.expanduser("~/.minecraft")):
        key = os.path.normcase(os.path.abspath(cand))
        if os.path.isdir(cand) and key not in seen:
            seen.add(key)
            has_ps = os.path.isdir(os.path.join(cand, "packsync"))
            out.append(FoundDir("Vanilla: .minecraft%s" % ("" if has_ps else " — нет packsync"),
                                cand, has_ps, os.path.isdir(os.path.join(cand, "mods"))))
    out.sort(key=lambda d: (not d.has_packsync, d.label))
    return out


def read_pack_url(game_dir: str):
    """Адрес пака из <папка игры>/packsync/pack-url.txt."""
    p = os.path.join(game_dir, "packsync", "pack-url.txt")
    try:
        with open(p, encoding="utf-8") as fh:
            u = fh.readline().strip()
        if u and "REPLACE_ME" not in u:
            return re.sub(r"/pack\.toml$", "", u)
    except OSError:
        pass
    return None


# --------------------------------------------------------------------------- #
#  Создание инстанса Prism/Freesm прямо на диске (без zip)
# --------------------------------------------------------------------------- #

PACKSYNC_FILES = (
    "packwiz-installer-bootstrap.jar",
    "packwiz-installer.jar",
    "sync.cmd",
    "sync.sh",
    "LICENSE-packwiz-installer.txt",
)

LOADER_UID = {"neoforge": ("net.neoforged", "NeoForge"),
              "forge": ("net.minecraftforge", "Forge"),
              "fabric": ("net.fabricmc.fabric-loader", "Fabric Loader"),
              "quilt": ("org.quiltmc.quilt-loader", "Quilt Loader")}


def java_runtime_for(mc: str):
    """(major, component) — по данным piston-meta.mojang.com.

    component НЕ является функцией от версии Java: Mojang переименовал
    java-runtime-beta -> java-runtime-gamma на границе 1.18.2 / 1.19, поэтому
    ключом служит именно версия Minecraft. Проверено на реальных манифестах:

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


def java_major_for(mc: str) -> int:
    """Только мажорная версия Java (для тех, кому component не нужен)."""
    return java_runtime_for(mc)[0]


def install_prism_instance(instances_dir: str, name: str, base_url: str,
                           mc: str, loader: str, loader_version: str,
                           progress=None, on_log=None) -> str:
    """Создаёт инстанс Prism/Freesm НА ДИСКЕ — zip и диалог импорта не нужны.

    Prism сканирует каталог instances/ и подхватывает новый инстанс сам.
    """
    def rep(pct, msg):
        if progress:
            progress(pct, msg)

    inst_id = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "modpack"
    inst = os.path.join(instances_dir, inst_id)
    game = os.path.join(inst, ".minecraft")
    ps = os.path.join(game, PACKSYNC_REMOTE)
    os.makedirs(ps, exist_ok=True)
    rep(5, "Создаю " + inst)

    prelaunch = (
        '"$INST_JAVA" -jar "$INST_DIR/minecraft/packsync/packwiz-installer-bootstrap.jar" '
        '--bootstrap-no-update '
        '--bootstrap-main-jar "$INST_DIR/minecraft/packsync/packwiz-installer.jar" '
        '--pack-folder "$INST_DIR/minecraft" -g "%s/pack.toml"' % base_url.rstrip("/"))

    cfg = (
        "[General]\n"
        "ConfigVersion=1.2\n"
        "InstanceType=OneSix\n"
        "name=%s\n"
        "OverrideCommands=true\n"
        "PreLaunchCommand=%s\n"
        "OverrideMemory=true\n"
        "MaxMemAlloc=6144\n"
        "MinMemAlloc=2048\n"
        "PermGen=512\n"
        "OverrideConsole=true\n"
        "ShowConsole=true\n"
        "ShowConsoleOnError=true\n" % (name, prelaunch))
    with open(os.path.join(inst, "instance.cfg"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(cfg)

    luid, lname = LOADER_UID.get(loader, ("net.neoforged", "NeoForge"))
    jm, juid = java_runtime_for(mc)
    mmc = {
        "components": [
            {"cachedName": "Minecraft",
             "cachedRequires": [{"equals": str(jm), "suggests": "%d.0.1" % jm, "uid": juid}],
             "cachedVersion": mc, "important": True, "uid": "net.minecraft", "version": mc},
            {"cachedName": lname,
             "cachedRequires": [{"equals": mc, "uid": "net.minecraft"}],
             "cachedVersion": loader_version, "cachedVolatile": True,
             "important": True, "uid": luid, "version": loader_version},
        ],
        "formatVersion": 1,
    }
    with open(os.path.join(inst, "mmc-pack.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(mmc, fh, indent=4)
        fh.write("\n")
    rep(15, "instance.cfg и mmc-pack.json записаны")

    with open(os.path.join(ps, "pack-url.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(base_url.rstrip("/") + "/pack.toml\n")

    total = len(PACKSYNC_FILES)
    for i, fn in enumerate(PACKSYNC_FILES):
        rep(20 + int(70 * i / max(1, total)), "Скачиваю " + fn)
        try:
            data = http_get(base_url.rstrip("/") + "/packsync/" + fn, binary=True)
        except Exception as e:                              # noqa: BLE001
            msg = "не удалось скачать packsync/%s: %s" % (fn, e)
            if on_log:
                on_log("ОШИБКА " + msg)
            raise RuntimeError(msg)
        with open(os.path.join(ps, fn), "wb") as fh:
            fh.write(data)
        if on_log:
            on_log("packsync/%s  %.2f МБ" % (fn, len(data) / 1048576))
    rep(100, "Инстанс создан: " + inst)
    return inst


def prism_instances_dirs() -> list:
    out = []
    for label, bases, nested in LAUNCHER_LAYOUTS:
        if not nested:
            continue
        for b in bases:
            if os.path.isdir(b) or os.path.isdir(os.path.dirname(b)):
                out.append((label, b))
    seen, res = set(), []
    for label, b in out:
        k = os.path.normcase(os.path.abspath(b))
        if k in seen:
            continue
        seen.add(k)
        res.append((label, b))
    return res
