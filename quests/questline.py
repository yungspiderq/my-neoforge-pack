#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Описание квестовой линейки. Это ДАННЫЕ — их редактирует автор пака.
SNBT из них генерирует scripts/gen_quests.py.

Формат текста: (english, russian).
  • english попадает в lang/en_us.snbt — это fallback-локаль FTB Quests,
    она грузится и отправляется игроку ВСЕГДА;
  • russian попадает в lang/ru_ru.snbt — подхватится, если в клиенте выбран
    русский язык.

ID — 16-символьный uppercase hex (формат QuestObjectBase.getCodeString).
ВАЖНО: readID() перегенерирует ID, если он равен 0 или 1 либо уже занят,
поэтому нули и единицы использовать нельзя.

Схема ID (младший байт квеста ДОЛЖЕН быть 0 — в него генератор пишет индекс
задачи/награды, поэтому на квест максимум 15 задач и 15 наград):

    главы    0x C00n          -> 000000000000C001
    квесты   0x 1c q0         -> глава c, квест q:  0x1110, 0x1120, ... 0x1230
    задачи   0x 2c qt         -> 0x2110, 0x2111, ...
    награды  0x 3c qr         -> 0x3110, 0x3111, ...

ID задач и наград генератор проставляет САМ — в questline.py их писать не нужно.

Задачи (type):
    item        — иметь/сдать предмет      {item, count(long), consume_items}
    checkmark   — просто отметить          {}
    kill        — убить мобов              {entity, value}
    dimension   — посетить измерение       {dimension}
    advancement — получить достижение      {advancement}
    xp          — уровень опыта            {value, points}
    stat        — статистика               {stat, value}
    location / biome / structure / observation / fluid / custom / gamestage

Награды (type):
    item        {item, count(int), random_bonus(int), only_one(bool)}
    xp_levels   {xp_levels(int)}      <- ВНИМАНИЕ: поле называется xp_levels
    xp          {xp(int)}
    command     {command, permission_level(int), silent(bool), feedback_message}
    toast       {description}         <- title уходит в lang как reward.<id>.title
    reward_table / loot / random / choice / advancement / custom / gamestage / all_table / currency

Типы числовых полей (проверено по исходникам FTB Quests 2101.1.36):
    x, y, size, icon_scale, default_quest_size  -> double  (0.0d)
    order_index, version, min_required_deps     -> int     (0)
    ItemTask.count                              -> LONG    (8L)
    ItemReward.count, random_bonus              -> int     (8)
    булевы                                      -> byte    (0b / 1b)
