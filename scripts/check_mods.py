#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_mods.py — оффлайн-проверка состава модов пака.

Зачем: packwiz следит только за тем, чтобы файлы скачивались, а за
совместимостью модов между собой — никто. Когда аддон FTB Quests собирают под
одну версию FTB Quests, а в паке оказывается другая, игра падает не на старте,
а в самый неподходящий момент (например, при открытии книги квестов) с
неочевидным `MixinApplyError`. Такой случай уже был — см. BLOCKED ниже.

Что делает скрипт:
  1. читает mods/*.pw.toml и восстанавливает по имени файла modid и версию;
  2. сверяет набор модов со списком BLOCKED (заведомо несовместимые пары);
  3. сверяет со списком REQUIRED (моды, которые обязаны быть в паке);
  4. ищет дубли — два разных .pw.toml с одинаковым jar-именем;
  5. предупреждает, если у мода нет блока [update] (обновлять придётся руками).

Запуск:
  python3 scripts/check_mods.py           # проверка
  python3 scripts/check_mods.py --json    # машинный вывод

Скрипт встроен в CI (.github/workflows/validate.yml и pages.yml), поэтому
случайно вернуть «сломанный» мод в пак не получится.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
MODS_DIR = os.path.join(ROOT, "mods")

sys.path.insert(0, SCRIPT_DIR)
from pw import read_toml  # noqa: E402  (строгий TOML-парсер, как у packwiz)

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RST = "\033[0m"

# --------------------------------------------------------------------------- #
#  Правила
# --------------------------------------------------------------------------- #

# Заведомо несовместимые комбинации. Ключ — modid «плохого» мода.
# bad_below/bad_above применяются к его версии, needs_* — к версии партнёра.
BLOCKED = {
    "certain_questing_additions": {
        "bad_below": None,          # ломаются все известные версии (<= 1.2.0.4)
        "needs_mod": "ftbquests",
        "needs_ge": "2101.1.21",    # начиная с этой версии FTB Quests
        "reason": (
            "Certain Questing Additions 1.2.0.4 (последняя сборка на 2026-08-06) "
            "скомпилирован под FTB Quests 2101.1.15…2101.1.20: его миксин "
            "ChapterImageConfigGroupMixin целится в анонимный класс "
            "ChapterImageButton$3 и @Shadow-ит синтетическое поле val$name. "
            "В FTB Quests 2101.1.21+ этот класс — синтетический $SwitchMap "
            "для ChapterImage$TextAlign, поля val$name в нём нет. "
            "Результат: InvalidMixinException → MixinApplyError → краш "
            "«Rendering screen» при первом же открытии книги квестов."
        ),
        "fix": (
            "не добавлять мод, пока автор не выпустит сборку под FTB Quests "
            "2101.1.21+ (репозиторий: github.com/HollowHorizon/"
            "CertainQuestingAdditions). Понижать FTB Quests нельзя: наша книга "
            "использует text_on_image / click_action у ChapterImage — это "
            "появилось только в 2101.1.28, а FTB Quests Entity Visualization "
            "требует >= 2101.1.29."
        ),
        "crash": "crash-2026-10-04_09.33.55-client.txt",
    },
}

# Моды, без которых пак не работает.
REQUIRED = {
    "ftbquests": "книга квестов — ядро пака",
    "ftblibrary": "обязательная зависимость FTB Quests",
    "ftbteams": "обязательная зависимость FTB Quests",
    "architectury": "обязательная зависимость FTB-модов",
    "kubejs": "кастомные предметы, рецепты и диагностика пака",
    "rhino": "JS-движок для KubeJS",
    "galosphere": "контент 9-й секции главы «Земли Рассвета» — без него "
                  "квесты «Глубины Галосферы» невыполнимы",
}

# modid по префиксу имени jar-файла (там, где он не выводится механически).
MODID_BY_PREFIX = [
    ("ftbquestsentityvis", "ftbquestsentityvis"),
    ("ftb-quests-optimizer", "ftbqopt"),
    ("ftbquestsoptimizer", "ftbqopt"),
    ("ftb-quests", "ftbquests"),
    ("ftb-library", "ftblibrary"),
    ("ftb-teams", "ftbteams"),
    ("journeymap-api", "journeymap_api"),
    ("journeymap", "journeymap"),
    ("better-advanced-tooltips", "betteradvancedtooltips"),
    ("architectury-api", "architectury"),
    ("just-enough-items", "jei"),
    ("mousetweaks", "mousetweaks"),
    ("certain_questing_additions", "certain_questing_additions"),
    ("certain-questing-additions", "certain_questing_additions"),
]

def _ver_key(ver: str):
    """Ключ сравнения версий: числовые части как числа, остальное как строки."""
    out = []
    for part in re.split(r"[.\-+]", ver or ""):
        if part.isdigit():
            out.append((1, int(part), ""))
        elif part:
            out.append((0, 0, part.lower()))
    return out


def ver_ge(a: str, b: str) -> bool:
    return _ver_key(a) >= _ver_key(b)


_VERSION_RE = re.compile(
    r"(?<![\w.])(\d+(?:\.\d+)+"            # 13.0.11 / 2101.7.2 / 3.2.0
    r"(?:[-.](?:build|beta|alpha|rc|pre|snapshot)\.?\d+)?)"  # -build.377
    r"(?![\w.])",
    re.IGNORECASE,
)


def minecraft_version() -> str:
    """Версия Minecraft из pack.toml — чтобы не принять её за версию мода."""
    try:
        return str(read_toml(os.path.join(ROOT, "pack.toml")).get("versions", {}).get("minecraft", ""))
    except Exception:
        return ""


_MC_VERSION = None


def split_filename(filename: str):
    """'kubejs-neoforge-2101.7.2-build.377.jar' -> ('kubejs-neoforge', '2101.7.2-build.377').

    Версией считается первое число вида N.N[.N…], которое не является версией
    Minecraft: в 'Jade-1.21.1-NeoForge-15.10.6.jar' это 15.10.6, а в
    'ftb-quests-neoforge-2101.1.36.jar' — 2101.1.36.
    """
    global _MC_VERSION
    if _MC_VERSION is None:
        _MC_VERSION = minecraft_version()
    stem = filename
    if stem.lower().endswith(".jar"):
        stem = stem[:-4]
    for m in _VERSION_RE.finditer(stem):
        if m.group(1) == _MC_VERSION:
            continue
        return stem[: m.start()].rstrip("-_+"), m.group(1)
    return stem, ""


def guess_modid(filename: str) -> str:
    """Восстановить modid по имени jar-файла (для оффлайн-сверки правил)."""
    base, _ = split_filename(filename)
    toks = [t for t in re.split(r"[-_+]", base) if t]
    # лоадер и версия Minecraft в имени файла — не часть modid,
    # но только если токен целиком такой
    mc = minecraft_version()
    toks = [t for t in toks
            if t.lower() not in ("neoforge", "forge", "quilt", "universal")
            and t != mc and not re.match(r"^mc\d", t, re.IGNORECASE)]
    stem = "_".join(toks)
    low = re.sub(r"[-_]", "", stem.lower())
    for prefix, modid in MODID_BY_PREFIX:
        norm = re.sub(r"[-_]", "", prefix.lower())
        if low.startswith(norm) or low == norm + "api":
            return modid
    # FTBQuestsOptimizer -> ftb_questsoptimizer
    stem = re.sub(r"(?<!^)(?=[A-Z])", "_", stem)
    return stem.lower()


def load_mods():
    """-> [{slug, path, name, filename, modid, version, side, has_update, mr_id}]"""
    out = []
    if not os.path.isdir(MODS_DIR):
        return out
    for fn in sorted(os.listdir(MODS_DIR)):
        if not fn.endswith(".pw.toml"):
            continue
        path = os.path.join(MODS_DIR, fn)
        data = read_toml(path)
        filename = data.get("filename", "")
        _, version = split_filename(filename)
        upd = data.get("update", {}) if isinstance(data.get("update"), dict) else {}
        mr = upd.get("modrinth", {}) if isinstance(upd.get("modrinth"), dict) else {}
        out.append({
            "slug": fn[: -len(".pw.toml")],
            "path": path,
            "name": data.get("name", fn),
            "filename": filename,
            "modid": guess_modid(filename),
            "version": version,
            "side": data.get("side", "both"),
            "has_update": bool(upd),
            "mr_id": mr.get("mod-id", ""),
        })
    return out


def check(verbose=True):
    mods = load_mods()
    by_id = {}
    errors = []
    warnings = []

    for m in mods:
        by_id.setdefault(m["modid"], []).append(m)

    # 1. дубли jar-имён
    seen = {}
    for m in mods:
        key = m["filename"].lower()
        if key in seen:
            errors.append("дубль jar-файла %s: %s и %s"
                          % (m["filename"], seen[key], m["slug"]))
        seen[key] = m["slug"]

    # 2. REQUIRED
    for modid, why in REQUIRED.items():
        if modid not in by_id:
            errors.append("в паке нет %s (%s)" % (modid, why))

    # 3. BLOCKED
    for modid, rule in BLOCKED.items():
        if modid not in by_id:
            continue
        m = by_id[modid][0]
        bad = True
        lo, hi = rule.get("bad_below"), rule.get("bad_above")
        if lo and ver_ge(m["version"], lo):
            bad = False
        if hi and not ver_ge(m["version"], hi):
            bad = False
        need = rule.get("needs_mod")
        if need and need in by_id:
            nver = by_id[need][0]["version"]
            if rule.get("needs_ge") and not ver_ge(nver, rule["needs_ge"]):
                bad = False
            if rule.get("needs_lt") and ver_ge(nver, rule["needs_lt"]):
                bad = False
        if bad:
            errors.append(
                "%s %s несовместим с %s %s.\n      Причина: %s\n      Что делать: %s"
                % (m["name"], m["version"] or "?",
                   need or "паком", by_id[need][0]["version"] if need in by_id else "",
                   rule["reason"], rule["fix"])
            )

    # 4. нет [update]
    for m in mods:
        if not m["has_update"]:
            warnings.append("нет [update] — обновлять вручную: mods/%s.pw.toml" % m["slug"])

    if verbose:
        print("%s%d модов в паке%s" % (GREEN if not errors else RED, len(mods), RST))
        for m in mods:
            print("   %-24s %-12s %s" % (m["modid"], m["version"] or "?", m["filename"]))
        for w in warnings:
            print("   %s!%s %s" % (YELLOW, RST, w))
        for e in errors:
            print("   %sXX%s %s" % (RED, RST, e))
        if errors:
            print("\n%sНАЙДЕНЫ НЕСОВМЕСТИМЫЕ МОДЫ: %d%s" % (RED, len(errors), RST))
        else:
            print("\n%sСостав модов в порядке%s" % (GREEN, RST))
    return errors, warnings, mods


def main():
    ap = argparse.ArgumentParser(description="Проверка состава и совместимости модов пака")
    ap.add_argument("--json", action="store_true", help="машинный вывод")
    args = ap.parse_args()

    errors, warnings, mods = check(verbose=not args.json)
    if args.json:
        print(json.dumps({
            "mods": [{k: m[k] for k in ("slug", "name", "modid", "version", "filename", "side")}
                     for m in mods],
            "errors": errors,
            "warnings": warnings,
        }, ensure_ascii=False, indent=2))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
