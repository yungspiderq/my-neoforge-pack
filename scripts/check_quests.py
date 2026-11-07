#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_quests.py — проверка квестов FTB Quests БЕЗ запуска Minecraft.

Ловит ровно те ошибки, из-за которых квесты молча не появляются или падают
при загрузке:
  1. синтаксис SNBT (файлы парсятся обратно настоящим парсером);
  2. формат ID: 16 символов uppercase hex, уникальны, не 0 и не 1
     (readID() иначе молча перегенерирует ID и все связи поедут);
  3. dependencies ссылаются на существующие квесты;
  4. типы задач и наград есть в реестре мода, обязательные поля на месте;
  5. lang-ключи: у каждой главы и квеста есть title, все ключи привязаны
     к существующим ID, списочные ключи — действительно списки;
  6. кастомные предметы kubejs:* из квестов зарегистрированы в
     startup_scripts и имеют рецепт в server_scripts;
  7. (опционально, --registry) все minecraft:* существуют в 1.21.1.

Запуск:
    python scripts/check_quests.py
    python scripts/check_quests.py --registry      # + сверка с реестром MC
    python scripts/gen_quests.py && python scripts/check_quests.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTS = os.path.join(ROOT, "config", "ftbquests", "quests")
KUBEJS = os.path.join(ROOT, "kubejs")

REGISTRY_PATH = os.path.join(ROOT, "scripts", "quests", "mc_registry_1.21.1.json")

TASK_TYPES = {"item", "checkmark", "kill", "dimension", "xp", "stat",
              "location", "advancement", "observation", "biome", "structure"}
TASK_REQUIRED = {"item": ["item"], "kill": ["entity", "value"],
                 "dimension": ["dimension"], "xp": ["value"],
                 "stat": ["stat", "value"],
                 "location": ["dimension", "position", "size"],
                 "advancement": ["advancement"],
                 "observation": ["timer", "observation_type", "to_observe"],
                 "biome": ["biome"], "structure": ["structure"]}
TASK_FIELD_TYPES = {
    "kill":       {"value": "long"},
    "xp":         {"value": "long"},
    "stat":       {"value": "int"},
    "observation": {"timer": "long", "observe_type": "int"},
    "item":       {"count": "long"},
}
OBSERVE_TYPES = {"block", "block_tag", "block_state", "block_entity",
                 "block_entity_type", "entity_type", "entity_type_tag"}
REWARD_TYPES = {"item", "xp_levels", "xp", "command", "toast"}
REWARD_REQUIRED = {"item": ["item"], "xp_levels": ["xp_levels"],
                   "xp": ["xp"], "command": ["command"]}
REWARD_FIELD_TYPES = {"item": {"count": "int", "random_bonus": "int"},
                      "xp_levels": {"xp_levels": "int"}, "xp": {"xp": "int"}}
VALID_SHAPES = {"circle", "diamond", "gear", "heart", "hexagon", "none",
                "octagon", "pentagon", "rsquare", "square", ""}
LIST_KEYS = {"quest_desc", "chapter_subtitle"}

# ChapterImage.writeData()/readData() — 2101.1.36. Картинки главы рисуются
# слоем BACKGROUND под линиями зависимостей и квестами; порядок между ними
# задаёт поле order.
IMAGE_FIELDS = {"x": "double", "y": "double", "width": "double",
                "height": "double", "rotation": "double", "image": "str",
                "color": "int", "alpha": "int", "order": "int",
                "click_action": "str", "dev": "bool", "corner": "bool",
                "dependency": "str", "position_locked": "bool",
                "text_on_image": "bool", "text_shadow": "bool",
                "text_inset": "int", "text_h_align": "str",
                "text_v_align": "str", "icon": "compound", "tags": "list"}
IMAGE_CLICK_ACTIONS = {"none", "open_uri", "open_quest", "run_command",
                       "custom_event", "show_recipe", "show_docs"}
IMAGE_TEXT_ALIGN = {"start", "middle", "end"}
# QuestLink.writeData()
LINK_FIELDS = {"x": "double", "y": "double", "shape": "str", "size": "double",
               "linked_quest": "str", "icon": "compound", "tags": "list"}
# иконка объекта (QuestObjectBase.rawIcon) пишется как ItemStack SNBT
ICON_KINDS = ("item:", "color:", "bullet:", "hollow_rectangle:", "part:")

