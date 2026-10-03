#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_quests.py — генератор квестов FTB Quests из quests/questline.py.

Зачем генератор, а не手写 .snbt:
  • ID (16-символьный hex) должны быть уникальны и не равны 0/1 — readID()
    молча перегенерирует их иначе;
  • lang-ключи строятся как "<objectType>.<ID>.<title|quest_desc|...>", то есть
    ЖЁСТКО привязаны к ID — рассинхрон даст пустые названия квестов;
  • типы числовых полей разные и неочевидные: x/y — double, ItemTask.count —
    LONG, ItemReward.count — int, KillTask.value — LONG, XPLevelsReward —
    поле с именем "xp_levels", а не "levels".

Всё это проверяется СХЕМОЙ ниже. Схема выверена по исходникам FTB Quests
2101.1.36 (ветка 1.21.1/main), а не по догадкам: любое поле, которого нет
в схеме, приводит к ошибке генерации, а не к молча битому квесту.

Запуск:
    python scripts/gen_quests.py            # сгенерировать
    python scripts/gen_quests.py --check    # только проверить, ничего не писать
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "quests"))

OUT_DIR = os.path.join(ROOT, "config", "ftbquests", "quests")

# --------------------------------------------------------------------------- #
#  Схема (выверена по исходникам FTB Quests 2101.1.36)
# --------------------------------------------------------------------------- #

S, I, L, D, B, C, LS = "str", "int", "long", "double", "byte", "compound", "list<str>"
TRISTATE = "tristate"

TASK_SCHEMA = {
    "item":      {"item": C, "count": L, "consume_items": TRISTATE,
                  "only_from_crafting": TRISTATE, "match_components": S,
                  "task_screen_only": B},
    "checkmark": {},
    "kill":      {"entity": S, "value": L, "entityTypeTag": S,
                  "custom_name": S, "nbt_filter": S},
    "dimension": {"dimension": S},
    "xp":        {"value": L, "points": B},
}
TASK_REQUIRED = {"item": ["item"], "kill": ["entity", "value"],
                 "dimension": ["dimension"], "xp": ["value"]}

REWARD_SCHEMA = {
    "item":      {"item": C, "count": I, "random_bonus": I, "only_one": B},
    "xp_levels": {"xp_levels": I},
    "xp":        {"xp": I},
    "command":   {"command": S, "permission_level": I, "silent": B, "feedback_message": S},
    "toast":     {"description": S},
}
REWARD_REQUIRED = {"item": ["item"], "xp_levels": ["xp_levels"], "xp": ["xp"],
                   "command": ["command"]}

QUEST_SCHEMA = {
    "x": D, "y": D, "id": S, "shape": S, "guide_page": S, "size": D, "icon_scale": D,
    "optional": B, "invisible": B, "invisible_until_tasks": B, "min_width": I,
    "hide_dependent_lines": B, "hide_lock_icon": B, "ignore_reward_blocking": B,
    "min_required_dependencies": I, "max_completable_dependents": I,
    "repeat_cooldown": I, "dependency_requirement": S, "progression_mode": S,
    "preset": S,
    "hide_dependency_lines": TRISTATE, "disable_recipe_mod": TRISTATE,
    "hide_until_deps_visible": TRISTATE, "hide_until_deps_complete": TRISTATE,
    "hide_text_until_complete": TRISTATE, "can_repeat": TRISTATE,
    "hide_details_until_startable": TRISTATE, "require_sequential_tasks": TRISTATE,
    "dependencies": LS, "tasks": "list", "rewards": "list",
}

CHAPTER_SCHEMA = {
    "id": S, "group": S, "order_index": I, "filename": S, "always_invisible": B,
    "default_quest_shape": S, "default_quest_size": D,
    "default_hide_dependency_lines": B, "default_min_width": I,
    "progression_mode": S, "consume_items": TRISTATE,
    "hide_quest_details_until_startable": B, "hide_quest_until_deps_visible": B,
    "hide_quest_until_deps_complete": B, "hide_text_until_complete": B,
    "default_repeatable_quest": B, "require_sequential_tasks": B,
    "autofocus_id": S, "preset": S,
    "quests": "list", "quest_links": "list", "images": "list",
}

VALID_SHAPES = {"circle", "diamond", "gear", "heart", "hexagon", "none",
                "octagon", "pentagon", "rsquare", "square", ""}

