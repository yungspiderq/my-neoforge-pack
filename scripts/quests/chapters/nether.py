# -*- coding: utf-8 -*-
"""
Глава 2 — «Багровое Пекло» (Нижний мир).

Вход — через портал из главы «Земли Рассвета» (deps=["overworld:portalow"]).
Выход — крепость в Верхнем мире и очи Эндера, то есть глава 3.

Шесть секций: прибытие, крепость, торговля с пиглинами, незерит, боссы
и обратный путь наверх.
"""

from qdsl import (CUSTOM, Q, SEC, adv, biome, check, dim, give, halo, item,
                  kill, lvl, obs, portal, say, stat, struct, toast, xp)

EMBER   = 0xB0431F
ASH     = 0x7A6A5E
GOLD    = 0xC79A2E
DEEP    = 0x8E2B18
SOUL    = 0x2E8F8A
BOSS    = 0x6B1F2A
WAY     = 0x8A3FCF
GLOW    = 0xFFB347

SECTIONS = [
    SEC("arrival",  ("Arrival",      "Прибытие"),        EMBER),
    SEC("fortress", ("The Fortress", "Пламя крепости"),  DEEP),
    SEC("barter",   ("Gold and Swine", "Золото и свиньи"), GOLD),
    SEC("depths",   ("Black Gold",   "Чёрное золото"),   ASH),
    SEC("bosses",   ("Lords of Hell","Хозяева пекла"),   BOSS),
    SEC("way",      ("Way Back Up",  "Обратный путь"),   WAY),
]