"""

# --------------------------------------------------------------------------- #
#  Кастомные предметы KubeJS (регистрируются в kubejs/startup_scripts/)
# --------------------------------------------------------------------------- #

CUSTOM = {
    "quest_token":         "kubejs:quest_token",
    "quest_token_premium": "kubejs:quest_token_premium",
    "quest_medal":         "kubejs:quest_medal",
}

# --------------------------------------------------------------------------- #
#  Линейка
# --------------------------------------------------------------------------- #

QUESTLINE = [
    # ===================================================================== #
    {
        "id": 0xC001, "filename": "beginning", "shape": "circle",
        "title": ("Getting Started", "Начало"),
        "subtitle": [
            ("From bare hands to a full set of iron gear.",
             "От голых рук до полного комплекта железных инструментов."),
            ("Every quest here uses only vanilla items.",
             "Все квесты этой главы используют только ванильные предметы."),
        ],
        "quests": [
            {
                "id": 0x1110, "x": -4.5, "y": 0.0,
                "title": ("First Wood", "Первое дерево"),
                "desc": [
                    ("Punch a tree and collect 8 oak logs. Any log type counts "
                     "for crafting, but this quest specifically asks for oak.",
                     "Ударь дерево рукой и собери 8 дубовых брёвен. Для крафта "
                     "подойдёт любая древесина, но этот квест просит именно дуб."),
                ],
                "tasks": [{"type": "item", "item": "minecraft:oak_log", "count": 8}],
                "rewards": [{"type": "item", "item": "minecraft:crafting_table", "count": 1}],
            },
            {
                "id": 0x1120, "x": -3.0, "y": 0.0, "deps": [0x1110],
                "title": ("Workbench", "Верстак"),
                "desc": [
                    ("Craft a crafting table from 4 planks. Everything else "
                     "starts here.",
                     "Скрафти верстак из 4 досок. Всё остальное начинается здесь."),
                ],
                "tasks": [{"type": "item", "item": "minecraft:crafting_table", "count": 1}],
                "rewards": [{"type": "item", "item": "minecraft:stick", "count": 8}],
            },
            {
                "id": 0x1130, "x": -1.5, "y": 0.0, "deps": [0x1120],
                "title": ("Wooden Pickaxe", "Деревянная кирка"),
                "desc": [
                    ("Craft a wooden pickaxe: 3 planks + 2 sticks.",
                     "Скрафти деревянную кирку: 3 доски + 2 палки."),
                    ("Without it you cannot get cobblestone.",
                     "Без неё нельзя добыть булыжник."),
                ],
                "tasks": [{"type": "item", "item": "minecraft:wooden_pickaxe", "count": 1}],
                "rewards": [{"type": "item", "item": "minecraft:bread", "count": 6}],
            },
            {
                "id": 0x1140, "x": 0.0, "y": 0.0, "deps": [0x1130],
                "title": ("Stone Age", "Каменный век"),
                "desc": [
                    ("Mine 32 cobblestone and upgrade to a stone pickaxe.",
                     "Добудь 32 булыжника и перейди на каменную кирку."),
                    ("Stone tools last more than twice as long as wooden ones.",
                     "Каменные инструменты служат вдвое дольше деревянных."),
                ],
                "tasks": [
                    {"type": "item", "item": "minecraft:cobblestone", "count": 32},
                    {"type": "item", "item": "minecraft:stone_pickaxe", "count": 1},
                ],
                "rewards": [
                    {"type": "item", "item": "minecraft:torch", "count": 16},
                    {"type": "item", "item": "minecraft:coal", "count": 8},
                ],
            },
            {
                "id": 0x1150, "x": 1.5, "y": 0.0, "deps": [0x1140],
                "title": ("Iron", "Железо"),
                "desc": [
                    ("Smelt 8 iron ingots. Iron ore needs a stone pickaxe or "
                     "better — a wooden one destroys the drop.",
                     "Выплавь 8 железных слитков. Железную руду нужно копать "
                     "каменной киркой или лучше — деревянная уничтожает дроп."),
                ],
                "tasks": [{"type": "item", "item": "minecraft:iron_ingot", "count": 8}],
                "rewards": [
                    {"type": "item", "item": "minecraft:iron_pickaxe", "count": 1},
                    {"type": "item", "item": "minecraft:bucket", "count": 1},
                ],
            },
            {
                "id": 0x1160, "x": 3.0, "y": 0.0, "deps": [0x1150],
                "title": ("Fully Equipped", "Полный комплект"),
                "desc": [
                    ("Craft a full set of iron gear plus a shield.",
                     "Скрафти полный комплект железных инструментов и щит."),
                ],
                "tasks": [
                    {"type": "item", "item": "minecraft:iron_sword", "count": 1},
                    {"type": "item", "item": "minecraft:iron_axe", "count": 1},
                    {"type": "item", "item": "minecraft:iron_shovel", "count": 1},
                    {"type": "item", "item": "minecraft:shield", "count": 1},
                ],
                "rewards": [
                    {"type": "xp_levels", "xp_levels": 5},
                    {"type": "item", "item": "minecraft:golden_apple", "count": 1},
                ],
            },
        ],
    },

    # ===================================================================== #
    {
        "id": 0xC002, "filename": "food_and_farm", "shape": "square",
        "title": ("Food and Farming", "Еда и ферма"),
        "subtitle": [
            ("A stable food supply means you stop dying to hunger mid-expedition.",
             "Стабильная еда означает, что ты перестанешь умирать от голода посреди вылазки."),
        ],
        "quests": [
            {
                "id": 0x1210, "x": -3.0, "y": 0.0,
                "title": ("Daily Bread", "Хлеб насущный"),
                "desc": [
                    ("Grow wheat and bake 6 bread. Tall grass drops wheat seeds.",
                     "Вырасти пшеницу и испеки 6 хлеба. Семена выпадают из высокой травы."),
                ],
                "tasks": [
                    {"type": "item", "item": "minecraft:wheat", "count": 9},
                    {"type": "item", "item": "minecraft:bread", "count": 6},
                ],
                "rewards": [{"type": "item", "item": "minecraft:bone_meal", "count": 16}],
            },
            {
                "id": 0x1220, "x": -1.5, "y": 0.0, "deps": [0x1210],
                "title": ("Animal Husbandry", "Животноводство"),
                "desc": [
                    ("Cows drop leather; pigs and chickens are worth breeding too. "
                     "Leather is needed for books and item frames.",
                     "С коров падает кожа; свиней и кур тоже стоит разводить. "
                     "Кожа нужна для книг и рам."),
                ],
                "tasks": [
                    {"type": "item", "item": "minecraft:leather", "count": 4},
                    {"type": "item", "item": "minecraft:cooked_beef", "count": 8},
                    {"type": "item", "item": "minecraft:egg", "count": 8},
                ],
                "rewards": [
                    {"type": "item", "item": "minecraft:lead", "count": 4},
                    {"type": "item", "item": "minecraft:hay_block", "count": 4},
                ],
            },
            {
                "id": 0x1230, "x": 0.0, "y": 0.0, "deps": [0x1220],
                "title": ("Kitchen Garden", "Огород"),
                "desc": [
                    ("Carrots and potatoes come from zombie drops or village "
                     "farms. Golden carrots are the best saturation food in the game.",
                     "Морковь и картофель падают с зомби или берутся на фермах "
                     "в деревнях. Золотая морковь — лучшая еда по насыщению."),
                ],
                "tasks": [
                    {"type": "item", "item": "minecraft:carrot", "count": 16},
                    {"type": "item", "item": "minecraft:potato", "count": 16},
                    {"type": "item", "item": "minecraft:golden_carrot", "count": 4},
                ],
                "rewards": [{"type": "xp_levels", "xp_levels": 3}],
            },
            {
                "id": 0x1240, "x": 1.5, "y": 0.0, "deps": [0x1210],
                "title": ("Gone Fishing", "Рыбалка"),
                "desc": [
                    ("Craft a fishing rod and catch something. Fishing also drops "
                     "enchanted books and saddles as treasure.",
                     "Скрафти удочку и поймай что-нибудь. Рыбалка также даёт "
                     "зачарованные книги и сёдла в качестве сокровищ."),
                ],
                "tasks": [
                    {"type": "item", "item": "minecraft:fishing_rod", "count": 1},
                    {"type": "item", "item": "minecraft:cod", "count": 8},
                    {"type": "item", "item": "minecraft:salmon", "count": 4},
                ],
                "rewards": [
                    {"type": "item", "item": "minecraft:cooked_cod", "count": 8},
                    {"type": "xp_levels", "xp_levels": 2},
                ],
            },
        ],
    },

    # ===================================================================== #
    {
        "id": 0xC003, "filename": "exploration", "shape": "diamond",
        "title": ("Exploration", "Исследование"),
        "subtitle": [
            ("Caves, the Nether, the Stronghold and the End.",
             "Пещеры, Нижний мир, Крепость и Край."),
        ],
        "quests": [
            {
                "id": 0x1310, "x": -4.5, "y": 0.0,
                "title": ("Into the Depths", "В глубины"),
                "desc": [
                    ("Diamonds spawn below Y=16, most commonly around Y=-59. "
                     "Bring torches, food and a water bucket.",
                     "Алмазы встречаются ниже Y=16, чаще всего около Y=-59. "
                     "Возьми факелы, еду и ведро воды."),
                ],
                "tasks": [{"type": "item", "item": "minecraft:diamond", "count": 3}],
                "rewards": [{"type": "item", "item": "minecraft:diamond_pickaxe", "count": 1}],
            },
            {
                "id": 0x1320, "x": -3.0, "y": 0.0, "deps": [0x1310],
                "title": ("Obsidian", "Обсидиан"),
                "desc": [
                    ("Pour water over a lava pool. A diamond pickaxe is required "
                     "to mine obsidian.",
                     "Вылей воду на озеро лавы. Чтобы добыть обсидиан, нужна "
                     "алмазная кирка."),
                ],
                "tasks": [{"type": "item", "item": "minecraft:obsidian", "count": 10}],
                "rewards": [
                    {"type": "item", "item": "minecraft:flint_and_steel", "count": 1},
                    {"type": "item", "item": "minecraft:golden_apple", "count": 2},
                ],
            },
            {
                "id": 0x1330, "x": -1.5, "y": 0.0, "deps": [0x1320],
                "title": ("The Nether", "Нижний мир"),
                "desc": [
                    ("Build a 4x5 obsidian frame, light it and step through. "
                     "One block in the Nether equals eight in the Overworld.",
                     "Построй рамку 4x5 из обсидиана, подожги и вступи в портал. "
                     "Один блок в Нижнем мире равен восьми в Верхнем."),
                ],
                "tasks": [{"type": "dimension", "dimension": "minecraft:the_nether"}],
                "rewards": [
                    {"type": "item", "item": "minecraft:quartz", "count": 16},
                    {"type": "xp_levels", "xp_levels": 3},
                ],
            },
            {
                "id": 0x1340, "x": 0.0, "y": 0.0, "deps": [0x1330],
                "title": ("Blaze Rods", "Огненные стержни"),
                "desc": [
                    ("Find a Nether Fortress and kill blazes. Rods are needed for "
                     "eyes of ender and for brewing.",
                     "Найди крепость Нижнего мира и убей ифритов. Стержни нужны "
                     "для очей Края и для зельеварения."),
                ],
                "tasks": [
                    {"type": "item", "item": "minecraft:blaze_rod", "count": 7},
                    {"type": "kill", "entity": "minecraft:blaze", "value": 7},
                ],
                "rewards": [{"type": "item", "item": "minecraft:ender_pearl", "count": 14}],
            },
            {
                "id": 0x1350, "x": 1.5, "y": 0.0, "deps": [0x1340],
                "title": ("The Stronghold", "Крепость"),
                "desc": [
                    ("Craft eyes of ender and throw them to triangulate the "
                     "Stronghold. Bring a pickaxe and a bed marker.",
                     "Скрафти очи Края и бросай их, чтобы найти Крепость. "
                     "Возьми кирку и метку-кровать."),
                ],
                "tasks": [{"type": "item", "item": "minecraft:ender_eye", "count": 12}],
                "rewards": [
                    {"type": "xp_levels", "xp_levels": 8},
                    {"type": "item", "item": "minecraft:ender_chest", "count": 1},
                ],
            },
            {
                "id": 0x1360, "x": 3.0, "y": 0.0, "deps": [0x1350],
                "title": ("The End", "Край"),
                "desc": [
                    ("Enter the End portal and defeat the Ender Dragon. Destroy "
                     "the crystals on the pillars first.",
                     "Войди в портал Края и победи Дракона Края. Сначала уничтожь "
                     "кристаллы на столбах."),
                ],
                "tasks": [
                    {"type": "dimension", "dimension": "minecraft:the_end"},
                    {"type": "kill", "entity": "minecraft:ender_dragon", "value": 1},
                ],
                "rewards": [
                    {"type": "xp_levels", "xp_levels": 20},
                    {"type": "item", "item": "minecraft:shulker_box", "count": 1},
                    {"type": "item", "item": "minecraft:elytra", "count": 1},
                ],
            },
        ],
    },

    # ===================================================================== #
    #  Глава, завязанная на кастомные предметы KubeJS
    # ===================================================================== #
    {
        "id": 0xC004, "filename": "kubejs_custom", "shape": "gear",
        "title": ("Custom Content", "Кастомный контент"),
        "subtitle": [
            ("These items do not exist in vanilla — they are registered by "
             "KubeJS from the scripts in kubejs/.",
             "Этих предметов нет в ванили — их регистрирует KubeJS из скриптов "
             "в папке kubejs/."),
            ("If the recipes below do not appear, check kubejs/startup_scripts "
             "loaded and look at logs/kubejs/.",
             "Если рецепты ниже не появились, проверь загрузку "
             "kubejs/startup_scripts и загляни в logs/kubejs/."),
        ],
        "quests": [
            {
                "id": 0x1410, "x": -2.0, "y": 0.0,
                "title": ("Quest Token", "Медаль квеста"),
                "desc": [
                    ("Craft a Quest Token: 1 diamond + 1 gold ingot + 1 emerald, "
                     "shapeless.",
                     "Скрафти Медаль квеста: 1 алмаз + 1 золотой слиток + 1 изумруд, "
                     "бесформенный рецепт."),
                    ("This item is registered by KubeJS at "
                     "kubejs/startup_scripts/custom_items.js.",
                     "Этот предмет регистрируется KubeJS в "
                     "kubejs/startup_scripts/custom_items.js."),
                ],
                "tasks": [{"type": "item", "item": CUSTOM["quest_token"], "count": 1}],
                "rewards": [
                    {"type": "xp_levels", "xp_levels": 3},
                    {"type": "item", "item": "minecraft:gold_ingot", "count": 4},
                ],
            },
            {
                "id": 0x1420, "x": 0.0, "y": 0.0, "deps": [0x1410],
                "title": ("Premium Token", "Улучшенная медаль"),
                "desc": [
                    ("Upgrade the token in a shaped recipe: 3 netherite scrap "
                     "across the top, token in the middle, 3 gold below.",
                     "Улучши медаль форменным рецептом: 3 незеритовых обломка "
                     "сверху, медаль в центре, 3 золота снизу."),
                ],
                "tasks": [{"type": "item", "item": CUSTOM["quest_token_premium"], "count": 1}],
                "rewards": [
                    {"type": "item", "item": "minecraft:diamond", "count": 4},
                    {"type": "xp_levels", "xp_levels": 6},
                ],
            },
            {
                "id": 0x1430, "x": 2.0, "y": 0.0, "deps": [0x1420],
                "title": ("Master of Quests", "Мастер квестов"),
                "desc": [
                    ("The final custom item. Its recipe is registered from "
                     "kubejs/server_scripts/recipes.js and requires a Nether Star.",
                     "Финальный кастомный предмет. Его рецепт регистрируется из "
                     "kubejs/server_scripts/recipes.js и требует звезду Нижнего мира."),
                    ("Earning one means you have finished the Wither.",
                     "Получение означает, что ты одолел Иссушителя."),
                ],
                "tasks": [{"type": "item", "item": CUSTOM["quest_medal"], "count": 1}],
                "rewards": [
                    {"type": "xp_levels", "xp_levels": 30},
                    {"type": "item", "item": "minecraft:netherite_ingot", "count": 2},
                    {"type": "item", "item": "minecraft:enchanted_golden_apple", "count": 2},
                ],
            },
        ],
    },
]

# --------------------------------------------------------------------------- #
#  Настройки самого файла квестов (data.snbt)
#  Держим МИНИМАЛЬНЫМИ: readData() подставляет дефолты для отсутствующих
#  ключей, а лишний ключ неправильного типа может сломать загрузку.
# --------------------------------------------------------------------------- #

FILE_SETTINGS = {
    "default_quest_shape": "circle",
}

FILE_VERSION = 13          # BaseQuestFile.VERSION для FTB Quests 2101.1.36
