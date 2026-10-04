# -*- coding: utf-8 -*-
"""
Глава 3 — «Грань Пустоты» (Край).

Вход — через крепость из главы «Багровое Пекло».
Четыре секции: приземление и дракон, внешние острова, город Края и финал пака.
"""

from qdsl import (CUSTOM, Q, SEC, adv, biome, check, dim, give, halo, item,
                  kill, lvl, say, stat, struct, toast, xpr)

VOID    = 0x4B3A7A
ISLES   = 0x2F5F7A
CITY    = 0x8A6BBE
MASTER  = 0xC9A227
SHINE   = 0xB9A6FF

SECTIONS = [
    SEC("landing",  ("The Fall",        "Падение в Край"),  VOID),
    SEC("islands",  ("Outer Islands",   "Внешние острова"), ISLES),
    SEC("city",     ("City of the End", "Город Края"),      CITY),
    SEC("mastery",  ("Pack Master",     "Мастер пака"),     MASTER),
]

QUESTS = [
# --------------------------------------------------------------------------- #
#  1. ПАДЕНИЕ В КРАЙ
# --------------------------------------------------------------------------- #
Q("enter", ("The End", "Край"), section="landing", deps=["nether:stronghold"],
  icon="minecraft:end_stone", shape="hexagon", size=1.7,
  desc=[("Jump into the starry portal. You appear on an obsidian platform; "
         "if it is broken, bring blocks.",
         "Прыгай в звёздный портал. Появишься на обсидиановой платформе; "
         "если она разрушена, возьми с собой блоки."),
        ("The dragon heals from the crystals on the pillars. Break them first.",
         "Дракон лечится от кристаллов на колоннах. Сначала разбей их.")],
  tasks=[dim("minecraft:the_end"), adv("minecraft:end/root")],
  rewards=[lvl(8), give("minecraft:golden_carrot", 8)]),

Q("pillars", ("Obsidian Pillars", "Обсидиановые колонны"), section="landing",
  icon="minecraft:end_crystal",
  desc=[("Some crystals sit behind iron bars: dig up, or shoot through the "
         "gap. An exploded crystal hurts badly — keep distance.",
         "Часть кристаллов за железными прутьями: подкопайся или стреляй "
         "в щель. Взрыв кристалла очень больно бьёт — держи дистанцию.")],
  tasks=[kill("minecraft:end_crystal", 6), item("minecraft:obsidian", 12),
         item("minecraft:end_stone", 32)],
  rewards=[lvl(6), give("minecraft:arrow", 64)]),

Q("dragon", ("The Ender Dragon", "Дракон Края"), section="landing",
  deps=["pillars"], icon="minecraft:dragon_head", shape="gear", size=2.2,
  desc=[("Shoot it in the wings when it circles, hit it with a sword when it "
         "sits on the fountain. Beds and anchors explode here too — some "
         "people kill it that way.",
         "Стреляй по крыльям, когда он кружит, бей мечом, когда садится на "
         "фонтан. Кровати и якоря здесь тоже взрываются — некоторые убивают "
         "именно так.")],
  tasks=[kill("minecraft:ender_dragon", 1), adv("minecraft:end/kill_dragon")],
  rewards=[lvl(25), give("minecraft:enchanted_golden_apple", 2),
           toast("Край твой.")]),

Q("egg", ("Dragon Egg", "Яйцо дракона"), section="landing", deps=["dragon"],
  icon="minecraft:dragon_egg", shape="diamond", size=1.4,
  desc=[("It teleports when hit. Put a piston next to it and power the piston, "
         "or place a torch two blocks below and break the block above.",
         "Оно телепортируется от удара. Поставь рядом поршень и подай сигнал, "
         "либо поставь факел на два блока ниже и сломай блок сверху.")],
  tasks=[item("minecraft:dragon_egg"), adv("minecraft:end/dragon_egg")],
  rewards=[lvl(10), give("minecraft:glass", 16)]),

Q("breath", ("Dragon Breath", "Дыхание дракона"), section="landing",
  deps=["dragon"], icon="minecraft:dragon_breath",
  desc=[("Use a glass bottle on the purple cloud the dragon leaves on the "
         "fountain, or on its fireball.",
         "Набери стеклянной бутылочкой фиолетовое облако, которое дракон "
         "оставляет на фонтане, или его огненный шар.")],
  tasks=[item("minecraft:dragon_breath"), adv("minecraft:end/dragon_breath")],
  rewards=[lvl(8), give("minecraft:glass_bottle", 8)]),

Q("respawn", ("Dragon Again", "Дракон снова"), section="landing", deps=["egg"],
  icon="minecraft:end_crystal",
  desc=[("Four end crystals on the exit portal bring the dragon back. It drops "
         "experience again and opens another gateway.",
         "Четыре кристалла Края на выходном портале возвращают дракона. "
         "Он снова даст опыт и откроет ещё одни врата.")],
  tasks=[adv("minecraft:end/respawn_dragon"), item("minecraft:end_crystal", 4)],
  rewards=[lvl(15)]),

# --------------------------------------------------------------------------- #
#  2. ВНЕШНИЕ ОСТРОВА
# --------------------------------------------------------------------------- #
Q("gateway", ("The Gateway", "Врата"), section="islands", deps=["dragon"],
  icon="minecraft:ender_pearl", shape="hexagon", size=1.4,
  desc=[("A small bedrock portal appears after the kill. Throw an ender pearl "
         "into it, or drink to fit through.",
         "После убийства появляется маленький портал из коренной породы. "
         "Брось в него жемчуг Края или уменьшись, чтобы пройти.")],
  tasks=[adv("minecraft:end/enter_end_gateway"), item("minecraft:ender_pearl", 8)],
  rewards=[give("minecraft:ender_pearl", 4), lvl(5)]),

Q("outer", ("Outer Islands", "Внешние острова"), section="islands",
  deps=["gateway"], icon="minecraft:chorus_flower", shape="octagon", size=1.5,
  desc=[("Thousands of islands with chorus trees, end cities and ships. "
         "Bring blocks to bridge the gaps.",
         "Тысячи островов с хорусовыми деревьями, городами Края и кораблями. "
         "Возьми блоки, чтобы перебрасывать мосты.")],
  tasks=[biome("minecraft:end_highlands"), biome("minecraft:end_midlands"),
         biome("minecraft:small_end_islands"), biome("minecraft:end_barrens")],
  rewards=[lvl(12), give("minecraft:end_stone_bricks", 32)]),

Q("chorus", ("Chorus", "Хорус"), section="islands", deps=["outer"],
  icon="minecraft:chorus_fruit",
  desc=[("The fruit teleports you at random, the popped one is used for end "
         "rods and purpur. Bake it in a furnace.",
         "Плод случайно телепортирует, лопнувший нужен для стержней Края "
         "и пурпура. Запеки его в печи.")],
  tasks=[item("minecraft:chorus_fruit", 8), item("minecraft:popped_chorus_fruit", 4),
         item("minecraft:chorus_flower", 2)],
  rewards=[give("minecraft:chorus_flower", 4)]),

Q("endermen", ("Endermen of the End", "Эндермены Края"), section="islands",
  deps=["outer"], icon="minecraft:ender_pearl",
  desc=[("Here they are everywhere. A pumpkin on the head prevents eye "
         "contact; a two-block roof lets you fight safely.",
         "Здесь они повсюду. Тыква на голове спасает от зрительного контакта, "
         "а навес в два блока позволяет драться безопасно.")],
  tasks=[kill("minecraft:enderman", 20), item("minecraft:ender_pearl", 32)],
  rewards=[give("minecraft:ender_eye", 4), lvl(6)]),

Q("levitate", ("Levitation", "Левитация"), section="islands", deps=["outer"],
  icon="minecraft:shulker_shell", optional=True,
  desc=[("Get hit by a shulker bullet and float up 50 blocks without falling.",
         "Получи снарядом шалкера и пролететь вверх 50 блоков, не упав.")],
  tasks=[adv("minecraft:end/levitate")],
  rewards=[lvl(10), give("minecraft:feather", 16)]),

Q("spyglass", ("Look Up", "Взгляд вверх"), section="islands", deps=["dragon"],
  icon="minecraft:spyglass",
  desc=[("A copper spyglass and an amethyst shard. Look at the dragon through "
         "it during the fight.",
         "Медная подзорная труба и осколок аметиста. Посмотри на дракона "
         "через неё прямо во время боя.")],
  tasks=[adv("minecraft:adventure/spyglass_at_dragon"), item("minecraft:spyglass")],
  rewards=[give("minecraft:amethyst_shard", 8)]),

# --------------------------------------------------------------------------- #
#  3. ГОРОД КРАЯ
# --------------------------------------------------------------------------- #
Q("endcity", ("End City", "Город Края"), section="city", deps=["outer"],
  icon="minecraft:purpur_block", shape="hexagon", size=1.6,
  desc=[("Tall purple towers on the outer islands. The ship next to some of "
         "them carries exactly one thing you came for.",
         "Высокие фиолетовые башни на внешних островах. На корабле рядом "
         "с некоторыми из них лежит ровно одна нужная тебе вещь.")],
  tasks=[struct("minecraft:end_city"), adv("minecraft:end/find_end_city")],
  rewards=[lvl(12), give("minecraft:purpur_block", 32)]),

Q("shulker", ("Shulkers", "Шалкеры"), section="city", deps=["endcity"],
  icon="minecraft:shulker_shell",
  desc=[("Their bullets levitate you. A shield blocks the bullet, and two "
         "shells make a shulker box.",
         "Их снаряды заставляют левитировать. Щит блокирует снаряд, а две "
         "раковины дают шалкеровый ящик.")],
  tasks=[kill("minecraft:shulker", 6), item("minecraft:shulker_shell", 2)],
  rewards=[give("minecraft:shulker_shell", 2), lvl(6)]),

Q("elytra", ("Wings", "Крылья"), section="city", deps=["endcity"],
  icon="minecraft:elytra", shape="gear", size=2.0,
  desc=[("On the bow of the end ship, in an item frame. One pair per ship — "
         "and ships are far apart.",
         "На носу корабля Края, в рамке. Одна пара на корабль, а корабли "
         "далеко друг от друга.")],
  tasks=[item("minecraft:elytra"), adv("minecraft:end/elytra")],
  rewards=[lvl(20), give("minecraft:firework_rocket", 32),
           toast("Небо больше не предел.")]),

Q("flight", ("Flight", "Полёт"), section="city", deps=["elytra"],
  icon="minecraft:firework_rocket",
  desc=[("Jump, open the wings with the jump button, and boost with rockets "
         "made of paper and gunpowder.",
         "Прыгни, раскрой крылья кнопкой прыжка и разгоняйся ракетами из "
         "бумаги и пороха.")],
  tasks=[stat("minecraft:aviate_one_cm", 100000),
         stat("minecraft:fly_one_cm", 200000),
         item("minecraft:firework_rocket", 64)],
  rewards=[give("minecraft:firework_rocket", 64), lvl(8)]),

Q("box", ("Portable Chest", "Переносной сундук"), section="city",
  deps=["shulker"], icon="minecraft:shulker_box",
  desc=[("Two shells around a chest. It keeps its contents when broken — "
         "the best inventory in the game.",
         "Две раковины вокруг сундука. Он сохраняет содержимое при поломке — "
         "лучший инвентарь в игре.")],
  tasks=[item("minecraft:shulker_box"), stat("minecraft:open_shulker_box", 1),
         item("minecraft:chest", 8)],
  rewards=[give("minecraft:diamond", 6)]),

Q("purpur", ("Purple Stone", "Фиолетовый камень"), section="city",
  deps=["endcity"], icon="minecraft:dragon_head",
  desc=[("Purpur blocks and end rods are the building material of the cities. "
         "The dragon head sits on the bow of the ship, next to the elytra.",
         "Пурпур и стержни Края — строительный материал городов. Голова "
         "дракона стоит на носу корабля, рядом с элитрами.")],
  tasks=[item("minecraft:purpur_block", 32), item("minecraft:end_rod", 8),
         item("minecraft:dragon_head")],
  rewards=[lvl(10), give("minecraft:end_rod", 8)]),

# --------------------------------------------------------------------------- #
#  4. МАСТЕР ПАКА
# --------------------------------------------------------------------------- #
Q("trophy", ("Trophies", "Трофеи"), section="mastery", deps=["egg", "elytra"],
  icon="minecraft:dragon_egg", shape="diamond", size=1.5,
  desc=[("Everything that cannot be bought: the egg, the wings, the box and "
         "the star.",
         "Всё, что нельзя купить: яйцо, крылья, ящик и звезда.")],
  tasks=[item("minecraft:dragon_egg"), item("minecraft:elytra"),
         item("minecraft:shulker_box"), item("minecraft:nether_star")],
  rewards=[lvl(15), give("minecraft:netherite_block", 2)]),

Q("medal", ("Medal of the Master", "Медаль мастера"), section="mastery",
  deps=["trophy"], icon=CUSTOM["medal"], shape="gear", size=1.8,
  desc=[("A custom item of this pack: two diamond blocks, two emerald blocks, "
         "two premium tokens and a nether star.",
         "Свой предмет пака: два алмазных блока, два изумрудных блока, две "
         "улучшенные медали и звезда Незера."),
        ("Recipe is in JEI. Premium tokens are made in the Crimson Furnace "
         "chapter.",
         "Рецепт есть в JEI. Улучшенные медали делаются в главе «Багровое "
         "Пекло».")],
  tasks=[item(CUSTOM["medal"])],
  rewards=[lvl(25), give("minecraft:netherite_ingot", 4)]),

Q("veteran", ("Veteran", "Ветеран"), section="mastery", deps=["medal"],
  icon="minecraft:clock",
  desc=[("Five hours of play and five hundred kills. The statistics are "
         "counted for the whole world, not for this chapter.",
         "Пять часов игры и пятьсот убийств. Статистика считается по всему "
         "миру, а не по этой главе.")],
  tasks=[stat("minecraft:play_time", 360000), stat("minecraft:mob_kills", 500)],
  rewards=[give("minecraft:enchanted_golden_apple", 2), lvl(10)]),

Q("final", ("End of the Story", "Конец истории"), section="mastery",
  deps=["overworld:portalow", "nether:stronghold", "veteran"],
  icon=CUSTOM["medal"], shape="heart", size=2.0,
  desc=[("Three worlds, one book, every chapter closed. There is nothing left "
         "to tick — so tick this.",
         "Три мира, одна книга, все главы закрыты. Отмечать больше нечего — "
         "так что отметь это."),
        ("Thanks for playing this pack.", "Спасибо, что играешь в этот пак.")],
  tasks=[check()],
  rewards=[lvl(30), xpr(500),
           say('tellraw @s {"text":"Ты прошёл весь пак. Спасибо за игру!","color":"gold"}'),
           toast("Пак пройден полностью.")]),
]


