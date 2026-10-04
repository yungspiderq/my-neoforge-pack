# -*- coding: utf-8 -*-
"""
Глава 5 — «Вечное Звездосветье» (мод Eternal Starlight 0.9.1+1.21.1+neoforge).

Глава-витрина контентного мода: 12 секций, маленькие осмысленные квесты
(1-8 задач): сет брони, серия инструмента, один уникальный клинок со своим
характером, полный стройнабор одного камня, том пластинок одного автора.
Покрытие контента проверено генератором дизайна: union всех item-задач главы
равен полному списку item-форм мода из jar (1195 моделей минус spawn-egg и
trim-варианты отделки) — ни один предмет не потерян; длинные списки разбиты
на тома (схема ID пака: не больше 15 задач на квест).
"""

from qdsl import (CUSTOM, Q, SEC, biome, check, dim, give, item, kill, lvl,
                  struct, toast, xpr)

CLR_S1 = 0x2B4C7E
CLR_S2 = 0x6A4C93
CLR_S3 = 0x1F7A70
CLR_S4 = 0x8C5A2B
CLR_S5 = 0xA63A3A
CLR_S6 = 0x3A6AA6
CLR_S7 = 0x7A4C93
CLR_S8 = 0x7A1F4C
CLR_S9 = 0xC9A227

SECTIONS = [
    SEC("s1", ('The Road to the Starlight', 'Дорога в Звездосветье'), CLR_S1, pad=1.8),
    SEC("s2", ('The Bestiary', 'Бестиарий'), CLR_S2, pad=1.8),
    SEC("s3", ('Ores and Materials', 'Руды и материалы'), CLR_S3, pad=1.8),
    SEC("s4", ('The Arsenal: Nine Tiers', 'Арсенал: девять тиров'), CLR_S4, pad=1.8),
    SEC("s5", ('Unique Blades', 'Уникальные клинки'), CLR_S5, pad=1.8),
    SEC("s6", ('Arrows and a Quiver', 'Стрелы и колчан'), CLR_S6, pad=1.8),
    SEC("s7", ('The Raiment', 'Облачение'), CLR_S7, pad=1.8),
    SEC("s8", ('Table and Pocket', 'Стол и карман'), CLR_S8, pad=1.8),
    SEC("s9", ('Pearls and Finale', 'Жемчужины и финал'), CLR_S9, pad=1.8),
]

