#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_quests.py — генератор квестов FTB Quests из scripts/quests/questline.py.

Зачем генератор, а не рукописные .snbt:
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
sys.path.insert(0, os.path.join(ROOT, "scripts", "quests"))

OUT_DIR = os.path.join(ROOT, "config", "ftbquests", "quests")

# --------------------------------------------------------------------------- #
#  Схема (выверена по исходникам FTB Quests 2101.1.36)
# --------------------------------------------------------------------------- #

S, I, L, D, B, C, LS = "str", "int", "long", "double", "byte", "compound", "list<str>"
INTARRAY = "intarray"
TRISTATE = "tristate"

TASK_SCHEMA = {
    "item":        {"item": C, "count": L, "consume_items": TRISTATE,
                    "only_from_crafting": TRISTATE, "match_components": S,
                    "task_screen_only": B},
    "checkmark":   {},
    "kill":        {"entity": S, "value": L, "entityTypeTag": S,
                    "custom_name": S, "nbt_filter": S},
    "dimension":   {"dimension": S},
    "xp":          {"value": L, "points": B},
    "stat":        {"stat": S, "value": I},
    "location":    {"dimension": S, "ignore_dimension": B,
                    "position": INTARRAY, "size": INTARRAY},
    "advancement": {"advancement": S, "criterion": S},
    "observation": {"timer": L, "observation_type": S, "observe_type": I,
                    "to_observe": S},
    "biome":       {"biome": S},
    "structure":   {"structure": S},
}
TASK_REQUIRED = {"item": ["item"], "kill": ["entity", "value"],
                 "dimension": ["dimension"], "xp": ["value"],
                 "stat": ["stat", "value"],
                 "location": ["dimension", "position", "size"],
                 "advancement": ["advancement"],
                 "observation": ["timer", "observation_type", "to_observe"],
                 "biome": ["biome"], "structure": ["structure"]}

# ObserveType.NAME_MAP: id = name().toLowerCase(), а в NBT пишется ЕЩЁ и
# observe_type = ordinal(). Порядок enum из ObservationTask.java:
OBSERVE_TYPES = ["block", "block_tag", "block_state", "block_entity",
                 "block_entity_type", "entity_type", "entity_type_tag"]

REWARD_SCHEMA = {
    "item":      {"item": C, "count": I, "random_bonus": I, "only_one": B},
    "xp_levels": {"xp_levels": I},
    "xp":        {"xp": I},
    "command":   {"command": S, "permission_level": I, "silent": B,
                  "feedback_message": S},
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
    "preset": S, "icon": C,
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
    "progression_mode": S, "consume_items": TRISTATE, "icon": C,
    "hide_quest_details_until_startable": B, "hide_quest_until_deps_visible": B,
    "hide_quest_until_deps_complete": B, "hide_text_until_complete": B,
    "default_repeatable_quest": B, "require_sequential_tasks": B,
    "autofocus_id": S, "preset": S,
    "quests": "list", "quest_links": "list", "images": "list",
}

# поля, которые автор задаёт в questline.py, но которые НЕ попадают в SNBT главы
# как обычные ключи (обрабатываются генератором отдельно)
CHAPTER_META = {"id", "filename", "shape", "title", "subtitle", "quests",
                "layout", "cols", "dx", "dy", "pad_x", "pad_y", "sections",
                "banner", "banner_w", "banner_h", "banner_gap", "gate", "icon",
                "images", "links"}

# flow — раскладка по графу зависимостей (слева направо, ветвление видно);
# остальные — «геометрические»: порядок квестов в списке = порядок на экране
LAYOUTS = ("blocks", "flow", "line", "zigzag", "grid", "ring", "spiral", "tree")

# поля секции (layout="blocks"): key/title обязательны, остальное — оформление
SECTION_META = {"key", "title", "color", "alpha", "pad", "header", "backdrop",
                "header_h", "header_w"}

VALID_SHAPES = {"circle", "diamond", "gear", "heart", "hexagon", "none",
                "octagon", "pentagon", "rsquare", "square", ""}

# ChapterImage.writeData() — все поля картинки главы, сверено с исходниками
# 2101.1.36. "image" — строка-иконка Icon.getIcon():
#   "kubejs:textures/gui/x.png"  — текстура из ресурсов
#   "item:minecraft:diamond"     — иконка предмета
#   "color:#RRGGBB"               — сплошной цвет (панель/подложка)
#   "a + b"                      — несколько иконок друг на другом
IMAGE_SCHEMA = {
    "x": D, "y": D, "width": D, "height": D, "rotation": D, "image": S,
    "color": I, "alpha": I, "order": I, "click_action": S, "dev": B,
    "corner": B, "dependency": S, "position_locked": B, "text_on_image": B,
    "text_shadow": B, "text_inset": I, "text_h_align": S, "text_v_align": S,
}
# короткие имена автора -> имена полей NBT
IMAGE_ALIASES = {"w": "width", "h": "height", "rot": "rotation",
                 "lock": "position_locked", "text": "text_on_image",
                 "text_h": "text_h_align", "text_v": "text_v_align"}