QUESTS = [
# --------------------------------------------------------------------------- #
#  1. ПРИБЫТИЕ
# --------------------------------------------------------------------------- #
Q("enter", ("Step Into the Fire", "Шаг в огонь"), section="arrival",
  deps=["overworld:portalow"], icon="minecraft:netherrack",
  shape="pentagon", size=1.7,
  desc=[("There is no night here, no rain and no safe place. Build a shelter "
         "around the portal before you walk away: ghasts break it easily.",
         "Здесь нет ни ночи, ни дождя, ни безопасного места. Обстрой портал "
         "укрытием, прежде чем уходить: гасты ломают его очень легко."),
        ("Coordinates here are one eighth of the Overworld ones.",
         "Координаты здесь — одна восьмая от координат Верхнего мира.")],
  tasks=[dim("minecraft:the_nether"), adv("minecraft:nether/root")],
  rewards=[lvl(5), give("minecraft:golden_carrot", 8),
           toast("Добро пожаловать в пекло.")]),

Q("netherrack", ("Blood Stone", "Кровавый камень"), section="arrival",
  icon="minecraft:netherrack",
  desc=[("Netherrack melts instantly and is the cheapest building material "
         "here. Do not build a house of it.",
         "Незерак плавится мгновенно и это самый дешёвый местный материал. "
         "Дом из него строить не стоит.")],
  tasks=[item("minecraft:netherrack", 64), item("minecraft:nether_bricks", 16)],
  rewards=[give("minecraft:netherrack", 32)]),

Q("quartz", ("Quartz", "Кварц"), section="arrival",
  icon="minecraft:quartz",
  desc=[("Nether quartz ore gives experience and clean white blocks. It is "
         "everywhere, just look down.",
         "Незер-кварцевая руда даёт опыт и чисто-белые блоки. Её много, "
         "просто смотри под ноги.")],
  tasks=[item("minecraft:quartz", 24), item("minecraft:quartz_block", 8)],
  rewards=[lvl(4)]),

Q("glowstone", ("Glowstone", "Светокамень"), section="arrival",
  icon="minecraft:glowstone",
  desc=[("Hanging clusters under the ceiling. Break with Silk Touch to get "
         "whole blocks, otherwise dust.",
         "Висит гроздьями под потолком. Ломай «Шёлковым касанием» ради целых "
         "блоков, иначе получишь пыль.")],
  tasks=[item("minecraft:glowstone", 12), item("minecraft:glowstone_dust", 24)],
  rewards=[give("minecraft:glowstone", 4), give("minecraft:sea_lantern", 2)]),

Q("netherbiomes", ("Five Hells", "Пять пекл"), section="arrival",
  deps=["enter"], icon="minecraft:crimson_nylium", shape="octagon", size=1.5,
  desc=[("Wastes, crimson and warped forests, soul sand valley and basalt "
         "deltas. Each has its own mobs and sounds.",
         "Пустоши, багровый и искажённый леса, долина песка душ и базальтовые "
         "дельты. У каждого биома свои мобы и свои звуки.")],
  tasks=[biome("minecraft:nether_wastes"), biome("minecraft:crimson_forest"),
         biome("minecraft:warped_forest"), biome("minecraft:soul_sand_valley"),
         biome("minecraft:basalt_deltas"), adv("minecraft:nether/explore_nether")],
  rewards=[lvl(10), give("minecraft:golden_carrot", 8)]),

Q("fortress", ("Nether Fortress", "Крепость Незера"), section="arrival",
  deps=["enter"], icon="minecraft:nether_bricks", shape="rsquare", size=1.5,
  desc=[("Dark red brick corridors over the lava. Blazes, wither skeletons and "
         "nether wart grow here.",
         "Тёмно-красные кирпичные коридоры над лавой. Здесь живут ифриты, "
         "скелеты-иссушители и растёт незерский нарост.")],
  tasks=[struct("minecraft:fortress"), adv("minecraft:nether/find_fortress")],
  rewards=[give("minecraft:nether_bricks", 32), lvl(6)]),

Q("ghast", ("Giant Baby", "Гигантский младенец"), section="arrival",
  deps=["fortress"], icon="minecraft:ghast_tear",
  desc=[("A ghast fireball can be punched back with a bare hand or an arrow — "
         "that is how the achievement is earned. The tear is used in "
         "regeneration potions.",
         "Огненный шар гаста отбивается голой рукой или стрелой — так и "
         "получается достижение. Слеза нужна для зелий регенерации.")],
  tasks=[kill("minecraft:ghast", 3), item("minecraft:ghast_tear", 2),
         adv("minecraft:nether/return_to_sender")],
  rewards=[lvl(8), give("minecraft:fire_charge", 8)]),

# --------------------------------------------------------------------------- #
#  2. ПЛАМЯ КРЕПОСТИ
# --------------------------------------------------------------------------- #
Q("blaze", ("Blazes", "Ифриты"), section="fortress", deps=["fortress"],
  icon="minecraft:blaze_rod", shape="pentagon", size=1.5,
  desc=[("Blaze spawners are in the fortress towers. Bring a shield, a bow and "
         "something to stand behind. Rods are needed for the End and for "
         "brewing.",
         "Рассадники ифритов — в башнях крепости. Возьми щит, лук и то, "
         "за чем можно стоять. Стержни нужны для Края и зельеварения.")],
  tasks=[kill("minecraft:blaze", 8), item("minecraft:blaze_rod", 10),
         adv("minecraft:nether/obtain_blaze_rod")],
  rewards=[give("minecraft:blaze_powder", 4), lvl(8)]),

Q("witherskull", ("Skulls", "Головы"), section="fortress", deps=["blaze"],
  icon="minecraft:wither_skeleton_skull", shape="diamond", size=1.4,
  desc=[("Wither skeletons drop a skull with roughly 2.5% chance. Looting III "
         "makes it much faster. You need three.",
         "Скелет-иссушитель роняет голову с шансом около 2,5%. «Мародёрство III» "
         "сильно ускоряет дело. Нужно три.")],
  tasks=[kill("minecraft:wither_skeleton", 12),
         item("minecraft:wither_skeleton_skull", 3),
         adv("minecraft:nether/get_wither_skull")],
  rewards=[give("minecraft:coal_block", 8), lvl(6)]),

Q("wart", ("Nether Wart", "Незерский нарост"), section="fortress",
  deps=["fortress"], icon="minecraft:nether_wart",
  desc=[("Grows only on soul sand. Take a handful home: every potion starts "
         "with it.",
         "Растёт только на песке душ. Забери горсть домой: с него начинается "
         "любое зелье.")],
  tasks=[item("minecraft:nether_wart", 8), item("minecraft:soul_sand", 16)],
  rewards=[give("minecraft:soul_sand", 8)]),

Q("fireresist", ("Fire Resistance", "Огнестойкость"), section="fortress",
  deps=["wart", "blaze"], icon="minecraft:potion", shape="heart", size=1.4,
  desc=[("Water bottle + nether wart + magma cream. Three minutes of swimming "
         "in lava. Brew a stack before the Wither fight.",
         "Бутылка воды + незерский нарост + сгусток магмы. Три минуты плавания "
         "в лаве. Свари стек до боя с Иссушителем.")],
  tasks=[item("minecraft:blaze_powder", 4), item("minecraft:magma_cream", 4),
         adv("minecraft:nether/brew_potion")],
  rewards=[give("minecraft:glass_bottle", 12), lvl(6)]),

Q("shroom", ("Shroomlights", "Светошляпки"), section="fortress",
  deps=["netherbiomes"], icon="minecraft:shroomlight",
  desc=[("Orange glowing blocks in crimson forests, blue in warped ones. "
         "They light a base better than torches.",
         "Оранжевые светящиеся блоки в багровом лесу, синие — в искажённом. "
         "Освещают базу лучше факелов.")],
  tasks=[item("minecraft:shroomlight", 8), item("minecraft:crimson_fungus", 4),
         item("minecraft:warped_fungus", 4)],
  rewards=[give("minecraft:shroomlight", 4)]),

Q("souls", ("Valley of Souls", "Долина душ"), section="fortress",
  deps=["netherbiomes"], icon="minecraft:soul_lantern",
  desc=[("Skeletons here are fast and there are hundreds of them. Soul sand "
         "slows you down, soul soil does not — build paths from it.",
         "Скелеты здесь быстрые, и их сотни. Песок душ замедляет, почва душ — "
         "нет: из неё удобно делать дорожки.")],
  tasks=[item("minecraft:soul_soil", 16), item("minecraft:soul_lantern", 4),
         kill("minecraft:skeleton", 10)],
  rewards=[give("minecraft:soul_lantern", 8)]),

# --------------------------------------------------------------------------- #
#  3. ЗОЛОТО И СВИНЬИ
# --------------------------------------------------------------------------- #
Q("nethergold", ("Nether Gold", "Золото Незера"), section="barter",
  deps=["enter"], icon="minecraft:gold_nugget",
  desc=[("Nether gold ore gives nuggets even with a stone pickaxe. Nine "
         "nuggets make an ingot, and ingots make piglins friendly.",
         "Незер-золотая руда даёт самородки даже каменной киркой. Девять "
         "самородков — слиток, а слитки делают пиглинов дружелюбными.")],
  tasks=[item("minecraft:gold_nugget", 27), item("minecraft:gold_ingot", 6)],
  rewards=[give("minecraft:gold_ingot", 4)]),

Q("piglin", ("Barter", "Бартер"), section="barter", deps=["nethergold"],
  icon="minecraft:gold_ingot",
  desc=[("Throw a gold ingot at a piglin and wait. They pay with pearls, "
         "quartz, leather, and sometimes with the smithing template.",
         "Брось золотой слиток пиглину и подожди. Они платят жемчугом, "
         "кварцем, кожей, а иногда и кузнечным шаблоном."),
        ("Wear gold armor so they do not attack.",
         "Надень золотую броню, чтобы они не нападали.")],
  tasks=[adv("minecraft:nether/distract_piglin"),
         item("minecraft:gold_ingot", 8), item("minecraft:ender_pearl", 8)],
  rewards=[give("minecraft:gold_block", 2), lvl(4)]),

Q("bastion", ("Bastion Remnant", "Развалины бастиона"), section="barter",
  deps=["piglin"], icon="minecraft:gilded_blackstone", shape="hexagon", size=1.5,
  desc=[("Black stone castles full of piglin brutes. They do not forgive "
         "gold theft. Loot the chests: the netherite upgrade template is here.",
         "Чернокаменные замки, полные пиглинов-громилов. Кражу золота они "
         "не прощают. Обыщи сундуки: здесь лежит шаблон незеритового улучшения.")],
  tasks=[struct("minecraft:bastion_remnant"), adv("minecraft:nether/find_bastion"),
         adv("minecraft:nether/loot_bastion")],
  rewards=[give("minecraft:gold_block", 4), lvl(10)]),

Q("hoglin", ("Hoglin Hunt", "Охота на хоглина"), section="barter",
  deps=["bastion"], icon="minecraft:leather",
  desc=[("Hoglins attack on sight unless you stand in a warped forest. "
         "They drop leather and porkchops.",
         "Хоглины атакуют сразу, если ты не стоишь в искажённом лесу. "
         "С них падает кожа и свинина.")],
  tasks=[kill("minecraft:hoglin", 3), item("minecraft:leather", 8)],
  rewards=[give("minecraft:cooked_porkchop", 8)]),

Q("strider", ("Ride the Strider", "Прогулка на страйдере"), section="barter",
  deps=["netherbiomes"], icon="minecraft:warped_fungus_on_a_stick",
  desc=[("Saddle a strider and steer with a warped fungus on a stick. Lava "
         "is their water.",
         "Оседлай страйдера и управляй удочкой с искажённым грибом. "
         "Лава для них — как вода.")],
  tasks=[adv("minecraft:nether/ride_strider"),
         item("minecraft:warped_fungus_on_a_stick"),
         stat("minecraft:strider_one_cm", 20000)],
  rewards=[give("minecraft:saddle", 2)]),

Q("zpigmen", ("Angry Crowd", "Злая толпа"), section="barter", deps=["nethergold"],
  icon="minecraft:rotten_flesh",
  desc=[("Hit one zombified piglin and every piglin within 32 blocks comes "
         "for you. Choose the moment carefully.",
         "Ударь одного зомби-свиночеловека — и за тобой придут все в радиусе "
         "32 блоков. Выбирай момент осторожно.")],
  tasks=[kill("minecraft:zombified_piglin", 12), item("minecraft:gold_nugget", 36)],
  rewards=[give("minecraft:gold_ingot", 6)]),

# --------------------------------------------------------------------------- #
#  4. ЧЁРНОЕ ЗОЛОТО
# --------------------------------------------------------------------------- #
Q("debris", ("Ancient Debris", "Древние обломки"), section="depths",
  deps=["fortress"], icon="minecraft:ancient_debris", shape="rsquare", size=1.5,
  desc=[("Y=15, long tunnels every two blocks. Beds explode here and clear "
         "a large area — cheap mining, expensive sleep.",
         "Y=15, длинные штреки через два блока. Кровати здесь взрываются "
         "и вычищают большую площадь: добыча дешёвая, сон — дорогой.")],
  tasks=[item("minecraft:ancient_debris", 4),
         adv("minecraft:nether/obtain_ancient_debris")],
  rewards=[lvl(8), give("minecraft:diamond", 4)]),

Q("scrap", ("Netherite Scrap", "Незеритовый лом"), section="depths",
  deps=["debris"], icon="minecraft:netherite_scrap",
  desc=[("Smelt debris in a furnace: four scrap and four gold make one "
         "netherite ingot.",
         "Переплавь обломки в печи: четыре лома и четыре золота дают один "
         "незеритовый слиток.")],
  tasks=[item("minecraft:netherite_scrap", 4), item("minecraft:netherite_ingot")],
  rewards=[give("minecraft:netherite_scrap", 2)]),

Q("upgrade", ("Smithing Template", "Шаблон улучшения"), section="depths",
  deps=["bastion", "scrap"], icon="minecraft:netherite_upgrade_smithing_template",
  desc=[("The template is consumed on every upgrade, but it can be duplicated "
         "with diamonds and netherrack.",
         "Шаблон расходуется при каждом улучшении, но его можно размножить "
         "алмазами и незераком.")],
  tasks=[item("minecraft:netherite_upgrade_smithing_template")],
  rewards=[give("minecraft:diamond", 6)]),

Q("ngear", ("Netherite Tools", "Незеритовые инструменты"), section="depths",
  deps=["upgrade"], icon="minecraft:netherite_pickaxe",
  desc=[("They do not burn in lava and mine faster than diamond.",
         "Они не горят в лаве и копают быстрее алмазных.")],
  tasks=[item("minecraft:netherite_pickaxe"), item("minecraft:netherite_sword")],
  rewards=[lvl(10)]),

Q("narmor", ("Netherite Armor", "Незеритовая броня"), section="depths",
  deps=["ngear"], icon="minecraft:netherite_chestplate", shape="diamond",
  size=1.6,
  desc=[("Four ingots per piece. Knockback resistance is the reason people "
         "grind for it.",
         "По четыре слитка на предмет. Сопротивление отбрасыванию — вот ради "
         "чего всё это.")],
  tasks=[item("minecraft:netherite_helmet"), item("minecraft:netherite_chestplate"),
         adv("minecraft:nether/netherite_armor")],
  rewards=[lvl(15), give("minecraft:netherite_ingot", 2)]),

Q("crying", ("Crying Obsidian", "Плачущий обсидиан"), section="depths",
  deps=["debris"], icon="minecraft:crying_obsidian",
  desc=[("Found in bastions and ruined portals. Needed for the respawn anchor.",
         "Встречается в бастионах и разрушенных порталах. Нужен для якоря "
         "возрождения.")],
  tasks=[item("minecraft:crying_obsidian", 4),
         adv("minecraft:nether/obtain_crying_obsidian")],
  rewards=[give("minecraft:obsidian", 8)]),

Q("anchor", ("Respawn Anchor", "Якорь возрождения"), section="depths",
  deps=["crying"], icon="minecraft:respawn_anchor",
  desc=[("Six crying obsidian and three glowstone. Charge with glowstone and "
         "use it — your spawn moves to the Nether.",
         "Шесть плачущего обсидиана и три светокамня. Заряди светокамнем "
         "и нажми — точка возрождения переедет в Незер.")],
  tasks=[item("minecraft:respawn_anchor"),
         adv("minecraft:nether/charge_respawn_anchor")],
  rewards=[give("minecraft:glowstone", 6)]),

Q("lodestone", ("Lodestone", "Магнетит"), section="depths", deps=["quartz"],
  icon="minecraft:lodestone",
  desc=[("A compass bound to a lodestone always points at it, in any "
         "dimension. Mark your portal.",
         "Компас, привязанный к магнетиту, всегда указывает на него в любом "
         "измерении. Отметь свой портал.")],
  tasks=[item("minecraft:lodestone"), adv("minecraft:nether/use_lodestone")],
  rewards=[give("minecraft:compass", 2)]),

# --------------------------------------------------------------------------- #
#  5. ХОЗЯЕВА ПЕКЛА
# --------------------------------------------------------------------------- #
Q("wither", ("The Wither", "Иссушитель"), section="bosses",
  deps=["witherskull", "blaze"], icon="minecraft:nether_star",
  shape="hexagon", size=1.9,
  desc=[("Four soul sand in a T, three skulls on top. Summon it in a long "
         "tunnel dug in the bedrock roof — the Wither cannot break through "
         "and you can shoot it from the side.",
         "Четыре песка душ буквой Т, три черепа сверху. Призывай в длинном "
         "тоннеле, вырытом в крыше из коренной породы: Иссушитель не сможет "
         "пробиться, а ты будешь стрелять сбоку."),
        ("Bring a bow with Power, golden apples and milk.",
         "Возьми лук с «Мощью», золотые яблоки и молоко.")],
  tasks=[kill("minecraft:wither", 1), item("minecraft:nether_star"),
         adv("minecraft:nether/summon_wither")],
  rewards=[lvl(20), give("minecraft:golden_apple", 4),
           say('tellraw @s {"text":"Звезда Незера твоя.","color":"gold"}')]),

Q("beacon", ("Beacon", "Маяк"), section="bosses", deps=["wither"],
  icon="minecraft:beacon", shape="gear", size=1.6,
  desc=[("Three obsidian, five glass, one nether star. A pyramid of iron "
         "blocks underneath decides the radius and the effects.",
         "Три обсидиана, пять стекла, звезда Незера. Пирамида из железных "
         "блоков снизу определяет радиус и эффекты.")],
  tasks=[item("minecraft:beacon"), adv("minecraft:nether/create_beacon"),
         stat("minecraft:interact_with_beacon", 1)],
  rewards=[lvl(12), give("minecraft:iron_block", 16)]),

Q("fullbeacon", ("Full Beacon", "Полный маяк"), section="bosses", deps=["beacon"],
  icon="minecraft:iron_block", shape="gear", size=1.7,
  desc=[("A four-level pyramid: 164 blocks of iron, gold, diamond, emerald or "
         "netherite. All six effects at once.",
         "Пирамида в четыре уровня: 164 блока железа, золота, алмазов, "
         "изумрудов или незерита. Все шесть эффектов сразу.")],
  tasks=[adv("minecraft:nether/create_full_beacon"),
         item("minecraft:iron_block", 64)],
  rewards=[lvl(20), give("minecraft:netherite_block")]),

Q("alleffects", ("Whole Spectrum", "Весь спектр"), section="bosses",
  deps=["fireresist"], icon="minecraft:potion", shape="gear", size=1.4,
  optional=True,
  desc=[("Hold every status effect at the same time, including the bad ones. "
         "Beacon, potions, a witch and a pufferfish will help.",
         "Держи одновременно все эффекты, включая вредные. Помогут маяк, "
         "зелья, ведьма и иглобрюх.")],
  tasks=[adv("minecraft:nether/all_effects")],
  rewards=[lvl(15), give("minecraft:enchanted_golden_apple", 2)]),

Q("premium", ("Premium Token", "Улучшенная медаль"), section="bosses",
  deps=["narmor"], icon=CUSTOM["premium"], shape="gear", size=1.5,
  desc=[("A custom item of this pack: three netherite scrap around a token, "
         "three gold ingots underneath. The recipe is in JEI.",
         "Свой предмет пака: три незеритовых лома вокруг медали и три золотых "
         "слитка снизу. Рецепт есть в JEI.")],
  tasks=[item(CUSTOM["premium"]), item(CUSTOM["token"], 3)],
  rewards=[lvl(10), give("minecraft:netherite_scrap", 2)]),

# --------------------------------------------------------------------------- #
#  6. ОБРАТНЫЙ ПУТЬ
# --------------------------------------------------------------------------- #
Q("eyes", ("Eyes of Ender", "Очи Эндера"), section="way", deps=["blaze"],
  icon="minecraft:ender_eye", shape="hexagon", size=1.4,
  desc=[("Blaze powder plus an ender pearl. Take twelve: some of them break, "
         "and some will have to be thrown into the portal frame.",
         "Огненный порошок плюс жемчуг Края. Бери двенадцать: часть сломается, "
         "часть придётся вставить в раму портала.")],
  tasks=[item("minecraft:ender_eye", 12), item("minecraft:blaze_powder", 6)],
  rewards=[give("minecraft:ender_eye", 2), lvl(6)]),

Q("stronghold", ("Stronghold", "Крепость"), section="way", deps=["eyes"],
  icon="minecraft:end_portal_frame", shape="gear", size=1.7,
  desc=[("Throw an eye and follow it. When it starts going down, dig. "
         "The portal room is under the library.",
         "Брось око и иди за ним. Когда оно начнёт уходить вниз — копай. "
         "Комната портала находится под библиотекой.")],
  tasks=[struct("minecraft:stronghold"), adv("minecraft:story/follow_ender_eye"),
         obs("minecraft:end_portal_frame", "block", 20)],
  rewards=[lvl(10), give("minecraft:ender_eye", 4)]),

Q("lastprep", ("Before the Fall", "Перед падением"), section="way",
  deps=["stronghold"], icon="minecraft:golden_carrot",
  desc=[("Food, blocks to bridge with, fireworks for the elytra later, and "
         "a bed you are NOT going to sleep in.",
         "Еда, блоки для мостов, фейерверки на потом для элитр и кровать, "
         "в которой ты спать НЕ будешь."),
        ("Tick the box when the inventory is ready.",
         "Поставь галочку, когда инвентарь готов.")],
  tasks=[item("minecraft:golden_carrot", 16), item("minecraft:ender_pearl", 8),
         check()],
  rewards=[lvl(8), give("minecraft:firework_rocket", 16)]),
]