# TranslationKey enum: TITLE(str), QUEST_SUBTITLE(str), QUEST_DESC(list),
# CHAPTER_SUBTITLE(list)
TRANSLATION_KEYS = {
    "chapter": {"title": S, "chapter_subtitle": LS},
    "quest":   {"title": S, "quest_subtitle": S, "quest_desc": LS},
    "task":    {"title": S},
    "reward":  {"title": S},
}


class GenError(Exception):
    pass


# --------------------------------------------------------------------------- #
#  SNBT
# --------------------------------------------------------------------------- #

class Long(int):
    """Маркер long-литерала: в SNBT это 8L, а не 8."""


class Double(float):
    """Маркер double-литерала: в SNBT это 1.5d."""


def quote(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') \
                        .replace("\n", "\\n").replace("\r", "\\r") \
                        .replace("\t", "\\t") + '"'


def snbt(value, indent: int = 0, pad: str = "\t") -> str:
    """Пишет значение в SNBT. Ключи сортируются — FTB Quests при сохранении
    делает то же самое (SNBT.setShouldSortKeysOnWrite(true)), поэтому совпадение
    порядка устраняет лишний diff, когда квесты правят в игре."""
    if isinstance(value, bool):
        return "1b" if value else "0b"
    if isinstance(value, Long):
        return "%dL" % int(value)
    if isinstance(value, Double):
        f = float(value)
        txt = repr(f)
        if "." not in txt and "e" not in txt and "E" not in txt:
            txt += ".0"
        return txt + "d"
    if isinstance(value, int):
        return str(int(value))
    if isinstance(value, float):
        return snbt(Double(value))
    if isinstance(value, str):
        return quote(value)
    if isinstance(value, (list, tuple)):
        if not value:
            return "[ ]"
        items = [snbt(v, indent + 1, pad) for v in value]
        if all(isinstance(v, (dict,)) for v in value):
            inner = (",\n" + pad * (indent + 1)).join(items)
            return "[\n" + pad * (indent + 1) + inner + "\n" + pad * indent + "]"
        return "[" + ", ".join(items) + "]"
    if isinstance(value, dict):
        if not value:
            return "{ }"
        keys = sorted(value.keys())
        lines = ["%s%s: %s" % (pad * (indent + 1), k, snbt(value[k], indent + 1, pad))
                 for k in keys]
        return "{\n" + ",\n".join(lines) + "\n" + pad * indent + "}"
    raise GenError("неподдерживаемый тип для SNBT: %r" % type(value))


def write_snbt(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(snbt(data) + "\n")


# --------------------------------------------------------------------------- #
#  Валидация
# --------------------------------------------------------------------------- #

def code_string(n: int) -> str:
    """QuestObjectBase.getCodeString(long) = String.format("%016X", id)."""
    if n <= 1:
        raise GenError("ID %d недопустим: readID() перегенерирует 0 и 1" % n)
    if n < 0 or n > 0x7FFFFFFFFFFFFFFF:
        raise GenError("ID %d вне диапазона long" % n)
    return "%016X" % n


def coerce(field: str, value, want: str, ctx: str):
    if want == S:
        if not isinstance(value, str):
            raise GenError("%s: поле %s должно быть строкой, получено %r" % (ctx, field, value))
        return value
    if want == I:
        if isinstance(value, bool) or not isinstance(value, int):
            raise GenError("%s: поле %s должно быть int, получено %r" % (ctx, field, value))
        return int(value)
    if want == L:
        if isinstance(value, bool) or not isinstance(value, int):
            raise GenError("%s: поле %s должно быть long (целое), получено %r" % (ctx, field, value))
        return Long(value)
    if want == D:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise GenError("%s: поле %s должно быть double, получено %r" % (ctx, field, value))
        return Double(float(value))
    if want == B:
        if not isinstance(value, bool):
            raise GenError("%s: поле %s должно быть bool, получено %r" % (ctx, field, value))
        return value
    if want == C:
        if not isinstance(value, dict):
            raise GenError("%s: поле %s должно быть compound, получено %r" % (ctx, field, value))
        return value
    if want == LS:
        if not isinstance(value, (list, tuple)) or any(not isinstance(x, str) for x in value):
            raise GenError("%s: поле %s должно быть списком строк" % (ctx, field))
        return list(value)
    if want == TRISTATE:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str) and value in ("default", "true", "false"):
            return value
        raise GenError("%s: поле %s должно быть tristate (default/true/false)" % (ctx, field))
    raise GenError("%s: неизвестный тип в схеме: %s" % (ctx, want))


def validate_entry(entry: dict, schema: dict, required, ctx: str, kind: str) -> dict:
    """Проверяет словарь against схема; возвращает SNBT-ready копию."""
    t = entry.get("type")
    if kind in ("task", "reward"):
        allowed = TASK_SCHEMA if kind == "task" else REWARD_SCHEMA
        req = TASK_REQUIRED if kind == "task" else REWARD_REQUIRED
        if t not in allowed:
            raise GenError("%s: неизвестный type=%r. Разрешены (проверены по "
                           "исходникам): %s" % (ctx, t, ", ".join(sorted(allowed))))
        schema = allowed[t]
        required = req.get(t, [])
    out = {"type": t} if kind in ("task", "reward") else {}
    for r in required:
        if r not in entry:
            raise GenError("%s: отсутствует обязательное поле %r" % (ctx, r))
    for k, v in entry.items():
        if k == "type":
            continue
        if k not in schema:
            raise GenError("%s: неизвестное поле %r (type=%r). Разрешены: %s"
                           % (ctx, k, t, ", ".join(sorted(schema))))
        out[k] = coerce("%s.%s" % (ctx, k), v, schema[k], ctx)
    if kind == "item_holder" or "item" in out:
        pass
    return out


def item_stack(item_id: str, count: int = 1) -> dict:
    """ItemStack SNBT для 1.20.5+: {id, count} (компоненты заменили tag).

    FTB пишет saveItemSingleLine(itemStack.copyWithCount(1)) — то есть count
    внутри item ВСЕГДА 1, а реальное количество хранится в отдельном поле count.
    """
    if not isinstance(item_id, str) or ":" not in item_id:
        raise GenError("item должен быть вида 'namespace:path', получено %r" % item_id)
    ns, path = item_id.split(":", 1)
    if not re_ok(ns) or not re_ok(path):
        raise GenError("некорректный идентификатор предмета: %r" % item_id)
    return {"id": item_id, "count": 1}


def re_ok(s: str) -> bool:
    import re as _re
    return bool(_re.fullmatch(r"[a-z0-9_.\-/]+", s))


# --------------------------------------------------------------------------- #
#  Генерация
# --------------------------------------------------------------------------- #

def text_pair(v, field, ctx):
    """(en, ru) -> два значения; одиночная строка дублируется в обе локали."""
    if isinstance(v, str):
        return v, v
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, str) for x in v):
        return v[0], v[1]
    raise GenError("%s: %s должен быть строкой или парой (en, ru), получено %r" % (ctx, field, v))