QUESTS = [
# --- секция s1 ---
Q("q001", ('A Sky of a Million Stars', 'Небо миллиона звёзд'), section="s1",
  icon="eternal_starlight:orb_of_prophecy",
  size=1.6,
  desc=[
      ('Eternal Starlight opens the Starlight dimension: night, auroras and 24 biomes.',
       'Eternal Starlight открывает измерение Звездосветья: ночь, сияния и 24 биома.'),
      ('The portal is not built from blocks - the orb of prophecy opens it in your hands.',
       'Портал не строят из блоков — его открывает сфера пророчества в руках.'),
  ],
  tasks=[
      item("eternal_starlight:orb_of_prophecy"),
      dim("eternal_starlight:starlight"),
  ],
  rewards=[
      lvl(4),
      toast('Ты в Вечном Звездосветье. Небо здесь не кончается.'),
  ]),

Q("q002", ('The Five Portal Ruins', 'Пять руин врат'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:dusted_shard",
  size=1.2,
  desc=[
      ('Common, cold, desert, forest and jungle portal ruins: chests with dusted shards.',
       'Обычные, холодные, пустынные, лесные и тропические руины порталов: сундуки с запылёнными осколками.'),
      ('Someone opened the gates before you - and did not come back.',
       'Кто-то открыл врата до тебя — и не вернулся.'),
  ],
  tasks=[
      struct("eternal_starlight:portal_ruins_common"),
      struct("eternal_starlight:portal_ruins_cold"),
      struct("eternal_starlight:portal_ruins_desert"),
      struct("eternal_starlight:portal_ruins_forest"),
      struct("eternal_starlight:portal_ruins_jungle"),
  ],
  rewards=[
      xpr(120),
      give("eternal_starlight:dusted_shard", 8),
  ]),

Q("q003", ('Starlight Forests', 'Леса Звездосветья'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:starlit_lily_pad",
  desc=[
      ('Six forest biomes: from sparse taiga to dense canopies and torreya thickets.',
       'Шесть лесных биомов: от редкой тайги до густого полога и тисовых рощ.'),
      ('The compass spins: navigate by the glow of crystals.',
       'Компас крутится: ориентируйся по сиянию кристаллов.'),
  ],
  tasks=[
      biome("eternal_starlight:starlight_forest"),
      biome("eternal_starlight:starlight_dense_forest"),
      biome("eternal_starlight:umbral_plains"),
      biome("eternal_starlight:glimmer_scrubland"),
      biome("eternal_starlight:starlight_permafrost_forest"),
      biome("eternal_starlight:permafrost_peaks"),
  ],
  rewards=[
      xpr(110),
  ]),

Q("q004", ('Seas and Shores', 'Моря и берега'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:starlit_lily_pad",
  desc=[
      ('Starlit seas, kelp forests, warm and grim shores: the water glows at night.',
       'Звёздные моря, ламинарии, тёплые и мрачные берега: вода здесь светится ночью.'),
      ('A boat is not a luxury but the only way across.',
       'Лодка — не роскошь, а единственный путь.'),
  ],
  tasks=[
      biome("eternal_starlight:starlight_taiga"),
      biome("eternal_starlight:dark_swamp"),
      biome("eternal_starlight:scarlet_forest"),
      biome("eternal_starlight:torreya_forest"),
      biome("eternal_starlight:crystallized_desert"),
      biome("eternal_starlight:lucent_mycelium_isle"),
  ],
  rewards=[
      xpr(110),
  ]),

Q("q005", ('Isles and Plains', 'Острова и равнины'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:starlit_lily_pad",
  desc=[
      ('Solaris isles, mycelium isles, umbral plains and shimmering scrublands.',
       'Солнечные острова, мицелиевые островки, тенистые равнины и мерцающие кустарники.'),
      ('Each isle hides its own flora - and its own danger.',
       'Каждый остров прячет свою флору — и свою опасность.'),
  ],
  tasks=[
      biome("eternal_starlight:solaris_isles"),
      biome("eternal_starlight:starlit_sky"),
      biome("eternal_starlight:shimmer_river"),
      biome("eternal_starlight:ether_river"),
      biome("eternal_starlight:starlit_sea"),
      biome("eternal_starlight:icy_sea"),
  ],
  rewards=[
      xpr(110),
  ]),

Q("q006", ('Ice, Desert and the Abyss', 'Лёд, пустыня и Бездна'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:starlit_lily_pad",
  desc=[
      ('Permafrost peaks, crystallized desert and the Abyss: the darkest biome.',
       'Вершины мерзлоты, кристаллизованная пустыня и Бездна: темнейший биом.'),
      ('In the Abyss lives the reason this chapter is worth finishing.',
       'В Бездне живёт то, ради чего стоило дойти до конца.'),
  ],
  tasks=[
      biome("eternal_starlight:spiral_kelp_forest"),
      biome("eternal_starlight:lush_shallow_sea"),
      biome("eternal_starlight:the_abyss"),
      biome("eternal_starlight:warm_shore"),
      biome("eternal_starlight:grim_shore"),
  ],
  rewards=[
      xpr(130),
  ]),

Q("q007", ('The Golem Forge and the Cursed Garden', 'Кузница легиона и Проклятый сад'), section="s1",
  deps=['q006'],
  icon="eternal_starlight:golem_steel_ingot",
  desc=[
      ('The forge births starlight golems; in the garden nothing blooms twice.',
       'В кузнице рождаются звездосветные големы; в саду ничего не цветёт дважды.'),
      ('In the forge look for energy blocks: deactivate them and the golem becomes vulnerable.',
       'В кузнице ищи энергоблоки: выключи — и голем станет уязвим.'),
  ],
  tasks=[
      struct("eternal_starlight:golem_forge"),
      struct("eternal_starlight:cursed_garden"),
  ],
  rewards=[
      xpr(100),
  ]),

Q("q008", ('The Stranghoul Den', 'Логово странгуля'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:tenacious_vine",
  desc=[
      ('A den in the dark: the stranghoul hunts here at night.',
       'Логово во тьме: странгуль охотится здесь по ночам.'),
      ('A bowl of spicy stew hires it for a day. Seriously.',
       'Миска острого рагу нанимает его на день. Серьёзно.'),
  ],
  tasks=[
      struct("eternal_starlight:stranghoul_den"),
  ],
  rewards=[
      xpr(60),
  ]),

# --- секция s2 ---
Q("q009", ('Small Fry of the Star Night', 'Мелочь звёздной ночи'), section="s2",
  deps=['q008'],
  icon="eternal_starlight:gleech_egg",
  desc=[
      ('Ratlin, gleech and shadow snail: the humble fauna of the dimension.',
       'Крысёныш, гиявка и теневая улитка: скромная фауна измерения.'),
      ('A thrown gleech egg heals by bloodletting - hit a mob, not yourself.',
       'Брошенное яйцо гиявки лечит кровопусканием — бей в моба, не в себя.'),
  ],
  tasks=[
      kill("eternal_starlight:ratlin", 1),
      kill("eternal_starlight:gleech", 1),
      kill("eternal_starlight:shadow_snail", 1),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q010", ('The Gentle and the Winged', 'Кроткие и крылатые'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('The aurora deer drops antlers only when it rams hard blocks - make it angry.',
       'Полярный олень роняет рога, лишь тараня твёрдые блоки — разозли его.'),
      ('The crystallized moth is tamed with meat and strikes with a sound wave.',
       'Кристаллизованный мотылёк приручается мясом и бьёт звуковой волной.'),
  ],
  tasks=[
      kill("eternal_starlight:aurora_deer", 1),
      kill("eternal_starlight:shimmer_lacewing", 1),
      kill("eternal_starlight:crystallized_moth", 1),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q011", ('Angler of the Star Seas', 'Рыболов звёздных морей'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:luminofish",
  desc=[
      ('Luminofish glows, rookfish is armour-plated: both bite at night.',
       'Светорыба светится, туровик бронирован: оба клюют ночью.'),
      ('The rookfish air sac is the core of breathing boots.',
       'Воздушный мешок туровика — основа дышащих ботинок.'),
  ],
  tasks=[
      kill("eternal_starlight:luminofish", 1),
      kill("eternal_starlight:rookfish", 1),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q012", ('The Bird and the Ent', 'Птица и энт'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:starfire_bird_egg",
  desc=[
      ('Do not kill the starfire bird for starfire: put seeds in its nest instead.',
       'Не убивай птицу-звездопала ради звездопала: положи семена в её гнездо.'),
      ('The ent is an old tree that walks. It does not like axes.',
       'Энт — старое дерево, которое ходит. Топоров не любит.'),
  ],
  tasks=[
      kill("eternal_starlight:starfire_bird", 1),
      kill("eternal_starlight:ent", 1),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q013", ('Night Hunters', 'Ночные охотники'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:tentacle_spike",
  desc=[
      ('Dusk spiders, star skeletons and the thirst walker: the night has teeth.',
       'Сумеречные пауки, звёздные скелеты и жаждущий странник: у ночи есть зубы.'),
      ("The walker's tooth of hunger is a building material - and a weapon.",
       'Зуб голода странника — стройматериал и оружие.'),
  ],
  tasks=[
      kill("eternal_starlight:nightfall_spider", 1),
      kill("eternal_starlight:lonestar_skeleton", 1),
      kill("eternal_starlight:thirst_walker", 1),
  ],
  rewards=[
      xpr(80),
  ]),

Q("q014", ('Elements and Predators', 'Стихии и хищники'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:tentacle_spike",
  desc=[
      ('Creteors fall with meteor showers; the yeti wears the permafrost; the seeker watches.',
       'Метеориперы падают с метеоритным дождём; йети носит мерзлоту; искатель наблюдает.'),
      ('Its tentacle becomes a spike - and a key to abyssal loot.',
       'Его щупальце становится шипальцем — и ключом к добыче Бездны.'),
  ],
  tasks=[
      kill("eternal_starlight:seeker", 1),
      kill("eternal_starlight:creteor", 1),
      kill("eternal_starlight:yeti", 1),
  ],
  rewards=[
      xpr(90),
  ]),

Q("q015", ('Permafrost and Stranghoul', 'Мерзлота и странгуль'), section="s2",
  deps=['q014'],
  icon="eternal_starlight:tenacious_vine",
  desc=[
      ('The permafrost spits from afar and hides under ashen snow.',
       'Мерзлотник плюётся издалека и прячется под пепельным снегом.'),
      ('The stranghoul hunts other mobs: witness a hunt - and hire the hunter.',
       'Странгуль охотится на других мобов: увидь охоту — и найми охотника.'),
  ],
  tasks=[
      kill("eternal_starlight:permafrost", 1),
      kill("eternal_starlight:stranghoul", 1),
  ],
  rewards=[
      xpr(90),
  ]),

Q("q016", ('A Tangled Death', 'Запутанная смерть'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:tenacious_vine",
  desc=[
      ('The tangled, its husk and skull: the tenacious vine does not let go even of the dead.',
       'Запутанный, кадавр и череп: цепкая лоза не отпускает даже мёртвых.'),
      ('The skull explodes - chain two kills for the mod achievement.',
       'Череп взрывается — сцепи два убийства ради достижения мода.'),
  ],
  tasks=[
      kill("eternal_starlight:tangled", 1),
      kill("eternal_starlight:tangled_husk", 1),
      kill("eternal_starlight:tangled_skull", 1),
  ],
  rewards=[
      xpr(80),
  ]),

Q("q017", ('The Gatekeeper', 'Привратник'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:starfire",
  size=1.7,
  desc=[
      ('First boss: the Gatekeeper tests the worthy with fireballs and fury.',
       'Первый босс: Привратник проверяет достойных огненными шарами и яростью.'),
      ('Pass his challenge - and take what he guards.',
       'Пройди испытание — и забери то, что он стережёт.'),
  ],
  tasks=[
      kill("eternal_starlight:the_gatekeeper", 1),
  ],
  rewards=[
      lvl(10),
      toast('Привратник пал. Врата открыты.'),
  ]),

Q("q018", ('The Lunar Monstrosity', 'Лунное чудовище'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:orb_of_prophecy",
  size=1.7,
  desc=[
      ('The second boss waits in the Abyss. Ignite it - only fire makes it vulnerable.',
       'Второй босс ждёт в Бездне. Подожги его — только огонь делает его уязвимым.'),
      ('Breath and thorns fly in arcs: keep distance, do not stand in the pools.',
       'Дыхание и шипы летят по дуге: держи дистанцию, не стой в лужах.'),
  ],
  tasks=[
      biome("eternal_starlight:the_abyss"),
      kill("eternal_starlight:lunar_monstrosity", 1),
  ],
  rewards=[
      lvl(12),
      toast('Лунное чудовище одолено. Через терни — к звёздам.'),
  ]),

Q("q019", ('Golems of Stone and Light', 'Големы камня и света'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:golem_steel_ingot",
  size=1.3,
  desc=[
      ('The grimstone golem is summoned with a carved lunar cactus on bricks.',
       'Мракокаменный голем призывается вырезанной лунной опунцией на кирпичах.'),
      ('The starlight golem is invulnerable while its energy block hums: deactivate or freeze it.',
       'Звездосветный неуязвим, пока гудит его энергоблок: обесточь или заморозь трубкой.'),
  ],
  tasks=[
      kill("eternal_starlight:grimstone_golem", 1),
      kill("eternal_starlight:starlight_golem", 1),
  ],
  rewards=[
      xpr(110),
  ]),

Q("q020", ('Golems of Sky and Aether', 'Големы неба и эфира'), section="s2",
  deps=['q009'],
  icon="eternal_starlight:golem_steel_ingot",
  size=1.3,
  desc=[
      ('The astral golem falls from the sky with the meteor shower.',
       'Астральный голем падает с небес вместе с метеоритным дождём.'),
      ('The aethersent one is summoned with a carved cactus on an aethersent block.',
       'Эфиросцентный призывается вырезанной опунцией на эфиросцентном блоке.'),
  ],
  tasks=[
      kill("eternal_starlight:astral_golem", 1),
      kill("eternal_starlight:aethersent_golem", 1),
  ],
  rewards=[
      xpr(110),
  ]),

# --- секция s3 ---
Q("q021", ('Six Tears of the Starlight', 'Шесть слёз Звездосветья'), section="s3",
  deps=['q020'],
  icon="eternal_starlight:glacite_shard",
  desc=[
      ('Glacite, thioquartz, dusted shard, malarite, starlit diamond and starfire.',
       'Леднит, тиокварц, запылённый осколок, маларит, звёздный алмаз и звездопал.'),
      ('Starfire is not mined: help the starfire birds nest - and they will share.',
       'Звездопал не добывают киркой: помоги птицам свить гнездо — и они поделятся.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_shard"),
      item("eternal_starlight:thioquartz_shard"),
      item("eternal_starlight:dusted_shard"),
      item("eternal_starlight:malarite"),
      item("eternal_starlight:starlit_diamond"),
      item("eternal_starlight:starfire"),
  ],
  rewards=[
      xpr(90),
  ]),

Q("q022", ('The Soft Materials', 'Мягкие материалы'), section="s3",
  deps=['q021'],
  icon="eternal_starlight:shivering_gel",
  desc=[
      ('Saltpetre, shivering gel, soul dew, crinoa, cactus gel and velvet moss.',
       'Селитра, дрожащий гель, роса душ, криноя, кактусовый гель и бархамох.'),
      ('Each is a reagent: bombs, stews and amulets all start here.',
       'Всё это реагенты: бомбы, каша и амулеты начинаются отсюда.'),
  ],
  tasks=[
      item("eternal_starlight:saltpeter_powder"),
      item("eternal_starlight:shivering_gel"),
      item("eternal_starlight:soul_dew"),
      item("eternal_starlight:crinoa_ball"),
      item("eternal_starlight:lunaris_cactus_gel"),
      item("eternal_starlight:velvetumoss_ball"),
  ],
  rewards=[
      xpr(80),
  ]),

Q("q023", ('Five Ingots', 'Пять слитков'), section="s3",
  deps=['q021'],
  icon="eternal_starlight:alloy_furnace",
  desc=[
      ('Glacite, deepsilver, unrealium, aethersent and golem steel: the metal ladder.',
       'Леднит, глубинное серебро, нереалий, эфиросцент и големосталь: лестница металлов.'),
      ('The alloy furnace smelts what a normal one cannot.',
       'Доменная печь переплавляет то, что обычная не берёт.'),
  ],
  tasks=[
      item("eternal_starlight:deepsilver_ingot"),
      item("eternal_starlight:unrealium_ingot"),
      item("eternal_starlight:aethersent_ingot"),
      item("eternal_starlight:golem_steel_ingot"),
  ],
  rewards=[
      xpr(100),
  ]),

Q("q024", ('Liquid Glow and Resin', 'Жидкое сияние и смола'), section="s3",
  deps=['q021'],
  icon="eternal_starlight:flowglaze",
  desc=[
      ('Throw starfire into sand - flowglaze. Hew torreya logs - amaramber.',
       'Брось звездопал в песок — глазутёк. Обтеши тисовые брёвна — амарянтарь.'),
      ('The crystalborn catalyst runs on crystals and redstone: a desertification machine.',
       'Кристаллический катализатор работает на кристаллах и редстоуне: машина опустынивания.'),
  ],
  tasks=[
      item("eternal_starlight:flowglaze"),
      item("eternal_starlight:raw_amaramber"),
      item("eternal_starlight:starcore"),
      item("eternal_starlight:crystalborn_catalyst"),
  ],
  rewards=[
      xpr(90),
  ]),

Q("q025", ('Veins of the Deep Rocks', 'Жилы глубинных пород'), section="s3",
  deps=['q021'],
  icon="eternal_starlight:voidstone_starlit_diamond_ore",
  desc=[
      ('Voidstone and nightfall mud hold the veins: silk touch keeps the block, fortune the count.',
       'Пустокамень и сумеречный саман хранят жилы: шёлковое касание хранит блок, удача — количество.'),
      ('This is the ore map of the dimension: the arsenal follows it.',
       'Это карта руд измерения: дальше по ней пойдёт арсенал.'),
  ],
  tasks=[
      item("eternal_starlight:voidstone_starlit_diamond_ore"),
      item("eternal_starlight:voidstone_malarite_ore"),
      item("eternal_starlight:voidstone_deepsilver_ore"),
      item("eternal_starlight:voidstone_starcore_ore"),
      item("eternal_starlight:voidstone_saltpeter_ore"),
      item("eternal_starlight:voidstone_redstone_ore"),
      item("eternal_starlight:packed_nightfall_mud_malarite_ore"),
      item("eternal_starlight:packed_nightfall_mud_deepsilver_ore"),
  ],
  rewards=[
      xpr(90),
  ]),

# --- секция s4 ---
Q("q026", ('Weapons: the thermal springstone set', 'Оружие: Меч из термального истокамня'), section="s4",
  deps=['q025'],
  icon="eternal_starlight:thermal_springstone_sword",
  desc=[
      ('Thermal springstone lies under giant plants: only fire burns them away.',
       'Термальный истокамень лежит под гигантскими растениями: их сжигает только огонь.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:thermal_springstone_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q027", ('Tools: the thermal springstone set', 'Инструмент: Кирка из термального истокамня'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:thermal_springstone_pickaxe",
  desc=[
      ('Thermal springstone lies under giant plants: only fire burns them away.',
       'Термальный истокамень лежит под гигантскими растениями: их сжигает только огонь.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:thermal_springstone_pickaxe"),
      item("eternal_starlight:thermal_springstone_axe"),
      item("eternal_starlight:thermal_springstone_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q028", ('Armour: the thermal springstone set', 'Броня: Шлем из термального истокамня'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:thermal_springstone_helmet",
  desc=[
      ('Thermal springstone lies under giant plants: only fire burns them away.',
       'Термальный истокамень лежит под гигантскими растениями: их сжигает только огонь.'),
      ('Four pieces, one glow: wear the whole set.',
       'Четыре части, одно сияние: носи весь сет.'),
  ],
  tasks=[
      item("eternal_starlight:thermal_springstone_helmet"),
      item("eternal_starlight:thermal_springstone_chestplate"),
      item("eternal_starlight:thermal_springstone_leggings"),
      item("eternal_starlight:thermal_springstone_boots"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q029", ('Weapons: the glacite set', 'Оружие: Леднитовый меч'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:glacite_sword",
  desc=[
      ('Glacite is forged from shards of the permafrost peaks.',
       'Леднит куют из осколков вершин вечной мерзлоты.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_sword"),
      item("eternal_starlight:glacite_shield"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q030", ('Tools: the glacite set', 'Инструмент: Леднитовая кирка'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:glacite_pickaxe",
  desc=[
      ('Glacite is forged from shards of the permafrost peaks.',
       'Леднит куют из осколков вершин вечной мерзлоты.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_pickaxe"),
      item("eternal_starlight:glacite_axe"),
      item("eternal_starlight:glacite_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q031", ('Armour: the glacite set', 'Броня: Леднитовый шлем'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:glacite_helmet",
  desc=[
      ('Glacite is forged from shards of the permafrost peaks.',
       'Леднит куют из осколков вершин вечной мерзлоты.'),
      ('Four pieces, one glow: wear the whole set.',
       'Четыре части, одно сияние: носи весь сет.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_helmet"),
      item("eternal_starlight:glacite_chestplate"),
      item("eternal_starlight:glacite_leggings"),
      item("eternal_starlight:glacite_boots"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q032", ('Weapons: the malarite set', 'Оружие: Маларитовый меч'), section="s4",
  deps=['q031'],
  icon="eternal_starlight:malarite_sword",
  desc=[
      ('Malarite is dug from night swamp mud; its spear outreaches a sword.',
       'Маларит добывают из грязи ночных болот; его копьё длиннее меча.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:malarite_sword"),
      item("eternal_starlight:malarite_spear"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q033", ('Tools: the malarite set', 'Инструмент: Маларитовая кирка'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:malarite_pickaxe",
  desc=[
      ('Malarite is dug from night swamp mud; its spear outreaches a sword.',
       'Маларит добывают из грязи ночных болот; его копьё длиннее меча.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:malarite_pickaxe"),
      item("eternal_starlight:malarite_axe"),
      item("eternal_starlight:malarite_sickle"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q034", ('Weapons: the deepsilver set', 'Оружие: Меч из глубинного серебра'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:deepsilver_sword",
  desc=[
      ('Deepsilver does not tarnish in the dusk: look in packed mud.',
       'Глубинное серебро не тускнеет в сумерках: ищи в самане.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:deepsilver_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q035", ('Tools: the deepsilver set', 'Инструмент: Кирка из глубинного серебра'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:deepsilver_pickaxe",
  desc=[
      ('Deepsilver does not tarnish in the dusk: look in packed mud.',
       'Глубинное серебро не тускнеет в сумерках: ищи в самане.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:deepsilver_pickaxe"),
      item("eternal_starlight:deepsilver_axe"),
      item("eternal_starlight:deepsilver_sickle"),
      item("eternal_starlight:deepsilver_brush"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q036", ('Armour: the deepsilver set', 'Броня: Шлем из глубинного серебра'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:deepsilver_helmet",
  desc=[
      ('Deepsilver does not tarnish in the dusk: look in packed mud.',
       'Глубинное серебро не тускнеет в сумерках: ищи в самане.'),
      ('Four pieces, one glow: wear the whole set.',
       'Четыре части, одно сияние: носи весь сет.'),
  ],
  tasks=[
      item("eternal_starlight:deepsilver_helmet"),
      item("eternal_starlight:deepsilver_chestplate"),
      item("eternal_starlight:deepsilver_leggings"),
      item("eternal_starlight:deepsilver_boots"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q037", ('Weapons: the starlit diamond set', 'Оружие: Меч из звёздного алмаза'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:starlit_diamond_sword",
  desc=[
      ('Starlit diamond is harder than diamond and glows faintly in the dark.',
       'Звёздный алмаз твёрже алмаза и слабо светится в темноте.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:starlit_diamond_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q038", ('Tools: the starlit diamond set', 'Инструмент: Кирка из звёздного алмаза'), section="s4",
  deps=['q037'],
  icon="eternal_starlight:starlit_diamond_pickaxe",
  desc=[
      ('Starlit diamond is harder than diamond and glows faintly in the dark.',
       'Звёздный алмаз твёрже алмаза и слабо светится в темноте.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:starlit_diamond_pickaxe"),
      item("eternal_starlight:starlit_diamond_axe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q039", ('Armour: the starlit diamond set', 'Броня: Шлем из звёздного алмаза'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:starlit_diamond_helmet",
  desc=[
      ('Starlit diamond is harder than diamond and glows faintly in the dark.',
       'Звёздный алмаз твёрже алмаза и слабо светится в темноте.'),
      ('Four pieces, one glow: wear the whole set.',
       'Четыре части, одно сияние: носи весь сет.'),
  ],
  tasks=[
      item("eternal_starlight:starlit_diamond_helmet"),
      item("eternal_starlight:starlit_diamond_chestplate"),
      item("eternal_starlight:starlit_diamond_leggings"),
      item("eternal_starlight:starlit_diamond_boots"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q040", ('Weapons: the unrealium set', 'Оружие: Нереалиевый меч'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:unrealium_sword",
  desc=[
      ('Unrealium is lighter than shadow: a full set is the mod achievement.',
       'Нереалий легче тени: полный сет — достижение мода.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:unrealium_sword"),
      item("eternal_starlight:unrealium_crossbow"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q041", ('Tools: the unrealium set', 'Инструмент: Нереалиевая кирка'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:unrealium_pickaxe",
  desc=[
      ('Unrealium is lighter than shadow: a full set is the mod achievement.',
       'Нереалий легче тени: полный сет — достижение мода.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:unrealium_pickaxe"),
      item("eternal_starlight:unrealium_axe"),
      item("eternal_starlight:unrealium_sickle"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q042", ('Armour: the unrealium set', 'Броня: Нереалиевый шлем'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:unrealium_helmet",
  desc=[
      ('Unrealium is lighter than shadow: a full set is the mod achievement.',
       'Нереалий легче тени: полный сет — достижение мода.'),
      ('Four pieces, one glow: wear the whole set.',
       'Четыре части, одно сияние: носи весь сет.'),
  ],
  tasks=[
      item("eternal_starlight:unrealium_helmet"),
      item("eternal_starlight:unrealium_chestplate"),
      item("eternal_starlight:unrealium_leggings"),
      item("eternal_starlight:unrealium_boots"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q043", ('Weapons: the starfire set', 'Оружие: Звездопальный меч'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:starfire_sword",
  desc=[
      ('Starfire gear burns with a cold flame the birds gave you.',
       'Снаряжение звездопала горит холодным пламенем, подаренным птицами.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:starfire_sword"),
      item("eternal_starlight:starfire_crossbow"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q044", ('Tools: the starfire set', 'Инструмент: Звездопальная кирка'), section="s4",
  deps=['q043'],
  icon="eternal_starlight:starfire_pickaxe",
  desc=[
      ('Starfire gear burns with a cold flame the birds gave you.',
       'Снаряжение звездопала горит холодным пламенем, подаренным птицами.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:starfire_pickaxe"),
      item("eternal_starlight:starfire_axe"),
      item("eternal_starlight:starfire_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q045", ('Weapons: the flowglaze set', 'Оружие: Глазутёковый меч'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:flowglaze_sword",
  desc=[
      ('Flowglaze flows where you strike: the sand remembers the starfire.',
       'Глазутёк течёт, куда ударишь: песок помнит звездопал.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:flowglaze_sword"),
      item("eternal_starlight:flowglaze_bow"),
      item("eternal_starlight:flowglaze_shield"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q046", ('Tools: the flowglaze set', 'Инструмент: Глазутёковая кирка'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:flowglaze_pickaxe",
  desc=[
      ('Flowglaze flows where you strike: the sand remembers the starfire.',
       'Глазутёк течёт, куда ударишь: песок помнит звездопал.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:flowglaze_pickaxe"),
      item("eternal_starlight:flowglaze_axe"),
      item("eternal_starlight:flowglaze_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q047", ('Weapons: the amaramber set', 'Оружие: Амарянтарный меч'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:amaramber_sword",
  desc=[
      ('Amaramber is the resin of torreya: warm, amber, stubborn.',
       'Амарянтарь — смола тиса: тёплая, янтарная, упрямая.'),
      ('Blades of this tier share one temper - and one upgrade path.',
       'Клинки этого тира одного характера — и одного пути улучшений.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q048", ('Tools: the amaramber set', 'Инструмент: Амарянтарная кирка'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:amaramber_pickaxe",
  desc=[
      ('Amaramber is the resin of torreya: warm, amber, stubborn.',
       'Амарянтарь — смола тиса: тёплая, янтарная, упрямая.'),
      ('Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.',
       'Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_pickaxe"),
      item("eternal_starlight:amaramber_axe"),
      item("eternal_starlight:amaramber_sickle"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q049", ('Armour: the amaramber set', 'Броня: amaramber'), section="s4",
  deps=['q026'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Amaramber is the resin of torreya: warm, amber, stubborn.',
       'Амарянтарь — смола тиса: тёплая, янтарная, упрямая.'),
      ('Four pieces, one glow: wear the whole set.',
       'Четыре части, одно сияние: носи весь сет.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_chestplate"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q050", ('Templates of Ascent', 'Шаблоны восхождения'), section="s4",
  deps=['q049'],
  icon="eternal_starlight:starfire_upgrade_smithing_template",
  desc=[
      ('The starfire template upgrades thermal gear; flowglaze upgrades glacite gear.',
       'Шаблон звездопала улучшает термальное снаряжение; глазутёка — леднитовое.'),
      ('The smithing table is the stair between tiers.',
       'Стол кузнеца — лестница между тирами.'),
  ],
  tasks=[
      item("eternal_starlight:starfire_upgrade_smithing_template"),
      item("eternal_starlight:flowglaze_upgrade_smithing_template"),
  ],
  rewards=[
      xpr(60),
  ]),

# --- секция s5 ---
Q("q051", ('Dagger of Hunger', 'Кинжал голода'), section="s5",
  deps=['q050'],
  icon="eternal_starlight:dagger_of_hunger",
  desc=[
      ('Feed it with strikes: the hungry dagger hits harder when fed.',
       'Корми его ударами: голодный кинжал бьёт сильнее.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:dagger_of_hunger"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q052", ('Shattered Sword', 'Расколотый меч'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:shattered_sword",
  desc=[
      ('Join blade and hilt: shattered does not mean dead.',
       'Собери лезвие и рукоять: расколотое — не значит мёртвое.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:shattered_sword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q053", ('Glistering Sword', 'Сверкающий меч'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:glistering_sword",
  desc=[
      ('It glisters where it strikes: first of the glistering family.',
       'Сверкает там, где бьёт: первый из семьи сверкающих.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_sword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q054", ('Glistering Greatsword', 'Большой сверкающий меч'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:glistering_greatsword",
  desc=[
      ('The two-handed glistering: wide swing, wide shine.',
       'Двуручный сверкающий: широкий замах, широкий блеск.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q055", ('Glistering Bow', 'Сверкающий лук'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:glistering_bow",
  desc=[
      ('Its arrows shine like tracers.',
       'Стрелы сверкающего лука светятся трассерами.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_bow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q056", ('Glistering Morning Star', 'Сверкающая денница'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:glistering_morning_star",
  desc=[
      ('The morning star: heavy, honest, toothy.',
       'Денница: тяжёлая, честная, зубастая.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_morning_star"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q057", ('Energy Sword', 'Энергомеч'), section="s5",
  deps=['q056'],
  icon="eternal_starlight:energy_sword",
  desc=[
      ('The energy sword: a blade of pure spark.',
       'Энергомеч: клинок из чистой вспышки.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:energy_sword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q058", ('Energy Boomerang', 'Энергетический бумеранг'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:energy_boomerang",
  desc=[
      ('It returns. Always. Keep your hand open.',
       'Возвращается. Всегда. Держи руку открытой.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:energy_boomerang"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q059", ('Golem Steel Greatsword', 'Големостальной двуручный меч'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:golem_steel_greatsword",
  desc=[
      ('Golem steel greatsword: slow as a golem, and as inevitable.',
       'Двуручник из големостали: медленный, как голем, и такой же неизбежный.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:golem_steel_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q060", ('Mechanical Crossbow', 'Механический арбалет'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:mechanical_crossbow",
  desc=[
      ('The mechanical crossbow: reloads itself, forgives a shaking hand.',
       'Механический арбалет: перезаряжается сам, прощает дрожащую руку.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:mechanical_crossbow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q061", ('Crystal Greatsword', 'Кристальный двуручный меч'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:crystal_greatsword",
  desc=[
      ('Crystal greatsword: a heavy shard of a constellation.',
       'Кристальный двуручный: тяжёлый осколок созвездия.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:crystal_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q062", ('Crystal Crossbow', 'Кристальный арбалет'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:crystal_crossbow",
  desc=[
      ('Crystal crossbow: hits with ice and light.',
       'Кристальный арбалет: бьёт лёдом и светом.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:crystal_crossbow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q063", ('Wilted Crossbow', 'Увядший арбалет'), section="s5",
  deps=['q062'],
  icon="eternal_starlight:wilted_crossbow",
  desc=[
      ('The wilted crossbow: garden poison in every bolt.',
       'Увядший арбалет: яд садов в каждом болте.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:wilted_crossbow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q064", ('Moonring Bow', 'Кольцелунный лук'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:moonring_bow",
  desc=[
      ('Moonring bow: the arrow arc mirrors the moon.',
       'Кольцелунный лук: дуга стрелы повторяет дугу луны.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:moonring_bow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q065", ('Moonring Greatsword', 'Большой кольцелунный меч'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:moonring_greatsword",
  desc=[
      ('The greater moonring: a lunar crescent in steel.',
       'Большой кольцелунный: серп луны в стали.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:moonring_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q066", ('Crescent Spear', 'Копьё полумесяца'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:crescent_spear",
  desc=[
      ('Crescent spear: reaches where a sword cannot.',
       'Копьё полумесяца: достаёт там, где меч не дотянется.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:crescent_spear"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q067", ('Gravity Pickaxe', 'Гравитационная кирка'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:gravity_pickaxe",
  desc=[
      ('Gravity pickaxe: ore pulls itself into your inventory.',
       'Гравитационная кирка: руда сама тянется в инвентарь.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:gravity_pickaxe"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q068", ('Bow of Blood', 'Кровавый лук'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:bow_of_blood",
  desc=[
      ("Bow of blood: drinks the enemy's life and shares with you.",
       'Кровавый лук: пьёт жизнь врага и делится с тобой.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:bow_of_blood"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q069", ('Coldsnap', 'Хладохлыст'), section="s5",
  deps=['q068'],
  icon="eternal_starlight:coldsnap",
  desc=[
      ('Coldsnap: a whip of eternal ice, frost instead of a wound.',
       'Хладохлыст: хлыст из вечного льда, мороз вместо раны.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:coldsnap"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q070", ('Candlash', 'Конфехлыст'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:candlash",
  desc=[
      ('Candlash: sweet to look at, bitter to hit.',
       'Конфехлыст: сладкий на вид, горький на удар.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:candlash"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q071", ('Underminer', 'Подкопщик'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:underminer",
  desc=[
      ('The underminer: digs the enemy from inside their armour.',
       'Подкопщик: копает врага изнутри доспеха.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:underminer"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q072", ('Flesh Grinder', 'Плотерубка'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:flesh_grinder",
  desc=[
      ('The flesh grinder: not for the faint of stomach.',
       'Плотерубка: не для слабых желудком.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:flesh_grinder"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q073", ('Bonemore', 'Костолом'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:bonemore",
  desc=[
      ('Bonemore: a shield in one hand, an argument in the other.',
       'Костолом: щит в одной руке, аргумент в другой.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:bonemore"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q074", ('Living Arm', 'Живая рука'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:living_arm",
  desc=[
      ('The living arm: a weapon that holds you, not the other way.',
       'Живая рука: оружие, которое держит тебя, а не наоборот.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:living_arm"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q075", ('Pungency Fruit Spear', 'Копьё из острого фрукта'), section="s5",
  deps=['q074'],
  icon="eternal_starlight:pungency_fruit_spear",
  desc=[
      ('Pungency fruit spear: numbness instead of a wound.',
       'Копьё из острого фрукта: онемение вместо раны.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:pungency_fruit_spear"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q076", ('Pungency Fruit Axe', 'Топор из острого фрукта'), section="s5",
  deps=['q051'],
  icon="eternal_starlight:pungency_fruit_axe",
  desc=[
      ('Pungency fruit axe: a salad weapon.',
       'Топор из острого фрукта: салатное оружие.'),
      ('One of the twenty-six unique blades of the Starlight.',
       'Один из двадцати шести уникальных клинков Звездосветья.'),
  ],
  tasks=[
      item("eternal_starlight:pungency_fruit_axe"),
  ],
  rewards=[
      xpr(35),
  ]),

# --- секция s6 ---
Q("q077", ('Glacite Arrow', 'Леднитовая стрела'), section="s6",
  deps=['q076'],
  icon="eternal_starlight:glacite_arrow",
  desc=[
      ('Glacite arrow: slows the target with frost.',
       'Леднитовая стрела: замедляет цель морозом.'),
      ('Fletch a bundle: the quiver quest is next.',
       'Наряди связку: впереди квест колчана.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q078", ('Malarite Arrow', 'Маларитовая стрела'), section="s6",
  deps=['q077'],
  icon="eternal_starlight:malarite_arrow",
  desc=[
      ('Malarite arrow: heavy and straightforward.',
       'Маларитовая стрела: тяжёлая, прямолинейная.'),
      ('Fletch a bundle: the quiver quest is next.',
       'Наряди связку: впереди квест колчана.'),
  ],
  tasks=[
      item("eternal_starlight:malarite_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q079", ('Amaramber Arrow', 'Амарянтарная стрела'), section="s6",
  deps=['q077'],
  icon="eternal_starlight:amaramber_arrow",
  desc=[
      ('Amaramber arrow: resin clings to the wound.',
       'Амарянтарная стрела: смола липнет к ране.'),
      ('Fletch a bundle: the quiver quest is next.',
       'Наряди связку: впереди квест колчана.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q080", ('Thioquartz Arrow', 'Тиокварцевая стрела'), section="s6",
  deps=['q077'],
  icon="eternal_starlight:thioquartz_arrow",
  desc=[
      ('Thioquartz arrow: sparks with sulphur.',
       'Тиокварцевая стрела: искрит серой.'),
      ('Fletch a bundle: the quiver quest is next.',
       'Наряди связку: впереди квест колчана.'),
  ],
  tasks=[
      item("eternal_starlight:thioquartz_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q081", ('Air Sac Arrow', 'Стрела из воздушного мешка'), section="s6",
  deps=['q077'],
  icon="eternal_starlight:air_sac_arrow",
  desc=[
      ('Air sac arrow: light flight, light damage.',
       'Стрела из воздушного мешка: лёгкий полёт, лёгкий урон.'),
      ('Fletch a bundle: the quiver quest is next.',
       'Наряди связку: впереди квест колчана.'),
  ],
  tasks=[
      item("eternal_starlight:air_sac_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q082", ('Voracious Arrow', 'Прожорливая стрела'), section="s6",
  deps=['q077'],
  icon="eternal_starlight:voracious_arrow",
  desc=[
      ('Voracious arrow: finishes what the bolt did not.',
       'Прожорливая стрела: доедает то, что не добил болт.'),
      ('Fletch a bundle: the quiver quest is next.',
       'Наряди связку: впереди квест колчана.'),
  ],
  tasks=[
      item("eternal_starlight:voracious_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q083", ('Aethersent Arrow', 'Эфиросцентная стрела'), section="s6",
  deps=['q082'],
  icon="eternal_starlight:aethersent_arrow",
  desc=[
      ('Aethersent arrow: glows in flight - a lantern of the night.',
       'Эфиросцентная стрела: светится в полёте — фонарь ночи.'),
      ('Fletch a bundle: the quiver quest is next.',
       'Наряди связку: впереди квест колчана.'),
  ],
  tasks=[
      item("eternal_starlight:aethersent_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q084", ('The Galactic Quiver', 'Галактический колчан'), section="s6",
  deps=['q077'],
  icon="eternal_starlight:galactic_quiver",
  size=1.4,
  desc=[
      ('All seven arrow kinds, four of each, in one quiver.',
       'Все семь видов стрел по четыре штуки в одном колчане.'),
      ('The galactic quiver keeps them sorted even in the dark.',
       'Галактический колчан держит их по полочкам даже в темноте.'),
  ],
  tasks=[
      item("eternal_starlight:galactic_quiver"),
      item("eternal_starlight:glacite_arrow", 4),
      item("eternal_starlight:malarite_arrow", 4),
      item("eternal_starlight:amaramber_arrow", 4),
      item("eternal_starlight:thioquartz_arrow", 4),
      item("eternal_starlight:air_sac_arrow", 4),
      item("eternal_starlight:voracious_arrow", 4),
      item("eternal_starlight:aethersent_arrow", 4),
  ],
  rewards=[
      xpr(120),
      toast('Колчан полон: все семь стрел Звездосветья.'),
  ]),

# --- секция s7 ---
Q("q085", ('The Aethersent Raiment', 'Эфиросцентное облачение'), section="s7",
  deps=['q084'],
  icon="eternal_starlight:aethersent_hood",
  size=1.2,
  desc=[
      ('Hood, cape, bottoms and boots of aethersent: the sky-weave set.',
       'Капюшон, накидка, штаны и сапоги из эфиросцента: набор небесного плетения.'),
      ('It fell from the sky with the meteors - weave it back.',
       'Он упал с небес с метеорами — сплети его заново.'),
  ],
  tasks=[
      item("eternal_starlight:aethersent_hood"),
      item("eternal_starlight:aethersent_cape"),
      item("eternal_starlight:aethersent_bottoms"),
      item("eternal_starlight:aethersent_boots"),
  ],
  rewards=[
      xpr(80),
  ]),

Q("q086", ('Mask, Robe, Boots', 'Маска, одеяние, ботинки'), section="s7",
  deps=['q085'],
  icon="eternal_starlight:alchemist_mask",
  desc=[
      ('The alchemist set breathes where nothing breathes; air sac boots soften falls.',
       'Набор алхимика дышит там, где не дышит ничто; ботинки из воздушного мешка гасят падение.'),
      ('The Abyss becomes a little kinder with them.',
       'С ними Бездна чуть добрее.'),
  ],
  tasks=[
      item("eternal_starlight:alchemist_mask"),
      item("eternal_starlight:alchemist_robe"),
      item("eternal_starlight:air_sac_boots"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q087", ('Four Trim Patterns', 'Четыре узора отделки'), section="s7",
  deps=['q085'],
  icon="eternal_starlight:keeper_armor_trim_smithing_template",
  desc=[
      ('Keeper, forge, blooming and twining: four patterns for the smithing table.',
       'Привратник, кузница, цвет и плетение: четыре узора для стола кузнеца.'),
      ("Trim is the armour's final flourish.",
       'Отделка — последний штрих доспеха.'),
  ],
  tasks=[
      item("eternal_starlight:keeper_armor_trim_smithing_template"),
      item("eternal_starlight:forge_armor_trim_smithing_template"),
      item("eternal_starlight:blooming_armor_trim_smithing_template"),
      item("eternal_starlight:twining_armor_trim_smithing_template"),
  ],
  rewards=[
      xpr(60),
  ]),

# --- секция s8 ---
Q("q088", ('Berries and Fruits', 'Ягоды и плоды'), section="s8",
  deps=['q087'],
  icon="eternal_starlight:lunar_berries",
  desc=[
      ('Starlight cooking: everything edible and everything from here.',
       'Звёздная кухня: всё съедобное и всё отсюда.'),
      ('Spicy fruit gives numbness - it absorbs damage for you.',
       'Острый фрукт даёт онемение — оно поглощает урон за тебя.'),
  ],
  tasks=[
      item("eternal_starlight:lunar_berries"),
      item("eternal_starlight:pungency_fruit"),
      item("eternal_starlight:silver_pungency_fruit"),
      item("eternal_starlight:crinoa"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q089", ('Grains and Porridges', 'Злаки и каши'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:nocturnal_millet",
  desc=[
      ('Starlight cooking: everything edible and everything from here.',
       'Звёздная кухня: всё съедобное и всё отсюда.'),
      ('Spicy fruit gives numbness - it absorbs damage for you.',
       'Острый фрукт даёт онемение — оно поглощает урон за тебя.'),
  ],
  tasks=[
      item("eternal_starlight:nocturnal_millet"),
      item("eternal_starlight:forgotten_nocturnal_millet"),
      item("eternal_starlight:roasted_forgotten_nocturnal_millet"),
      item("eternal_starlight:crinoa_porridge"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q090", ('Meat and Fish', 'Мясо и рыба'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:rookfish",
  desc=[
      ('Starlight cooking: everything edible and everything from here.',
       'Звёздная кухня: всё съедобное и всё отсюда.'),
      ('Spicy fruit gives numbness - it absorbs damage for you.',
       'Острый фрукт даёт онемение — оно поглощает урон за тебя.'),
  ],
  tasks=[
      item("eternal_starlight:rookfish"),
      item("eternal_starlight:rookfish_skewer"),
      item("eternal_starlight:rotten_flesh_jerky"),
      item("eternal_starlight:rotten_ham"),
      item("eternal_starlight:shadow_escargot"),
      item("eternal_starlight:starfire_bird_egg"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q091", ('Hot and Hearty', 'Горячее и сытное'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:bouldershroom_stew",
  desc=[
      ('Starlight cooking: everything edible and everything from here.',
       'Звёздная кухня: всё съедобное и всё отсюда.'),
      ('Spicy fruit gives numbness - it absorbs damage for you.',
       'Острый фрукт даёт онемение — оно поглощает урон за тебя.'),
  ],
  tasks=[
      item("eternal_starlight:bouldershroom_stew"),
      item("eternal_starlight:jinglestem_sandwich"),
      item("eternal_starlight:jinglestem_crisp"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q092", ('Amulets', 'Амулеты'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:butterfly_wings_amulet",
  desc=[
      ('Pocket miracles of the Starlight: each has a use, none is ballast.',
       'Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.'),
      ('The aetherstrike rocket calls a meteor shower - make a wish.',
       'Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.'),
  ],
  tasks=[
      item("eternal_starlight:butterfly_wings_amulet"),
      item("eternal_starlight:fungus_amulet"),
      item("eternal_starlight:crescent_pendant"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q093", ('Warrior Pendants', 'Подвески воина'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:battleaxe_pendant",
  desc=[
      ('Pocket miracles of the Starlight: each has a use, none is ballast.',
       'Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.'),
      ('The aetherstrike rocket calls a meteor shower - make a wish.',
       'Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.'),
  ],
  tasks=[
      item("eternal_starlight:battleaxe_pendant"),
      item("eternal_starlight:warhammer_pendant"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q094", ('Curios of the Abyss', 'Диковины Бездны'), section="s8",
  deps=['q093'],
  icon="eternal_starlight:chain_of_souls",
  desc=[
      ('Pocket miracles of the Starlight: each has a use, none is ballast.',
       'Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.'),
      ('The aetherstrike rocket calls a meteor shower - make a wish.',
       'Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.'),
  ],
  tasks=[
      item("eternal_starlight:chain_of_souls"),
      item("eternal_starlight:soulit_spectator"),
      item("eternal_starlight:orb_of_prophecy"),
      item("eternal_starlight:blossom_of_stars"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q095", ("Explorer's Pocket", 'Карман исследователя'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:book",
  desc=[
      ('Pocket miracles of the Starlight: each has a use, none is ballast.',
       'Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.'),
      ('The aetherstrike rocket calls a meteor shower - make a wish.',
       'Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.'),
  ],
  tasks=[
      item("eternal_starlight:book"),
      item("eternal_starlight:starlit_painting"),
      item("eternal_starlight:starlight_silver_coin"),
      item("eternal_starlight:seeking_eye"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q096", ('Bombs and Projectiles', 'Бомбы и снаряды'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:sonar_bomb",
  desc=[
      ('Pocket miracles of the Starlight: each has a use, none is ballast.',
       'Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.'),
      ('The aetherstrike rocket calls a meteor shower - make a wish.',
       'Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.'),
  ],
  tasks=[
      item("eternal_starlight:sonar_bomb"),
      item("eternal_starlight:tear_bomb"),
      item("eternal_starlight:frozen_bomb"),
      item("eternal_starlight:frozen_tube"),
      item("eternal_starlight:ashen_snowball"),
      item("eternal_starlight:aetherstrike_rocket"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q097", ('Small Things of the Night', 'Мелочи ночи'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:saltpeter_matchbox",
  desc=[
      ('Pocket miracles of the Starlight: each has a use, none is ballast.',
       'Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.'),
      ('The aetherstrike rocket calls a meteor shower - make a wish.',
       'Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.'),
  ],
  tasks=[
      item("eternal_starlight:saltpeter_matchbox"),
      item("eternal_starlight:tenacious_vine"),
      item("eternal_starlight:shadow_snail_shell"),
      item("eternal_starlight:shadow_snail_shell_powder"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q098", ('Discs by Depus', 'Пластинки: Depus'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:music_disc_deep_blue",
  desc=[
      ('8 disc(s) by Depus, hidden in structure chests and boss pockets.',
       '8 пластинки автора Depus: спрятаны в сундуках структур и карманах боссов.'),
      ('A jukebox in your overworld home is the best way to remember the stars.',
       'Проигрыватель в земном доме — лучший способ вспомнить звёзды.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_deep_blue"),
      item("eternal_starlight:music_disc_fake_light"),
      item("eternal_starlight:music_disc_les_iles_du_ciel"),
      item("eternal_starlight:music_disc_nest_ii"),
      item("eternal_starlight:music_disc_optimized_option"),
      item("eternal_starlight:music_disc_solaris"),
      item("eternal_starlight:music_disc_the_dark_side"),
      item("eternal_starlight:music_disc_viridescent"),
  ],
  rewards=[
      xpr(110),
  ]),

Q("q099", ('Discs by Strantran', 'Пластинки: Strantran'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:music_disc_stars_shining_upon_the_sea",
  desc=[
      ('1 disc(s) by Strantran, hidden in structure chests and boss pockets.',
       '1 пластинки автора Strantran: спрятаны в сундуках структур и карманах боссов.'),
      ('A jukebox in your overworld home is the best way to remember the stars.',
       'Проигрыватель в земном доме — лучший способ вспомнить звёзды.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_stars_shining_upon_the_sea"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q100", ('Discs by TohokuAlpha', 'Пластинки: TohokuAlpha'), section="s8",
  deps=['q099'],
  icon="eternal_starlight:music_disc_ether_rain",
  desc=[
      ('3 disc(s) by TohokuAlpha, hidden in structure chests and boss pockets.',
       '3 пластинки автора TohokuAlpha: спрятаны в сундуках структур и карманах боссов.'),
      ('A jukebox in your overworld home is the best way to remember the stars.',
       'Проигрыватель в земном доме — лучший способ вспомнить звёзды.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_ether_rain"),
      item("eternal_starlight:music_disc_tranquility"),
      item("eternal_starlight:music_disc_tranquility_ii"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q101", ('Discs by Бинке', 'Пластинки: Бинке'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:music_disc_brisk",
  desc=[
      ('6 disc(s) by Бинке, hidden in structure chests and boss pockets.',
       '6 пластинки автора Бинке: спрятаны в сундуках структур и карманах боссов.'),
      ('A jukebox in your overworld home is the best way to remember the stars.',
       'Проигрыватель в земном доме — лучший способ вспомнить звёзды.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_brisk"),
      item("eternal_starlight:music_disc_moonlight"),
      item("eternal_starlight:music_disc_nest"),
      item("eternal_starlight:music_disc_profundity"),
      item("eternal_starlight:music_disc_sacred_desert"),
      item("eternal_starlight:music_disc_spirit"),
  ],
  rewards=[
      xpr(90),
  ]),

Q("q102", ('Discs by Депус', 'Пластинки: Депус'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:music_disc_mechanical_fossil",
  desc=[
      ('2 disc(s) by Депус, hidden in structure chests and boss pockets.',
       '2 пластинки автора Депус: спрятаны в сундуках структур и карманах боссов.'),
      ('A jukebox in your overworld home is the best way to remember the stars.',
       'Проигрыватель в земном доме — лучший способ вспомнить звёзды.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_mechanical_fossil"),
      item("eternal_starlight:music_disc_wailing_well"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q103", ('Discs by КрЛайт', 'Пластинки: КрЛайт'), section="s8",
  deps=['q088'],
  icon="eternal_starlight:music_disc_dusk_o_ereyesterday",
  desc=[
      ('4 disc(s) by КрЛайт, hidden in structure chests and boss pockets.',
       '4 пластинки автора КрЛайт: спрятаны в сундуках структур и карманах боссов.'),
      ('A jukebox in your overworld home is the best way to remember the stars.',
       'Проигрыватель в земном доме — лучший способ вспомнить звёзды.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_dusk_o_ereyesterday"),
      item("eternal_starlight:music_disc_posterity"),
      item("eternal_starlight:music_disc_the_thorny_reign"),
      item("eternal_starlight:music_disc_whisper_of_the_stars"),
  ],
  rewards=[
      xpr(70),
  ]),

# --- секция s9 ---
Q("q104", ('Light of the Night', 'Свет ночи'), section="s9",
  deps=['q020', 'q050', 'q084', 'q103'],
  icon="eternal_starlight:red_starlight_crystal_lantern",
  desc=[
      ('Decorative pearls of the dimension: crystal lanterns in four colours, star cores and dusk light.',
       'Декоративные жемчужины измерения: кристальные фонари четырёх цветов, звёздные ядра и сумеречный свет.'),
      ('Building blocks are not content, but these lights are too good to leave unspoken.',
       'Строительные блоки — не контент, но эти огни слишком хороши, чтобы молчать о них.'),
  ],
  tasks=[
      item("eternal_starlight:red_starlight_crystal_lantern"),
      item("eternal_starlight:blue_starlight_crystal_lantern"),
      item("eternal_starlight:starcore_light"),
      item("eternal_starlight:orbflora_light"),
      item("eternal_starlight:reinforced_dusk_light"),
      item("eternal_starlight:dusk_light"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q105", ('Flowers With No Home', 'Цветы, которых нет дома'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:sacred_starlight_flower",
  desc=[
      ('Floristic pearls: sacred starlight flower, whisperbloom, fire orchid, sea rosa.',
       'Флористические жемчужины: священный звездоцвет, шептоцвет, огненная орхидея, морская роза.'),
      ('Each flower grows only in its biome - a mini-expedition apiece.',
       'Каждый цветок растёт только в своём биоме — это мини-экспедиция.'),
  ],
  tasks=[
      item("eternal_starlight:sacred_starlight_flower"),
      item("eternal_starlight:starlight_flower"),
      item("eternal_starlight:whisperbloom"),
      item("eternal_starlight:fire_orchid"),
      item("eternal_starlight:sea_rosa"),
      item("eternal_starlight:orbflora"),
      item("eternal_starlight:starlight_torchflower"),
      item("eternal_starlight:starlit_lily_pad"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q106", ('Furs and Aviaries', 'Меха и вольеры'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:white_yeti_fur",
  desc=[
      ('Six yeti furs and starfire bird aviaries: a warm floor and a living starfire farm.',
       'Шесть мехов йети и вольеры птиц-звездопалов: тёплый пол и живой завод звездопала.'),
      ('An aviary with seeds inside breeds the birds - that is how starfire renews.',
       'Вольер с семенами внутри размножает птиц — так звездопал возобновляется.'),
  ],
  tasks=[
      item("eternal_starlight:white_yeti_fur"),
      item("eternal_starlight:orange_yeti_fur"),
      item("eternal_starlight:pink_yeti_fur"),
      item("eternal_starlight:purple_yeti_fur"),
      item("eternal_starlight:red_yeti_fur"),
      item("eternal_starlight:yellow_yeti_fur"),
      item("eternal_starlight:starfire_bird_nest"),
      item("eternal_starlight:oak_starfire_bird_aviary"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q107", ('Northern Flotilla', 'Флотилия севера'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:lunar_boat",
  size=1.2,
  desc=[
      ('Lunar, northland and banyin boats with their cargo variants.',
       'Лунные, северные и баньяновые лодки с грузовыми вариантами.'),
      ('The starlit sea is faster to cross than to walk around.',
       'Звёздное море быстрее переплыть, чем обойти.'),
  ],
  tasks=[
      item("eternal_starlight:lunar_boat"),
      item("eternal_starlight:lunar_chest_boat"),
      item("eternal_starlight:northland_boat"),
      item("eternal_starlight:northland_chest_boat"),
      item("eternal_starlight:banyin_boat"),
      item("eternal_starlight:banyin_chest_boat"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q108", ('Southern Flotilla', 'Флотилия юга'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:scarlet_boat",
  size=1.2,
  desc=[
      ('Scarlet, torreya, jinglestem rafts and cradlewood boats: the whole fleet.',
       'Алые, тисовые, звоноствольные плоты и колыбельниковые лодки: весь флот.'),
      ('Jinglestem rings in the wind - music on the road.',
       'Звоноствол звенит на ветру — музыка в дороге.'),
  ],
  tasks=[
      item("eternal_starlight:scarlet_boat"),
      item("eternal_starlight:scarlet_chest_boat"),
      item("eternal_starlight:torreya_boat"),
      item("eternal_starlight:torreya_chest_boat"),
      item("eternal_starlight:jinglestem_raft"),
      item("eternal_starlight:jinglestem_chest_raft"),
      item("eternal_starlight:cradlewood_boat"),
      item("eternal_starlight:cradlewood_chest_boat"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q109", ('Encyclopaedia Tail', 'Хвост энциклопедии'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:abyssal_fruit",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:abyssal_fruit"),
      item("eternal_starlight:aethersent_nugget"),
      item("eternal_starlight:air_sac_mask"),
      item("eternal_starlight:amaramber_hoe"),
      item("eternal_starlight:amaramber_ingot"),
      item("eternal_starlight:amaramber_mask"),
      item("eternal_starlight:amaramber_nugget"),
      item("eternal_starlight:amaramber_shovel"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q110", ('Encyclopaedia Tail · 2', 'Хвост энциклопедии · 2'), section="s9",
  deps=['q109'],
  icon="eternal_starlight:aurora_deer_antler",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:aurora_deer_antler"),
      item("eternal_starlight:aurora_deer_steak"),
      item("eternal_starlight:blue_starlight_crystal_shard"),
      item("eternal_starlight:broken_doomeden_bone"),
      item("eternal_starlight:cinder_brick"),
      item("eternal_starlight:cooked_aurora_deer_steak"),
      item("eternal_starlight:cooked_luminaris"),
      item("eternal_starlight:cooked_luminofish"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q111", ('Encyclopaedia Tail · 3', 'Хвост энциклопедии · 3'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:cooked_ratlin_meat",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:cooked_ratlin_meat"),
      item("eternal_starlight:cooked_rookfish"),
      item("eternal_starlight:cooked_shadow_snail_meat"),
      item("eternal_starlight:creteor_hide"),
      item("eternal_starlight:crinoa_seeds"),
      item("eternal_starlight:deepsilver_hoe"),
      item("eternal_starlight:deepsilver_nugget"),
      item("eternal_starlight:deepsilver_shovel"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q112", ('Encyclopaedia Tail · 4', 'Хвост энциклопедии · 4'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:doomeden_carrion",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:doomeden_carrion"),
      item("eternal_starlight:doomeden_rag"),
      item("eternal_starlight:doomeden_rapier"),
      item("eternal_starlight:ether_bucket"),
      item("eternal_starlight:etheric_eye"),
      item("eternal_starlight:eye_of_doom"),
      item("eternal_starlight:flare_brick"),
      item("eternal_starlight:flowglaze_hoe"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q113", ('Encyclopaedia Tail · 5', 'Хвост энциклопедии · 5'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:flowglaze_shovel",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:flowglaze_shovel"),
      item("eternal_starlight:glacite_hoe"),
      item("eternal_starlight:glacite_shovel"),
      item("eternal_starlight:gleech_egg"),
      item("eternal_starlight:golem_steel_nugget"),
      item("eternal_starlight:loot_bag"),
      item("eternal_starlight:luminaris"),
      item("eternal_starlight:luminaris_bucket"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q114", ('Encyclopaedia Tail · 6', 'Хвост энциклопедии · 6'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:luminofish",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:luminofish"),
      item("eternal_starlight:luminofish_bucket"),
      item("eternal_starlight:lunaris_cactus_fruit"),
      item("eternal_starlight:malarite_hoe"),
      item("eternal_starlight:malarite_shovel"),
      item("eternal_starlight:nightfall_spider_eye"),
      item("eternal_starlight:nocturnal_millet_seeds"),
      item("eternal_starlight:oxidized_golem_steel_ingot"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q115", ('Encyclopaedia Tail · 7', 'Хвост энциклопедии · 7'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:oxidized_golem_steel_nugget",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:oxidized_golem_steel_nugget"),
      item("eternal_starlight:pearl_necklace"),
      item("eternal_starlight:petal_scythe"),
      item("eternal_starlight:popped_nocturnal_millet_bucket"),
      item("eternal_starlight:pungency_fruit_seeds"),
      item("eternal_starlight:pungency_fruit_upgrade_smithing_template"),
      item("eternal_starlight:pungency_stew"),
      item("eternal_starlight:rage_of_stars"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q116", ('Encyclopaedia Tail · 8', 'Хвост энциклопедии · 8'), section="s9",
  deps=['q115'],
  icon="eternal_starlight:ratlin_meat",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:ratlin_meat"),
      item("eternal_starlight:raw_aethersent"),
      item("eternal_starlight:raw_deepsilver"),
      item("eternal_starlight:red_starlight_crystal_shard"),
      item("eternal_starlight:rookfish_air_sac"),
      item("eternal_starlight:rookfish_bucket"),
      item("eternal_starlight:seeds_launcher"),
      item("eternal_starlight:seeker_tentacle"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q117", ('Encyclopaedia Tail · 9', 'Хвост энциклопедии · 9'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:shadow_snail_meat",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:shadow_snail_meat"),
      item("eternal_starlight:shadow_snail_pie"),
      item("eternal_starlight:shattered_sword_blade"),
      item("eternal_starlight:starfall_longbow"),
      item("eternal_starlight:starfire_hammer"),
      item("eternal_starlight:starfire_hoe"),
      item("eternal_starlight:starfire_shovel"),
      item("eternal_starlight:starlit_diamond_hoe"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q118", ('Encyclopaedia Tail · 10', 'Хвост энциклопедии · 10'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:starlit_diamond_shovel",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:starlit_diamond_shovel"),
      item("eternal_starlight:tear_bomb_minecart"),
      item("eternal_starlight:tenacious_petal"),
      item("eternal_starlight:tentacle_spike"),
      item("eternal_starlight:thermal_springstone_hammer"),
      item("eternal_starlight:thermal_springstone_hoe"),
      item("eternal_starlight:thermal_springstone_ingot"),
      item("eternal_starlight:thermal_springstone_shovel"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q119", ('Encyclopaedia Tail · 11', 'Хвост энциклопедии · 11'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:tooth_of_hunger",
  desc=[
      ('Small things the sections above did not name: every thing of the mod is counted.',
       'Мелочи, которые не назвали секции выше: каждая вещь мода учтена.'),
      ('Hand them in - and no blank stripes remain in the book.',
       'Сдай их — и в книге не останется белых полос.'),
  ],
  tasks=[
      item("eternal_starlight:tooth_of_hunger"),
      item("eternal_starlight:unrealium_hoe"),
      item("eternal_starlight:unrealium_nugget"),
      item("eternal_starlight:unrealium_shovel"),
      item("eternal_starlight:wand_of_teleportation"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q120", ('The Star Encyclopaedia', 'Звёздная энциклопедия'), section="s9",
  deps=['q104'],
  icon="eternal_starlight:blossom_of_stars",
  size=1.8,
  desc=[
      ('The chapter capstone: bosses felled, biomes walked, blades in hand, quiver full.',
       'Замковый камень главы: боссы пали, биомы исхожены, клинки в руках, колчан полон.'),
      ('A blossom of stars in hand - the signature of a traveller between stars.',
       'Звездоцвет в руке — подпись путешественника между звёзд.'),
  ],
  tasks=[
      item("eternal_starlight:blossom_of_stars"),
  ],
  rewards=[
      lvl(30),
      give(CUSTOM["premium"]),
      toast('Вечное Звездосветье познано: оружие, звери, биомы и боссы — всё твоё.'),
  ]),

]

CHAPTER = {
    "id": 0xC005, "filename": "starlight",
    "layout": "blocks", "cols": 2, "dx": 2.1, "dy": 1.45,
    "pad_x": 4.5, "pad_y": 6.5,
    "shape": "hexagon", "icon": "eternal_starlight:orb_of_prophecy",
    "banner": "banner_starlight", "banner_w": 13.0, "banner_h": 3.25,
    "banner_gap": 2.9,
    "title": ("The Eternal Starlight", "Вечное Звездосветье"),
    "subtitle": [
        ("The Eternal Starlight mod: the Starlight dimension, 24 biomes, "
         "8 structures, two bosses, nine gear tiers and over a thousand blocks "
         "and items.",
         "Мод Eternal Starlight: измерение Вечного Звездосветья, 24 биома, "
         "8 структур, два босса, девять тиров снаряжения и больше тысячи "
         "блоков и предметов."),
        ("Small quests, one step each: the whole mod is covered, not a single "
         "item is lost.",
         "Маленькие квесты по одному шагу: покрыт весь мод, ни один предмет "
         "не потерян."),
    ],
    "sections": SECTIONS,
    "quests": QUESTS,
    "images": [
        {
            "at": 'q001', "dx": 0.0, "dy": -1.5,
            "w": 6.4, "h": 0.8, "image": 'kubejs:textures/gui/plate.png',
            "color": 0x2B4C7E, "alpha": 225, "order": -35,
            "lock": True, "text": True,
            "text_shadow": True, "text_inset": 8,
            "title": ('The orb opens in your hands', 'Сфера открывается в руках'),
        },
        {
            "at": 'q008', "dx": 0.0, "dy": -1.4,
            "w": 5.6, "h": 0.8, "image": 'kubejs:textures/gui/plate.png',
            "color": 0x6A4C93, "alpha": 225, "order": -35,
            "lock": True, "text": True,
            "text_shadow": True, "text_inset": 8,
            "title": ('A bowl of stew = a day of service', 'Миска рагу = день службы'),
        },
        {
            "at": 'q009', "dx": 0.0, "dy": 0.0,
            "w": 2.6, "h": 2.6, "image": 'kubejs:textures/gui/halo.png',
            "color": 0xFFD75E, "alpha": 120, "order": -30,
            "lock": True, "text": False,
            "text_shadow": True, "text_inset": 8,
        },
        {
            "at": 'q009', "dx": 0.0, "dy": -1.6,
            "w": 5.2, "h": 0.8, "image": 'kubejs:textures/gui/plate.png',
            "color": 0x2A0E14, "alpha": 225, "order": -35,
            "lock": True, "text": True,
            "text_shadow": True, "text_inset": 8,
            "title": ('It is a trial, not a brawl', 'Это испытание, не драка'),
        },
        {
            "at": 'q010', "dx": 0.0, "dy": 0.0,
            "w": 2.6, "h": 2.6, "image": 'kubejs:textures/gui/halo.png',
            "color": 0x9A5AC7, "alpha": 120, "order": -30,
            "lock": True, "text": False,
            "text_shadow": True, "text_inset": 8,
        },
        {
            "at": 'q010', "dx": 0.0, "dy": -1.6,
            "w": 5.2, "h": 0.8, "image": 'kubejs:textures/gui/plate.png',
            "color": 0x2A0E14, "alpha": 225, "order": -35,
            "lock": True, "text": True,
            "text_shadow": True, "text_inset": 8,
            "title": ('Ignite it - else immortal', 'Подожги — иначе бессмертен'),
        },
        {
            "at": 'q011', "dx": 0.0, "dy": -1.5,
            "w": 5.6, "h": 0.8, "image": 'kubejs:textures/gui/plate.png',
            "color": 0x1F7A70, "alpha": 225, "order": -35,
            "lock": True, "text": True,
            "text_shadow": True, "text_inset": 8,
            "title": ('Deactivate the energy block first', 'Сначала обесточь энергоблок'),
        },
        {
            "at": 'q120', "dx": 0.0, "dy": 0.0,
            "w": 2.6, "h": 2.6, "image": 'kubejs:textures/gui/halo.png',
            "color": 0xFFD75E, "alpha": 120, "order": -30,
            "lock": True, "text": False,
            "text_shadow": True, "text_inset": 8,
        },
    ],
    "links": [],
}