def build_images():
    return [
        halo("enter", GLOW, 4.0, 210),
        halo("wither", 0xFF6A3C, 4.4, 210),
        halo("beacon", 0xFFE9A8, 3.6, 190),
        halo("stronghold", WAY, 3.6, 200),
        # предупреждение у боя с Иссушителем
        {
            "at": "wither", "dx": 0.0, "dy": 1.6, "w": 5.2, "h": 0.8,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x2A0B0B, "alpha": 240, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Boss. Prepare first.", "Босс. Сначала подготовься."),
        },
        # подсказка про уровень добычи обломков
        {
            "at": "debris", "dx": 0.0, "dy": -1.35, "w": 4.4, "h": 0.75,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x1B1B22, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Y = 15, dig sideways", "Y = 15, копай вбок"),
        },
        # кликабельный переход в главу про Край
        portal("stronghold", "end:enter", dx=2.6, dy=0.0, size=1.9,
               texture="portal_end.png",
               title=("To the End", "В Край")),
    ]


CHAPTER = {
    "id": 0xC002, "filename": "nether",
    "layout": "blocks", "cols": 2, "dx": 2.1, "dy": 1.45,
    "pad_x": 4.5, "pad_y": 6.5,
    "shape": "pentagon", "icon": "minecraft:netherrack",
    "banner": "banner_nether", "banner_w": 13.0, "banner_h": 3.25,
    "banner_gap": 2.9,
    "title": ("The Crimson Furnace", "Багровое Пекло"),
    "subtitle": [
        ("No water, no sleep, no sky. Everything here burns or wants to burn "
         "you.",
         "Ни воды, ни сна, ни неба. Здесь всё либо горит, либо хочет сжечь "
         "тебя."),
        ("Get in through the portal from the Dawnlands, get out through the "
         "stronghold.",
         "Вход — через портал из Земель Рассвета, выход — через крепость."),
    ],
    "sections": SECTIONS,
    "quests": QUESTS,
    "images": build_images(),
    "links": [
        # «откуда мы пришли»: та же задача, но видна и в этой главе
        {"quest": "overworld:portalow"},
    ],
}
