# -*- coding: utf-8 -*-
"""
Пролог — «Погасшая звезда».

Сюжетная рамка пака: над миром уже третьи сутки не восходит солнце,
а на горизонте горит звезда, которой там быть не должно. Игрок —
последний звездочёт обсерватории — находит её осколок и отправляется
по следу света: Земли Рассвета -> Багровое Пекло -> Грань Пустоты ->
Вечное Звездосветье.

Глава чисто сюжетная: задачи-галочки и простые предметы, чтобы игрок
прочитал историю и понял, куда идти. Портал-картинки ведут в первую
главу каждой части. Дальше сюжет продолжается главами контентных модов.
"""

from qdsl import (Q, SEC, check, give, halo, item, lvl, portal, toast, xpr)

NIGHT = 0x2B3A67
SHARD = 0x6A4C93
ROAD  = 0x1F7A70

SECTIONS = [
    SEC("wake", ("The Last Night", "Последняя ночь"), NIGHT),
    SEC("call", ("The Call", "Зов"), SHARD),
    SEC("road", ("The Road", "Дорога"), ROAD),
]

QUESTS = [
# --------------------------------------------------------------------------- #
#  1. ПОСЛЕДНЯЯ НОЧЬ
# --------------------------------------------------------------------------- #
Q("wake", ("The Last Night", "Последняя ночь"), section="wake",
  icon="minecraft:amethyst_shard", shape="hexagon", size=1.6,
  desc=[("You wake on the cold stone of the observatory. The night has lasted "
         "three days. The sun is gone, and in its place a star burns low over "
         "the horizon — a star that was never in any of your charts.",
         "Ты просыпаешься на холодном камне обсерватории. Ночь длится третьи "
         "сутки. Солнце не взошло, а на горизонте низко горит звезда — та, "
         "которой не было ни на одной твоей карте."),
        ("The book on the lectern is open. Its first page is blank except for "
         "one line in your own hand: «When the star goes out, follow its light».",
         "Книга на пюпитре открыта. На первой странице пусто, если не считать "
         "строки, написанной твоим почерком: «Когда звезда погаснет, иди за её "
         "светом».")],
  tasks=[check()],
  rewards=[give("kubejs:quest_token"), lvl(1), toast("Небо ждёт.")]),

Q("shard", ("The Shard", "Осколок"), section="wake", deps=["wake"],
  icon="minecraft:amethyst_shard",
  desc=[("Something fell into the courtyard last night. The shard is still "
         "warm, and the light inside it does not go out when you cover it with "
         "your hand.",
         "Прошлой ночью что-то упало во двор. Осколок ещё тёплый, и свет "
         "внутри не гаснет, даже когда накрываешь его ладонью."),
        ("It is not amethyst. Amethyst does not whisper.",
         "Это не аметист. Аметист не шепчет.")],
  tasks=[item("minecraft:amethyst_shard")],
  rewards=[xpr(50), give("kubejs:quest_token")]),

Q("observatory", ("The Observatory", "Обсерватория"), section="wake",
  deps=["shard"], icon="minecraft:spyglass",
  desc=[("The observatory remembers you. The telescope is intact, the charts "
         "are scattered across the floor, and the brass rings still turn.",
         "Обсерватория помнит тебя. Телескоп цел, карты разбросаны по полу, "
         "а латунные кольца всё ещё вращаются."),
        ("Through the lens the dying star has a shape: a gate, not a sun.",
         "В объективе у погасшей звезды есть форма: это не солнце, а врата.")],
  tasks=[item("minecraft:spyglass"), check()],
  rewards=[lvl(2), give("kubejs:quest_token")]),

# --------------------------------------------------------------------------- #
#  2. ЗОВ
# --------------------------------------------------------------------------- #
Q("chart", ("The Star Chart", "Звёздная карта"), section="call",
  deps=["observatory"], icon="minecraft:map", shape="diamond", size=1.4,
  desc=[("The chart points to the Dawnlands: the first hills, the first trees, "
         "the old road under them. That is where the light fell first.",
         "Карта указывает на Земли Рассвета: первые холмы, первые деревья и "
         "старую дорогу под ними. Именно туда свет упал в первый раз."),
        ("Draw a fresh map and take paper with you. The road will not stay "
         "still.",
         "Начерти новую карту и возьми с собой бумагу. Дорога не будет стоять "
         "на месте.")],
  tasks=[item("minecraft:map"), item("minecraft:paper", 8)],
  rewards=[xpr(80), give("minecraft:compass")]),

Q("lantern", ("The Stargazer's Lantern", "Фонарь звездочёта"), section="call",
  deps=["chart"], icon="minecraft:lantern",
  desc=[("An ordinary lantern will do for the dark. But keep the shard close: "
         "it shows the traces of starlight that no eye can see.",
         "Для темноты хватит и обычного фонаря. Но осколок держи рядом: он "
         "показывает следы звёздного света, которых не видит глаз."),
        ("Later, when you find starfire and a starlit diamond, you will build a "
         "proper Stargazer's Lantern.",
         "Позже, когда найдёшь звездопал и звёздный алмаз, соберёшь настоящий "
         "Фонарь звездочёта.")],
  tasks=[item("minecraft:lantern"), check()],
  rewards=[give("minecraft:torch", 16), lvl(2)]),

Q("road", ("The Road Begins", "Дорога начинается"), section="call",
  deps=["lantern"], icon="minecraft:oak_sapling", shape="hexagon", size=1.5,
  desc=[("The first tree is the beginning of everything. Wood, a bench, a "
         "pickaxe — the old road is buried under ordinary survival.",
         "Первое дерево — начало всего. Дерево, верстак, кирка: старая дорога "
         "погребена под обычным выживанием."),
        ("Open the Dawnlands chapter and start with the first log. The book will "
         "guide you further.",
         "Открой главу «Земли Рассвета» и начни с первого бревна. Книга "
         "проведёт дальше.")],
  tasks=[check()],
  rewards=[give("kubejs:quest_token"), lvl(3),
           toast("Земли Рассвета ждут.")]),

# --------------------------------------------------------------------------- #
#  3. ДОРОГА
# --------------------------------------------------------------------------- #
Q("nether", ("The Call of Fire", "Зов огня"), section="road",
  deps=["road"], icon="minecraft:netherrack", shape="gear", size=1.8,
  desc=[("The second shard fell into the Nether. The light there does not warm "
         "— it tests. Build the obsidian gate and step through.",
         "Второй осколок упал в Незер. Тамошний свет не греет — он испытывает. "
         "Собери обсидиановые врата и войди."),
        ("The Crimson Hells chapter will take you from the first netherrack to "
         "the fortress and the End portal.",
         "Глава «Багровое Пекло» проведёт от первого незерака до крепости и "
         "портала в Край.")],
  tasks=[check()],
  rewards=[lvl(5), give("minecraft:golden_carrot", 8)]),

Q("void", ("The Call of the Void", "Зов пустоты"), section="road",
  deps=["nether"], icon="minecraft:end_crystal", shape="gear", size=1.8,
  desc=[("The End is not the end. It is a seal. The dragon guards the first "
         "door, and beyond it the void remembers the star's true name.",
         "Край — не конец. Это печать. Дракон сторожит первую дверь, а за ней "
         "пустота помнит настоящее имя звезды."),
        ("Defeat the dragon, find the gateway and follow the outer islands.",
         "Победи дракона, найди врата и иди по внешним островам.")],
  tasks=[check()],
  rewards=[lvl(8), give("kubejs:quest_token_premium")]),

Q("starlight", ("The Call of Starlight", "Зов Звездосветья"), section="road",
  deps=["void"], icon="eternal_starlight:orb_of_prophecy", shape="hexagon",
  size=2.0,
  desc=[("When the dragon falls, the sky opens. The Eternal Starlight is the "
         "star's own world: light turned into land, forests and seas, nine "
         "lights and two guardians.",
         "Когда дракон падает, небо открывается. Вечное Звездосветье — мир "
         "самой звезды: свет, ставший землёй, лесами и морями, девять огней и "
         "два стража."),
        ("Find the Orb of Prophecy. It will show you the way to the Gatekeeper "
         "and the Moon Beast — and to the heart of the dying star.",
         "Найди Орб пророчества. Он укажет путь к Привратнику и Лунному "
         "чудовищу — и к сердцу погасшей звезды.")],
  tasks=[check()],
  rewards=[lvl(12), give("kubejs:quest_token_premium"),
           toast("Звезда зовёт по имени.")]),
]