errs, warns, oks = [], [], []
alldeps = []            # [(id_зависимости, контекст)] — заполняется при разборе глав


def err(m): errs.append(m)
def warn(m): warns.append(m)
def ok(m): oks.append(m)


# --------------------------------------------------------------------------- #
#  SNBT-парсер (рекурсивный спуск)
# --------------------------------------------------------------------------- #

UNQUOTED = re.compile(r"[A-Za-z0-9_.\-+]+")
NUM = re.compile(r"^-?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?[bBsSlLfFdD]?$", re.I)


class SnbtError(Exception):
    pass


class Snbt:
    def __init__(self, text: str):
        self.s = text
        self.i = 0

    def ws(self):
        while self.i < len(self.s):
            c = self.s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif self.s.startswith("//", self.i):
                j = self.s.find("\n", self.i)
                self.i = len(self.s) if j < 0 else j
            elif self.s.startswith("/*", self.i):
                j = self.s.find("*/", self.i)
                self.i = len(self.s) if j < 0 else j + 2
            else:
                break

    def parse(self):
        self.ws()
        v = self.value()
        self.ws()
        if self.i != len(self.s):
            raise SnbtError("лишние данные после значения на позиции %d: %r"
                            % (self.i, self.s[self.i:self.i + 40]))
        return v

    def value(self):
        self.ws()
        if self.i >= len(self.s):
            raise SnbtError("неожиданный конец файла")
        c = self.s[self.i]
        if c == "{":
            return self.compound()
        if c == "[":
            return self.list()
        if c in "\"'":            # строка в кавычках — до числового скаляра
            return self.quoted()
        return self.scalar()

    def compound(self):
        self.i += 1
        out = {}
        self.ws()
        if self.i < len(self.s) and self.s[self.i] == "}":
            self.i += 1
            return out
        while True:
            self.ws()
            key = self.key()
            self.ws()
            if self.i >= len(self.s) or self.s[self.i] != ":":
                raise SnbtError("ожидалось ':' после ключа %r (позиция %d)" % (key, self.i))
            self.i += 1
            if key in out:
                raise SnbtError("дублирующийся ключ %r в compound" % key)
            out[key] = self.value()
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1
                continue
            if self.i < len(self.s) and self.s[self.i] == "}":
                self.i += 1
                return out
            raise SnbtError("ожидалась ',' или '}' на позиции %d" % self.i)

    def key(self):
        c = self.s[self.i]
        if c in '"\'':
            return self.quoted()
        m = UNQUOTED.match(self.s, self.i)
        if not m:
            raise SnbtError("некорректный ключ на позиции %d" % self.i)
        self.i = m.end()
        return m.group(0)

    def quoted(self):
        q = self.s[self.i]
        self.i += 1
        out = []
        while True:
            if self.i >= len(self.s):
                raise SnbtError("незакрытая строка")
            c = self.s[self.i]
            if c == "\\":
                nxt = self.s[self.i + 1] if self.i + 1 < len(self.s) else ""
                out.append({"n": "\n", "t": "\t", "r": "\r"}.get(nxt, nxt))
                self.i += 2
                continue
            if c == q:
                self.i += 1
                return "".join(out)
            out.append(c)
            self.i += 1

    def list(self):
        self.i += 1
        self.ws()
        # типизированные списки: [I; ...] [B; ...] [L; ...]
        if self.i + 1 < len(self.s) and self.s[self.i + 1] == ";" and self.s[self.i] in "IBL":
            self.i += 2
        out = []
        self.ws()
        if self.i < len(self.s) and self.s[self.i] == "]":
            self.i += 1
            return out
        while True:
            out.append(self.value())
            self.ws()
            if self.i < len(self.s) and self.s[self.i] == ",":
                self.i += 1
                continue
            if self.i < len(self.s) and self.s[self.i] == "]":
                self.i += 1
                return out
            raise SnbtError("ожидалась ',' или ']' на позиции %d" % self.i)

    def scalar(self):
        m = UNQUOTED.match(self.s, self.i)
        if not m:
            raise SnbtError("некорректное значение на позиции %d" % self.i)
        tok = m.group(0)
        self.i = m.end()
        if tok in ("true", "false"):
            return tok == "true"
        if not NUM.match(tok):
            # нечисловой неэкранированный токен = строка (SNBT это допускает)
            return tok
        return tok            # оставляем строкой с суффиксом — тип проверим отдельно