def build(questline, file_version, file_settings):
    chapters, ids, used_ids = [], {}, {}
    translations = {"en_us": {}, "ru_ru": {}}
    problems = []

    def take(n, what):
        if n in used_ids:
            raise GenError("дублирующийся ID %s: %s и %s" % (code_string(n), used_ids[n], what))
        used_ids[n] = what
        return code_string(n)

    for ci, ch in enumerate(questline):
        ctx = "глава %r" % ch.get("filename", ci)
        if "id" not in ch or "filename" not in ch:
            raise GenError("%s: нужны 'id' и 'filename'" % ctx)
        shape = ch.get("shape", "")
        if shape not in VALID_SHAPES:
            raise GenError("%s: shape=%r нет среди текстур мода (%s)"
                           % (ctx, shape, ", ".join(sorted(x for x in VALID_SHAPES if x))))

        ch_id_raw = ch["id"]
        ch_id = take(ch_id_raw, ctx)

        # заголовок и подзаголовок главы -> lang
        t_en, t_ru = text_pair(ch["title"], "title", ctx)
        translations["en_us"]["chapter.%s.title" % ch_id] = t_en
        translations["ru_ru"]["chapter.%s.title" % ch_id] = t_ru
        sub = ch.get("subtitle") or []
        if sub:
            for loc, idx in (("en_us", 0), ("ru_ru", 1)):
                lines = []
                for item in sub:
                    pair = item if isinstance(item, (list, tuple)) else (item, item)
                    lines.append(pair[idx] if isinstance(pair, (list, tuple)) else pair)
                translations[loc]["chapter.%s.chapter_subtitle" % ch_id] = lines

        chapter_nbt = {
            "id": ch_id,
            "group": "",                 # пустая строка = default group (так пишет сам мод)
            "order_index": ci,
            "filename": ch["filename"],
            "default_quest_shape": shape,
            "default_hide_dependency_lines": False,
            "quests": [],
            "quest_links": [],
            "images": [],
        }
        for k, v in ch.items():
            if k in ("id", "filename", "shape", "title", "subtitle", "quests"):
                continue
            if k not in CHAPTER_SCHEMA:
                raise GenError("%s: неизвестное поле главы %r" % (ctx, k))
            chapter_nbt[k] = coerce("%s.%s" % (ctx, k), v, CHAPTER_SCHEMA[k], ctx)

        for qi, q in enumerate(ch.get("quests", [])):
            qctx = "%s / квест %#x" % (ctx, q.get("id", 0))
            if "id" not in q:
                raise GenError("%s: нужен 'id'" % qctx)
            q_id = take(q["id"], qctx)
            ids[q["id"]] = q_id

            quest_nbt = {
                "id": q_id,
                "x": Double(float(q.get("x", qi * 1.5))),
                "y": Double(float(q.get("y", 0.0))),
            }
            for k, v in q.items():
                if k in ("id", "x", "y", "title", "subtitle", "desc", "deps", "tasks", "rewards"):
                    continue
                if k not in QUEST_SCHEMA:
                    raise GenError("%s: неизвестное поле квеста %r" % (qctx, k))
                quest_nbt[k] = coerce("%s.%s" % (qctx, k), v, QUEST_SCHEMA[k], qctx)

            # --- текст квеста -> lang ---
            if "title" in q:
                te, tr = text_pair(q["title"], "title", qctx)
                translations["en_us"]["quest.%s.title" % q_id] = te
                translations["ru_ru"]["quest.%s.title" % q_id] = tr
            if "subtitle" in q:
                se, sr = text_pair(q["subtitle"], "subtitle", qctx)
                translations["en_us"]["quest.%s.quest_subtitle" % q_id] = se
                translations["ru_ru"]["quest.%s.quest_subtitle" % q_id] = sr
            if q.get("desc"):
                for loc, idx in (("en_us", 0), ("ru_ru", 1)):
                    lines = []
                    for item in q["desc"]:
                        pair = item if isinstance(item, (list, tuple)) else (item, item)
                        lines.append(pair[idx] if isinstance(pair, (list, tuple)) else pair)
                    translations[loc]["quest.%s.quest_desc" % q_id] = lines

            # --- задачи ---
            tasks = []
            for ti, t in enumerate(q.get("tasks", [])):
                tctx = "%s / задача %d" % (qctx, ti + 1)
                raw = dict(t)
                if raw.get("type") == "item" and "item" in raw:
                    raw["item"] = item_stack(raw["item"], raw.get("count", 1))
                t_id = take(_sub_id(q["id"], 0x2000, ti, "задача"), tctx)
                entry = validate_entry(raw, TASK_SCHEMA, None, tctx, "task")
                entry = {"id": t_id, **entry}
                # count=1 FTB не пишет
                if entry.get("count") == 1:
                    entry.pop("count", None)
                tasks.append(entry)
            if tasks:
                quest_nbt["tasks"] = tasks

            # --- награды ---
            rewards = []
            for ri, r in enumerate(q.get("rewards", [])):
                rctx = "%s / награда %d" % (qctx, ri + 1)
                raw = dict(r)
                if raw.get("type") == "item" and "item" in raw:
                    raw["item"] = item_stack(raw["item"], raw.get("count", 1))
                r_id = take(_sub_id(q["id"], 0x3000, ri, "награда"), rctx)
                entry = validate_entry(raw, REWARD_SCHEMA, None, rctx, "reward")
                entry = {"id": r_id, **entry}
                if entry.get("count") == 1:
                    entry.pop("count", None)
                rewards.append(entry)
            if rewards:
                quest_nbt["rewards"] = rewards

            chapter_nbt["quests"].append(quest_nbt)

        chapters.append((ch, ch_id, chapter_nbt))

    # --- зависимости: проверяем, что все цели существуют ---
    for ch, ch_id, nbt in chapters:
        for q, qn in zip(ch.get("quests", []), nbt["quests"]):
            deps = q.get("deps") or []
            out = []
            for d in deps:
                if d not in ids:
                    raise GenError("квест %#x ссылается на несуществующую зависимость %#x"
                                   % (q["id"], d))
                out.append(ids[d])
            if out:
                qn["dependencies"] = sorted(out)

    data_nbt = {"version": int(file_version)}
    for k, v in (file_settings or {}).items():
        if k == "default_quest_shape":
            if v not in VALID_SHAPES:
                raise GenError("data.snbt: default_quest_shape=%r недопустима" % v)
            data_nbt[k] = v
        else:
            raise GenError("data.snbt: поле %r не проверено — добавьте его в схему "
                           "gen_quests.py, прежде чем использовать" % k)

    return chapters, data_nbt, translations, used_ids