# --------------------------------------------------------------------------- #
#  Картинки главы
# --------------------------------------------------------------------------- #
def build_images():
    return [
        halo("wake", NIGHT, 3.2),
        halo("road", ROAD, 3.2),
        halo("starlight", SHARD, 3.8, 190),
        # подсказка у первой страницы
        {
            "at": "wake", "dx": 0.0, "dy": -1.45, "w": 5.4, "h": 0.75,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x1E1E28, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Three days without dawn", "Три дня без рассвета"),
        },
        # кликабельные порталы в первые главы частей
        portal("road", "overworld:wood", dx=2.5, dy=0.0, size=1.8,
               color=0x3E7A3A, title=("To the Dawnlands", "В Земли Рассвета")),
        portal("nether", "nether:enter", dx=-2.5, dy=0.0, size=1.8,
               color=0x96403C, title=("To the Nether", "В Незер")),
        portal("void", "end:enter", dx=2.5, dy=0.0, size=1.8,
               color=0x4B3A7A, title=("To the End", "В Край")),
        portal("starlight", "starlight:q001", dx=0.0, dy=-2.1, size=2.0,
               color=0x6A4C93, title=("To the Eternal Starlight",
                                       "В Вечное Звездосветье")),
    ]


CHAPTER = {
    "id": 0xC001, "filename": "prologue",
    "layout": "blocks", "cols": 2, "dx": 2.1, "dy": 1.45,
    "pad_x": 4.5, "pad_y": 6.5,
    "shape": "hexagon", "icon": "eternal_starlight:orb_of_prophecy",
    "banner": "banner_starlight", "banner_w": 13.0, "banner_h": 3.25,
    "banner_gap": 2.9,
    "title": ("The Dying Star", "Погасшая звезда"),
    "subtitle": [
        ("The sun has not risen for three days. A star burns where no star "
         "should be, and its light is calling you.",
         "Солнце не всходило три дня. Там, где звезды быть не должно, горит "
         "звезда, и её свет зовёт тебя."),
        ("A story-driven prologue: read it, take the shard and follow the road "
         "through the Dawnlands, the Crimson Hells, the Edge of the Void and "
         "into the Eternal Starlight.",
         "Сюжетный пролог: прочитай его, возьми осколок и пройди дорогу через "
         "Земли Рассвета, Багровое Пекло, Грань Пустоты и Вечное "
         "Звездосветье."),
    ],
    "sections": SECTIONS,
    "quests": QUESTS,
    "images": build_images(),
    "links": [],
}