def build_images():
    return [
        halo("dragon", SHINE, 5.2, 220),
        halo("elytra", 0xFFE9A8, 4.4, 200),
        halo("medal", MASTER, 4.2, 210),
        halo("final", 0xFFFFFF, 5.0, 180),
        {
            "at": "egg", "dx": 0.0, "dy": 1.45, "w": 5.0, "h": 0.8,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x1A1430, "alpha": 240, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Piston, not a pickaxe", "Поршень, а не кирка"),
        },
        {
            "at": "gateway", "dx": 0.0, "dy": -1.4, "w": 5.0, "h": 0.8,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x0F2438, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Throw a pearl in", "Брось внутрь жемчуг"),
        },
        {
            "at": "final", "dx": 0.0, "dy": 1.7, "w": 6.2, "h": 0.9,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x2A2410, "alpha": 240, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Thank you for playing", "Спасибо за игру"),
        },
    ]


CHAPTER = {
    "id": 0xC003, "filename": "end",
    "layout": "blocks", "cols": 2, "dx": 2.1, "dy": 1.45,
    "pad_x": 4.5, "pad_y": 6.5,
    "shape": "hexagon", "icon": "minecraft:end_crystal",
    "banner": "banner_end", "banner_w": 13.0, "banner_h": 3.25,
    "banner_gap": 2.9,
    "title": ("Edge of the Void", "Грань Пустоты"),
    "subtitle": [
        ("Nothing grows here and nothing forgives a mistake. Only islands, "
         "dragons and loot.",
         "Здесь ничего не растёт и ничего не прощает ошибок. Только острова, "
         "драконы и добыча."),
        ("The last chapter: the dragon, the wings and the medal of the pack.",
         "Последняя глава: дракон, крылья и медаль пака."),
    ],
    "sections": SECTIONS,
    "quests": QUESTS,
    "images": build_images(),
    "links": [
        {"quest": "nether:stronghold"},
    ],
}