def read_snbt(path: str):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    try:
        return Snbt(text).parse()
    except SnbtError as e:
        raise SnbtError("%s: %s" % (os.path.basename(path), e))


def num_kind(raw) -> str:
    """Тип числового литерала SNBT: long / float / double / byte / short / int."""
    if isinstance(raw, bool):
        return "bool"
    if not isinstance(raw, str):
        return "unknown"
    t = raw[-1].lower()
    if t == "l":
        return "long"
    if t == "f":
        return "float"
    if t == "d":
        return "double"
    if t == "b":
        return "byte"
    if t == "s":
        return "short"
    return "int"


# --------------------------------------------------------------------------- #
#  Проверки
# --------------------------------------------------------------------------- #

ID_RE = re.compile(r"^[0-9A-F]{16}$")


KUBEJS_TEX_RE = re.compile(r"^[a-z0-9_.\-]+:textures/[a-z0-9_./\-]+\.(png|jpg)$")


def check_id(v, ctx):
    if not isinstance(v, str) or not ID_RE.match(v):
        err("%s: id=%r не является 16-символьным uppercase hex" % (ctx, v))
        return None
    if int(v, 16) in (0, 1):
        err("%s: id=%s недопустим (0 и 1 перегенерируются модом)" % (ctx, v))
        return None
    return v


def check_item_stack(item, ctx):
    if not isinstance(item, dict):
        err("%s: item должен быть compound, получено %r" % (ctx, type(item).__name__))
        return None
    iid = item.get("id")
    if not isinstance(iid, str) or ":" not in iid:
        err("%s: item.id должен быть 'namespace:path', получено %r" % (ctx, iid))
        return None
    cnt = item.get("count", 1)
    if num_kind(cnt) not in ("int",):
        err("%s: item.count должен быть int (внутри стака), получено %r (%s)"
            % (ctx, cnt, num_kind(cnt)))
    return iid


def check_icon_field(icon, ctx):
    """QuestObjectBase.icon — это ItemStack SNBT {id, count} либо строка-иконка
    (Icon.getIcon). Возвращает id предмета, если иконка предметная."""
    if isinstance(icon, str):
        if icon.endswith((".png", ".jpg")) or icon.startswith(ICON_KINDS):
            return None
        warn("%s: icon=%r — нестандартная строка-иконка" % (ctx, icon))
        return None
    if isinstance(icon, dict):
        iid = check_item_stack(icon, ctx)
        return iid
    err("%s: icon должен быть compound или строкой, получено %r"
        % (ctx, type(icon).__name__))
    return None


def check_image(img, ctx, ids):
    """Картинка главы. Проверяет типы полей, строку-иконку, click_action и
    зависимость (картинка показывается только после завершения квеста)."""
    if not isinstance(img, dict):
        err("%s: image должен быть compound" % ctx)
        return None
    for k, v in img.items():
        if k == "id":
            continue
        want = IMAGE_FIELDS.get(k)
        if want is None:
            warn("%s: неизвестное поле картинки %r — мод его проигнорирует"
                 % (ctx, k))
            continue
        if want in ("double", "int") and num_kind(v) != want:
            err("%s: поле %s должно быть %s, получено %r (%s)"
                % (ctx, k, want, v, num_kind(v)))
        elif want == "bool" and not (isinstance(v, bool)
                                     or (num_kind(v) == "byte"
                                         and str(v) in ("0b", "1b"))):
            err("%s: поле %s должно быть bool (0b/1b), получено %r" % (ctx, k, v))
        elif want == "str" and not isinstance(v, str):
            err("%s: поле %s должно быть строкой, получено %r" % (ctx, k, v))
        elif want == "compound":
            check_icon_field(v, ctx + "." + k)
    im = img.get("image")
    if not isinstance(im, str) or not im:
        err("%s: image.image должен быть непустой строкой-иконкой" % ctx)
    elif im.endswith((".png", ".jpg")):
        if not KUBEJS_TEX_RE.match(im):
            warn("%s: image=%r — путь не похож на ресурс пака" % (ctx, im))
        elif im.split(":", 1)[0] == "kubejs":
            # картинка обязана лежать в ресурсах пака, иначе в книге будет
            # «missing texture»; рисуется всё через scripts/gen_textures.py
            ns, path = im.split(":", 1)
            fp = os.path.join(KUBEJS, "assets", ns, path)
            if not os.path.isfile(fp):
                err("%s: текстура %s не найдена (%s). Перегенерируйте: "
                    "python scripts/gen_textures.py" % (ctx, im, fp))
            else:
                yield_items_tex.append(im)
    elif not (im.startswith(ICON_KINDS) or "#" in im or " + " in im):
        warn("%s: image=%r — нестандартный формат иконки" % (ctx, im))
    ca = img.get("click_action")
    if isinstance(ca, str) and ca:
        if ca.split(":", 1)[0] not in IMAGE_CLICK_ACTIONS:
            err("%s: click_action=%r — тип не из %s"
                % (ctx, ca, ", ".join(sorted(IMAGE_CLICK_ACTIONS))))
    for a in ("text_h_align", "text_v_align"):
        if img.get(a) not in (None, *IMAGE_TEXT_ALIGN):
            err("%s: %s=%r не из %s" % (ctx, a, img[a],
                                        ", ".join(sorted(IMAGE_TEXT_ALIGN))))
    if img.get("text_on_image") in (True, "1b") and img.get("id") is None:
        warn("%s: text_on_image без id — заголовок из lang-таблицы не найдётся"
             % ctx)
    return img.get("dependency")