# эти ключи автора обрабатывает генератор, в NBT они не пишутся
IMAGE_META = {"at", "dx", "dy", "dep", "title", "fit", "margin",
              "align_y", "offset", "click_quest", "click_command",
              "click_uri"}

# ImageClickAction.ActionType — id перечисления; в NBT пишется "<type>:<data>"
CLICK_ACTIONS = ("none", "open_uri", "open_quest", "run_command",
                 "custom_event", "show_recipe", "show_docs")

TEXT_ALIGN = ("start", "middle", "end")

# QuestLink.writeData() — «портал» к квесту из другой главы
LINK_SCHEMA = {"x": D, "y": D, "shape": S, "size": D}
LINK_META = {"quest", "at", "dx", "dy"}

# TranslationKey enum: TITLE(str), QUEST_SUBTITLE(str), QUEST_DESC(list),
# CHAPTER_SUBTITLE(list). Ключ lang-таблицы строится как
# "<objectType.id>.<ID16hex>.<subKey>" (TranslationManager.makeKey), поэтому
# заголовок картинки главы живёт в ключе image.<ID>.title.
TRANSLATION_KEYS = {
    "chapter":    {"title": S, "chapter_subtitle": LS},
    "quest":      {"title": S, "quest_subtitle": S, "quest_desc": LS},
    "task":       {"title": S},
    "reward":     {"title": S},
    "image":      {"title": S},
    "quest_link": {"title": S},
}


class GenError(Exception):
    pass


# --------------------------------------------------------------------------- #
#  SNBT
# --------------------------------------------------------------------------- #

class Long(int):
    """Маркер long-литерала: в SNBT это 8L, а не 8."""


class IntArray(list):
    """Маркер IntArrayTag: в SNBT это [I; 1, 2, 3]."""


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
        # округление до 1e-6: координаты считаются арифметикой раскладки,
        # и без него в файл уезжает хвост вида 7.300000000000001d
        f = round(float(value), 6)
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
    if isinstance(value, IntArray):
        return "[I; %s]" % ", ".join(str(int(v)) for v in value)
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
    if want == INTARRAY:
        if not isinstance(value, (list, tuple)) or len(value) != 3 or \
                any(isinstance(v, bool) or not isinstance(v, int) for v in value):
            raise GenError("%s: поле %s должно быть целочисленным массивом из 3 "
                           "элементов ([x, y, z]), получено %r" % (ctx, field, value))
        return IntArray([int(v) for v in value])
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


