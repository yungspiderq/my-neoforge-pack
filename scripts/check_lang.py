#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_lang.py — контроль полноты русского перевода Galosphere.

Мод Galosphere 1.21.1-1.5.5 поставляет «русский» перевод, который устарел ещё
в 1.20.x: из 297 ключей en_us.json в нём закрыто лишь 73 (ещё 34 — мёртвые
ключи старой номенклатуры: silver → palladium, warped_anchor → burrow_anchor,
advancements.story.* → advancements.galosphere.*). В игре это выглядит как
английские названия почти всех блоков/предметов/достижений.

Мы кладём ПОЛНЫЙ ru_ru-оверрайд в kubejs/assets/galosphere/lang/ru_ru.json
(папка kubejs/assets работает как ресурс-пак с приоритетом выше jar'ов модов;
языковые файлы Minecraft мержит по ключам). Этот скрипт гарантирует, что
оверрайд остаётся полным и валидным:

  1. каждый ключ en_us присутствует в ru_ru (иначе в игре снова английский);
  2. нет лишних ключей (опечатка в имени ключа = тихий пропуск перевода);
  3. значения непустые;
  4. ни одно значение не оставлено английским (ru == en);
  5. плейсхолдеры формата (%s, %d, %1$s…) совпадают с английскими.

Эталон ключей — снимок en_us.json из jar'а мода:
    scripts/lang/galosphere_en_us.json
(в пак игрокам НЕ входит — scripts/ исключён .packwizignore'ом).

Режимы:
    python scripts/check_lang.py                  # офлайн, по снимку
    python scripts/check_lang.py --online         # скачать jar по mods/galosphere.pw.toml
                                                  # и свериться с живым en_us.json
    python scripts/check_lang.py --online --update-snapshot
                                                  # то же + перезаписать снимок
                                                  # (после обновления версии мода)

Код возврата: 0 — перевод полный, 1 — найдены проблемы, 2 — ошибка окружения.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "scripts" / "lang" / "galosphere_en_us.json"
OVERRIDE = ROOT / "kubejs" / "assets" / "galosphere" / "lang" / "ru_ru.json"
PW_TOML = ROOT / "mods" / "galosphere.pw.toml"

FMT_RE = re.compile(r"%(?:\d+\$)?[sdf]")


def die(msg: str, code: int = 2) -> "NoReturn":  # type: ignore[name-defined]
    print(f"[check_lang] ОШИБКА: {msg}")
    sys.exit(code)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"файл не найден: {path}")
    except json.JSONDecodeError as e:
        die(f"{path.name}: невалидный JSON: {e}")


def fetch_en_online() -> dict:
    """Скачать jar Galosphere по mods/galosphere.pw.toml и вернуть en_us.json."""
    import urllib.request

    toml = PW_TOML.read_text(encoding="utf-8")
    m = re.search(r'^url\s*=\s*"([^"]+)"', toml, re.M)
    if not m:
        die(f"в {PW_TOML.name} не найден url для скачивания")
    url = m.group(1)
    print(f"[check_lang] скачиваю {url} …")
    req = urllib.request.Request(url, headers={"User-Agent": "my-neoforge-pack/check_lang"})
    try:
        data = urllib.request.urlopen(req, timeout=120).read()
    except Exception as e:  # noqa: BLE001
        die(f"не удалось скачать jar: {e}")
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        raw = z.read("assets/galosphere/lang/en_us.json")
    except Exception as e:  # noqa: BLE001
        die(f"не удалось прочитать en_us.json из jar: {e}")
    return json.loads(raw.decode("utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--online", action="store_true",
                    help="сверить с en_us.json из живого jar'а (нужен интернет)")
    ap.add_argument("--update-snapshot", action="store_true",
                    help="перезаписать снимок scripts/lang/galosphere_en_us.json (с --online)")
    args = ap.parse_args()

    if args.online:
        en = fetch_en_online()
        if args.update_snapshot:
            SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
            SNAPSHOT.write_text(
                json.dumps(en, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                encoding="utf-8")
            print(f"[check_lang] снимок обновлён: {SNAPSHOT.relative_to(ROOT)} ({len(en)} ключей)")
    else:
        en = load_json(SNAPSHOT)
        if args.update_snapshot:
            die("--update-snapshot имеет смысл только вместе с --online")

    ru = load_json(OVERRIDE)
    problems: list[str] = []

    missing = sorted(k for k in en if k not in ru)
    extra = sorted(k for k in ru if k not in en)
    empty = sorted(k for k, v in ru.items() if not str(v).strip())
    untranslated = sorted(k for k in en if k in ru and ru[k] == en[k])

    placeholders = []
    for k, v in sorted(en.items()):
        if k not in ru:
            continue
        want, got = FMT_RE.findall(str(v)), FMT_RE.findall(str(ru[k]))
        if want != got:
            placeholders.append(f"{k}: en={want} ru={got}")

    for label, items in (("не переведено ключей", missing),
                         ("лишних ключей", extra),
                         ("пустых значений", empty),
                         ("значений, оставленных английскими", untranslated)):
        if items:
            problems.append(f"{label}: {len(items)}")
            for k in items[:20]:
                problems.append(f"    {k}")
            if len(items) > 20:
                problems.append(f"    … и ещё {len(items) - 20}")
    if placeholders:
        problems.append(f"плейсхолдеры не совпадают: {len(placeholders)}")
        problems.extend(f"    {p}" for p in placeholders[:20])

    total = len(en)
    covered = sum(1 for k in en if k in ru and str(ru[k]).strip() and ru[k] != en[k])
    if problems:
        print(f"[check_lang] ru_ru: {covered}/{total} ключей — НАЙДЕНЫ ПРОБЛЕМЫ:")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print(f"[check_lang] OK: ru_ru Galosphere покрывает {covered}/{total} ключей "
          f"({'живой jar' if args.online else 'снимок ' + SNAPSHOT.name})")


if __name__ == "__main__":
    main()