def check_quest_link(lk, ctx, ids):
    """QuestLink — иконка квеста из другой главы: linked_quest обязан быть
    code-строкой существующего квеста."""
    if not isinstance(lk, dict):
        err("%s: quest_link должен быть compound" % ctx)
        return None
    for k, v in lk.items():
        if k == "id":
            continue
        want = LINK_FIELDS.get(k)
        if want is None:
            warn("%s: неизвестное поле ссылки %r — мод его проигнорирует"
                 % (ctx, k))
            continue
        if want in ("double",) and num_kind(v) != "double":
            err("%s: поле %s должно быть double, получено %r (%s)"
                % (ctx, k, v, num_kind(v)))
        elif want == "str" and not isinstance(v, str):
            err("%s: поле %s должно быть строкой, получено %r" % (ctx, k, v))
    if lk.get("shape") not in (None, *VALID_SHAPES):
        err("%s: shape=%r недопустима" % (ctx, lk.get("shape")))
    return lk.get("linked_quest")


def check_tasks_rewards(entries, allowed, required, kind, ctx, ids):
    if not isinstance(entries, list):
        err("%s: %s должен быть списком" % (ctx, kind))
        return
    for n, e in enumerate(entries, 1):
        ectx = "%s/%s[%d]" % (ctx, kind, n)
        if not isinstance(e, dict):
            err("%s: ожидался compound" % ectx)
            continue
        eid = check_id(e.get("id"), ectx)
        if eid:
            if eid in ids:
                err("%s: дублирующийся id %s (уже использован как %s в %s)"
                    % (ectx, eid, ids[eid][0], ids[eid][1]))
            ids[eid] = (kind[:-1], ectx)   # "tasks"->"task", "rewards"->"reward"
        t = e.get("type")
        if t not in allowed:
            err("%s: неизвестный type=%r (допустимы: %s)"
                % (ectx, t, ", ".join(sorted(allowed))))
            continue
        for r in required.get(t, []):
            if r not in e:
                err("%s: type=%r требует поле %r" % (ectx, t, r))
        ft = TASK_FIELD_TYPES.get(t, {}) if kind == "tasks" else REWARD_FIELD_TYPES.get(t, {})
        for fk, fw in ft.items():
            if fk in e and num_kind(e[fk]) != fw:
                err("%s: поле %s должно быть %s, получено %r (%s)"
                    % (ectx, fk, fw, e[fk], num_kind(e[fk])))
        if t == "item":
            iid = check_item_stack(e.get("item"), ectx)
            yield_items.append(iid)
        if t == "stat":
            yield_stats.append(e.get("stat"))
        if t == "biome":
            yield_biomes.append(e.get("biome"))
        if t == "structure":
            yield_structs.append(e.get("structure"))
        if t == "advancement":
            yield_advs.append(e.get("advancement"))
        if t == "observation":
            ot = e.get("observation_type")
            if ot not in OBSERVE_TYPES:
                err("%s: observation_type=%r не из enum ObserveType" % (ectx, ot))
            if num_kind(e.get("observe_type")) != "int":
                err("%s: observe_type должен быть int (ordinal enum)" % ectx)
        if t == "kill":
            if not isinstance(e.get("entity"), str) or ":" not in str(e.get("entity")):
                err("%s: entity должен быть 'namespace:path'" % ectx)
            else:
                yield_ents.append(e["entity"])
            if num_kind(e.get("value")) != "long":
                err("%s: value должен быть long (например 7L), получено %r (%s)"
                    % (ectx, e.get("value"), num_kind(e.get("value"))))
        if t == "dimension":
            if not isinstance(e.get("dimension"), str):
                err("%s: dimension должен быть строкой" % ectx)
            else:
                yield_dims.append(e["dimension"])
        if t == "xp_levels" and num_kind(e.get("xp_levels")) != "int":
            err("%s: xp_levels должен быть int, получено %r (%s)"
                % (ectx, e.get("xp_levels"), num_kind(e.get("xp_levels"))))
        # NB: у XPTask поле называется value (long); поле xp (int) есть только
        # у XPReward — его проверяет REWARD_FIELD_TYPES выше.