def _sub_id(quest_id: int, base: int, index: int, what: str) -> int:
    """ID задачи/награды из ID квеста.

    Младший байт ID квеста должен быть нулевым — туда пишется индекс
    под-объекта (0..15). Например квест 0x1110:
        задача 0 -> 0x2110, задача 1 -> 0x2111, ...
        награда 0 -> 0x3110
    Квесты в одной главе разнесены шагом 0x10, поэтому диапазоны не пересекаются.
    """
    if index > 0xF:
        raise GenError("у квеста %#x больше 15 под-объектов (%s) — не хватает "
                       "младшего байта ID" % (quest_id, what))
    slot = quest_id & 0xFFF
    if slot == 0:
        raise GenError("ID квеста %#x: младшие 12 бит не должны быть нулём" % quest_id)
    if slot % 0x10 != 0:
        raise GenError("ID квеста %#x: младший байт должен быть 0, чтобы в нём "
                       "разместить индекс (%s). Используйте схему 0x1cq0 из "
                       "документации questline.py" % (quest_id, what))
    return base + slot + index


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="только проверить, не писать")
    ap.add_argument("--out", default=OUT_DIR, help="куда писать (по умолчанию config/ftbquests/quests)")
    args = ap.parse_args()

    import questline as Q

    chapters, data_nbt, translations, used = build(Q.QUESTLINE, Q.FILE_VERSION, Q.FILE_SETTINGS)

    nq = sum(len(c[2]["quests"]) for c in chapters)
    nt = sum(len(q.get("tasks", [])) for c in chapters for q in c[2]["quests"])
    nr = sum(len(q.get("rewards", [])) for c in chapters for q in c[2]["quests"])
    print("глав: %d   квестов: %d   задач: %d   наград: %d   уникальных ID: %d"
          % (len(chapters), nq, nt, nr, len(used)))

    # --- перекрёстная проверка lang-ключей ---
    # used: {int id -> описание}; lang-ключи содержат code-строки, поэтому
    # сравнивать нужно именно с ними
    obj_ids = {code_string(k) for k in used}
    for loc, table in translations.items():
        for key in table:
            parts = key.split(".")
            if len(parts) != 3:
                raise GenError("некорректный lang-ключ: " + key)
            if parts[1] not in obj_ids:
                raise GenError("lang-ключ %s ссылается на несуществующий ID" % key)
            if parts[2] not in TRANSLATION_KEYS.get(parts[0], {}):
                raise GenError("lang-ключ %s: неизвестный суб-ключ %r" % (key, parts[2]))
            want = TRANSLATION_KEYS[parts[0]][parts[2]]
            val = table[key]
            if want == LS and not isinstance(val, list):
                raise GenError("lang-ключ %s должен быть списком строк" % key)
            if want == S and not isinstance(val, str):
                raise GenError("lang-ключ %s должен быть строкой" % key)
    print("lang-ключей: en_us=%d ru_ru=%d — все привязаны к существующим ID"
          % (len(translations["en_us"]), len(translations["ru_ru"])))

    if args.check:
        print("CHECK OK — ничего не записано")
        return 0

    out = args.out
    # чистим старое, чтобы не оставалось глав от предыдущей версии линейки
    import shutil
    if os.path.isdir(out):
        shutil.rmtree(out)

    write_snbt(os.path.join(out, "data.snbt"), data_nbt)
    write_snbt(os.path.join(out, "chapter_groups.snbt"), {"chapter_groups": []})
    for ch, ch_id, nbt in chapters:
        write_snbt(os.path.join(out, "chapters", ch["filename"] + ".snbt"), nbt)
    for loc, table in translations.items():
        write_snbt(os.path.join(out, "lang", loc + ".snbt"), table)

    total = sum(len(f) for _, _, f in os.walk(out))
    print("записано в %s:" % os.path.relpath(out, ROOT))
    for root, dirs, files in os.walk(out):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            print("   %-46s %6d байт" % (os.path.relpath(p, out).replace(os.sep, "/"),
                                         os.path.getsize(p)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GenError as e:
        print("\033[31mОШИБКА ГЕНЕРАЦИИ:\033[0m %s" % e, file=sys.stderr)
        sys.exit(1)