def layout_points(layout, n, cols=4, dx=1.5, dy=1.5):
    """«Геометрические» раскладки: координаты зависят только от номера квеста.

    Шаг 1.5 — как в редакторе FTB Quests. Для ветвящихся деревьев используйте
    layout="flow" (см. flow_points).
    """
    import math
    pts = []
    if layout == "line":
        for k in range(n):
            pts.append(((k - (n - 1) / 2) * dx, 0.0))
    elif layout == "zigzag":
        for k in range(n):
            r, c = divmod(k, cols)
            x = c if r % 2 == 0 else (cols - 1 - c)
            pts.append(((x - (cols - 1) / 2) * dx, r * dy))
    elif layout == "grid":
        rows = max(1, -(-n // cols))
        for k in range(n):
            r, c = divmod(k, cols)
            pts.append(((c - (cols - 1) / 2) * dx, (r - (rows - 1) / 2) * dy))
    elif layout == "ring":
        R = 1.8 + 0.22 * n
        for k in range(n):
            a = -math.pi / 2 + 2 * math.pi * k / max(1, n)
            pts.append((R * math.cos(a), R * math.sin(a)))
    elif layout == "spiral":
        for k in range(n):
            a = k * 0.85
            r = 0.9 + k * 0.34
            pts.append((r * math.cos(a), r * math.sin(a)))
    elif layout == "tree":
        for k in range(n):
            branch = 0.0 if k % 3 == 0 else (1.7 if (k // 3) % 2 == 0 else -1.7)
            pts.append((branch, k * dy))
    else:
        raise GenError("неизвестная раскладка %r (есть: %s)"
                       % (layout, ", ".join(LAYOUTS)))
    return pts


def flow_points(n, deps, dx=2.0, dy=1.35):
    """Слоистая раскладка по графу зависимостей (слева направо).

    deps: {индекс_квеста_0based: [индексы_родителей]} — только внутри главы.
    Слой узла = 1 + максимум слоёв родителей, у корней 0. Внутри слоя узлы
    сортируются по медиане позиций родителей/детей (несколько проходов
    вверх-вниз), поэтому линии зависимостей почти не пересекаются и глава
    читается как дерево прокачки, а не как свалка кружков.
    """
    if n == 0:
        return []
    layer = {}
    state = [0] * n                     # 0 не был, 1 в стеке, 2 готов

    def visit(i, stack):
        if state[i] == 1:
            cycle = stack[stack.index(i):] + [i]
            raise GenError("цикл в зависимостях главы: %s"
                           % " -> ".join(str(c + 1) for c in cycle))
        if state[i] == 2:
            return layer[i]
        state[i] = 1
        d = 0
        for p in deps.get(i, []):
            if p == i:
                raise GenError("квест %d зависит сам от себя" % (i + 1))
            d = max(d, visit(p, stack + [i]) + 1)
        state[i] = 2
        layer[i] = d
        return d

    for i in range(n):
        visit(i, [])

    children = {i: [] for i in range(n)}
    for i, ps in deps.items():
        for p in ps:
            children.setdefault(p, []).append(i)

    max_layer = max(layer.values())
    layers = [[] for _ in range(max_layer + 1)]
    for i in range(n):                  # порядок объявления как начальный
        layers[layer[i]].append(i)

    pos = {}
    for L in layers:
        for k, i in enumerate(L):
            pos[i] = k

    def bary(i, neigh):
        vals = [pos[j] for j in neigh if j in pos]
        return sum(vals) / len(vals) if vals else float(pos[i])

    for _ in range(8):
        for li in range(1, len(layers)):
            L = layers[li]
            L.sort(key=lambda i: (bary(i, deps.get(i, [])), i))
            for k, i in enumerate(L):
                pos[i] = k
        for li in range(len(layers) - 2, -1, -1):
            L = layers[li]
            L.sort(key=lambda i: (bary(i, children.get(i, [])), i))
            for k, i in enumerate(L):
                pos[i] = k

    pts = [None] * n
    for i in range(n):
        L = layers[layer[i]]
        pts[i] = (layer[i] * dx, (pos[i] - (len(L) - 1) / 2.0) * dy)
    return pts


def blocks_layout(n, deps_by_idx, sec_of, sections, dx, dy, cols, pad_x, pad_y):
    """Раскладка «витрина»: глава делится на секции, каждая рисуется отдельным
    блоком со своей подложкой и подписью.

    Внутри секции — обычная слоистая раскладка flow по её собственным
    зависимостям; связи между секциями остаются (линии рисуются поверх блоков),
    но на геометрию не влияют. Блоки укладываются полками по cols штук в ряд.

    Возвращает (positions {индекс0: (x, y)}, boxes {секция: (x0, y0, x1, y1)}).
    """
    members = {s: [] for s in sections}
    for i in range(n):
        members[sec_of[i]].append(i)

    local_pts, sizes = {}, {}
    for sec in sections:
        mem = members[sec]
        remap = {i: k for k, i in enumerate(mem)}
        ldeps = {k: [remap[p] for p in deps_by_idx.get(i, []) if p in remap]
                 for k, i in enumerate(mem)}
        pts = flow_points(len(mem), ldeps, dx, dy)
        minx = min(p[0] for p in pts)
        miny = min(p[1] for p in pts)
        local_pts[sec] = {i: (pts[k][0] - minx, pts[k][1] - miny)
                          for k, i in enumerate(mem)}
        sizes[sec] = (max(p[0] for p in pts) - minx, max(p[1] for p in pts) - miny)

    positions, boxes = {}, {}
    y_off = 0.0
    for row in range(0, len(sections), max(1, cols)):
        chunk = sections[row:row + max(1, cols)]
        x_off, row_h = 0.0, 0.0
        for sec in chunk:
            w, h = sizes[sec]
            for i, (lx, ly) in local_pts[sec].items():
                positions[i] = (x_off + lx, y_off + ly)
            boxes[sec] = (x_off, y_off, x_off + w, y_off + h)
            x_off += w + pad_x
            row_h = max(row_h, h)
        y_off += row_h + pad_y
    return positions, boxes


# --------------------------------------------------------------------------- #
#  ID
#
#  Схема (младший полубайт квеста всегда 0 — в него пишутся индексы задач
#  и наград, до 15 штук на квест):
#      глава      0xC000 + ci                     ci = 1..255
#      квест      0x100000 + ci*0x1000 + qi*0x10  qi = 1..255
#      задача     0x200000 + slot + t             t  = 0..15
#      награда    0x300000 + slot + r             r  = 0..15
#      картинка   0x400000 + ci*0x1000 + i        i  = 1..255
#      quest_link 0x500000 + ci*0x1000 + l        l  = 1..255
#  где slot = (id квеста) & 0xFFFFF = ci*0x1000 + qi*0x10.
#  Диапазоны не пересекаются, поэтому коллизий не бывает by construction.
# --------------------------------------------------------------------------- #

QUEST_BASE, TASK_BASE, REWARD_BASE, IMAGE_BASE, LINK_BASE = \
    0x100000, 0x200000, 0x300000, 0x400000, 0x500000
CHAPTER_BASE = 0xC000


def quest_id_of(ci: int, qi: int) -> int:
    """ci — номер главы с 1, qi — номер квеста с 1."""
    if not 1 <= ci <= 0xFF:
        raise GenError("номер главы %d вне диапазона 1..255" % ci)
    if not 1 <= qi <= 0xFF:
        raise GenError("номер квеста %d вне диапазона 1..255 (глава %d)" % (qi, ci))
    return QUEST_BASE + ci * 0x1000 + qi * 0x10


def quest_index_of(raw: int):
    """raw id квеста -> (ci, qi); None, если это не id квеста."""
    if raw < QUEST_BASE or raw >= QUEST_BASE + 0x100000:
        return None
    slot = raw - QUEST_BASE
    if slot % 0x10 != 0:
        return None
    return slot // 0x1000, (slot % 0x1000) // 0x10


def image_id_of(ci: int, ii: int) -> int:
    return IMAGE_BASE + ci * 0x1000 + ii


def link_id_of(ci: int, li: int) -> int:
    return LINK_BASE + ci * 0x1000 + li


def _sub_id(quest_id: int, base: int, index: int, what: str) -> int:
    """ID задачи/награды из ID квеста (см. схему выше)."""
    if index > 0xF:
        raise GenError("у квеста %#x больше 15 под-объектов (%s) — не хватает "
                       "младшего полубайта ID" % (quest_id, what))
    slot = quest_id & 0xFFFFF
    if slot == 0:
        raise GenError("ID квеста %#x: младшие 20 бит не должны быть нулём" % quest_id)
    if slot % 0x10 != 0:
        raise GenError("ID квеста %#x: младший полубайт должен быть 0, чтобы в нём "
                       "разместить индекс (%s). Используйте quest_id_of() из "
                       "gen_quests.py" % (quest_id, what))
    return base + slot + index


def build(questline, file_version, file_settings):
    chapters = []
    ids = {}                 # int id -> code string
    used_ids = {}            # int id -> описание, кто занял
    translations = {"en_us": {}, "ru_ru": {}}

    def take(n, what):
        if n in used_ids:
            raise GenError("дублирующийся ID %s: %s и %s"
                           % (code_string(n), used_ids[n], what))
        used_ids[n] = what
        ids[n] = code_string(n)
        return code_string(n)

    # --- pass 0: обязательные поля глав -------------------------------------
    for ci, ch in enumerate(questline, start=1):
        ctx = "глава #%d %r" % (ci, ch.get("filename", ci))
        for req in ("id", "filename", "title"):
            if req not in ch:
                raise GenError("%s: нет обязательного поля %r" % (ctx, req))
        layout = ch.get("layout", "flow")
        if layout not in LAYOUTS:
            raise GenError("%s: layout=%r не из %s" % (ctx, layout, ", ".join(LAYOUTS)))
        shape = ch.get("shape", "")
        if shape not in VALID_SHAPES:
            raise GenError("%s: shape=%r нет среди текстур мода" % (ctx, shape))
        if not (ch.get("quests") or []):
            raise GenError("%s: нет ни одного квеста" % ctx)
        for k in ch:
            if k not in CHAPTER_META and k not in CHAPTER_SCHEMA:
                raise GenError("%s: неизвестное поле главы %r" % (ctx, k))
        sec_keys = [sec.get("key") for sec in (ch.get("sections") or [])]
        if len(set(sec_keys)) != len(sec_keys):
            raise GenError("%s: дублирующийся key секции" % ctx)
        for sec in (ch.get("sections") or []):
            for k in sec:
                if k not in SECTION_META:
                    raise GenError("%s: неизвестное поле секции %r" % (ctx, k))
            for req in ("key", "title"):
                if req not in sec:
                    raise GenError("%s: у секции нет %r" % (ctx, req))
        for qi, q in enumerate(ch["quests"], 1):
            if layout == "blocks":
                if q.get("section") not in sec_keys:
                    raise GenError("%s / квест %d: section=%r не объявлен в "
                                   "sections главы (%s)"
                                   % (ctx, qi, q.get("section"), ", ".join(sec_keys)))
            elif "section" in q:
                raise GenError("%s / квест %d: section работает только с "
                               "layout=\"blocks\"" % (ctx, qi))
            for k in q:
                if k in ("key", "deps", "x", "y", "title", "subtitle", "desc",
                         "tasks", "rewards", "icon", "section"):
                    continue
                if k not in QUEST_SCHEMA:
                    raise GenError("%s / квест %d: неизвестное поле %r" % (ctx, qi, k))

    # --- pass 1: ID квестов и ключи для зависимостей ------------------------
    # Глобальные ключи всегда содержат имя главы ("<файл>:<key|номер>"), поэтому
    # одинаковые key в разных главах не конфликтуют. Внутри главы key и номер
    # квеста доступны и без префикса.
    keymap = {}              # "<файл>:<key|номер>" -> (raw id, контекст)
    localmap = {}            # "<файл>" -> {"<key>": (raw id, контекст)}

    def reg(key, raw, ctx):
        if key in keymap:
            raise GenError("дублирующийся ключ квеста %r: %s и %s"
                           % (key, keymap[key][1], ctx))
        keymap[key] = (raw, ctx)

    for ci, ch in enumerate(questline, start=1):
        fn = ch["filename"]
        localmap.setdefault(fn, {})
        for qi, q in enumerate(ch["quests"], start=1):
            raw = quest_id_of(ci, qi)
            ctx = "%s / квест %d" % (fn, qi)
            reg("%s:%d" % (fn, qi), raw, ctx)
            if q.get("key"):
                if not isinstance(q["key"], str):
                    raise GenError("%s: key должен быть строкой" % ctx)
                if ":" in q["key"]:
                    raise GenError("%s: key не должен содержать двоеточие" % ctx)
                if q["key"] in localmap[fn]:
                    raise GenError("%s: дублирующийся key внутри главы" % ctx)
                localmap[fn][q["key"]] = (raw, ctx)
                reg("%s:%s" % (fn, q["key"]), raw, ctx)

    def dep_raw(spec, fn, ctx):
        if isinstance(spec, bool):
            raise GenError("%s: ссылка не должна быть bool" % ctx)
        if isinstance(spec, int):
            key = "%s:%d" % (fn, spec)
        elif isinstance(spec, str):
            if ":" in spec:
                key = spec
            elif spec in localmap.get(fn, {}):
                return localmap[fn][spec][0]
            else:
                key = "%s:%s" % (fn, spec)
        else:
            raise GenError("%s: ссылка %r — не номер и не строка" % (ctx, spec))
        if key not in keymap:
            raise GenError(
                "%s: %r не найдено. Формат: номер квеста в этой главе (3), его "
                'key ("diamonds") либо "<файл_главы>:<key|номер>" '
                '("overworld:portalow")' % (ctx, spec))
        return keymap[key][0]


    # --- pass 2: зависимости ------------------------------------------------
    deps_raw = {}            # raw id квеста -> [raw id]
    prev_chapter_last = None
    for ci, ch in enumerate(questline, start=1):
        fn = ch["filename"]
        n = len(ch["quests"])
        for qi, q in enumerate(ch["quests"], start=1):
            raw = quest_id_of(ci, qi)
            ctx = "%s / квест %d" % (fn, qi)
            specs = q.get("deps")
            if specs is None:
                # без явных deps — цепочка от предыдущего квеста главы;
                # первый квест может быть «привязан» к предыдущей главе (gate)
                if qi > 1:
                    specs = [qi - 1]
                elif ch.get("gate") and prev_chapter_last is not None:
                    deps_raw[raw] = [prev_chapter_last]
                    continue
                else:
                    specs = []
            if isinstance(specs, (int, str)):
                specs = [specs]
            if not isinstance(specs, (list, tuple)):
                raise GenError("%s: deps должен быть списком" % ctx)
            out = []
            for s in specs:
                t = dep_raw(s, fn, ctx)
                if t == raw:
                    raise GenError("%s: квест зависит сам от себя" % ctx)
                out.append(t)
            deps_raw[raw] = sorted(set(out))
        prev_chapter_last = quest_id_of(ci, n)

    # --- pass 3: раскладки ---------------------------------------------------
    positions = {}           # raw id квеста -> (x, y)
    section_boxes = {}       # ci -> {секция: (x0, y0, x1, y1)}
    section_order = {}       # ci -> [key секции]
    for ci, ch in enumerate(questline, start=1):
        n = len(ch["quests"])
        layout = ch.get("layout", "flow")
        if layout == "blocks":
            secs = [sec["key"] for sec in ch["sections"]]
            section_order[ci] = secs
            sec_of = {}
            deps_by_idx = {}
            for qi in range(1, n + 1):
                raw = quest_id_of(ci, qi)
                sec_of[qi - 1] = ch["quests"][qi - 1]["section"]
                idxs = []
                for d in deps_raw.get(raw, []):
                    t = quest_index_of(d)
                    if t and t[0] == ci:
                        idxs.append(t[1] - 1)
                deps_by_idx[qi - 1] = idxs
            pts, boxes = blocks_layout(n, deps_by_idx, sec_of, secs,
                                       float(ch.get("dx", 2.0)),
                                       float(ch.get("dy", 1.4)),
                                       int(ch.get("cols", 2)),
                                       float(ch.get("pad_x", 4.0)),
                                       float(ch.get("pad_y", 5.0)))
            section_boxes[ci] = boxes
            for qi in range(1, n + 1):
                positions[quest_id_of(ci, qi)] = pts[qi - 1]
        elif layout == "flow":
            local = {}
            for qi in range(1, n + 1):
                raw = quest_id_of(ci, qi)
                idxs = []
                for d in deps_raw.get(raw, []):
                    t = quest_index_of(d)
                    if t and t[0] == ci:
                        idxs.append(t[1] - 1)
                local[qi - 1] = idxs
            pts = flow_points(n, local, float(ch.get("dx", 2.0)),
                              float(ch.get("dy", 1.35)))
        else:
            pts = layout_points(layout, n, ch.get("cols", 4),
                                float(ch.get("dx", 1.5)), float(ch.get("dy", 1.5)))
        for qi in range(1, n + 1):
            positions[quest_id_of(ci, qi)] = pts[qi - 1]

    # --- pass 4: NBT ---------------------------------------------------------
    for ci, ch in enumerate(questline, start=1):
        ctx = "глава #%d %r" % (ci, ch.get("filename", ci))
        fn = ch["filename"]
        quests = ch["quests"]
        n = len(quests)

        ch_id = take(ch["id"], ctx)
        t_en, t_ru = text_pair(ch["title"], "title", ctx)
        translations["en_us"]["chapter.%s.title" % ch_id] = t_en
        translations["ru_ru"]["chapter.%s.title" % ch_id] = t_ru
        for loc, idx in (("en_us", 0), ("ru_ru", 1)):
            lines = []
            for item in (ch.get("subtitle") or []):
                pair = item if isinstance(item, (list, tuple)) else (item, item)
                lines.append(pair[idx] if isinstance(pair, (list, tuple)) else pair)
            if lines:
                translations[loc]["chapter.%s.chapter_subtitle" % ch_id] = lines

        chapter_nbt = {
            "id": ch_id,
            "group": "",
            "order_index": ci - 1,
            "filename": fn,
            "default_quest_shape": ch.get("shape", ""),
            "default_hide_dependency_lines": False,
            "quests": [],
            "quest_links": [],
            "images": [],
        }
        for k, v in ch.items():
            if k in CHAPTER_META:
                continue
            chapter_nbt[k] = coerce("%s.%s" % (ctx, k), v, CHAPTER_SCHEMA[k], ctx)
        if "icon" in ch:
            chapter_nbt["icon"] = item_stack(ch["icon"], 1)

        chapter_quests = []
        for qi, q in enumerate(quests, start=1):
            qctx = "%s / квест %d" % (ctx, qi)
            raw_id = quest_id_of(ci, qi)
            q_id = take(raw_id, qctx)
            qx, qy = positions[raw_id]

            quest_nbt = {
                "id": q_id,
                "x": Double(float(q.get("x", qx))),
                "y": Double(float(q.get("y", qy))),
            }
            for k, v in q.items():
                if k in ("key", "deps", "id", "x", "y", "title", "subtitle",
                         "desc", "tasks", "rewards", "icon", "section"):
                    continue
                quest_nbt[k] = coerce("%s.%s" % (qctx, k), v, QUEST_SCHEMA[k], qctx)
            if "icon" in q:
                quest_nbt["icon"] = item_stack(q["icon"], 1)

            for loc, idx in (("en_us", 0), ("ru_ru", 1)):
                pair = text_pair(q["title"], "title", qctx)
                translations[loc]["quest.%s.title" % q_id] = pair[idx]
                if q.get("subtitle"):
                    sp = text_pair(q["subtitle"], "subtitle", qctx)
                    translations[loc]["quest.%s.quest_subtitle" % q_id] = sp[idx]
                lines = []
                for item in (q.get("desc") or []):
                    p2 = item if isinstance(item, (list, tuple)) else (item, item)
                    lines.append(p2[idx] if isinstance(p2, (list, tuple)) else p2)
                if lines:
                    translations[loc]["quest.%s.quest_desc" % q_id] = lines

            tasks = []
            for ti, t in enumerate(q.get("tasks", [])):
                tctx = "%s / задача %d" % (qctx, ti + 1)
                raw = dict(t)
                if raw.get("type") == "observation":
                    name = raw.get("observation_type")
                    if name not in OBSERVE_TYPES:
                        raise GenError("%s: observation_type=%r не из enum "
                                       "ObserveType (%s)" % (tctx, name, OBSERVE_TYPES))
                    raw.setdefault("observe_type", OBSERVE_TYPES.index(name))
                if raw.get("type") == "item" and "item" in raw:
                    raw["item"] = item_stack(raw["item"], raw.get("count", 1))
                t_id = take(_sub_id(raw_id, TASK_BASE, ti, "задача"), tctx)
                entry = validate_entry(raw, TASK_SCHEMA, None, tctx, "task")
                entry = {"id": t_id, **entry}
                if entry.get("count") == 1:
                    entry.pop("count", None)
                tasks.append(entry)
            if tasks:
                quest_nbt["tasks"] = tasks
            else:
                raise GenError("%s: у квеста нет ни одной задачи" % qctx)

            rewards = []
            for ri, r in enumerate(q.get("rewards", [])):
                rctx = "%s / награда %d" % (qctx, ri + 1)
                raw = dict(r)
                if raw.get("type") == "item" and "item" in raw:
                    raw["item"] = item_stack(raw["item"], raw.get("count", 1))
                r_id = take(_sub_id(raw_id, REWARD_BASE, ri, "награда"), rctx)
                entry = validate_entry(raw, REWARD_SCHEMA, None, rctx, "reward")
                entry = {"id": r_id, **entry}
                if entry.get("count") == 1:
                    entry.pop("count", None)
                rewards.append(entry)
            if rewards:
                quest_nbt["rewards"] = rewards

            dep_codes = [code_string(d) for d in deps_raw.get(raw_id, [])]
            if dep_codes:
                quest_nbt["dependencies"] = sorted(set(dep_codes))

            chapter_nbt["quests"].append(quest_nbt)
            chapter_quests.append((raw_id, q, quest_nbt))

        # --- картинки главы (баннер + авторские) ---
        xs = [positions[quest_id_of(ci, qi)][0] for qi in range(1, n + 1)]
        ys = [positions[quest_id_of(ci, qi)][1] for qi in range(1, n + 1)]
        cx_all = (min(xs) + max(xs)) / 2.0
        cy_all = (min(ys) + max(ys)) / 2.0

        img_no = 0
        raw_images = []
        for sec in (ch.get("sections") or []):
            x0, y0, x1, y1 = section_boxes[ci][sec["key"]]
            color = int(sec.get("color", 0x2E6B3A))
            pad = float(sec.get("pad", 1.05))
            if sec.get("backdrop", True):
                img_no += 1
                raw_images.append((img_no, {
                    "x": Double((x0 + x1) / 2.0), "y": Double((y0 + y1) / 2.0),
                    "width": Double(x1 - x0 + 2 * pad + 1.0),
                    "height": Double(y1 - y0 + 2 * pad + 1.0),
                    "rotation": Double(0.0),
                    "image": "kubejs:textures/gui/panel_soft.png",
                    "color": color, "alpha": int(sec.get("alpha", 46)),
                    "order": -200, "position_locked": True,
                }, None, "%s / подложка секции %r" % (ctx, sec["key"])))
            if sec.get("header", True):
                img_no += 1
                hw = float(sec.get("header_w") or min(max(x1 - x0 + 2.2, 3.6), 9.5))
                hh = float(sec.get("header_h", 0.9))
                raw_images.append((img_no, {
                    "x": Double((x0 + x1) / 2.0),
                    "y": Double(y0 - pad - hh / 2.0 - 0.25),
                    "width": Double(hw), "height": Double(hh),
                    "rotation": Double(0.0),
                    "image": "kubejs:textures/gui/plate.png",
                    "color": color, "alpha": 225, "order": -40,
                    "text_on_image": True, "text_shadow": True, "text_inset": 7,
                    "position_locked": True,
                }, text_pair(sec["title"], "title",
                             "%s / секция %r" % (ctx, sec["key"])),
                    "%s / заголовок секции %r" % (ctx, sec["key"])))

        if ch.get("banner"):
            img_no += 1
            bw = float(ch.get("banner_w", 12.0))
            bh = float(ch.get("banner_h", 3.0))
            gap = float(ch.get("banner_gap", 1.7))
            raw_images.append((img_no, {
                "x": Double(cx_all),
                "y": Double(min(ys) - gap - bh / 2.0),
                "width": Double(bw), "height": Double(bh), "rotation": Double(0.0),
                "image": "kubejs:textures/gui/%s.png" % ch["banner"],
                "order": -100,
            }, None, "%s / баннер" % ctx))

        for im in (ch.get("images") or []):
            img_no += 1
            ictx = "%s / картинка %d" % (ctx, img_no)
            out, title, base = {}, None, None

            if "at" in im:
                tgt = dep_raw(im["at"], fn, ictx)
                if tgt not in positions:
                    raise GenError("%s: at=%r — не квест этой главы" % (ictx, im["at"]))
                base = positions[tgt]

            for k, v in im.items():
                if k in IMAGE_META:
                    continue
                kk = IMAGE_ALIASES.get(k, k)
                if kk not in IMAGE_SCHEMA:
                    raise GenError("%s: неизвестное поле картинки %r" % (ictx, k))
                out[kk] = coerce("%s.%s" % (ictx, kk), v, IMAGE_SCHEMA[kk], ictx)
            if "image" not in out:
                raise GenError("%s: нет поля image (строка-иконка)" % ictx)

            # --- позиция ---
            if im.get("fit") == "quests":
                m = float(im.get("margin", 1.5))
                out.setdefault("x", Double(cx_all))
                out.setdefault("y", Double(cy_all))
                out.setdefault("width", Double(max(xs) - min(xs) + 2 * m + 1.0))
                out.setdefault("height", Double(max(ys) - min(ys) + 2 * m + 1.0))
            elif "x" not in out or "y" not in out:
                if base is None:
                    raise GenError("%s: нужны x и y (или at=<ключ квеста>, или "
                                   "fit=\"quests\")" % ictx)
                bx = base[0] + float(im.get("dx", 0.0))
                by = base[1] + float(im.get("dy", 0.0))
                ay = im.get("align_y")
                if ay == "top":
                    by = min(ys) - float(im.get("offset", 3.0))
                elif ay == "bottom":
                    by = max(ys) + float(im.get("offset", 3.0))
                elif ay is not None:
                    raise GenError("%s: align_y=%r — бывает top/bottom" % (ictx, ay))
                out.setdefault("x", Double(bx))
                out.setdefault("y", Double(by))
            for fk in ("width", "height", "rotation"):
                out.setdefault(fk, Double(0.0 if fk == "rotation" else 1.0))

            # --- показывать только после завершения квеста ---
            if "dependency" in out:
                raise GenError("%s: пишите dep=<ключ квеста>, а не dependency "
                               "(code-строку генератор подставит сам)" % ictx)
            if "dep" in im:
                out["dependency"] = code_string(dep_raw(im["dep"], fn, ictx))

            # --- действие по клику ---
            clicks = [k for k in ("click_quest", "click_command", "click_uri")
                      if k in im]
            if len(clicks) > 1:
                raise GenError("%s: только одно из %s" % (ictx, ", ".join(clicks)))
            if clicks or "click_action" in out:
                if clicks:
                    k = clicks[0]
                    if k == "click_quest":
                        act = "open_quest:" + code_string(dep_raw(im[k], fn, ictx))
                    elif k == "click_command":
                        act = "run_command:" + str(im[k])
                    else:
                        act = "open_uri:" + str(im[k])
                    out["click_action"] = act
                act = out["click_action"]
                if act.split(":", 1)[0] not in CLICK_ACTIONS:
                    raise GenError("%s: click_action=%r — тип не из %s"
                                   % (ictx, act, ", ".join(CLICK_ACTIONS)))

            for a in ("text_h_align", "text_v_align"):
                if a in out and out[a] not in TEXT_ALIGN:
                    raise GenError("%s: %s=%r не из %s" % (ictx, a, out[a], TEXT_ALIGN))
            if out.get("text_on_image") and "title" not in im:
                raise GenError("%s: text_on_image без title — рисовать нечего" % ictx)
            if "title" in im:
                title = text_pair(im["title"], "title", ictx)
            raw_images.append((img_no, out, title, ictx))

        for img_no, out, title, ictx in raw_images:
            i_id = take(image_id_of(ci, img_no), ictx)
            entry = {"id": i_id}
            entry.update(out)
            chapter_nbt["images"].append(entry)
            if title:
                translations["en_us"]["image.%s.title" % i_id] = title[0]
                translations["ru_ru"]["image.%s.title" % i_id] = title[1]

        # --- ссылки на квесты других глав (quest_links) ---
        for li, lk in enumerate(ch.get("links") or [], start=1):
            lctx = "%s / ссылка %d" % (ctx, li)
            if "quest" not in lk:
                raise GenError("%s: нет поля quest" % lctx)
            tgt = dep_raw(lk["quest"], fn, lctx)
            out = {}
            for k, v in lk.items():
                if k in LINK_META:
                    continue
                if k not in LINK_SCHEMA:
                    raise GenError("%s: неизвестное поле ссылки %r" % (lctx, k))
                out[k] = coerce("%s.%s" % (lctx, k), v, LINK_SCHEMA[k], lctx)
            if "x" not in out or "y" not in out:
                if "at" in lk:
                    btgt = dep_raw(lk["at"], fn, lctx)
                    bx, by = positions[btgt]
                else:
                    # слева от первого столбца, на уровне квестов-наследников
                    bx = min(xs) - float(ch.get("dx", 2.0))
                    heirs = [positions[quest_id_of(ci, qi)][1] for qi in range(1, n + 1)
                             if tgt in deps_raw.get(quest_id_of(ci, qi), [])]
                    by = sum(heirs) / len(heirs) if heirs else 0.0
                out["x"] = Double(bx + float(lk.get("dx", 0.0)))
                out["y"] = Double(by + float(lk.get("dy", 0.0)))
            l_id = take(link_id_of(ci, li), lctx)
            entry = {"id": l_id, "linked_quest": code_string(tgt)}
            entry.update(out)
            chapter_nbt["quest_links"].append(entry)

        chapters.append((ch, ch_id, chapter_nbt, chapter_quests))

    data_nbt = {"version": int(file_version)}
    for k, v in (file_settings or {}).items():
        if k == "default_quest_shape":
            if v not in VALID_SHAPES:
                raise GenError("data.snbt: default_quest_shape=%r недопустима" % v)
            data_nbt[k] = v
        elif k == "fallback_locale" and isinstance(v, str):
            data_nbt[k] = v
        elif k == "default_consume_items" and isinstance(v, bool):
            data_nbt[k] = v
        else:
            raise GenError("data.snbt: поле %r не проверено — добавьте его в схему "
                           "gen_quests.py, прежде чем использовать" % k)

    return chapters, data_nbt, translations, used_ids


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
    ni = sum(len(c[2].get("images", [])) for c in chapters)
    nl = sum(len(c[2].get("quest_links", [])) for c in chapters)
    nd = sum(len(q.get("dependencies", [])) for c in chapters for q in c[2]["quests"])
    print("глав: %d   квестов: %d   задач: %d   наград: %d   картинок: %d   "
          "ссылок: %d   зависимостей: %d   уникальных ID: %d"
          % (len(chapters), nq, nt, nr, ni, nl, nd, len(used)))
    for ch, _cid, nbt, _cqs in chapters:
        pts = [(float(q["x"]), float(q["y"])) for q in nbt["quests"]]
        seen = {}
        for i, p_ in enumerate(pts, 1):
            if p_ in seen:
                raise GenError("глава %r: квесты %d и %d стоят в одной точке %s — "
                               "иконки наложатся друг на друга"
                               % (ch["filename"], seen[p_], i, p_))
            seen[p_] = i
        print("   %-14s квестов %-4d картинок %-3d ссылок %-2d  %s"
              % (ch["filename"], len(nbt["quests"]), len(nbt["images"]),
                 len(nbt["quest_links"]),
                 "x[%.1f…%.1f] y[%.1f…%.1f]" % (min(p[0] for p in pts),
                                                max(p[0] for p in pts),
                                                min(p[1] for p in pts),
                                                max(p[1] for p in pts))))

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
    for ch, ch_id, nbt, _cqs in chapters:
        write_snbt(os.path.join(out, "chapters", ch["filename"] + ".snbt"), nbt)
    for loc, table in translations.items():
        write_snbt(os.path.join(out, "lang", loc + ".snbt"), table)

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
