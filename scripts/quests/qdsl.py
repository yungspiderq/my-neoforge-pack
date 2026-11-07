#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qdsl.py — маленькие помощники для записи квестов в scripts/quests/chapters/*.py.

Это НЕ логика генерации: gen_quests.py по-прежнему проверяет каждую задачу и
награду по схеме, выверенной с исходниками FTB Quests 2101.1.36. Помощники
нужны только для того, чтобы данные глав читались как текст, а не как JSON,
и чтобы опечатка в имени аргумента ловилась сразу (TypeError), а не в игре.

Формат текста везде один: (english, russian). en_us — fallback-локаль FTB
Quests и грузится всегда, ru_ru подхватывается русским клиентом.

Типы задач (все, что использует линейка):
    item, checkmark, kill, dimension, xp, stat, location, advancement,
    observation, biome, structure
НЕ используются: fluid/energy (нужны моды с жидкостями/энергией), gamestage
(нужен Game Stages), custom (без обработчика задачу нельзя завершить —
интеграции KubeJS↔FTB Quests в KubeJS-core нет).
"""

# Кастомные предметы пака. Регистрируются в
# kubejs/startup_scripts/custom_items.js, рецепты — в
# kubejs/server_scripts/recipes.js, текстуры рисует scripts/gen_textures.py.
CUSTOM = {
    "token":   "kubejs:quest_token",
    "premium": "kubejs:quest_token_premium",
    "medal":   "kubejs:quest_medal",
}


# --------------------------------------------------------------------------- #
#  Задачи
# --------------------------------------------------------------------------- #

def item(item_id, count=1, **kw):
    """«Принеси N предметов». Предметы НЕ расходуются (default_consume_items=0)."""
    d = {"type": "item", "item": item_id}
    if count != 1:
        d["count"] = count
    d.update(kw)
    return d


def tag(tag_id, count=1):
    """«Принеси N любых предметов с тегом» — фильтр FTB Filter System.

    Работает только вместе с мостом kubejs/startup_scripts/ffs_tag_bridge.js:
    на 1.21.1 FFS не регистрирует ItemFilterAdapter в FTB Quests сам, мост
    делает это за него (иначе smart_filter в задаче требует сам себя).
    """
    return {"type": "item", "count": count,
            "item": {"id": "ftbfiltersystem:smart_filter", "count": 1,
                     "components": {"ftbfiltersystem:filter":
                                    "ftbfiltersystem:item_tag(%s)" % tag_id}}}


def check():
    """Галочка — «сделано вручную»: вехи, сюжетные отметки, финал."""
    return {"type": "checkmark"}


def kill(entity, count=1, **kw):
    """Убить N существ. entity — id типа существа, например minecraft:blaze."""
    return dict({"type": "kill", "entity": entity, "value": count}, **kw)


def stat(name, value):
    """Счётчик из Statistics (custom-стат): minecraft:walk_one_cm, mob_kills…

    Значение в единицах самой статистики: сантиметры, тики, штуки.
    """
    return {"type": "stat", "stat": name, "value": value}


def adv(advancement, criterion=None):
    """Ванильное достижение (можно указать конкретный критерий)."""
    d = {"type": "advancement", "advancement": advancement}
    if criterion:
        d["criterion"] = criterion
    return d


def biome(biome_id):
    """Побывать в биоме."""
    return {"type": "biome", "biome": biome_id}


def struct(structure_id):
    """Найти структуру (засчитывается, когда игрок оказывается внутри неё)."""
    return {"type": "structure", "structure": structure_id}


def dim(dimension_id):
    """Побывать в измерении."""
    return {"type": "dimension", "dimension": dimension_id}


def xp(levels=0, points=0):
    """Набрать опыт: levels — уровни, points — очки (что-то одно)."""
    if bool(levels) == bool(points):
        raise ValueError("xp(): задайте ровно одно из levels/points")
    d = {"type": "xp", "value": levels if levels else points}
    if points:
        d["points"] = True
    return d


def loc(dimension, position, size, ignore_dimension=False):
    """Побывать в конкретной области мира. position/size — [x, y, z]."""
    return {"type": "location", "dimension": dimension, "position": list(position),
            "size": list(size), "ignore_dimension": bool(ignore_dimension)}


def obs(to_observe, kind="block", timer=10):
    """Посмотреть на блок/сущность в течение timer тиков.

    kind — имя из enum ObserveType: block, block_tag, block_state,
    block_entity, block_entity_type, entity_type, entity_type_tag.
    """
    return {"type": "observation", "to_observe": to_observe,
            "observation_type": kind, "timer": timer}


# --------------------------------------------------------------------------- #
#  Награды
# --------------------------------------------------------------------------- #

def give(item_id, count=1, **kw):
    """Выдать предмет."""
    d = {"type": "item", "item": item_id}
    if count != 1:
        d["count"] = count
    d.update(kw)
    return d


def lvl(levels):
    """Выдать уровни опыта."""
    return {"type": "xp_levels", "xp_levels": int(levels)}


def xpr(points):
    """Выдать очки опыта (без повышения уровня «насильно»)."""
    return {"type": "xp", "xp": int(points)}


def say(command, silent=False, feedback=None):
    """Выполнить команду от имени сервера. @s = получивший награду."""
    d = {"type": "command", "command": command, "permission_level": 2}
    if silent:
        d["silent"] = True
    if feedback:
        d["feedback_message"] = feedback
    return d


def toast(text):
    """Всплывающее уведомление FTB Quests."""
    return {"type": "toast", "description": text}


# --------------------------------------------------------------------------- #
#  Квест
# --------------------------------------------------------------------------- #

def Q(key, title, desc=None, sub=None, icon=None, tasks=None, rewards=None,
      deps=None, shape=None, size=None, section=None, **extra):
    """Один квест.

    key   — короткое имя, на него ссылаются deps и картинки глав
            (внутри главы доступен и просто номер квеста: deps=[3]);
    title — (english, russian) или одна строка на обе локали;
    desc  — список строк/пар (en, ru): каждая строка = абзац в книге;
    deps  — список: номер квеста в этой главе, key, либо "<файл_главы>:<key>".
            Без deps квест наследует предыдущий (цепочка);
    section — ключ секции (обязателен при layout="blocks"): секция рисуется
            отдельным блоком со своей подложкой и подписью;
    shape/size — форма и размер иконки: так отмечаются вехи главы;
    extra — любые другие поля Quest из схемы gen_quests.py:
            optional, invisible_until_tasks, dependency_requirement,
            min_required_dependencies, can_repeat, hide_dependency_lines, …
    """
    d = {"key": key, "title": title}
    if desc is not None:
        d["desc"] = desc
    if sub is not None:
        d["subtitle"] = sub
    if icon is not None:
        d["icon"] = icon
    if shape is not None:
        d["shape"] = shape
    if size is not None:
        d["size"] = size
    if deps is not None:
        d["deps"] = deps
    if section is not None:
        d["section"] = section
    d["tasks"] = list(tasks or [])
    d["rewards"] = list(rewards or [])
    if not d["tasks"]:
        raise ValueError("квест %r: нет ни одной задачи" % key)
    d.update(extra)
    return d


# --------------------------------------------------------------------------- #
#  Оформление главы
# --------------------------------------------------------------------------- #

def SEC(key, title, color, alpha=46, pad=1.05, header=True, backdrop=True,
        header_w=None, header_h=0.9):
    """Секция главы для layout="blocks": цветная подложка + подпись сверху.

    color — 0xRRGGBB, один и тот же цвет идёт на подложку (полупрозрачно)
    и на пластинку заголовка (плотно). Подложка рисуется ПОД квестами
    (order=-200), заголовок — тоже под ними (order=-40), но текст поверх.
    """
    d = {"key": key, "title": title, "color": int(color), "alpha": int(alpha),
         "pad": float(pad), "header": header, "backdrop": backdrop}
    if header_w is not None:
        d["header_w"] = float(header_w)
    if header_h != 0.9:
        d["header_h"] = float(header_h)
    return d



def header(title, at, color, dx=0.0, w=4.2, h=0.85, offset=3.1):
    """Подпись раздела: пластинка с текстом поверх, в ряду над деревом квестов.

    Текст берётся из lang-таблицы (image.<ID>.title), поэтому он переводится
    и рисуется шрифтом игры, а не «запекается» в картинку.
    """
    return {
        "at": at, "align_y": "top", "offset": offset, "dx": dx,
        "w": w, "h": h,
        "image": "kubejs:textures/gui/plate.png",
        "color": color, "alpha": 210,
        "text": True, "text_shadow": True, "text_inset": 7,
        "title": title, "order": -40, "lock": True,
    }


def backdrop(color, alpha=54, margin=6.0):
    """Тёмная подложка под всё дерево квестов главы — иконки читаются лучше."""
    return {
        "fit": "quests", "margin": margin,
        "image": "kubejs:textures/gui/panel_soft.png",
        "color": color, "alpha": alpha, "order": -200, "lock": True,
    }


def halo(at, color, size=3.2, alpha=170):
    """Светящийся ореол позади вехи главы (рисуется под иконкой квеста)."""
    return {
        "at": at, "w": size, "h": size,
        "image": "kubejs:textures/gui/halo.png",
        "color": color, "alpha": alpha, "order": -50, "lock": True,
    }


def portal(at, target, dx=0.0, dy=0.0, size=1.6, texture="portal.png",
           color=None, title=None):
    """Кликабельная картинка-портал: left-click переносит к квесту другой главы.

    target — key квеста («nether:enter»); в NBT попадёт
    click_action: "open_quest:<ID>", который FTB Quests понимает сам.
    """
    d = {
        "at": at, "dx": dx, "dy": dy, "w": size, "h": size,
        "image": "kubejs:textures/gui/%s" % texture,
        "click_quest": target, "order": -30, "lock": True,
    }
    if color is not None:
        d["color"] = color
    if title is not None:
        d["title"] = title
    return d