yield_items, yield_ents, yield_dims = [], [], []
yield_items_tex = []
yield_stats, yield_biomes, yield_structs, yield_advs = [], [], [], []


def check_kubejs(items):
    custom = sorted({i for i in items if i and i.startswith("kubejs:")})
    if not custom:
        return
    registered, in_recipe = set(), set()
    start = os.path.join(KUBEJS, "startup_scripts")
    srv = os.path.join(KUBEJS, "server_scripts")
    for folder, sink in ((start, registered), (srv, in_recipe)):
        if not os.path.isdir(folder):
            continue
        for fn in sorted(os.listdir(folder)):
            if not fn.endswith(".js"):
                continue
            txt = open(os.path.join(folder, fn), encoding="utf-8").read()
            for m in re.finditer(r"event\.create\(\s*'([A-Za-z0-9_\-]+)'", txt):
                sink.add("kubejs:" + m.group(1))
            for m in re.finditer(r"'(kubejs:[A-Za-z0-9_\-]+)'", txt):
                sink.add(m.group(1))
    for iid in custom:
        if iid not in registered:
            err("квест ссылается на %s, но он НЕ зарегистрирован в kubejs/startup_scripts "
                "— задача никогда не выполнится" % iid)
        elif iid not in in_recipe:
            warn("%s зарегистрирован, но на него нет рецепта в kubejs/server_scripts "
                 "— игрок не сможет его получить" % iid)
        else:
            ok("kubejs: %s зарегистрирован и имеет рецепт" % iid)


