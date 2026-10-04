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
CLR_S5 = 0x7A1F4C
CLR_S6 = 0x556B2F

SECTIONS = [
    SEC("s1", ('The Road to the Starlight', 'Дорога в Звездосветье'), CLR_S1),
    SEC("s2", ('The Bestiary', 'Бестиарий'), CLR_S2),
    SEC("s3", ('Ores and Materials', 'Руды и материалы'), CLR_S3),
    SEC("s4", ('The Arsenal', 'Арсенал'), CLR_S4),
    SEC("s5", ('Table and Pocket', 'Стол и карман'), CLR_S5),
    SEC("s6", ('Building', 'Строительство'), CLR_S6),
]

QUESTS = [
# --- секция s1 ---
Q("q001", ('A Sky of a Million Stars', 'Небо миллиона звёзд'), section="s1",
  icon="eternal_starlight:orb_of_prophecy",
  size=1.6,
  desc=[
      ('Eternal Starlight открывает измерение Звездосветья: ночь, сияния и 24 биома.',
       'Eternal Starlight opens the Starlight dimension: night, auroras and 24 biomes.'),
      ('Портал не строят из блоков — его открывает сфера пророчества.',
       'The portal is not built from blocks - it is opened by the orb of prophecy.'),
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
      ('Обычные, холодные, пустынные, лесные и тропические руины порталов: сундуки с осколками.',
       'Common, cold, desert, forest and jungle portal ruins: chests with dusted shards.'),
      ('Кто-то открыл врата до тебя — и не вернулся.',
       'Someone opened the gates before you - and did not come back.'),
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
      ('Шесть лесных биомов: от редкой тайги до густого полога и тисовых рощ.',
       'Six forest biomes: from sparse taiga to dense canopies and torreya thickets.'),
      ('Компас крутится: ориентируйся по сиянию кристаллов.',
       'The compass spins: navigate by the glow of crystals.'),
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
      ('Звёздные моря, ламинарии, тёплые и мрачные берега: вода здесь светится ночью.',
       'Starlit seas, kelp forests, warm and grim shores: the water here glows at night.'),
      ('Лодка — не роскошь, а единственный путь.',
       'A boat is not a luxury but the only way across.'),
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
      ('Солнечные острова, мицелиевые островки, тенистые равнины и мерцающие кустарники.',
       'Solaris isles, mycelium isles, umbral plains and shimmering scrublands.'),
      ('Каждый остров прячет свою флору — и свою опасность.',
       'Each isle hides its own flora - and its own dangers.'),
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
      ('Вершины мерзлоты, кристаллизованная пустыня и Бездна: темнейший биом.',
       'Permafrost peaks, crystallized desert and the Abyss: the darkest biome of all.'),
      ('В Бездне живёт то, ради чего стоило дойти до конца.',
       'In the Abyss lives the reason this chapter is worth finishing.'),
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
      ('В кузнице рождаются звездосветные големы; в саду ничего не цветёт дважды.',
       'The forge is where starlight golems are born; the garden is where nothing blooms twice.'),
      ('В кузнице ищи энергоблоки: выключи — и голем станет уязвим.',
       'In the forge look for energy blocks: deactivate them and the golem becomes vulnerable.'),
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
      ('Логово во тьме: странгуль охотится здесь по ночам.',
       'A den in the dark: the stranghoul hunts here at night.'),
      ('Миска острого рагу нанимает его на день. Серьёзно.',
       'A bowl of spicy stew hires it for a day. Seriously.'),
  ],
  tasks=[
      struct("eternal_starlight:stranghoul_den"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q009", ('Northern Flotilla', 'Флотилия севера'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:lunar_boat",
  size=1.2,
  desc=[
      ('Лунные, северные и баньяновые лодки с грузовыми вариантами.',
       'Lunar, northland and banyin boats with their cargo variants.'),
      ('Звёздное море быстрее переплыть, чем обойти.',
       'The starlit sea is faster to cross than to walk around.'),
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

Q("q010", ('Southern Flotilla', 'Флотилия юга'), section="s1",
  deps=['q001'],
  icon="eternal_starlight:scarlet_boat",
  size=1.2,
  desc=[
      ('Алые, тисовые, звоноствольные плоты и колыбельниковые лодки: весь флот.',
       'Scarlet, torreya, jinglestem rafts and cradlewood boats: the whole fleet.'),
      ('Звоноствол звенит на ветру — музыка в дороге.',
       'Jinglestem rings in the wind - music on the road.'),
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

# --- секция s2 ---
Q("q011", ('Small Fry of the Star Night', 'Мелочь звёздной ночи'), section="s2",
  deps=['q010'],
  icon="eternal_starlight:gleech_egg",
  desc=[
      ('Крысёныш, гиявка и теневая улитка: скромная фауна измерения.',
       'Ratlin, gleech and shadow snail: the humble fauna of the dimension.'),
      ('Брошенное яйцо гиявки лечит кровопусканием — бей в моба, не в себя.',
       'A thrown gleech egg heals by bloodletting - hit a mob, not yourself.'),
  ],
  tasks=[
      kill("eternal_starlight:ratlin", 1),
      kill("eternal_starlight:gleech", 1),
      kill("eternal_starlight:shadow_snail", 1),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q012", ('The Gentle and the Winged', 'Кроткие и крылатые'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Полярный олень роняет рога, лишь тараня твёрдые блоки — разозли его.',
       'The aurora deer drops antlers only when it rams hard blocks - make it angry.'),
      ('Кристаллизованный мотылёк приручается мясом и бьёт звуковой волной.',
       'The crystallized moth is tamed with meat and strikes with a sound wave.'),
  ],
  tasks=[
      kill("eternal_starlight:aurora_deer", 1),
      kill("eternal_starlight:shimmer_lacewing", 1),
      kill("eternal_starlight:crystallized_moth", 1),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q013", ('Angler of the Star Seas', 'Рыболов звёздных морей'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:luminofish",
  desc=[
      ('Светорыба светится, туровик бронирован: оба клюют ночью.',
       'Luminofish glows, rookfish armour-plated: both bite at night.'),
      ('Воздушный мешок туровика — основа дышащих ботинок.',
       'The rookfish air sac is the core of breathing boots.'),
  ],
  tasks=[
      kill("eternal_starlight:luminofish", 1),
      kill("eternal_starlight:rookfish", 1),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q014", ('The Bird and the Ent', 'Птица и энт'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:starfire_bird_egg",
  desc=[
      ('Не убивай птицу-звездопала ради звездопала: положи семена в её гнездо.',
       'Do not kill the starfire bird for starfire: put seeds in its nest instead.'),
      ('Энт — старое дерево, которое ходит. Топоров не любит.',
       'The ent is an old tree that walks. It does not like axes.'),
  ],
  tasks=[
      kill("eternal_starlight:starfire_bird", 1),
      kill("eternal_starlight:ent", 1),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q015", ('Night Hunters', 'Ночные охотники'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:tentacle_spike",
  desc=[
      ('Сумеречные пауки, звёздные скелеты и жаждущий странник: у ночи есть зубы.',
       'Dusk spiders, star skeletons and the thirst walker: the night has teeth.'),
      ('Зуб голода странника — стройматериал и оружие.',
       "The walker's tooth of hunger is a building material - and a weapon."),
  ],
  tasks=[
      kill("eternal_starlight:nightfall_spider", 1),
      kill("eternal_starlight:lonestar_skeleton", 1),
      kill("eternal_starlight:thirst_walker", 1),
  ],
  rewards=[
      xpr(80),
  ]),

Q("q016", ('Elements and Predators', 'Стихии и хищники'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:tentacle_spike",
  desc=[
      ('Метеориперы падают с метеоритным дождём; йети носит мерзлоту; искатель наблюдает.',
       'Creteors fall with meteor showers; the yeti wears the permafrost; the seeker watches.'),
      ('Его щупальце становится шипальцем — и ключом к добыче Бездны.',
       'Its tentacle becomes a spike - and a key to the abyssal loot.'),
  ],
  tasks=[
      kill("eternal_starlight:seeker", 1),
      kill("eternal_starlight:creteor", 1),
      kill("eternal_starlight:yeti", 1),
  ],
  rewards=[
      xpr(90),
  ]),

Q("q017", ('Permafrost and Stranghoul', 'Мерзлота и странгуль'), section="s2",
  deps=['q016'],
  icon="eternal_starlight:tenacious_vine",
  desc=[
      ('Мерзлотник плюётся издалека и прячется под пепельным снегом.',
       'The permafrost spits from afar and hides under ashen snow.'),
      ('Странгуль охотится на других мобов: увидь охоту — и найми охотника.',
       'The stranghoul hunts other mobs: witness a hunt - and hire the hunter.'),
  ],
  tasks=[
      kill("eternal_starlight:permafrost", 1),
      kill("eternal_starlight:stranghoul", 1),
  ],
  rewards=[
      xpr(90),
  ]),

Q("q018", ('A Tangled Death', 'Запутанная смерть'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:tenacious_vine",
  desc=[
      ('Запутанный, кадавр и череп: цепкая лоза не отпускает даже мёртвых.',
       'The tangled, its husk and skull: the tenacious vine does not let go even of the dead.'),
      ('Череп взрывается — сцепи два убийства ради достижения мода.',
       'The skull explodes - chain two kills for the mod achievement.'),
  ],
  tasks=[
      kill("eternal_starlight:tangled", 1),
      kill("eternal_starlight:tangled_husk", 1),
      kill("eternal_starlight:tangled_skull", 1),
  ],
  rewards=[
      xpr(80),
  ]),

Q("q019", ('The Gatekeeper', 'Привратник'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:starfire",
  size=1.7,
  desc=[
      ('Первый босс: Привратник проверяет достойных огненными шарами и яростью.',
       'First boss: the Gatekeeper tests the worthy with fireballs and fury.'),
      ('Пройди испытание — и забери то, что он стережёт.',
       'Pass his challenge - and take what he guards.'),
  ],
  tasks=[
      kill("eternal_starlight:the_gatekeeper", 1),
  ],
  rewards=[
      lvl(10),
      toast('Привратник пал. Врата открыты.'),
  ]),

Q("q020", ('The Lunar Monstrosity', 'Лунное чудовище'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:orb_of_prophecy",
  size=1.7,
  desc=[
      ('Второй босс ждёт в Бездне. Подожги его — только огонь делает его уязвимым.',
       'The second boss waits in the Abyss. Ignite it - only fire makes it vulnerable.'),
      ('Дыхание и шипы летят по дуге: держи дистанцию, не стой в лужах.',
       'Breath and thorns fly in arcs: keep distance, do not stand in the pools.'),
  ],
  tasks=[
      biome("eternal_starlight:the_abyss"),
      kill("eternal_starlight:lunar_monstrosity", 1),
  ],
  rewards=[
      lvl(12),
      toast('Лунное чудовище одолено. Через терни — к звёздам.'),
  ]),

Q("q021", ('Golems of Stone and Light', 'Големы камня и света'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:golem_steel_ingot",
  size=1.3,
  desc=[
      ('Мракокаменный голем призывается вырезанной лунной опунцией на кирпичах.',
       'The grimstone golem is summoned with a carved lunar cactus on bricks.'),
      ('Звездосветный неуязвим, пока гудит его энергоблок: обесточь или заморозь трубкой.',
       'The starlight golem is invulnerable while its energy block hums: deactivate or freeze it.'),
  ],
  tasks=[
      kill("eternal_starlight:grimstone_golem", 1),
      kill("eternal_starlight:starlight_golem", 1),
  ],
  rewards=[
      xpr(110),
  ]),

Q("q022", ('Golems of Sky and Aether', 'Големы неба и эфира'), section="s2",
  deps=['q011'],
  icon="eternal_starlight:golem_steel_ingot",
  size=1.3,
  desc=[
      ('Астральный голем падает с небес вместе с метеоритным дождём.',
       'The astral golem falls from the sky with the meteor shower.'),
      ('Эфиросцентный призывается вырезанной опунцией на эфиросцентном блоке.',
       'The aethersent one is summoned with a carved cactus on an aethersent block.'),
  ],
  tasks=[
      kill("eternal_starlight:astral_golem", 1),
      kill("eternal_starlight:aethersent_golem", 1),
  ],
  rewards=[
      xpr(110),
  ]),

# --- секция s3 ---
Q("q023", ('Six Tears of the Starlight', 'Шесть слёз Звездосветья'), section="s3",
  deps=['q022'],
  icon="eternal_starlight:glacite_shard",
  desc=[
      ('Леднит, тиокварц, запылённый осколок, маларит, звёздный алмаз и звездопал.',
       'Glacite, thioquartz, dusted shard, malarite, starlit diamond and starfire.'),
      ('Звездопал не добывают киркой: помоги птицам свить гнездо — и они поделятся.',
       'Starfire is not mined: help the starfire birds nest - and they will share.'),
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

Q("q024", ('The Soft Materials', 'Мягкие материалы'), section="s3",
  deps=['q023'],
  icon="eternal_starlight:shivering_gel",
  desc=[
      ('Селитра, дрожащий гель, роса душ, криноя, кактусовый гель и бархамох.',
       'Saltpetre, shivering gel, soul dew, crinoa, cactus gel and velvet moss.'),
      ('Всё это реагенты: бомбы, каша и амулеты начинаются отсюда.',
       'Each is a reagent: bombs, stews and amulets all start here.'),
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

Q("q025", ('Five Ingots', 'Пять слитков'), section="s3",
  deps=['q023'],
  icon="eternal_starlight:alloy_furnace",
  desc=[
      ('Леднит, глубинное серебро, нереалий, эфиросцент и големосталь: лестница металлов.',
       'Glacite, deepsilver, unrealium, aethersent and golem steel: the metal ladder.'),
      ('Доменная печь переплавляет то, что обычная не берёт.',
       'The alloy furnace smelts what a normal one cannot.'),
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

Q("q026", ('Liquid Glow and Resin', 'Жидкое сияние и смола'), section="s3",
  deps=['q023'],
  icon="eternal_starlight:flowglaze",
  desc=[
      ('Брось звездопал в песок — глазутёк. Обтеши тисовые брёвна — амарянтарь.',
       'Throw starfire into sand - flowglaze. Hew torreya logs - amaramber.'),
      ('Кристаллический катализатор работает на кристаллах и редстоуне: машина опустынивания.',
       'The crystalborn catalyst runs on crystals and redstone: desertification machine.'),
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

Q("q027", ('Voidstone and its Veins', 'Пустокамень и его жилы'), section="s3",
  deps=['q023'],
  icon="eternal_starlight:voidstone",
  desc=[
      ('Рудные жилы глубинных пород: шёлковое касание хранит блок, удача — количество.',
       'Ore veins of the deep rocks: silk touch keeps the block, fortune keeps the count.'),
      ('Подозрительные блоки чистятся кистью: археология, а не добыча.',
       'Suspicious blocks are brushed clean - archaeology, not mining.'),
  ],
  tasks=[
      item("eternal_starlight:voidstone_deepsilver_ore"),
      item("eternal_starlight:voidstone_malarite_ore"),
      item("eternal_starlight:voidstone_redstone_ore"),
      item("eternal_starlight:voidstone_saltpeter_ore"),
      item("eternal_starlight:voidstone_starcore_ore"),
      item("eternal_starlight:voidstone_starlit_diamond_ore"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q028", ('Nightfall Mud and its Veins', 'Сумеречный саман и жилы'), section="s3",
  deps=['q023'],
  icon="eternal_starlight:packed_nightfall_mud",
  desc=[
      ('Рудные жилы глубинных пород: шёлковое касание хранит блок, удача — количество.',
       'Ore veins of the deep rocks: silk touch keeps the block, fortune keeps the count.'),
      ('Подозрительные блоки чистятся кистью: археология, а не добыча.',
       'Suspicious blocks are brushed clean - archaeology, not mining.'),
  ],
  tasks=[
      item("eternal_starlight:packed_nightfall_mud_deepsilver_ore"),
      item("eternal_starlight:packed_nightfall_mud_malarite_ore"),
      item("eternal_starlight:suspicious_dimslag"),
      item("eternal_starlight:suspicious_dusted_gravel"),
  ],
  rewards=[
      xpr(70),
  ]),

# --- секция s4 ---
Q("q029", ('Weapons: the thermal springstone set', 'Оружие: Меч из термального истокамня и компания'), section="s4",
  deps=['q028'],
  icon="eternal_starlight:thermal_springstone_sword",
  desc=[
      ('Термальный истокамень лежит под гигантскими растениями: их сжигает только огонь.',
       'Thermal springstone lies under giant plants: only fire burns them away.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:thermal_springstone_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q030", ('Tools: the thermal springstone set', 'Инструмент: Кирка из термального истокамня'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:thermal_springstone_pickaxe",
  desc=[
      ('Термальный истокамень лежит под гигантскими растениями: их сжигает только огонь.',
       'Thermal springstone lies under giant plants: only fire burns them away.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:thermal_springstone_pickaxe"),
      item("eternal_starlight:thermal_springstone_axe"),
      item("eternal_starlight:thermal_springstone_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q031", ('Armour: the thermal springstone set', 'Броня: Шлем из термального истокамня'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:thermal_springstone_helmet",
  desc=[
      ('Термальный истокамень лежит под гигантскими растениями: их сжигает только огонь.',
       'Thermal springstone lies under giant plants: only fire burns them away.'),
      ('Четыре части, одно сияние: носи весь сет.',
       'Four pieces, one glow: wear the whole set.'),
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

Q("q032", ('Weapons: the glacite set', 'Оружие: Леднитовый меч и компания'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:glacite_sword",
  desc=[
      ('Леднит куют из осколков вершин вечной мерзлоты.',
       'Glacite is forged from shards of the permafrost peaks.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_sword"),
      item("eternal_starlight:glacite_shield"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q033", ('Tools: the glacite set', 'Инструмент: Леднитовая кирка'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:glacite_pickaxe",
  desc=[
      ('Леднит куют из осколков вершин вечной мерзлоты.',
       'Glacite is forged from shards of the permafrost peaks.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_pickaxe"),
      item("eternal_starlight:glacite_axe"),
      item("eternal_starlight:glacite_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q034", ('Armour: the glacite set', 'Броня: Леднитовый шлем'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:glacite_helmet",
  desc=[
      ('Леднит куют из осколков вершин вечной мерзлоты.',
       'Glacite is forged from shards of the permafrost peaks.'),
      ('Четыре части, одно сияние: носи весь сет.',
       'Four pieces, one glow: wear the whole set.'),
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

Q("q035", ('Weapons: the malarite set', 'Оружие: Маларитовый меч и компания'), section="s4",
  deps=['q034'],
  icon="eternal_starlight:malarite_sword",
  desc=[
      ('Маларит добывают из грязи ночных болот; его копьё длиннее меча.',
       'Malarite is dug from night swamp mud; its spear outreaches a sword.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:malarite_sword"),
      item("eternal_starlight:malarite_spear"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q036", ('Tools: the malarite set', 'Инструмент: Маларитовая кирка'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:malarite_pickaxe",
  desc=[
      ('Маларит добывают из грязи ночных болот; его копьё длиннее меча.',
       'Malarite is dug from night swamp mud; its spear outreaches a sword.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:malarite_pickaxe"),
      item("eternal_starlight:malarite_axe"),
      item("eternal_starlight:malarite_sickle"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q037", ('Weapons: the deepsilver set', 'Оружие: Меч из глубинного серебра и компания'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:deepsilver_sword",
  desc=[
      ('Глубинное серебро не тускнеет в сумерках: ищи в самане.',
       'Deepsilver does not tarnish in the dusk: look in packed mud.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:deepsilver_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q038", ('Tools: the deepsilver set', 'Инструмент: Кирка из глубинного серебра'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:deepsilver_pickaxe",
  desc=[
      ('Глубинное серебро не тускнеет в сумерках: ищи в самане.',
       'Deepsilver does not tarnish in the dusk: look in packed mud.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
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

Q("q039", ('Armour: the deepsilver set', 'Броня: Шлем из глубинного серебра'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:deepsilver_helmet",
  desc=[
      ('Глубинное серебро не тускнеет в сумерках: ищи в самане.',
       'Deepsilver does not tarnish in the dusk: look in packed mud.'),
      ('Четыре части, одно сияние: носи весь сет.',
       'Four pieces, one glow: wear the whole set.'),
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

Q("q040", ('Weapons: the starlit diamond set', 'Оружие: Меч из звёздного алмаза и компания'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:starlit_diamond_sword",
  desc=[
      ('Звёздный алмаз твёрже алмаза и слабо светится в темноте.',
       'Starlit diamond is harder than diamond and glows faintly in the dark.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:starlit_diamond_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q041", ('Tools: the starlit diamond set', 'Инструмент: Кирка из звёздного алмаза'), section="s4",
  deps=['q040'],
  icon="eternal_starlight:starlit_diamond_pickaxe",
  desc=[
      ('Звёздный алмаз твёрже алмаза и слабо светится в темноте.',
       'Starlit diamond is harder than diamond and glows faintly in the dark.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:starlit_diamond_pickaxe"),
      item("eternal_starlight:starlit_diamond_axe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q042", ('Armour: the starlit diamond set', 'Броня: Шлем из звёздного алмаза'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:starlit_diamond_helmet",
  desc=[
      ('Звёздный алмаз твёрже алмаза и слабо светится в темноте.',
       'Starlit diamond is harder than diamond and glows faintly in the dark.'),
      ('Четыре части, одно сияние: носи весь сет.',
       'Four pieces, one glow: wear the whole set.'),
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

Q("q043", ('Weapons: the unrealium set', 'Оружие: Нереалиевый меч и компания'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:unrealium_sword",
  desc=[
      ('Нереалий легче тени: полный сет — достижение мода.',
       'Unrealium is lighter than shadow: a full set is the mod achievement.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:unrealium_sword"),
      item("eternal_starlight:unrealium_crossbow"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q044", ('Tools: the unrealium set', 'Инструмент: Нереалиевая кирка'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:unrealium_pickaxe",
  desc=[
      ('Нереалий легче тени: полный сет — достижение мода.',
       'Unrealium is lighter than shadow: a full set is the mod achievement.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:unrealium_pickaxe"),
      item("eternal_starlight:unrealium_axe"),
      item("eternal_starlight:unrealium_sickle"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q045", ('Armour: the unrealium set', 'Броня: Нереалиевый шлем'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:unrealium_helmet",
  desc=[
      ('Нереалий легче тени: полный сет — достижение мода.',
       'Unrealium is lighter than shadow: a full set is the mod achievement.'),
      ('Четыре части, одно сияние: носи весь сет.',
       'Four pieces, one glow: wear the whole set.'),
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

Q("q046", ('Weapons: the starfire set', 'Оружие: Звездопальный меч и компания'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:starfire_sword",
  desc=[
      ('Снаряжение звездопала горит холодным пламенем, подаренным птицами.',
       'Starfire gear burns with a cold flame the birds gave you.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:starfire_sword"),
      item("eternal_starlight:starfire_crossbow"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q047", ('Tools: the starfire set', 'Инструмент: Звездопальная кирка'), section="s4",
  deps=['q046'],
  icon="eternal_starlight:starfire_pickaxe",
  desc=[
      ('Снаряжение звездопала горит холодным пламенем, подаренным птицами.',
       'Starfire gear burns with a cold flame the birds gave you.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:starfire_pickaxe"),
      item("eternal_starlight:starfire_axe"),
      item("eternal_starlight:starfire_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q048", ('Weapons: the flowglaze set', 'Оружие: Глазутёковый меч и компания'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:flowglaze_sword",
  desc=[
      ('Глазутёк течёт, куда ударишь: песок помнит звездопал.',
       'Flowglaze flows where you strike: the sand remembers the starfire.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:flowglaze_sword"),
      item("eternal_starlight:flowglaze_bow"),
      item("eternal_starlight:flowglaze_shield"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q049", ('Tools: the flowglaze set', 'Инструмент: Глазутёковая кирка'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:flowglaze_pickaxe",
  desc=[
      ('Глазутёк течёт, куда ударишь: песок помнит звездопал.',
       'Flowglaze flows where you strike: the sand remembers the starfire.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:flowglaze_pickaxe"),
      item("eternal_starlight:flowglaze_axe"),
      item("eternal_starlight:flowglaze_scythe"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q050", ('Weapons: the amaramber set', 'Оружие: Амарянтарный меч и компания'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:amaramber_sword",
  desc=[
      ('Амарянтарь — смола тиса: тёплая, янтарная, упрямая.',
       'Amaramber is the resin of torreya: warm, amber, stubborn.'),
      ('Клинки этого тира одного характера — и одного пути улучшений.',
       'Blades of this tier share one temper - and one upgrade path.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_sword"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q051", ('Tools: the amaramber set', 'Инструмент: Амарянтарная кирка'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:amaramber_pickaxe",
  desc=[
      ('Амарянтарь — смола тиса: тёплая, янтарная, упрямая.',
       'Amaramber is the resin of torreya: warm, amber, stubborn.'),
      ('Косы косят траву пачками, серпы срезают колосья, кисть — для археологии.',
       'Scythes mow grass in bundles; sickles cut ears; the brush is for archaeology.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_pickaxe"),
      item("eternal_starlight:amaramber_axe"),
      item("eternal_starlight:amaramber_sickle"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q052", ('Armour: the amaramber set', 'Броня: amaramber'), section="s4",
  deps=['q029'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Амарянтарь — смола тиса: тёплая, янтарная, упрямая.',
       'Amaramber is the resin of torreya: warm, amber, stubborn.'),
      ('Четыре части, одно сияние: носи весь сет.',
       'Four pieces, one glow: wear the whole set.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_chestplate"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q053", ('Templates of Ascent', 'Шаблоны восхождения'), section="s4",
  deps=['q052'],
  icon="eternal_starlight:starfire_upgrade_smithing_template",
  desc=[
      ('Шаблон звездопала улучшает термальное снаряжение; глазутёка — леднитовое.',
       'Starfire template upgrades thermal gear; flowglaze upgrades glacite gear.'),
      ('Стол кузнеца — лестница между тирами.',
       'The smithing table is the stair between tiers.'),
  ],
  tasks=[
      item("eternal_starlight:starfire_upgrade_smithing_template"),
      item("eternal_starlight:flowglaze_upgrade_smithing_template"),
  ],
  rewards=[
      xpr(60),
  ]),

# --- секция s5 ---
Q("q054", ('Dagger of Hunger', 'Кинжал голода'), section="s5",
  deps=['q053'],
  icon="eternal_starlight:dagger_of_hunger",
  desc=[
      ('Корми его ударами: голодный кинжал бьёт сильнее.',
       'Feed it with strikes: the hungry dagger hits harder when fed.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:dagger_of_hunger"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q055", ('Shattered Sword', 'Расколотый меч'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:shattered_sword",
  desc=[
      ('Собери лезвие и рукоять: расколотое — не значит мёртвое.',
       'Join blade and hilt: shattered does not mean dead.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:shattered_sword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q056", ('Glistering Sword', 'Сверкающий меч'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:glistering_sword",
  desc=[
      ('Сверкает там, где бьёт: первый из семьи сверкающих.',
       'It glisters where it strikes: first of the glistering family.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_sword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q057", ('Glistering Greatsword', 'Большой сверкающий меч'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:glistering_greatsword",
  desc=[
      ('Двуручный сверкающий: широкий замах, широкий блеск.',
       'The two-handed glistering: wide swing, wide shine.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q058", ('Glistering Bow', 'Сверкающий лук'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:glistering_bow",
  desc=[
      ('Стрелы сверкающего лука светятся трассерами.',
       'Its arrows shine like tracers.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_bow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q059", ('Glistering Morning Star', 'Сверкающая денница'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:glistering_morning_star",
  desc=[
      ('Денница: тяжёлая, честная, зубастая.',
       'The morning star: heavy, honest, toothy.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:glistering_morning_star"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q060", ('Energy Sword', 'Энергомеч'), section="s5",
  deps=['q059'],
  icon="eternal_starlight:energy_sword",
  desc=[
      ('Энергомеч: клинок из чистой вспышки.',
       'The energy sword: a blade of pure spark.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:energy_sword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q061", ('Energy Boomerang', 'Энергетический бумеранг'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:energy_boomerang",
  desc=[
      ('Возвращается. Всегда. Держи руку открытой.',
       'It returns. Always. Keep your hand open.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:energy_boomerang"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q062", ('Golem Steel Greatsword', 'Големостальной двуручный меч'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:golem_steel_greatsword",
  desc=[
      ('Двуручник из големостали: медленный, как голем, и такой же неизбежный.',
       'Golem steel greatsword: slow as a golem, and as inevitable.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:golem_steel_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q063", ('Mechanical Crossbow', 'Механический арбалет'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:mechanical_crossbow",
  desc=[
      ('Механический арбалет: перезаряжается сам, прощает дрожащую руку.',
       'The mechanical crossbow: reloads itself, forgives a shaking hand.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:mechanical_crossbow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q064", ('Crystal Greatsword', 'Кристальный двуручный меч'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:crystal_greatsword",
  desc=[
      ('Кристальный двуручный: тяжёлый осколок созвездия.',
       'Crystal greatsword: a heavy shard of a constellation.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:crystal_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q065", ('Crystal Crossbow', 'Кристальный арбалет'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:crystal_crossbow",
  desc=[
      ('Кристальный арбалет: бьёт лёдом и светом.',
       'Crystal crossbow: hits with ice and light.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:crystal_crossbow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q066", ('Wilted Crossbow', 'Увядший арбалет'), section="s5",
  deps=['q065'],
  icon="eternal_starlight:wilted_crossbow",
  desc=[
      ('Увядший арбалон: яд садов в каждом болте.',
       'The wilted crossbow: garden poison in every bolt.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:wilted_crossbow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q067", ('Moonring Bow', 'Кольцелунный лук'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:moonring_bow",
  desc=[
      ('Кольцелунный лук: дуга стрелы повторяет дугу луны.',
       'Moonring bow: the arrow arc mirrors the moon.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:moonring_bow"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q068", ('Moonring Greatsword', 'Большой кольцелунный меч'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:moonring_greatsword",
  desc=[
      ('Большой кольцелунный: серп луны в стали.',
       'The greater moonring: a lunar crescent in steel.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:moonring_greatsword"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q069", ('Crescent Spear', 'Копьё полумесяца'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:crescent_spear",
  desc=[
      ('Копьё полумесяца: достает там, где меч не дотянется.',
       'Crescent spear: reaches where a sword cannot.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:crescent_spear"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q070", ('Gravity Pickaxe', 'Гравитационная кирка'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:gravity_pickaxe",
  desc=[
      ('Гравитационная кирка: руда сама тянется в инвентарь.',
       'Gravity pickaxe: ore pulls itself into your inventory.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:gravity_pickaxe"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q071", ('Bow of Blood', 'Кровавый лук'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:bow_of_blood",
  desc=[
      ('Кровавый лук: пьёт жизнь врага и делится с тобой.',
       "Bow of blood: drinks the enemy's life and shares with you."),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:bow_of_blood"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q072", ('Coldsnap', 'Хладохлыст'), section="s5",
  deps=['q071'],
  icon="eternal_starlight:coldsnap",
  desc=[
      ('Хладохлыст: хлыст из вечного льда, мороз вместо раны.',
       'Coldsnap: a whip of eternal ice, frost instead of a wound.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:coldsnap"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q073", ('Candlash', 'Конфехлыст'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:candlash",
  desc=[
      ('Конфехлыст: сладкий на вид, горький на удар.',
       'Candlash: sweet to look at, bitter to hit.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:candlash"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q074", ('Underminer', 'Подкопщик'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:underminer",
  desc=[
      ('Подкопщик: копает врага изнутри доспеха.',
       'The underminer: digs the enemy from inside their armour.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:underminer"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q075", ('Flesh Grinder', 'Плотерубка'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:flesh_grinder",
  desc=[
      ('Плотерубка: не для слабых желудком.',
       'The flesh grinder: not for the faint of stomach.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:flesh_grinder"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q076", ('Bonemore', 'Костолом'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:bonemore",
  desc=[
      ('Костолом: щит в одной руке, аргумент в другой.',
       'Bonemore: a shield in one hand, an argument in the other.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:bonemore"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q077", ('Living Arm', 'Живая рука'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:living_arm",
  desc=[
      ('Живая рука: оружие, которое держит тебя, а не наоборот.',
       'The living arm: a weapon that holds you, not the other way.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:living_arm"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q078", ('Pungency Fruit Spear', 'Копьё из острого фрукта'), section="s5",
  deps=['q077'],
  icon="eternal_starlight:pungency_fruit_spear",
  desc=[
      ('Копьё из острого фрукта: онемение вместо раны.',
       'Pungency fruit spear: numbness instead of a wound.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:pungency_fruit_spear"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q079", ('Pungency Fruit Axe', 'Топор из острого фрукта'), section="s5",
  deps=['q054'],
  icon="eternal_starlight:pungency_fruit_axe",
  desc=[
      ('Топор из острого фрукта: салатное оружие.',
       'Pungency fruit axe: a salad weapon.'),
      ('Уникальный клинок: один из двадцати семи, у каждого свой характер.',
       'A unique blade: one of twenty-seven, each with its own temper.'),
  ],
  tasks=[
      item("eternal_starlight:pungency_fruit_axe"),
  ],
  rewards=[
      xpr(35),
  ]),

# --- секция s6 ---
Q("q080", ('Glacite Arrow', 'Леднитовая стрела'), section="s6",
  deps=['q010', 'q022', 'q028', 'q053', 'q079'],
  icon="eternal_starlight:glacite_arrow",
  desc=[
      ('Леднитовая стрела: замедляет цель морозом.',
       'Glacite arrow: slows the target with frost.'),
      ('Наряди связку: впереди квест колчана.',
       'Fletch a bundle: the quiver quest is next.'),
  ],
  tasks=[
      item("eternal_starlight:glacite_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q081", ('Malarite Arrow', 'Маларитовая стрела'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:malarite_arrow",
  desc=[
      ('Маларитовая стрела: тяжёлая, прямолинейная.',
       'Malarite arrow: heavy and straightforward.'),
      ('Наряди связку: впереди квест колчана.',
       'Fletch a bundle: the quiver quest is next.'),
  ],
  tasks=[
      item("eternal_starlight:malarite_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q082", ('Amaramber Arrow', 'Амарянтарная стрела'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:amaramber_arrow",
  desc=[
      ('Амарянтарная стрела: смола липнет к ране.',
       'Amaramber arrow: resin clings to the wound.'),
      ('Наряди связку: впереди квест колчана.',
       'Fletch a bundle: the quiver quest is next.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q083", ('Thioquartz Arrow', 'Тиокварцевая стрела'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:thioquartz_arrow",
  desc=[
      ('Тиокварцевая стрела: искрит серой.',
       'Thioquartz arrow: sparks with sulphur.'),
      ('Наряди связку: впереди квест колчана.',
       'Fletch a bundle: the quiver quest is next.'),
  ],
  tasks=[
      item("eternal_starlight:thioquartz_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q084", ('Air Sac Arrow', 'Стрела из воздушного мешка'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:air_sac_arrow",
  desc=[
      ('Стрела из воздушного мешка: лёгкий полёт, лёгкий урон.',
       'Air sac arrow: light flight, light damage.'),
      ('Наряди связку: впереди квест колчана.',
       'Fletch a bundle: the quiver quest is next.'),
  ],
  tasks=[
      item("eternal_starlight:air_sac_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q085", ('Voracious Arrow', 'Прожорливая стрела'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:voracious_arrow",
  desc=[
      ('Прожорливая стрела: доедает то, что не добил болт.',
       'Voracious arrow: finishes what the bolt did not.'),
      ('Наряди связку: впереди квест колчана.',
       'Fletch a bundle: the quiver quest is next.'),
  ],
  tasks=[
      item("eternal_starlight:voracious_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q086", ('Aethersent Arrow', 'Эфиросцентная стрела'), section="s6",
  deps=['q085'],
  icon="eternal_starlight:aethersent_arrow",
  desc=[
      ('Эфиросцентная стрела: светится в полёте — фонарь ночи.',
       'Aethersent arrow: glows in flight - a lantern of the night.'),
      ('Наряди связку: впереди квест колчана.',
       'Fletch a bundle: the quiver quest is next.'),
  ],
  tasks=[
      item("eternal_starlight:aethersent_arrow"),
  ],
  rewards=[
      xpr(25),
  ]),

Q("q087", ('The Galactic Quiver', 'Галактический колчан'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:galactic_quiver",
  size=1.3,
  desc=[
      ('Все семь видов стрел по четыре штуки в одном колчане.',
       'All seven arrow kinds, four of each, in one quiver.'),
      ('Галактический колчан держит их по полочкам даже в темноте.',
       'The galactic quiver keeps them sorted even in the dark.'),
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

Q("q088", ('The Aethersent Raiment', 'Эфиросцентное облачение'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:aethersent_hood",
  size=1.2,
  desc=[
      ('Капюшон, накидка, штаны и сапоги из эфиросцента: набор небесного плетения.',
       'Hood, cape, bottoms and boots of aethersent: the sky-weave set.'),
      ('Он упал с небес с метеорами — сплети его заново.',
       'It fell from the sky with the meteors - weave it back.'),
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

Q("q089", ('Mask, Robe, Boots', 'Маска, одеяние, ботинки'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:alchemist_mask",
  desc=[
      ('Набор алхимика дышит там, где не дышит ничто; ботинки из воздушного мешка гасят падение.',
       'The alchemist set breathes where nothing breathes; air sac boots soften falls.'),
      ('С ними Бездна чуть добрее.',
       'The Abyss becomes a little kinder with them.'),
  ],
  tasks=[
      item("eternal_starlight:alchemist_mask"),
      item("eternal_starlight:alchemist_robe"),
      item("eternal_starlight:air_sac_boots"),
  ],
  rewards=[
      xpr(70),
  ]),

Q("q090", ('Four Trim Patterns', 'Четыре узора отделки'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:keeper_armor_trim_smithing_template",
  desc=[
      ('Привратник, кузница, цвет и плетение: четыре узора для стола кузнеца.',
       'Keeper, forge, blooming and twining: four patterns for the smithing table.'),
      ('Декор — тоже контент: энциклопедия учитывает отделки отдельно.',
       'Decoration is also content: the encyclopaedia counts trims separately.'),
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

Q("q091", ('Berries and Fruits', 'Ягоды и плоды'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:lunar_berries",
  desc=[
      ('Звёздная кухня: всё съедобное и всё отсюда.',
       'Starlight cooking: everything here is edible and everything is from here.'),
      ('Острый фрукт даёт онемение — оно поглощает урон за тебя.',
       'Spicy fruit gives numbness - it absorbs damage for you.'),
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

Q("q092", ('Grains and Porridges', 'Злаки и каши'), section="s6",
  deps=['q091'],
  icon="eternal_starlight:nocturnal_millet",
  desc=[
      ('Звёздная кухня: всё съедобное и всё отсюда.',
       'Starlight cooking: everything here is edible and everything is from here.'),
      ('Острый фрукт даёт онемение — оно поглощает урон за тебя.',
       'Spicy fruit gives numbness - it absorbs damage for you.'),
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

Q("q093", ('Meat and Fish', 'Мясо и рыба'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:rookfish",
  desc=[
      ('Звёздная кухня: всё съедобное и всё отсюда.',
       'Starlight cooking: everything here is edible and everything is from here.'),
      ('Острый фрукт даёт онемение — оно поглощает урон за тебя.',
       'Spicy fruit gives numbness - it absorbs damage for you.'),
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

Q("q094", ('Hot and Hearty', 'Горячее и сытное'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:bouldershroom_stew",
  desc=[
      ('Звёздная кухня: всё съедобное и всё отсюда.',
       'Starlight cooking: everything here is edible and everything is from here.'),
      ('Острый фрукт даёт онемение — оно поглощает урон за тебя.',
       'Spicy fruit gives numbness - it absorbs damage for you.'),
  ],
  tasks=[
      item("eternal_starlight:bouldershroom_stew"),
      item("eternal_starlight:jinglestem_sandwich"),
      item("eternal_starlight:jinglestem_crisp"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q095", ('Amulets', 'Амулеты'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:butterfly_wings_amulet",
  desc=[
      ('Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.',
       'Pocket miracles of the Starlight: each has a use, none is ballast.'),
      ('Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.',
       'The aetherstrike rocket calls a meteor shower - make a wish.'),
  ],
  tasks=[
      item("eternal_starlight:butterfly_wings_amulet"),
      item("eternal_starlight:fungus_amulet"),
      item("eternal_starlight:crescent_pendant"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q096", ('Warrior Pendants', 'Подвески воина'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:battleaxe_pendant",
  desc=[
      ('Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.',
       'Pocket miracles of the Starlight: each has a use, none is ballast.'),
      ('Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.',
       'The aetherstrike rocket calls a meteor shower - make a wish.'),
  ],
  tasks=[
      item("eternal_starlight:battleaxe_pendant"),
      item("eternal_starlight:warhammer_pendant"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q097", ('Curios of the Abyss', 'Диковины Бездны'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:chain_of_souls",
  desc=[
      ('Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.',
       'Pocket miracles of the Starlight: each has a use, none is ballast.'),
      ('Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.',
       'The aetherstrike rocket calls a meteor shower - make a wish.'),
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

Q("q098", ("Explorer's Pocket", 'Карман исследователя'), section="s6",
  deps=['q097'],
  icon="eternal_starlight:book",
  desc=[
      ('Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.',
       'Pocket miracles of the Starlight: each has a use, none is ballast.'),
      ('Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.',
       'The aetherstrike rocket calls a meteor shower - make a wish.'),
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

Q("q099", ('Bombs and Projectiles', 'Бомбы и снаряды'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:sonar_bomb",
  desc=[
      ('Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.',
       'Pocket miracles of the Starlight: each has a use, none is ballast.'),
      ('Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.',
       'The aetherstrike rocket calls a meteor shower - make a wish.'),
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

Q("q100", ('Small Things of the Night', 'Мелочи ночи'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:saltpeter_matchbox",
  desc=[
      ('Карманные чудеса Звездосветья: у каждого своё дело, балласта нет.',
       'Pocket miracles of the Starlight: each has a use, none is ballast.'),
      ('Эфирная ударная ракета зовёт метеоритный дождь — загадай желание.',
       'The aetherstrike rocket calls a meteor shower - make a wish.'),
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

Q("q101", ('Discs by Depus', 'Пластинки: Depus'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:music_disc_deep_blue",
  desc=[
      ('8 пластинки автора Depus: спрятаны в сундуках структур и карманах боссов.',
       '8 disc(s) by Depus, hidden in structure chests and boss pockets.'),
      ('Проигрыватель в земном доме — лучший способ вспомнить звёзды.',
       'A jukebox in your overworld home is the best way to remember the stars.'),
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

Q("q102", ('Discs by Strantran', 'Пластинки: Strantran'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:music_disc_stars_shining_upon_the_sea",
  desc=[
      ('1 пластинки автора Strantran: спрятаны в сундуках структур и карманах боссов.',
       '1 disc(s) by Strantran, hidden in structure chests and boss pockets.'),
      ('Проигрыватель в земном доме — лучший способ вспомнить звёзды.',
       'A jukebox in your overworld home is the best way to remember the stars.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_stars_shining_upon_the_sea"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q103", ('Discs by TohokuAlpha', 'Пластинки: TohokuAlpha'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:music_disc_ether_rain",
  desc=[
      ('3 пластинки автора TohokuAlpha: спрятаны в сундуках структур и карманах боссов.',
       '3 disc(s) by TohokuAlpha, hidden in structure chests and boss pockets.'),
      ('Проигрыватель в земном доме — лучший способ вспомнить звёзды.',
       'A jukebox in your overworld home is the best way to remember the stars.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_ether_rain"),
      item("eternal_starlight:music_disc_tranquility"),
      item("eternal_starlight:music_disc_tranquility_ii"),
  ],
  rewards=[
      xpr(60),
  ]),

Q("q104", ('Discs by Бинке', 'Пластинки: Бинке'), section="s6",
  deps=['q103'],
  icon="eternal_starlight:music_disc_brisk",
  desc=[
      ('6 пластинки автора Бинке: спрятаны в сундуках структур и карманах боссов.',
       '6 disc(s) by Бинке, hidden in structure chests and boss pockets.'),
      ('Проигрыватель в земном доме — лучший способ вспомнить звёзды.',
       'A jukebox in your overworld home is the best way to remember the stars.'),
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

Q("q105", ('Discs by Депус', 'Пластинки: Депус'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:music_disc_mechanical_fossil",
  desc=[
      ('2 пластинки автора Депус: спрятаны в сундуках структур и карманах боссов.',
       '2 disc(s) by Депус, hidden in structure chests and boss pockets.'),
      ('Проигрыватель в земном доме — лучший способ вспомнить звёзды.',
       'A jukebox in your overworld home is the best way to remember the stars.'),
  ],
  tasks=[
      item("eternal_starlight:music_disc_mechanical_fossil"),
      item("eternal_starlight:music_disc_wailing_well"),
  ],
  rewards=[
      xpr(50),
  ]),

Q("q106", ('Discs by КрЛайт', 'Пластинки: КрЛайт'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:music_disc_dusk_o_ereyesterday",
  desc=[
      ('4 пластинки автора КрЛайт: спрятаны в сундуках структур и карманах боссов.',
       '4 disc(s) by КрЛайт, hidden in structure chests and boss pockets.'),
      ('Проигрыватель в земном доме — лучший способ вспомнить звёзды.',
       'A jukebox in your overworld home is the best way to remember the stars.'),
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

Q("q107", ('Лунные доски: Trunk and Crown', 'Лунные доски: ствол и крона'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:lunar_log",
  desc=[
      ('Лунное дерево пахнет пылью и тихой ночью.',
       'Lunar wood smells of dust and quiet night.'),
      ('Бревно, древесина, обтёсанная пара, листья и саженец: всё дерево.',
       'Log, wood, stripped pair, leaves and sapling: the whole tree.'),
  ],
  tasks=[
      item("eternal_starlight:lunar_log"),
      item("eternal_starlight:lunar_wood"),
      item("eternal_starlight:stripped_lunar_log"),
      item("eternal_starlight:stripped_lunar_wood"),
      item("eternal_starlight:lunar_leaves"),
      item("eternal_starlight:lunar_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q108", ('Лунные доски: Joinery and Fence', 'Лунные доски: столярка и ограда'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:lunar_planks",
  desc=[
      ('Лунное дерево пахнет пылью и тихой ночью.',
       'Lunar wood smells of dust and quiet night.'),
      ('Доски, ступени, плита, дверь, люк, забор, калитка, кнопка, плита и таблички.',
       'Planks, stairs, slab, door, trapdoor, fence, gate, button, plate, signs.'),
      ('Скелет дома и садовый набор в одном квесте.',
       'The house skeleton and the garden set in one quest.'),
  ],
  tasks=[
      item("eternal_starlight:lunar_planks"),
      item("eternal_starlight:lunar_stairs"),
      item("eternal_starlight:lunar_slab"),
      item("eternal_starlight:lunar_door"),
      item("eternal_starlight:lunar_trapdoor"),
      item("eternal_starlight:lunar_fence"),
      item("eternal_starlight:lunar_fence_gate"),
      item("eternal_starlight:lunar_button"),
      item("eternal_starlight:lunar_pressure_plate"),
      item("eternal_starlight:lunar_sign"),
      item("eternal_starlight:lunar_hanging_sign"),
  ],
  rewards=[
      xpr(55),
  ]),

Q("q109", ('Северные доски: Trunk and Crown', 'Северные доски: ствол и крона'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:northland_log",
  desc=[
      ('Северное дерево пахнет хвоей и снегом.',
       'Northland wood smells of pine and snow.'),
      ('Бревно, древесина, обтёсанная пара, листья и саженец: всё дерево.',
       'Log, wood, stripped pair, leaves and sapling: the whole tree.'),
  ],
  tasks=[
      item("eternal_starlight:northland_log"),
      item("eternal_starlight:northland_wood"),
      item("eternal_starlight:stripped_northland_log"),
      item("eternal_starlight:stripped_northland_wood"),
      item("eternal_starlight:northland_leaves"),
      item("eternal_starlight:northland_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q110", ('Северные доски: Joinery and Fence', 'Северные доски: столярка и ограда'), section="s6",
  deps=['q109'],
  icon="eternal_starlight:northland_planks",
  desc=[
      ('Северное дерево пахнет хвоей и снегом.',
       'Northland wood smells of pine and snow.'),
      ('Доски, ступени, плита, дверь, люк, забор, калитка, кнопка, плита и таблички.',
       'Planks, stairs, slab, door, trapdoor, fence, gate, button, plate, signs.'),
      ('Скелет дома и садовый набор в одном квесте.',
       'The house skeleton and the garden set in one quest.'),
  ],
  tasks=[
      item("eternal_starlight:northland_planks"),
      item("eternal_starlight:northland_stairs"),
      item("eternal_starlight:northland_slab"),
      item("eternal_starlight:northland_door"),
      item("eternal_starlight:northland_trapdoor"),
      item("eternal_starlight:northland_fence"),
      item("eternal_starlight:northland_fence_gate"),
      item("eternal_starlight:northland_button"),
      item("eternal_starlight:northland_pressure_plate"),
      item("eternal_starlight:northland_sign"),
      item("eternal_starlight:northland_hanging_sign"),
  ],
  rewards=[
      xpr(55),
  ]),

Q("q111", ('Баньяновые доски: Trunk and Crown', 'Баньяновые доски: ствол и крона'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:banyin_log",
  desc=[
      ('Баньян гнётся, не ломаясь: любимец столяра.',
       "Banyin bends without breaking: the joiner's favourite."),
      ('Бревно, древесина, обтёсанная пара, листья и саженец: всё дерево.',
       'Log, wood, stripped pair, leaves and sapling: the whole tree.'),
  ],
  tasks=[
      item("eternal_starlight:banyin_log"),
      item("eternal_starlight:banyin_wood"),
      item("eternal_starlight:stripped_banyin_log"),
      item("eternal_starlight:stripped_banyin_wood"),
      item("eternal_starlight:banyin_leaves"),
      item("eternal_starlight:banyin_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q112", ('Баньяновые доски: Joinery and Fence', 'Баньяновые доски: столярка и ограда'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:banyin_planks",
  desc=[
      ('Баньян гнётся, не ломаясь: любимец столяра.',
       "Banyin bends without breaking: the joiner's favourite."),
      ('Доски, ступени, плита, дверь, люк, забор, калитка, кнопка, плита и таблички.',
       'Planks, stairs, slab, door, trapdoor, fence, gate, button, plate, signs.'),
      ('Скелет дома и садовый набор в одном квесте.',
       'The house skeleton and the garden set in one quest.'),
  ],
  tasks=[
      item("eternal_starlight:banyin_planks"),
      item("eternal_starlight:banyin_stairs"),
      item("eternal_starlight:banyin_slab"),
      item("eternal_starlight:banyin_door"),
      item("eternal_starlight:banyin_trapdoor"),
      item("eternal_starlight:banyin_fence"),
      item("eternal_starlight:banyin_fence_gate"),
      item("eternal_starlight:banyin_button"),
      item("eternal_starlight:banyin_pressure_plate"),
      item("eternal_starlight:banyin_sign"),
      item("eternal_starlight:banyin_hanging_sign"),
  ],
  rewards=[
      xpr(55),
  ]),

Q("q113", ('Алые доски: Trunk and Crown', 'Алые доски: ствол и крона'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:scarlet_log",
  desc=[
      ('Алое дерево горит цветом, а не огнём.',
       'Scarlet wood burns with colour, not with fire.'),
      ('Бревно, древесина, обтёсанная пара, листья и саженец: всё дерево.',
       'Log, wood, stripped pair, leaves and sapling: the whole tree.'),
  ],
  tasks=[
      item("eternal_starlight:scarlet_log"),
      item("eternal_starlight:scarlet_wood"),
      item("eternal_starlight:stripped_scarlet_log"),
      item("eternal_starlight:stripped_scarlet_wood"),
      item("eternal_starlight:scarlet_leaves"),
      item("eternal_starlight:scarlet_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q114", ('Алые доски: Joinery and Fence', 'Алые доски: столярка и ограда'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:scarlet_planks",
  desc=[
      ('Алое дерево горит цветом, а не огнём.',
       'Scarlet wood burns with colour, not with fire.'),
      ('Доски, ступени, плита, дверь, люк, забор, калитка, кнопка, плита и таблички.',
       'Planks, stairs, slab, door, trapdoor, fence, gate, button, plate, signs.'),
      ('Скелет дома и садовый набор в одном квесте.',
       'The house skeleton and the garden set in one quest.'),
  ],
  tasks=[
      item("eternal_starlight:scarlet_planks"),
      item("eternal_starlight:scarlet_stairs"),
      item("eternal_starlight:scarlet_slab"),
      item("eternal_starlight:scarlet_door"),
      item("eternal_starlight:scarlet_trapdoor"),
      item("eternal_starlight:scarlet_fence"),
      item("eternal_starlight:scarlet_fence_gate"),
      item("eternal_starlight:scarlet_button"),
      item("eternal_starlight:scarlet_pressure_plate"),
      item("eternal_starlight:scarlet_sign"),
      item("eternal_starlight:scarlet_hanging_sign"),
  ],
  rewards=[
      xpr(55),
  ]),

Q("q115", ('Тисовые доски: Trunk and Crown', 'Тисовые доски: ствол и крона'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:torreya_log",
  desc=[
      ('Тис прячет амарянтарь внутри брёвен.',
       'Torreya hides amaramber inside its logs.'),
      ('Бревно, древесина, обтёсанная пара, листья и саженец: всё дерево.',
       'Log, wood, stripped pair, leaves and sapling: the whole tree.'),
  ],
  tasks=[
      item("eternal_starlight:torreya_log"),
      item("eternal_starlight:torreya_wood"),
      item("eternal_starlight:stripped_torreya_log"),
      item("eternal_starlight:stripped_torreya_wood"),
      item("eternal_starlight:torreya_leaves"),
      item("eternal_starlight:torreya_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q116", ('Тисовые доски: Joinery and Fence', 'Тисовые доски: столярка и ограда'), section="s6",
  deps=['q115'],
  icon="eternal_starlight:torreya_planks",
  desc=[
      ('Тис прячет амарянтарь внутри брёвен.',
       'Torreya hides amaramber inside its logs.'),
      ('Доски, ступени, плита, дверь, люк, забор, калитка, кнопка, плита и таблички.',
       'Planks, stairs, slab, door, trapdoor, fence, gate, button, plate, signs.'),
      ('Скелет дома и садовый набор в одном квесте.',
       'The house skeleton and the garden set in one quest.'),
  ],
  tasks=[
      item("eternal_starlight:torreya_planks"),
      item("eternal_starlight:torreya_stairs"),
      item("eternal_starlight:torreya_slab"),
      item("eternal_starlight:torreya_door"),
      item("eternal_starlight:torreya_trapdoor"),
      item("eternal_starlight:torreya_fence"),
      item("eternal_starlight:torreya_fence_gate"),
      item("eternal_starlight:torreya_button"),
      item("eternal_starlight:torreya_pressure_plate"),
      item("eternal_starlight:torreya_sign"),
      item("eternal_starlight:torreya_hanging_sign"),
  ],
  rewards=[
      xpr(55),
  ]),

Q("q117", ('Доски из звоноствола: Trunk and Crown', 'Доски из звоноствола: ствол и крона'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:jinglestem_log",
  desc=[
      ('Звоноствол звенит на ветру: музыка в дороге.',
       'Jinglestem rings in the wind: music on the road.'),
      ('Бревно, древесина, обтёсанная пара, листья и саженец: всё дерево.',
       'Log, wood, stripped pair, leaves and sapling: the whole tree.'),
  ],
  tasks=[
      item("eternal_starlight:jinglestem_log"),
      item("eternal_starlight:jinglestem_wood"),
      item("eternal_starlight:stripped_jinglestem_log"),
      item("eternal_starlight:stripped_jinglestem_wood"),
      item("eternal_starlight:jinglestem_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q118", ('Доски из звоноствола: Joinery and Fence', 'Доски из звоноствола: столярка и ограда'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:jinglestem_planks",
  desc=[
      ('Звоноствол звенит на ветру: музыка в дороге.',
       'Jinglestem rings in the wind: music on the road.'),
      ('Доски, ступени, плита, дверь, люк, забор, калитка, кнопка, плита и таблички.',
       'Planks, stairs, slab, door, trapdoor, fence, gate, button, plate, signs.'),
      ('Скелет дома и садовый набор в одном квесте.',
       'The house skeleton and the garden set in one quest.'),
  ],
  tasks=[
      item("eternal_starlight:jinglestem_planks"),
      item("eternal_starlight:jinglestem_stairs"),
      item("eternal_starlight:jinglestem_slab"),
      item("eternal_starlight:jinglestem_door"),
      item("eternal_starlight:jinglestem_trapdoor"),
      item("eternal_starlight:jinglestem_fence"),
      item("eternal_starlight:jinglestem_fence_gate"),
      item("eternal_starlight:jinglestem_button"),
      item("eternal_starlight:jinglestem_pressure_plate"),
      item("eternal_starlight:jinglestem_sign"),
      item("eternal_starlight:jinglestem_hanging_sign"),
  ],
  rewards=[
      xpr(55),
  ]),

Q("q119", ('Колыбельниковые доски: Trunk and Crown', 'Колыбельниковые доски: ствол и крона'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cradlewood_log",
  desc=[
      ('Колыбельник скрипит как колыбельная: мягко, медленно, безопасно.',
       'Cradlewood creaks like a lullaby: soft, slow, safe.'),
      ('Бревно, древесина, обтёсанная пара, листья и саженец: всё дерево.',
       'Log, wood, stripped pair, leaves and sapling: the whole tree.'),
  ],
  tasks=[
      item("eternal_starlight:cradlewood_log"),
      item("eternal_starlight:cradlewood_wood"),
      item("eternal_starlight:stripped_cradlewood_log"),
      item("eternal_starlight:stripped_cradlewood_wood"),
      item("eternal_starlight:cradlewood_leaves"),
      item("eternal_starlight:cradlewood_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q120", ('Колыбельниковые доски: Joinery and Fence', 'Колыбельниковые доски: столярка и ограда'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cradlewood_planks",
  desc=[
      ('Колыбельник скрипит как колыбельная: мягко, медленно, безопасно.',
       'Cradlewood creaks like a lullaby: soft, slow, safe.'),
      ('Доски, ступени, плита, дверь, люк, забор, калитка, кнопка, плита и таблички.',
       'Planks, stairs, slab, door, trapdoor, fence, gate, button, plate, signs.'),
      ('Скелет дома и садовый набор в одном квесте.',
       'The house skeleton and the garden set in one quest.'),
  ],
  tasks=[
      item("eternal_starlight:cradlewood_planks"),
      item("eternal_starlight:cradlewood_stairs"),
      item("eternal_starlight:cradlewood_slab"),
      item("eternal_starlight:cradlewood_door"),
      item("eternal_starlight:cradlewood_trapdoor"),
      item("eternal_starlight:cradlewood_fence"),
      item("eternal_starlight:cradlewood_fence_gate"),
      item("eternal_starlight:cradlewood_button"),
      item("eternal_starlight:cradlewood_pressure_plate"),
      item("eternal_starlight:cradlewood_sign"),
      item("eternal_starlight:cradlewood_hanging_sign"),
  ],
  rewards=[
      xpr(55),
  ]),

Q("q121", ('Мракокамень: Base and Variants', 'Мракокамень: основа и варианты'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:grimstone",
  desc=[
      ('Базовый блок и его полированные/кирпичные/плиточные варианты.',
       'The base block and its polished/bricked/tiled variants.'),
      ('Формы — в следующем квесте.',
       'Shapes come in the next quest.'),
  ],
  tasks=[
      item("eternal_starlight:grimstone"),
      item("eternal_starlight:grimstone_bricks"),
      item("eternal_starlight:grimstone_deepsilver_ore"),
      item("eternal_starlight:grimstone_malarite_ore"),
      item("eternal_starlight:grimstone_redstone_ore"),
      item("eternal_starlight:grimstone_saltpeter_ore"),
      item("eternal_starlight:grimstone_starcore_ore"),
      item("eternal_starlight:grimstone_starlit_diamond_ore"),
      item("eternal_starlight:grimstone_tiles"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q122", ('Мракокамень: Shapes', 'Мракокамень: формы'), section="s6",
  deps=['q121'],
  icon="eternal_starlight:grimstone_stairs",
  desc=[
      ('Ступени, плиты и стены семейства: тройка строителя.',
       "Stairs, slabs and walls of the family: the builder's trio."),
      ('',
       ''),
  ],
  tasks=[
      item("eternal_starlight:grimstone_slab"),
      item("eternal_starlight:grimstone_stairs"),
      item("eternal_starlight:grimstone_wall"),
  ],
  rewards=[
      xpr(30),
  ]),

Q("q123", ('Full Set: Колотый мракокамень', 'Полный набор: Колотый мракокамень'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cobbled_grimstone",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:cobbled_grimstone"),
      item("eternal_starlight:cobbled_grimstone_slab"),
      item("eternal_starlight:cobbled_grimstone_stairs"),
      item("eternal_starlight:cobbled_grimstone_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q124", ('Full Set: Полированный мракокамень', 'Полный набор: Полированный мракокамень'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:polished_grimstone",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_grimstone"),
      item("eternal_starlight:polished_grimstone_tiles"),
      item("eternal_starlight:polished_grimstone_slab"),
      item("eternal_starlight:polished_grimstone_stairs"),
      item("eternal_starlight:polished_grimstone_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q125", ('Full Set: grimstone_brick', 'Полный набор: grimstone_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:grimstone_brick_slab"),
      item("eternal_starlight:grimstone_brick_stairs"),
      item("eternal_starlight:grimstone_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q126", ('Full Set: grimstone_tile', 'Полный набор: grimstone_tile'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:grimstone_tile_slab"),
      item("eternal_starlight:grimstone_tile_stairs"),
      item("eternal_starlight:grimstone_tile_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q127", ('Full Set: polished_grimstone_tile', 'Полный набор: polished_grimstone_tile'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_grimstone_tile_slab"),
      item("eternal_starlight:polished_grimstone_tile_stairs"),
      item("eternal_starlight:polished_grimstone_tile_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q128", ('Full Set: Бездносланец', 'Полный набор: Бездносланец'), section="s6",
  deps=['q127'],
  icon="eternal_starlight:abysslate",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:abysslate"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q129", ('Full Set: Полированный бездносланец', 'Полный набор: Полированный бездносланец'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:polished_abysslate",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_abysslate"),
      item("eternal_starlight:polished_abysslate_bricks"),
      item("eternal_starlight:polished_abysslate_slab"),
      item("eternal_starlight:polished_abysslate_stairs"),
      item("eternal_starlight:polished_abysslate_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q130", ('Full Set: polished_abysslate_brick', 'Полный набор: polished_abysslate_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_abysslate_brick_slab"),
      item("eternal_starlight:polished_abysslate_brick_stairs"),
      item("eternal_starlight:polished_abysslate_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q131", ('Full Set: Криобездносланец', 'Полный набор: Криобездносланец'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cryobysslate",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:cryobysslate"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q132", ('Full Set: Полированный криобездносланец', 'Полный набор: Полированный криобездносланец'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:polished_cryobysslate",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_cryobysslate"),
      item("eternal_starlight:polished_cryobysslate_bricks"),
      item("eternal_starlight:polished_cryobysslate_slab"),
      item("eternal_starlight:polished_cryobysslate_stairs"),
      item("eternal_starlight:polished_cryobysslate_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q133", ('Full Set: polished_cryobysslate_brick', 'Полный набор: polished_cryobysslate_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_cryobysslate_brick_slab"),
      item("eternal_starlight:polished_cryobysslate_brick_stairs"),
      item("eternal_starlight:polished_cryobysslate_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q134", ('Full Set: Термобездносланец', 'Полный набор: Термобездносланец'), section="s6",
  deps=['q133'],
  icon="eternal_starlight:thermabysslate",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:thermabysslate"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q135", ('Full Set: Полированный термобездносланец', 'Полный набор: Полированный термобездносланец'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:polished_thermabysslate",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_thermabysslate"),
      item("eternal_starlight:polished_thermabysslate_bricks"),
      item("eternal_starlight:polished_thermabysslate_slab"),
      item("eternal_starlight:polished_thermabysslate_stairs"),
      item("eternal_starlight:polished_thermabysslate_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q136", ('Full Set: polished_thermabysslate_brick', 'Полный набор: polished_thermabysslate_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_thermabysslate_brick_slab"),
      item("eternal_starlight:polished_thermabysslate_brick_stairs"),
      item("eternal_starlight:polished_thermabysslate_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q137", ('Пустокамень: Base and Variants', 'Пустокамень: основа и варианты'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:voidstone",
  desc=[
      ('Базовый блок и его полированные/кирпичные/плиточные варианты.',
       'The base block and its polished/bricked/tiled variants.'),
      ('Формы — в следующем квесте.',
       'Shapes come in the next quest.'),
  ],
  tasks=[
      item("eternal_starlight:voidstone"),
      item("eternal_starlight:voidstone_deepsilver_ore"),
      item("eternal_starlight:voidstone_malarite_ore"),
      item("eternal_starlight:voidstone_redstone_ore"),
      item("eternal_starlight:voidstone_saltpeter_ore"),
      item("eternal_starlight:voidstone_spike"),
      item("eternal_starlight:voidstone_starcore_ore"),
      item("eternal_starlight:voidstone_starlit_diamond_ore"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q138", ('Пустокамень: Shapes', 'Пустокамень: формы'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:voidstone_stairs",
  desc=[
      ('Ступени, плиты и стены семейства: тройка строителя.',
       "Stairs, slabs and walls of the family: the builder's trio."),
      ('',
       ''),
  ],
  tasks=[
      item("eternal_starlight:voidstone_brick_slab"),
      item("eternal_starlight:voidstone_brick_stairs"),
      item("eternal_starlight:voidstone_brick_wall"),
      item("eternal_starlight:voidstone_slab"),
      item("eternal_starlight:voidstone_stairs"),
      item("eternal_starlight:voidstone_tile_slab"),
      item("eternal_starlight:voidstone_tile_stairs"),
      item("eternal_starlight:voidstone_tile_wall"),
      item("eternal_starlight:voidstone_wall"),
  ],
  rewards=[
      xpr(30),
  ]),

Q("q139", ('Full Set: Колотый пустокамень', 'Полный набор: Колотый пустокамень'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cobbled_voidstone",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:cobbled_voidstone"),
      item("eternal_starlight:cobbled_voidstone_slab"),
      item("eternal_starlight:cobbled_voidstone_stairs"),
      item("eternal_starlight:cobbled_voidstone_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q140", ('Full Set: Полированный пустокамень', 'Полный набор: Полированный пустокамень'), section="s6",
  deps=['q139'],
  icon="eternal_starlight:polished_voidstone",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_voidstone"),
      item("eternal_starlight:polished_voidstone_slab"),
      item("eternal_starlight:polished_voidstone_stairs"),
      item("eternal_starlight:polished_voidstone_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q141", ('Full Set: Пустокаменные кирпичи', 'Полный набор: Пустокаменные кирпичи'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:voidstone_bricks",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:voidstone_bricks"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q142", ('Full Set: Пустокаменный плитняк', 'Полный набор: Пустокаменный плитняк'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:voidstone_tiles",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:voidstone_tiles"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q143", ('Full Set: Радианит', 'Полный набор: Радианит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:radianite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:radianite"),
      item("eternal_starlight:radianite_brick_slab"),
      item("eternal_starlight:radianite_brick_stairs"),
      item("eternal_starlight:radianite_brick_wall"),
      item("eternal_starlight:radianite_slab"),
      item("eternal_starlight:radianite_stairs"),
      item("eternal_starlight:radianite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q144", ('Full Set: Колотый радианит', 'Полный набор: Колотый радианит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cobbled_radianite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:cobbled_radianite"),
      item("eternal_starlight:cobbled_radianite_slab"),
      item("eternal_starlight:cobbled_radianite_stairs"),
      item("eternal_starlight:cobbled_radianite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q145", ('Full Set: Полированный радианит', 'Полный набор: Полированный радианит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:polished_radianite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_radianite"),
      item("eternal_starlight:polished_radianite_slab"),
      item("eternal_starlight:polished_radianite_stairs"),
      item("eternal_starlight:polished_radianite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q146", ('Full Set: Радианитовые кирпичи', 'Полный набор: Радианитовые кирпичи'), section="s6",
  deps=['q145'],
  icon="eternal_starlight:radianite_bricks",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:radianite_bricks"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q147", ('Full Set: Радианитовая колонна', 'Полный набор: Радианитовая колонна'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:radianite_pillar",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:radianite_pillar"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q148", ('Full Set: Стеллагмит', 'Полный набор: Стеллагмит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:stellagmite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:stellagmite"),
      item("eternal_starlight:stellagmite_slab"),
      item("eternal_starlight:stellagmite_stairs"),
      item("eternal_starlight:stellagmite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q149", ('Full Set: Полированный стеллагмит', 'Полный набор: Полированный стеллагмит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:polished_stellagmite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_stellagmite"),
      item("eternal_starlight:polished_stellagmite_slab"),
      item("eternal_starlight:polished_stellagmite_stairs"),
      item("eternal_starlight:polished_stellagmite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q150", ('Full Set: Расплавленный стеллагмит', 'Полный набор: Расплавленный стеллагмит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:molten_stellagmite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:molten_stellagmite"),
      item("eternal_starlight:molten_stellagmite_slab"),
      item("eternal_starlight:molten_stellagmite_stairs"),
      item("eternal_starlight:molten_stellagmite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q151", ('Full Set: Истокамень', 'Полный набор: Истокамень'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:springstone",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:springstone"),
      item("eternal_starlight:springstone_bricks"),
      item("eternal_starlight:springstone_slab"),
      item("eternal_starlight:springstone_stairs"),
      item("eternal_starlight:springstone_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q152", ('Full Set: Полированный истокамень', 'Полный набор: Полированный истокамень'), section="s6",
  deps=['q151'],
  icon="eternal_starlight:polished_springstone",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_springstone"),
      item("eternal_starlight:polished_springstone_slab"),
      item("eternal_starlight:polished_springstone_stairs"),
      item("eternal_starlight:polished_springstone_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q153", ('Full Set: springstone_brick', 'Полный набор: springstone_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:springstone_brick_slab"),
      item("eternal_starlight:springstone_brick_stairs"),
      item("eternal_starlight:springstone_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q154", ('Full Set: Термальный истокамень', 'Полный набор: Термальный истокамень'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:thermal_springstone",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:thermal_springstone"),
      item("eternal_starlight:thermal_springstone_brick_slab"),
      item("eternal_starlight:thermal_springstone_brick_stairs"),
      item("eternal_starlight:thermal_springstone_brick_wall"),
      item("eternal_starlight:thermal_springstone_slab"),
      item("eternal_starlight:thermal_springstone_stairs"),
      item("eternal_starlight:thermal_springstone_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q155", ('Full Set: Термально-истокаменные кирпичи', 'Полный набор: Термально-истокаменные кирпичи'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:thermal_springstone_bricks",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:thermal_springstone_bricks"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q156", ('Full Set: Токсит', 'Полный набор: Токсит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:toxite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:toxite"),
      item("eternal_starlight:toxite_brick_slab"),
      item("eternal_starlight:toxite_brick_stairs"),
      item("eternal_starlight:toxite_brick_wall"),
      item("eternal_starlight:toxite_slab"),
      item("eternal_starlight:toxite_stairs"),
      item("eternal_starlight:toxite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q157", ('Full Set: Полированный токсит', 'Полный набор: Полированный токсит'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:polished_toxite",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_toxite"),
      item("eternal_starlight:polished_toxite_slab"),
      item("eternal_starlight:polished_toxite_stairs"),
      item("eternal_starlight:polished_toxite_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q158", ('Full Set: Токситовые кирпичи', 'Полный набор: Токситовые кирпичи'), section="s6",
  deps=['q157'],
  icon="eternal_starlight:toxite_bricks",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:toxite_bricks"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q159", ('Full Set: doomeden_brick', 'Полный набор: doomeden_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:doomeden_brick_slab"),
      item("eternal_starlight:doomeden_brick_stairs"),
      item("eternal_starlight:doomeden_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q160", ('Full Set: polished_doomeden_brick', 'Полный набор: polished_doomeden_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:polished_doomeden_brick_slab"),
      item("eternal_starlight:polished_doomeden_brick_stairs"),
      item("eternal_starlight:polished_doomeden_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q161", ('Full Set: doomeden_tile', 'Полный набор: doomeden_tile'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:doomeden_tile_slab"),
      item("eternal_starlight:doomeden_tile_stairs"),
      item("eternal_starlight:doomeden_tile_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q162", ('Full Set: nightfall_mud_brick', 'Полный набор: nightfall_mud_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:nightfall_mud_brick_slab"),
      item("eternal_starlight:nightfall_mud_brick_stairs"),
      item("eternal_starlight:nightfall_mud_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q163", ('Full Set: dusted_brick', 'Полный набор: dusted_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:dusted_brick_slab"),
      item("eternal_starlight:dusted_brick_stairs"),
      item("eternal_starlight:dusted_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q164", ('Full Set: eternal_ice_brick', 'Полный набор: eternal_ice_brick'), section="s6",
  deps=['q163'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:eternal_ice_brick_slab"),
      item("eternal_starlight:eternal_ice_brick_stairs"),
      item("eternal_starlight:eternal_ice_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q165", ('Full Set: haze_ice_brick', 'Полный набор: haze_ice_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:haze_ice_brick_slab"),
      item("eternal_starlight:haze_ice_brick_stairs"),
      item("eternal_starlight:haze_ice_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q166", ('Full Set: flare_brick', 'Полный набор: flare_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:flare_brick",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:flare_brick_slab"),
      item("eternal_starlight:flare_brick_stairs"),
      item("eternal_starlight:flare_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q167", ('Full Set: cut_flare_brick', 'Полный набор: cut_flare_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:cut_flare_brick_slab"),
      item("eternal_starlight:cut_flare_brick_stairs"),
      item("eternal_starlight:cut_flare_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q168", ('Full Set: flare_tile', 'Полный набор: flare_tile'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:flare_tile_slab"),
      item("eternal_starlight:flare_tile_stairs"),
      item("eternal_starlight:flare_tile_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q169", ('Full Set: cut_flare_tile', 'Полный набор: cut_flare_tile'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:cut_flare_tile_slab"),
      item("eternal_starlight:cut_flare_tile_stairs"),
      item("eternal_starlight:cut_flare_tile_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q170", ('Full Set: nebulaite_brick', 'Полный набор: nebulaite_brick'), section="s6",
  deps=['q169'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:nebulaite_brick_slab"),
      item("eternal_starlight:nebulaite_brick_stairs"),
      item("eternal_starlight:nebulaite_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q171", ('Full Set: amaramber_brick', 'Полный набор: amaramber_brick'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_brick_slab"),
      item("eternal_starlight:amaramber_brick_stairs"),
      item("eternal_starlight:amaramber_brick_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q172", ('Full Set: tooth_of_hunger_tile', 'Полный набор: tooth_of_hunger_tile'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:tooth_of_hunger_tile_slab"),
      item("eternal_starlight:tooth_of_hunger_tile_stairs"),
      item("eternal_starlight:tooth_of_hunger_tile_wall"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q173", ('Full Set: Лунная мозаика', 'Полный набор: Лунная мозаика'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:lunar_mosaic",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:lunar_mosaic"),
      item("eternal_starlight:lunar_mosaic_fence"),
      item("eternal_starlight:lunar_mosaic_fence_gate"),
      item("eternal_starlight:lunar_mosaic_slab"),
      item("eternal_starlight:lunar_mosaic_stairs"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q174", ('golem_steel: Base and Variants', 'golem_steel: основа и варианты'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Базовый блок и его полированные/кирпичные/плиточные варианты.',
       'The base block and its polished/bricked/tiled variants.'),
      ('Формы — в следующем квесте.',
       'Shapes come in the next quest.'),
  ],
  tasks=[
      item("eternal_starlight:golem_steel_bars"),
      item("eternal_starlight:golem_steel_block"),
      item("eternal_starlight:golem_steel_crate"),
      item("eternal_starlight:golem_steel_grate"),
      item("eternal_starlight:golem_steel_jet"),
      item("eternal_starlight:golem_steel_pillar"),
      item("eternal_starlight:golem_steel_tiles"),
  ],
  rewards=[
      xpr(35),
  ]),

Q("q175", ('golem_steel: Shapes', 'golem_steel: формы'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:golem_steel_stairs",
  desc=[
      ('Ступени, плиты и стены семейства: тройка строителя.',
       "Stairs, slabs and walls of the family: the builder's trio."),
      ('',
       ''),
  ],
  tasks=[
      item("eternal_starlight:golem_steel_slab"),
      item("eternal_starlight:golem_steel_stairs"),
  ],
  rewards=[
      xpr(30),
  ]),

Q("q176", ('Full Set: golem_steel_tile', 'Полный набор: golem_steel_tile'), section="s6",
  deps=['q175'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:golem_steel_tile_slab"),
      item("eternal_starlight:golem_steel_tile_stairs"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q177", ('Full Set: oxidized_golem_steel', 'Полный набор: oxidized_golem_steel'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:oxidized_golem_steel_bars"),
      item("eternal_starlight:oxidized_golem_steel_block"),
      item("eternal_starlight:oxidized_golem_steel_grate"),
      item("eternal_starlight:oxidized_golem_steel_jet"),
      item("eternal_starlight:oxidized_golem_steel_pillar"),
      item("eternal_starlight:oxidized_golem_steel_tiles"),
      item("eternal_starlight:oxidized_golem_steel_slab"),
      item("eternal_starlight:oxidized_golem_steel_stairs"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q178", ('Full Set: oxidized_golem_steel_tile', 'Полный набор: oxidized_golem_steel_tile'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond",
  desc=[
      ('Всё семейство блоков: основа, варианты и формы — ничего не потеряно.',
       'Every block of the family: base, variants and shapes - nothing lost.'),
      ('Строители считают наборами, а не блоками.',
       'Builders count sets, not blocks.'),
  ],
  tasks=[
      item("eternal_starlight:oxidized_golem_steel_tile_slab"),
      item("eternal_starlight:oxidized_golem_steel_tile_stairs"),
  ],
  rewards=[
      xpr(45),
  ]),

Q("q179", ('Crystals and Clusters', 'Кристаллы и друзы'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:blazing_starcore_block",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:blazing_starcore_block"),
      item("eternal_starlight:blooming_blue_starlight_crystal_cluster"),
      item("eternal_starlight:blooming_red_starlight_crystal_cluster"),
      item("eternal_starlight:blue_starlight_crystal_block"),
      item("eternal_starlight:blue_starlight_crystal_cluster"),
      item("eternal_starlight:blue_starlight_crystal_lantern"),
      item("eternal_starlight:eternal_ice_deepsilver_ore"),
      item("eternal_starlight:eternal_ice_redstone_ore"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q180", ('Crystals and Clusters · 2', 'Кристаллы и друзы · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:eternal_ice_saltpeter_ore",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:eternal_ice_saltpeter_ore"),
      item("eternal_starlight:eternal_ice_starcore_ore"),
      item("eternal_starlight:eternal_ice_starlit_diamond_ore"),
      item("eternal_starlight:haze_ice_deepsilver_ore"),
      item("eternal_starlight:haze_ice_redstone_ore"),
      item("eternal_starlight:haze_ice_saltpeter_ore"),
      item("eternal_starlight:haze_ice_starcore_ore"),
      item("eternal_starlight:haze_ice_starlit_diamond_ore"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q181", ('Crystals and Clusters · 3', 'Кристаллы и друзы · 3'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:nightfall_mud_deepsilver_ore",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:nightfall_mud_deepsilver_ore"),
      item("eternal_starlight:nightfall_mud_malarite_ore"),
      item("eternal_starlight:packed_nightfall_mud_deepsilver_ore"),
      item("eternal_starlight:packed_nightfall_mud_malarite_ore"),
      item("eternal_starlight:raw_aethersent_block"),
      item("eternal_starlight:raw_amaramber_block"),
      item("eternal_starlight:raw_deepsilver_block"),
      item("eternal_starlight:raw_flowglaze"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q182", ('Crystals and Clusters · 4', 'Кристаллы и друзы · 4'), section="s6",
  deps=['q181'],
  icon="eternal_starlight:red_starlight_crystal_block",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:red_starlight_crystal_block"),
      item("eternal_starlight:red_starlight_crystal_cluster"),
      item("eternal_starlight:red_starlight_crystal_lantern"),
      item("eternal_starlight:starcore_block"),
      item("eternal_starlight:starlit_diamond_block"),
      item("eternal_starlight:thioquartz_block"),
      item("eternal_starlight:unrealium_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q183", ('Light of the Night', 'Свет ночи'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:acacia_starfire_bird_aviary",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:acacia_starfire_bird_aviary"),
      item("eternal_starlight:amaramber_candle"),
      item("eternal_starlight:amaramber_lantern"),
      item("eternal_starlight:bamboo_starfire_bird_aviary"),
      item("eternal_starlight:banyin_starfire_bird_aviary"),
      item("eternal_starlight:birch_starfire_bird_aviary"),
      item("eternal_starlight:cherry_starfire_bird_aviary"),
      item("eternal_starlight:cradlewood_starfire_bird_aviary"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q184", ('Light of the Night · 2', 'Свет ночи · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:crimson_starfire_bird_aviary",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:crimson_starfire_bird_aviary"),
      item("eternal_starlight:dark_oak_starfire_bird_aviary"),
      item("eternal_starlight:doomed_redstone_torch"),
      item("eternal_starlight:doomed_torch"),
      item("eternal_starlight:doomeden_light"),
      item("eternal_starlight:dusk_light"),
      item("eternal_starlight:eternal_ice_lantern"),
      item("eternal_starlight:gloomcandle_root"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q185", ('Light of the Night · 3', 'Свет ночи · 3'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:haze_ice_lantern",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:haze_ice_lantern"),
      item("eternal_starlight:jinglestem_starfire_bird_aviary"),
      item("eternal_starlight:jungle_starfire_bird_aviary"),
      item("eternal_starlight:lunar_starfire_bird_aviary"),
      item("eternal_starlight:lunaris_cactus_fruit_lantern"),
      item("eternal_starlight:mangrove_starfire_bird_aviary"),
      item("eternal_starlight:northland_starfire_bird_aviary"),
      item("eternal_starlight:oak_starfire_bird_aviary"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q186", ('Light of the Night · 4', 'Свет ночи · 4'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:orbflora_light",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:orbflora_light"),
      item("eternal_starlight:reinforced_dusk_light"),
      item("eternal_starlight:sacred_lanternvine"),
      item("eternal_starlight:scarlet_starfire_bird_aviary"),
      item("eternal_starlight:spruce_starfire_bird_aviary"),
      item("eternal_starlight:starcore_light"),
      item("eternal_starlight:starfire_bird_nest"),
      item("eternal_starlight:starlight_torchflower"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q187", ('Light of the Night · 5', 'Свет ночи · 5'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:torreya_starfire_bird_aviary",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:torreya_starfire_bird_aviary"),
      item("eternal_starlight:warped_starfire_bird_aviary"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q188", ('Ice and Frost', 'Лёд и стужа'), section="s6",
  deps=['q187'],
  icon="eternal_starlight:eternal_ice",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:eternal_ice"),
      item("eternal_starlight:eternal_ice_bricks"),
      item("eternal_starlight:flowglaze_pane"),
      item("eternal_starlight:haze_ice"),
      item("eternal_starlight:haze_ice_bricks"),
      item("eternal_starlight:permafrost_spawner"),
      item("eternal_starlight:reinforced_ice"),
      item("eternal_starlight:reinforced_ice_pane"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q189", ('Ice and Frost · 2', 'Лёд и стужа · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:thin_eternal_ice",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:thin_eternal_ice"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q190", ('Flora of the Forests', 'Флора лесов'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:amaramber_grass",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:amaramber_grass"),
      item("eternal_starlight:amaramber_grass_bush"),
      item("eternal_starlight:amethysia_grass"),
      item("eternal_starlight:aureate_flower"),
      item("eternal_starlight:blazebank_grass"),
      item("eternal_starlight:blooming_shadegrieve"),
      item("eternal_starlight:blue_crystal_moss_block"),
      item("eternal_starlight:blue_crystal_moss_carpet"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q191", ('Flora of the Forests · 2', 'Флора лесов · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:bouldershroom",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:bouldershroom"),
      item("eternal_starlight:bouldershroom_block"),
      item("eternal_starlight:bouldershroom_roots"),
      item("eternal_starlight:bouldershroom_stem"),
      item("eternal_starlight:cave_moss"),
      item("eternal_starlight:cave_moss_block"),
      item("eternal_starlight:cave_moss_carpet"),
      item("eternal_starlight:chiseled_twilight_sandstone"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q192", ('Flora of the Forests · 3', 'Флора лесов · 3'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:conebloom",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:conebloom"),
      item("eternal_starlight:crescent_grass"),
      item("eternal_starlight:crystallized_lunar_grass"),
      item("eternal_starlight:crystallized_sand"),
      item("eternal_starlight:cut_twilight_sandstone"),
      item("eternal_starlight:cut_twilight_sandstone_slab"),
      item("eternal_starlight:cut_twilight_sandstone_stairs"),
      item("eternal_starlight:cut_twilight_sandstone_wall"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q193", ('Flora of the Forests · 4', 'Флора лесов · 4'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:dead_lunar_bush",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:dead_lunar_bush"),
      item("eternal_starlight:dusted_gravel"),
      item("eternal_starlight:fantasy_grass_block"),
      item("eternal_starlight:fantasy_grass_carpet"),
      item("eternal_starlight:glimmerfly_bush"),
      item("eternal_starlight:glowing_crescent_grass"),
      item("eternal_starlight:glowing_lunar_bush"),
      item("eternal_starlight:glowing_lunar_grass"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q194", ('Flora of the Forests · 5', 'Флора лесов · 5'), section="s6",
  deps=['q193'],
  icon="eternal_starlight:glowing_mossy_dusted_gravel",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:glowing_mossy_dusted_gravel"),
      item("eternal_starlight:glowing_mushroom"),
      item("eternal_starlight:glowing_mushroom_block"),
      item("eternal_starlight:glowing_mushroom_stem"),
      item("eternal_starlight:glowing_night_sprouts"),
      item("eternal_starlight:glowing_nightfall_mud"),
      item("eternal_starlight:glowing_parasol_grass"),
      item("eternal_starlight:golden_grass"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q195", ('Flora of the Forests · 6', 'Флора лесов · 6'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:golden_grass_block",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:golden_grass_block"),
      item("eternal_starlight:lunar_bush"),
      item("eternal_starlight:lunar_grass"),
      item("eternal_starlight:moonlight_bush"),
      item("eternal_starlight:mossy_dusted_gravel"),
      item("eternal_starlight:muddy_banyin_roots"),
      item("eternal_starlight:night_sprouts"),
      item("eternal_starlight:nightfall_dirt"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q196", ('Flora of the Forests · 7', 'Флора лесов · 7'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:nightfall_dirt_path",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:nightfall_dirt_path"),
      item("eternal_starlight:nightfall_grass_block"),
      item("eternal_starlight:nightfall_mud"),
      item("eternal_starlight:nightfall_mud_bricks"),
      item("eternal_starlight:nightfan_bush"),
      item("eternal_starlight:packed_nightfall_mud"),
      item("eternal_starlight:parasol_grass"),
      item("eternal_starlight:pink_rose"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q197", ('Flora of the Forests · 8', 'Флора лесов · 8'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:pink_rose_bush",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:pink_rose_bush"),
      item("eternal_starlight:red_crystal_moss_block"),
      item("eternal_starlight:red_crystal_moss_carpet"),
      item("eternal_starlight:red_velvetumoss_flower"),
      item("eternal_starlight:sacred_starlight_flower"),
      item("eternal_starlight:scarlet_grass"),
      item("eternal_starlight:shining_mushroom"),
      item("eternal_starlight:shining_mushroom_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q198", ('Flora of the Forests · 9', 'Флора лесов · 9'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:shining_mushroom_stem",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:shining_mushroom_stem"),
      item("eternal_starlight:small_glowing_night_sprouts"),
      item("eternal_starlight:small_night_sprouts"),
      item("eternal_starlight:starlight_flower"),
      item("eternal_starlight:stellafly_bush"),
      item("eternal_starlight:sunset_thornbloom"),
      item("eternal_starlight:suspicious_dusted_gravel"),
      item("eternal_starlight:swamp_rose"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q199", ('Flora of the Forests · 10', 'Флора лесов · 10'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:tall_crescent_grass",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:tall_crescent_grass"),
      item("eternal_starlight:tall_glowing_crescent_grass"),
      item("eternal_starlight:tall_golden_grass"),
      item("eternal_starlight:tenacious_nightfall_grass_block"),
      item("eternal_starlight:torreya_vines"),
      item("eternal_starlight:twilight_sand"),
      item("eternal_starlight:twilight_sandstone"),
      item("eternal_starlight:twilight_sandstone_slab"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q200", ('Flora of the Forests · 11', 'Флора лесов · 11'), section="s6",
  deps=['q199'],
  icon="eternal_starlight:twilight_sandstone_stairs",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:twilight_sandstone_stairs"),
      item("eternal_starlight:twilight_sandstone_wall"),
      item("eternal_starlight:whisperbloom"),
      item("eternal_starlight:wick_grass"),
      item("eternal_starlight:withered_starlight_flower"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q201", ('Flora of the Seas', 'Флора морей'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:crystallum_coral",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:crystallum_coral"),
      item("eternal_starlight:crystallum_coral_block"),
      item("eternal_starlight:crystallum_coral_fan"),
      item("eternal_starlight:dead_crystallum_coral"),
      item("eternal_starlight:dead_crystallum_coral_block"),
      item("eternal_starlight:dead_crystallum_coral_fan"),
      item("eternal_starlight:dead_golden_coral"),
      item("eternal_starlight:dead_golden_coral_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q202", ('Flora of the Seas · 2', 'Флора морей · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:dead_golden_coral_fan",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:dead_golden_coral_fan"),
      item("eternal_starlight:dead_tentacles_coral"),
      item("eternal_starlight:dead_tentacles_coral_block"),
      item("eternal_starlight:dead_tentacles_coral_fan"),
      item("eternal_starlight:golden_coral"),
      item("eternal_starlight:golden_coral_block"),
      item("eternal_starlight:golden_coral_fan"),
      item("eternal_starlight:moonlight_lily_pad"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q203", ('Flora of the Seas · 3', 'Флора морей · 3'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:spiral_kelp",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:spiral_kelp"),
      item("eternal_starlight:starlight_seagrass"),
      item("eternal_starlight:starlit_lily_pad"),
      item("eternal_starlight:tentacles_coral"),
      item("eternal_starlight:tentacles_coral_block"),
      item("eternal_starlight:tentacles_coral_fan"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q204", ('Yeti Furs and Carpets', 'Мех йети и ковры'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:black_yeti_fur",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:black_yeti_fur"),
      item("eternal_starlight:black_yeti_fur_carpet"),
      item("eternal_starlight:blue_yeti_fur"),
      item("eternal_starlight:blue_yeti_fur_carpet"),
      item("eternal_starlight:brown_yeti_fur"),
      item("eternal_starlight:brown_yeti_fur_carpet"),
      item("eternal_starlight:cyan_yeti_fur"),
      item("eternal_starlight:cyan_yeti_fur_carpet"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q205", ('Yeti Furs and Carpets · 2', 'Мех йети и ковры · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:gray_yeti_fur",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:gray_yeti_fur"),
      item("eternal_starlight:gray_yeti_fur_carpet"),
      item("eternal_starlight:green_yeti_fur"),
      item("eternal_starlight:green_yeti_fur_carpet"),
      item("eternal_starlight:light_blue_yeti_fur"),
      item("eternal_starlight:light_blue_yeti_fur_carpet"),
      item("eternal_starlight:light_gray_yeti_fur"),
      item("eternal_starlight:light_gray_yeti_fur_carpet"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q206", ('Yeti Furs and Carpets · 3', 'Мех йети и ковры · 3'), section="s6",
  deps=['q205'],
  icon="eternal_starlight:lime_yeti_fur",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:lime_yeti_fur"),
      item("eternal_starlight:lime_yeti_fur_carpet"),
      item("eternal_starlight:magenta_yeti_fur"),
      item("eternal_starlight:magenta_yeti_fur_carpet"),
      item("eternal_starlight:orange_yeti_fur"),
      item("eternal_starlight:orange_yeti_fur_carpet"),
      item("eternal_starlight:pink_yeti_fur"),
      item("eternal_starlight:pink_yeti_fur_carpet"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q207", ('Yeti Furs and Carpets · 4', 'Мех йети и ковры · 4'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:purple_yeti_fur",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:purple_yeti_fur"),
      item("eternal_starlight:purple_yeti_fur_carpet"),
      item("eternal_starlight:red_yeti_fur"),
      item("eternal_starlight:red_yeti_fur_carpet"),
      item("eternal_starlight:white_yeti_fur"),
      item("eternal_starlight:white_yeti_fur_carpet"),
      item("eternal_starlight:yellow_yeti_fur"),
      item("eternal_starlight:yellow_yeti_fur_carpet"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q208", ('Mechanisms and Storage', 'Механизмы и хранение'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:abyssal_geyser",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:abyssal_geyser"),
      item("eternal_starlight:abyssal_magma_block"),
      item("eternal_starlight:alloy_furnace"),
      item("eternal_starlight:amaramber_bricks"),
      item("eternal_starlight:charged_chiseled_polished_doomeden_bricks"),
      item("eternal_starlight:chiseled_flare_pillar"),
      item("eternal_starlight:chiseled_golem_steel_block"),
      item("eternal_starlight:chiseled_grimstone"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q209", ('Mechanisms and Storage · 2', 'Механизмы и хранение · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:chiseled_nebulaite_bricks",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:chiseled_nebulaite_bricks"),
      item("eternal_starlight:chiseled_polished_abysslate"),
      item("eternal_starlight:chiseled_polished_cryobysslate"),
      item("eternal_starlight:chiseled_polished_doomeden_bricks"),
      item("eternal_starlight:chiseled_polished_thermabysslate"),
      item("eternal_starlight:chiseled_radianite"),
      item("eternal_starlight:chiseled_springstone"),
      item("eternal_starlight:chiseled_tooth_of_hunger_tiles"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q210", ('Mechanisms and Storage · 3', 'Механизмы и хранение · 3'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:chiseled_toxite",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:chiseled_toxite"),
      item("eternal_starlight:chiseled_voidstone"),
      item("eternal_starlight:cracked_grimstone_bricks"),
      item("eternal_starlight:cracked_grimstone_tiles"),
      item("eternal_starlight:cracked_voidstone_bricks"),
      item("eternal_starlight:cracked_voidstone_tiles"),
      item("eternal_starlight:cryobyssal_geyser"),
      item("eternal_starlight:cryobyssal_magma_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q211", ('Mechanisms and Storage · 4', 'Механизмы и хранение · 4'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:crystalborn_catalyst",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:crystalborn_catalyst"),
      item("eternal_starlight:cut_flare_bricks"),
      item("eternal_starlight:cut_flare_tiles"),
      item("eternal_starlight:deepsilver_bars"),
      item("eternal_starlight:deepsilver_grate"),
      item("eternal_starlight:doomeden_bricks"),
      item("eternal_starlight:doomeden_keyhole"),
      item("eternal_starlight:doomeden_tiles"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q212", ('Mechanisms and Storage · 5', 'Механизмы и хранение · 5'), section="s6",
  deps=['q211'],
  icon="eternal_starlight:dusted_bricks",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:dusted_bricks"),
      item("eternal_starlight:flare_bricks"),
      item("eternal_starlight:flare_tiles"),
      item("eternal_starlight:flowglaze_bricks"),
      item("eternal_starlight:nebulaite_bricks"),
      item("eternal_starlight:oxidized_alloy_furnace"),
      item("eternal_starlight:oxidized_chiseled_golem_steel_block"),
      item("eternal_starlight:polished_doomeden_bricks"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q213", ('Mechanisms and Storage · 6', 'Механизмы и хранение · 6'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:redstone_doomeden_keyhole",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:redstone_doomeden_keyhole"),
      item("eternal_starlight:thermabyssal_geyser"),
      item("eternal_starlight:thermabyssal_magma_block"),
      item("eternal_starlight:tooth_of_hunger_tiles"),
      item("eternal_starlight:torreya_tiles"),
      item("eternal_starlight:unrealium_bars"),
      item("eternal_starlight:waxed_alloy_furnace"),
      item("eternal_starlight:waxed_chiseled_golem_steel_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q214", ('Mechanisms and Storage · 7', 'Механизмы и хранение · 7'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:waxed_golem_steel_bars",
  desc=[
      ('Блоки темы: каждый из них в этом квесте или его томах.',
       'Blocks of the theme: every one of them is in this quest or its volumes.'),
      ('Ни один блок мода не потерян — энциклопедия проверяет.',
       'Not a single block of the mod is lost - the encyclopaedia checks it.'),
  ],
  tasks=[
      item("eternal_starlight:waxed_golem_steel_bars"),
      item("eternal_starlight:waxed_golem_steel_grate"),
      item("eternal_starlight:waxed_golem_steel_jet"),
      item("eternal_starlight:waxed_golem_steel_pillar"),
      item("eternal_starlight:waxed_golem_steel_tiles"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q215", ('And Other Blocks', 'И прочие блоки'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:accumulator",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:accumulator"),
      item("eternal_starlight:aethersent_block"),
      item("eternal_starlight:algaleaves"),
      item("eternal_starlight:ashen_snow"),
      item("eternal_starlight:banyin_button"),
      item("eternal_starlight:banyin_door"),
      item("eternal_starlight:banyin_fence"),
      item("eternal_starlight:banyin_fence_gate"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q216", ('And Other Blocks · 2', 'И прочие блоки · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:banyin_hanging_sign",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:banyin_hanging_sign"),
      item("eternal_starlight:banyin_leaves"),
      item("eternal_starlight:banyin_log"),
      item("eternal_starlight:banyin_planks"),
      item("eternal_starlight:banyin_pressure_plate"),
      item("eternal_starlight:banyin_roots"),
      item("eternal_starlight:banyin_sapling"),
      item("eternal_starlight:banyin_sign"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q217", ('And Other Blocks · 3', 'И прочие блоки · 3'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:banyin_slab",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:banyin_slab"),
      item("eternal_starlight:banyin_stairs"),
      item("eternal_starlight:banyin_trapdoor"),
      item("eternal_starlight:banyin_wood"),
      item("eternal_starlight:blue_crystal_roots"),
      item("eternal_starlight:blue_crystalfleur"),
      item("eternal_starlight:blue_crystalfleur_vine"),
      item("eternal_starlight:blue_crystallized_lunar_log"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q218", ('And Other Blocks · 4', 'И прочие блоки · 4'), section="s6",
  deps=['q217'],
  icon="eternal_starlight:budding_thioquartz",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:budding_thioquartz"),
      item("eternal_starlight:carved_lunaris_cactus_fruit"),
      item("eternal_starlight:circulush"),
      item("eternal_starlight:cradlewood_button"),
      item("eternal_starlight:cradlewood_door"),
      item("eternal_starlight:cradlewood_fence"),
      item("eternal_starlight:cradlewood_fence_gate"),
      item("eternal_starlight:cradlewood_hanging_sign"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q219", ('And Other Blocks · 5', 'И прочие блоки · 5'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cradlewood_leaves",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:cradlewood_leaves"),
      item("eternal_starlight:cradlewood_log"),
      item("eternal_starlight:cradlewood_planks"),
      item("eternal_starlight:cradlewood_pressure_plate"),
      item("eternal_starlight:cradlewood_sapling"),
      item("eternal_starlight:cradlewood_sign"),
      item("eternal_starlight:cradlewood_slab"),
      item("eternal_starlight:cradlewood_stairs"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q220", ('And Other Blocks · 6', 'И прочие блоки · 6'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cradlewood_trapdoor",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:cradlewood_trapdoor"),
      item("eternal_starlight:cradlewood_wood"),
      item("eternal_starlight:crescentleaf"),
      item("eternal_starlight:crinoa"),
      item("eternal_starlight:crinoa_bale"),
      item("eternal_starlight:cyan_lunar_leaves"),
      item("eternal_starlight:dead_lunar_log"),
      item("eternal_starlight:deepsilver_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q221", ('And Other Blocks · 7', 'И прочие блоки · 7'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:desert_amethysia",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:desert_amethysia"),
      item("eternal_starlight:dimslag"),
      item("eternal_starlight:drying_rack"),
      item("eternal_starlight:dusk_emitter"),
      item("eternal_starlight:dusk_glass"),
      item("eternal_starlight:dusk_lockbox"),
      item("eternal_starlight:eclipse_core"),
      item("eternal_starlight:energy_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q222", ('And Other Blocks · 8', 'И прочие блоки · 8'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:energy_transmitter",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:energy_transmitter"),
      item("eternal_starlight:fantabud"),
      item("eternal_starlight:fantafern"),
      item("eternal_starlight:fantagrass"),
      item("eternal_starlight:fire_orchid"),
      item("eternal_starlight:flare_spawner"),
      item("eternal_starlight:flowglaze"),
      item("eternal_starlight:flowglaze_brick_slab"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q223", ('And Other Blocks · 9', 'И прочие блоки · 9'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:flowglaze_brick_stairs",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:flowglaze_brick_stairs"),
      item("eternal_starlight:flowglaze_brick_wall"),
      item("eternal_starlight:glacite"),
      item("eternal_starlight:glacite_block"),
      item("eternal_starlight:gladespike"),
      item("eternal_starlight:glintgrass"),
      item("eternal_starlight:gloreed"),
      item("eternal_starlight:glowing_grimstone"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q224", ('And Other Blocks · 10', 'И прочие блоки · 10'), section="s6",
  deps=['q223'],
  icon="eternal_starlight:glowing_voidstone",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:glowing_voidstone"),
      item("eternal_starlight:glowlis"),
      item("eternal_starlight:green_fantabud"),
      item("eternal_starlight:green_fantafern"),
      item("eternal_starlight:green_fantagrass"),
      item("eternal_starlight:hanging_algaleaves"),
      item("eternal_starlight:hanging_fantagrass"),
      item("eternal_starlight:icicle"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q225", ('And Other Blocks · 11', 'И прочие блоки · 11'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:jinglestem_button",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:jinglestem_button"),
      item("eternal_starlight:jinglestem_door"),
      item("eternal_starlight:jinglestem_fence"),
      item("eternal_starlight:jinglestem_fence_gate"),
      item("eternal_starlight:jinglestem_hanging_sign"),
      item("eternal_starlight:jinglestem_log"),
      item("eternal_starlight:jinglestem_planks"),
      item("eternal_starlight:jinglestem_pressure_plate"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q226", ('And Other Blocks · 12', 'И прочие блоки · 12'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:jinglestem_sapling",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:jinglestem_sapling"),
      item("eternal_starlight:jinglestem_sign"),
      item("eternal_starlight:jinglestem_slab"),
      item("eternal_starlight:jinglestem_stairs"),
      item("eternal_starlight:jinglestem_trapdoor"),
      item("eternal_starlight:jinglestem_wood"),
      item("eternal_starlight:jingling_pickle"),
      item("eternal_starlight:loot_chest"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q227", ('And Other Blocks · 13', 'И прочие блоки · 13'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:lumenstem",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:lumenstem"),
      item("eternal_starlight:luminis"),
      item("eternal_starlight:lunar_button"),
      item("eternal_starlight:lunar_door"),
      item("eternal_starlight:lunar_fence"),
      item("eternal_starlight:lunar_fence_gate"),
      item("eternal_starlight:lunar_hanging_sign"),
      item("eternal_starlight:lunar_leaves"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q228", ('And Other Blocks · 14', 'И прочие блоки · 14'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:lunar_log",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:lunar_log"),
      item("eternal_starlight:lunar_mat"),
      item("eternal_starlight:lunar_monstrosity_spawner"),
      item("eternal_starlight:lunar_planks"),
      item("eternal_starlight:lunar_pressure_plate"),
      item("eternal_starlight:lunar_reed"),
      item("eternal_starlight:lunar_sapling"),
      item("eternal_starlight:lunar_sign"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q229", ('And Other Blocks · 15', 'И прочие блоки · 15'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:lunar_slab",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:lunar_slab"),
      item("eternal_starlight:lunar_stairs"),
      item("eternal_starlight:lunar_trapdoor"),
      item("eternal_starlight:lunar_vine"),
      item("eternal_starlight:lunar_wood"),
      item("eternal_starlight:lunaris_cactus"),
      item("eternal_starlight:lunaris_cactus_gel_block"),
      item("eternal_starlight:malarite_block"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q230", ('And Other Blocks · 16', 'И прочие блоки · 16'), section="s6",
  deps=['q229'],
  icon="eternal_starlight:marimold",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:marimold"),
      item("eternal_starlight:marimold_block"),
      item("eternal_starlight:marimold_stem"),
      item("eternal_starlight:mauve_fern"),
      item("eternal_starlight:mechanical_spawner"),
      item("eternal_starlight:moonlight_duckweed"),
      item("eternal_starlight:nebulaite"),
      item("eternal_starlight:nightfall_farmland"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q231", ('And Other Blocks · 17', 'И прочие блоки · 17'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:nightfall_podzol",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:nightfall_podzol"),
      item("eternal_starlight:nightfan"),
      item("eternal_starlight:northland_button"),
      item("eternal_starlight:northland_door"),
      item("eternal_starlight:northland_fence"),
      item("eternal_starlight:northland_fence_gate"),
      item("eternal_starlight:northland_hanging_sign"),
      item("eternal_starlight:northland_leaves"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q232", ('And Other Blocks · 18', 'И прочие блоки · 18'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:northland_log",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:northland_log"),
      item("eternal_starlight:northland_planks"),
      item("eternal_starlight:northland_pressure_plate"),
      item("eternal_starlight:northland_sapling"),
      item("eternal_starlight:northland_sign"),
      item("eternal_starlight:northland_slab"),
      item("eternal_starlight:northland_stairs"),
      item("eternal_starlight:northland_trapdoor"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q233", ('And Other Blocks · 19', 'И прочие блоки · 19'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:northland_wood",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:northland_wood"),
      item("eternal_starlight:orange_scarlet_bud"),
      item("eternal_starlight:orbflora"),
      item("eternal_starlight:purple_lunar_leaves"),
      item("eternal_starlight:purple_scarlet_bud"),
      item("eternal_starlight:red_crystal_roots"),
      item("eternal_starlight:red_crystalfleur"),
      item("eternal_starlight:red_crystalfleur_vine"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q234", ('And Other Blocks · 20', 'И прочие блоки · 20'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:red_crystallized_lunar_log",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:red_crystallized_lunar_log"),
      item("eternal_starlight:red_scarlet_bud"),
      item("eternal_starlight:red_velvetumoss"),
      item("eternal_starlight:red_velvetumoss_villi"),
      item("eternal_starlight:saltpeter_block"),
      item("eternal_starlight:scarlet_button"),
      item("eternal_starlight:scarlet_door"),
      item("eternal_starlight:scarlet_fence"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q235", ('And Other Blocks · 21', 'И прочие блоки · 21'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:scarlet_fence_gate",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:scarlet_fence_gate"),
      item("eternal_starlight:scarlet_hanging_sign"),
      item("eternal_starlight:scarlet_leaves"),
      item("eternal_starlight:scarlet_leaves_pile"),
      item("eternal_starlight:scarlet_log"),
      item("eternal_starlight:scarlet_planks"),
      item("eternal_starlight:scarlet_pressure_plate"),
      item("eternal_starlight:scarlet_sapling"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q236", ('And Other Blocks · 22', 'И прочие блоки · 22'), section="s6",
  deps=['q235'],
  icon="eternal_starlight:scarlet_sign",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:scarlet_sign"),
      item("eternal_starlight:scarlet_slab"),
      item("eternal_starlight:scarlet_stairs"),
      item("eternal_starlight:scarlet_trapdoor"),
      item("eternal_starlight:scarlet_wood"),
      item("eternal_starlight:sea_rosa"),
      item("eternal_starlight:shadegrieve"),
      item("eternal_starlight:solar_egg"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q237", ('And Other Blocks · 23', 'И прочие блоки · 23'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlight_golem_spawner",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:starlight_golem_spawner"),
      item("eternal_starlight:stonett"),
      item("eternal_starlight:stripped_banyin_log"),
      item("eternal_starlight:stripped_banyin_wood"),
      item("eternal_starlight:stripped_cradlewood_log"),
      item("eternal_starlight:stripped_cradlewood_wood"),
      item("eternal_starlight:stripped_jinglestem_log"),
      item("eternal_starlight:stripped_jinglestem_wood"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q238", ('And Other Blocks · 24', 'И прочие блоки · 24'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:stripped_lunar_log",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:stripped_lunar_log"),
      item("eternal_starlight:stripped_lunar_wood"),
      item("eternal_starlight:stripped_northland_log"),
      item("eternal_starlight:stripped_northland_wood"),
      item("eternal_starlight:stripped_scarlet_log"),
      item("eternal_starlight:stripped_scarlet_wood"),
      item("eternal_starlight:stripped_torreya_log"),
      item("eternal_starlight:stripped_torreya_wood"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q239", ('And Other Blocks · 25', 'И прочие блоки · 25'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:suspicious_dimslag",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:suspicious_dimslag"),
      item("eternal_starlight:tall_gladespike"),
      item("eternal_starlight:tangled_skull"),
      item("eternal_starlight:tear_bomb"),
      item("eternal_starlight:the_gatekeeper_spawner"),
      item("eternal_starlight:thioquartz_cluster"),
      item("eternal_starlight:torreya_button"),
      item("eternal_starlight:torreya_campfire"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q240", ('And Other Blocks · 26', 'И прочие блоки · 26'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:torreya_door",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:torreya_door"),
      item("eternal_starlight:torreya_fence"),
      item("eternal_starlight:torreya_fence_gate"),
      item("eternal_starlight:torreya_hanging_sign"),
      item("eternal_starlight:torreya_leaves"),
      item("eternal_starlight:torreya_log"),
      item("eternal_starlight:torreya_planks"),
      item("eternal_starlight:torreya_pressure_plate"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q241", ('And Other Blocks · 27', 'И прочие блоки · 27'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:torreya_sapling",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:torreya_sapling"),
      item("eternal_starlight:torreya_sign"),
      item("eternal_starlight:torreya_slab"),
      item("eternal_starlight:torreya_stairs"),
      item("eternal_starlight:torreya_tile_slab"),
      item("eternal_starlight:torreya_tile_stairs"),
      item("eternal_starlight:torreya_tile_wall"),
      item("eternal_starlight:torreya_trapdoor"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q242", ('And Other Blocks · 28', 'И прочие блоки · 28'), section="s6",
  deps=['q241'],
  icon="eternal_starlight:torreya_wood",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:torreya_wood"),
      item("eternal_starlight:twilvewyrm_herb"),
      item("eternal_starlight:velvetumoss"),
      item("eternal_starlight:velvetumoss_villi"),
      item("eternal_starlight:vividstalk"),
      item("eternal_starlight:waxed_golem_steel_block"),
      item("eternal_starlight:waxed_golem_steel_slab"),
      item("eternal_starlight:waxed_golem_steel_stairs"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q243", ('And Other Blocks · 29', 'И прочие блоки · 29'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:waxed_golem_steel_tile_slab",
  desc=[
      ('Всё, что не вошло в темы выше: хвост строительного двора.',
       'Everything that did not fit the themes above: the tail of the building yard.'),
      ('Union всех квестов по-прежнему равен всему моду.',
       'The union of all quests still equals the whole mod.'),
  ],
  tasks=[
      item("eternal_starlight:waxed_golem_steel_tile_slab"),
      item("eternal_starlight:waxed_golem_steel_tile_stairs"),
      item("eternal_starlight:withered_desert_amethysia"),
  ],
  rewards=[
      xpr(40),
  ]),

Q("q244", ('Encyclopaedia Tome', 'Том энциклопедии'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:abyssal_fruit",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q245", ('Encyclopaedia Tome · 2', 'Том энциклопедии · 2'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:aurora_deer_antler",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q246", ('Encyclopaedia Tome · 3', 'Том энциклопедии · 3'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:cooked_ratlin_meat",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q247", ('Encyclopaedia Tome · 4', 'Том энциклопедии · 4'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:doomeden_carrion",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q248", ('Encyclopaedia Tome · 5', 'Том энциклопедии · 5'), section="s6",
  deps=['q247'],
  icon="eternal_starlight:flowglaze_shovel",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q249", ('Encyclopaedia Tome · 6', 'Том энциклопедии · 6'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:luminofish",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q250", ('Encyclopaedia Tome · 7', 'Том энциклопедии · 7'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:oxidized_golem_steel_nugget",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q251", ('Encyclopaedia Tome · 8', 'Том энциклопедии · 8'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:ratlin_meat",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q252", ('Encyclopaedia Tome · 9', 'Том энциклопедии · 9'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:shadow_snail_meat",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q253", ('Encyclopaedia Tome · 10', 'Том энциклопедии · 10'), section="s6",
  deps=['q080'],
  icon="eternal_starlight:starlit_diamond_shovel",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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

Q("q254", ('Encyclopaedia Tome · 11', 'Том энциклопедии · 11'), section="s6",
  deps=['q253'],
  icon="eternal_starlight:tooth_of_hunger",
  desc=[
      ('Предметы, которые секции выше не назвали: каждый получает свою строку здесь.',
       'Items the sections above did not name: each gets its line here.'),
      ('Сдай их — энциклопедия должна быть полной.',
       'Hand them in - the encyclopaedia must be complete.'),
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
    "images": [],
    "links": [],
}