def load_registry():
    """Реестр лежит в репозитории (scripts/quests/mc_registry_1.21.1.json),
    собран из клиентского jar 1.21.1 — CI работает без интернета."""
    if not os.path.isfile(REGISTRY_PATH):
        warn("нет %s — проверка minecraft:* пропущена" % REGISTRY_PATH)
        return None
    try:
        return json.load(open(REGISTRY_PATH, encoding="utf-8"))
    except Exception as e:                                      # noqa: BLE001
        warn("реестр не читается (%s)" % e)
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quests-dir", default=QUESTS)
    ap.add_argument("--registry", action="store_true", default=True,
                    help="сверить minecraft:* с реестром 1.21.1 из репозитория "
                         "(включено по умолчанию)")
    ap.add_argument("--no-registry", dest="registry", action="store_false",
                    help="отключить сверку с реестром")
    args = ap.parse_args()

    qd = args.quests_dir
    if not os.path.isdir(qd):
        print("нет каталога %s — сначала запустите scripts/gen_quests.py" % qd)
        return 1

    ids = {}
    chapters = 0
    quests = 0

    # --- data.snbt ---
    dp = os.path.join(qd, "data.snbt")
    if not os.path.isfile(dp):
        err("нет data.snbt")
    else:
        d = read_snbt(dp)
        v = d.get("version")
        if num_kind(v) != "int":
            err("data.snbt: version должен быть int, получено %r (%s)" % (v, num_kind(v)))
        elif int(v) != 13:
            warn("data.snbt: version=%s, для FTB Quests 2101.1.36 ожидается 13" % v)
        else:
            ok("data.snbt: version 13")
        shape = d.get("default_quest_shape", "")
        if shape not in VALID_SHAPES:
            err("data.snbt: default_quest_shape=%r не существует среди текстур мода" % shape)

    # --- chapter_groups.snbt ---
    cg = os.path.join(qd, "chapter_groups.snbt")
    if os.path.isfile(cg):
        g = read_snbt(cg)
        if "chapter_groups" not in g:
            err("chapter_groups.snbt: нет ключа chapter_groups")
        else:
            ok("chapter_groups.snbt: групп %d" % len(g["chapter_groups"]))
    else:
        err("нет chapter_groups.snbt")

    # --- главы ---
    chdir = os.path.join(qd, "chapters")
    files = sorted(f for f in os.listdir(chdir)) if os.path.isdir(chdir) else []
    if not files:
        err("в chapters/ нет ни одного файла")
    for fn in files:
        if not fn.endswith(".snbt"):
            err("chapters/%s: расширение должно быть .snbt" % fn)
            continue
        path = os.path.join(chdir, fn)
        try:
            ch = read_snbt(path)
        except SnbtError as e:
            err("chapters/%s: SNBT не парсится: %s" % (fn, e))
            continue
        chapters += 1
        ctx = "chapters/" + fn
        cid = check_id(ch.get("id"), ctx)
        if cid:
            if cid in ids:
                err("%s: дублирующийся id главы %s" % (ctx, cid))
            ids[cid] = ("chapter", ctx)
        if ch.get("filename") != fn[:-5]:
            err("%s: filename=%r не совпадает с именем файла %r — мод берёт имя "
                "из файла, расхождение собьёт переводы"
                % (ctx, ch.get("filename"), fn[:-5]))
        if num_kind(ch.get("order_index")) != "int":
            err("%s: order_index должен быть int" % ctx)
        if ch.get("default_quest_shape", "") not in VALID_SHAPES:
            err("%s: default_quest_shape=%r недопустима" % (ctx, ch.get("default_quest_shape")))
        if "group" not in ch:
            err("%s: нет group (для группы по умолчанию должна быть пустая строка)" % ctx)
        for extra in ("quests", "quest_links", "images"):
            if not isinstance(ch.get(extra, []), list):
                err("%s: %s должен быть списком" % (ctx, extra))
        # картинки главы: у каждой должен быть свой id (иначе мод выдаст
        # случайный, и заголовок из lang-таблицы перестанет находиться)
        for ii, img in enumerate(ch.get("images", []), 1):
            ictx = "%s/images[%d]" % (ctx, ii)
            if isinstance(img, dict):
                if "id" in img:
                    iid = check_id(img["id"], ictx)
                    if iid:
                        if iid in ids:
                            err("%s: дублирующийся id картинки %s (уже %s в %s)"
                                % (ictx, iid, ids[iid][0], ids[iid][1]))
                        ids[iid] = ("image", ictx)
                else:
                    warn("%s: нет id — мод сгенерирует случайный, заголовок "
                         "и зависимость из lang-таблицы потеряются" % ictx)
                dep = check_image(img, ictx, ids)
                if dep:
                    alldeps.append((dep, ictx))
            else:
                err("%s: image должен быть compound" % ictx)

        # ссылки на квесты других глав
        for li, lk in enumerate(ch.get("quest_links", []), 1):
            lctx = "%s/quest_links[%d]" % (ctx, li)
            if not isinstance(lk, dict):
                err("%s: quest_link должен быть compound" % lctx)
                continue
            lid = check_id(lk.get("id"), lctx)
            if lid:
                if lid in ids:
                    err("%s: дублирующийся id ссылки %s (уже %s в %s)"
                        % (lctx, lid, ids[lid][0], ids[lid][1]))
                ids[lid] = ("quest_link", lctx)
            tgt = check_quest_link(lk, lctx, ids)
            if tgt:
                alldeps.append((tgt, lctx))
            else:
                err("%s: нет linked_quest — ссылка никуда не ведёт" % lctx)

        # иконка главы — тоже ItemStack, её предмет надо сверить с реестром
        if "icon" in ch:
            iid = check_icon_field(ch["icon"], ctx + ".icon")
            if iid:
                yield_items.append(iid)

        quest_ids_here = []
        for qi, q in enumerate(ch.get("quests", []), 1):
            qctx = "%s/quests[%d]" % (ctx, qi)
            if not isinstance(q, dict):
                err("%s: ожидался compound" % qctx)
                continue
            quests += 1
            qid = check_id(q.get("id"), qctx)
            if qid:
                if qid in ids:
                    err("%s: дублирующийся id квеста %s (уже используется как %s в %s)"
                        % (qctx, qid, ids[qid][0], ids[qid][1]))
                ids[qid] = ("quest", qctx)
                quest_ids_here.append(qid)
            for axis in ("x", "y"):
                if num_kind(q.get(axis)) != "double":
                    err("%s: %s должен быть double (например 1.5d), получено %r (%s)"
                        % (qctx, axis, q.get(axis), num_kind(q.get(axis))))
            check_tasks_rewards(q.get("tasks", []), TASK_TYPES, TASK_REQUIRED,
                                "tasks", qctx, ids)
            check_tasks_rewards(q.get("rewards", []), REWARD_TYPES, REWARD_REQUIRED,
                                "rewards", qctx, ids)
            if not q.get("tasks"):
                warn("%s: у квеста нет ни одной задачи — его невозможно завершить" % qctx)
            if "icon" in q:
                iid = check_icon_field(q["icon"], qctx + ".icon")
                if iid:
                    yield_items.append(iid)
            for k, v in q.items():
                if k not in ("id", "x", "y", "shape", "size", "icon_scale", "dependencies",
                             "icon", "tags",
                             "tasks", "rewards", "optional", "invisible", "min_width",
                             "guide_page", "progression_mode", "preset", "can_repeat",
                             "repeat_cooldown", "min_required_dependencies",
                             "max_completable_dependents", "dependency_requirement",
                             "hide_dependency_lines", "hide_dependent_lines",
                             "hide_lock_icon", "ignore_reward_blocking",
                             "invisible_until_tasks", "disable_recipe_mod",
                             "hide_until_deps_visible", "hide_until_deps_complete",
                             "hide_text_until_complete", "hide_details_until_startable",
                             "require_sequential_tasks", "dep_control_pts"):
                    warn("%s: неизвестное поле %r — мод его проигнорирует" % (qctx, k))

        # зависимости проверяем после чтения всех глав
        for qi, q in enumerate(ch.get("quests", []), 1):
            deps = q.get("dependencies")
            if deps is None:
                continue
            if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
                err("%s/quests[%d]: dependencies должен быть списком строк" % (ctx, qi))
                continue
            for d in deps:
                alldeps.append((d, "%s/quests[%d]" % (ctx, qi)))

    # --- lang ---
    langdir = os.path.join(qd, "lang")
    lang_tables = {}
    if not os.path.isdir(langdir):
        err("нет каталога lang/ — заголовки квестов будут пустыми")
    else:
        for fn in sorted(os.listdir(langdir)):
            if not fn.endswith(".snbt"):
                continue
            loc = fn[:-5]
            try:
                lang_tables[loc] = read_snbt(os.path.join(langdir, fn))
            except SnbtError as e:
                err("lang/%s: SNBT не парсится: %s" % (fn, e))
        if "en_us" not in lang_tables:
            err("нет lang/en_us.snbt — это fallback-локаль FTB Quests, без неё "
                "заголовки не появятся ни у кого")
        else:
            ok("lang: локалей %d (%s)" % (len(lang_tables), ", ".join(sorted(lang_tables))))

    for loc, table in lang_tables.items():
        for key, val in table.items():
            parts = key.split(".")
            if len(parts) != 3:
                err("lang/%s: ключ %r должен быть вида <тип>.<ID>.<поле>" % (loc, key))
                continue
            otype, oid, field = parts
            if otype not in ("chapter", "quest", "task", "reward", "image",
                             "quest_link", "chapter_group", "reward_table"):
                err("lang/%s: ключ %s — неизвестный тип объекта %r"
                    % (loc, key, otype))
            if oid not in ids:
                err("lang/%s: ключ %s ссылается на несуществующий ID" % (loc, key))
            elif ids[oid][0] != otype:
                err("lang/%s: ключ %s — объект %s, а в ключе заявлен %r"
                    % (loc, key, ids[oid][0], otype))
            if field in LIST_KEYS:
                if not isinstance(val, list) or any(not isinstance(x, str) for x in val):
                    err("lang/%s: %s должен быть списком строк" % (loc, key))
            else:
                if not isinstance(val, str):
                    err("lang/%s: %s должен быть строкой" % (loc, key))

    # у каждой главы и квеста должен быть title хотя бы в en_us
    if "en_us" in lang_tables:
        t = lang_tables["en_us"]
        named = 0
        for oid, (kind, ctx) in ids.items():
            # заголовок нужен только главам и квестам; у задач и наград его нет
            # (у toast-награды title опционален)
            if kind not in ("chapter", "quest"):
                continue
            key = "%s.%s.title" % (kind, oid)
            if key not in t:
                err("нет заголовка %s (%s) — объект отобразится пустым" % (key, ctx))
            else:
                named += 1
        ok("заголовков в en_us: %d (главы + квесты)" % named)

    # --- зависимости ---
    for d, ctx in alldeps:
        if d not in ids:
            err("%s: зависимость %s не существует" % (ctx, d))
        else:
            kind, dctx = ids[d]
            if kind != "quest":
                err("%s: зависимость %s указывает на %s, а должна на квест"
                    % (ctx, d, kind))
            elif dctx == ctx:
                err("%s: квест зависит сам от себя" % ctx)
    ok("зависимостей проверено: %d" % len(alldeps))

    # --- KubeJS ---
    check_kubejs(yield_items)

    # --- реестр Minecraft и модов ---
    # Ванильные ID сверяются с основным реестром; ID модов — с секцией
    # reg["mods"]["<namespace>"] (собирается из jar мода, см. README в
    # scripts/quests). kubejs:* проверяет check_kubejs() выше.
    if args.registry:
        reg = load_registry()
        if reg:
            mods_reg = reg.get("mods") or {}
            checks = [("предмет/блок", yield_items, set(reg["items"]), "items"),
                      ("моб", yield_ents, set(reg["entities"]), "entities"),
                      ("биом", yield_biomes, set(reg["biomes"]), "biomes"),
                      ("структура", yield_structs, set(reg["structures"]), "structures"),
                      ("достижение", yield_advs, set(reg["advancements"]), "advancements"),
                      ("custom-стат", [x and x.split(":")[-1] for x in yield_stats],
                       set(reg["custom_stats"]), "custom_stats"),
                      ("измерение", yield_dims, set(reg["dimensions"]), "dimensions")]
            total_bad = 0
            for label, vals, pool, kind in checks:
                # пулы собраны разнородно: lang даёт имена без неймспейса,
                # а worldgen/advancement — с ним. Приводим всё к bare-виду.
                bare = {(q.split(":", 1)[1] if ":" in q else q) for q in pool}
                mbare = {ns: {(q.split(":", 1)[1] if ":" in q else q)
                              for q in mreg.get(kind, [])}
                         for ns, mreg in mods_reg.items()}
                bad = []
                for v in sorted({x for x in vals if x}):
                    if v.startswith("kubejs:"):
                        continue
                    ns, sep, path = v.partition(":")
                    if not sep:                 # без неймспейса — считаем minecraft
                        ns, path = "minecraft", v
                    if ns == "minecraft":
                        if path not in bare:
                            bad.append(v)
                    elif ns not in mbare:
                        bad.append("%s (в реестре нет мода %r)" % (v, ns))
                    elif path not in mbare[ns]:
                        bad.append(v)
                if bad:
                    total_bad += len(bad)
                    for b in bad:
                        err("%s %s отсутствует в реестре %s"
                            % (label, b, reg.get("minecraft", "1.21.1")))
                elif vals:
                    ok("%s-ов проверено: %d — все есть в реестре %s"
                       % (label, len({x for x in vals if x}), reg.get("minecraft", "")))
            if total_bad == 0:
                extra = ("+ моды: " + ", ".join(sorted(mods_reg))) if mods_reg else ""
                ok("все ID сверены с реестром Minecraft %s %s"
                   % (reg.get("minecraft"), extra))

    # --- итог ---
    print()
    print("глав: %d   квестов: %d   уникальных ID: %d" % (chapters, quests, len(ids)))
    print("предметов в задачах/наградах: %d   мобов: %d   измерений: %d"
          % (len(set(yield_items)), len(set(yield_ents)), len(set(yield_dims))))
    print("текстур пака в картинках глав: %d — все файлы найдены"
          % len(set(yield_items_tex)))
    print()
    for m in oks:
        print("  \033[32mOK\033[0m  " + m)
    for m in warns:
        print("  \033[33m!!\033[0m  " + m)
    for m in errs:
        print("  \033[31mXX\033[0m  " + m)
    print()
    if errs:
        print("\033[31mПРОВАЛЕНО: %d ошибок, %d предупреждений\033[0m" % (len(errs), len(warns)))
        return 1
    print("\033[32mКВЕСТЫ ВАЛИДНЫ\033[0m (%d предупреждений)" % len(warns))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SnbtError as e:
        print("\033[31mОШИБКА SNBT:\033[0m %s" % e, file=sys.stderr)
        sys.exit(1)
