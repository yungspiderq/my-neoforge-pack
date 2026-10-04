# -*- coding: utf-8 -*-
"""
Глава 4 — «Галосфера» (мод Galosphere 1.5.5).

Отдельная глава-витрина контентного мода: вход — розовый портал у «Глубокой
тьмы» в Землях Рассвета. Восемь секций покрывают ВЕСЬ контент мода:
  • Розовая соль     — соляные пещеры, три оттенка соли, застройка, консервы;
  • Лишайниковый сад — лишайники, кордицепсы, спектры, искры, шашки;
  • Кристальные каньоны — аллюрит/люмьер/опал, искорки, гаджеты света, стройка;
  • Палладий и стерлинг — руда, блоки, броня, знамя, конь, бомба;
  • Кроты и мешочки  — норы, горные заказы кротов, подарки, опаловые саженцы;
  • Руины и археология — забытые руины, черепки, отделка «Вера»;
  • Мастерская глубин — дротик, табличка, стол горения, декор, мембраны, якорь;
  • Святилище и берсерк — святилище, эхо-колокол, призыв и убийство берсерка,
    консервированное улучшение, финал главы.

Проверенные факты о моде (по jar 1.5.5): палладий генерируется по всему
Верхнему миру (мелкие жилы до Y=48, в каньонах крупные до Y=112);
консервированные спавнятся в соляных пещерах группами по 4; спектры —
в лишайниковых (нерестятся на лишайниковом мхе); искорки — в каньонах;
святилище соли — только в соляных пещерах; забытые руины — реки/горы/холмы/
тайга; сломанный эхо-колокол и отделка «Вера» — подарки кротов (rare/epic);
опаловые хлопья превращают саженец в опаловый (критерий достижения opalising:
match_tool opal_flakes по #minecraft:saplings).
"""

from qdsl import (Q, SEC, adv, biome, check, give, halo, item, kill, lvl,
                  obs, portal, struct, toast, xpr)

SALT    = 0xC8609B   # розовая соль
SALTL   = 0xF2A6D2   # светлый розовый
MOSS    = 0x6A8F3C   # лишайниковый зелёный
CRYSTAL = 0x59A0D6   # кристальный синий
PALLAD  = 0x9AA7C7   # серебряно-палладиевый
MOLEC   = 0x8F6F4A   # кротовий коричневый
RUIN    = 0xA8763E   # терракота руин
WORK    = 0x4E8A8A   # стальная бирюза мастерской
SHRINE  = 0x8A2F4F   # тёмный сок святилища
GOLD    = 0xFFD75E

SECTIONS = [
    SEC("salt",     ("Pink Salt",          "Розовая соль"),        SALT),
    SEC("lichen",   ("Lichen Gardens",     "Лишайниковый сад"),    MOSS),
    SEC("crystal",  ("Crystal Canyons",    "Кристальные каньоны"), CRYSTAL),
    SEC("palladium",("Palladium & Sterling","Палладий и стерлинг"),PALLAD),
    SEC("mole",     ("Moles and Pouches",  "Кроты и мешочки"),     MOLEC),
    SEC("ruins",    ("Ruins & Archaeology","Руины и археология"),  RUIN),
    SEC("workshop", ("Workshop of Depths", "Мастерская глубин"),   WORK),
    SEC("shrine",   ("Shrine & Berserker", "Святилище и берсерк"), SHRINE),
]

QUESTS = [
# --------------------------------------------------------------------------- #
#  1. РОЗОВАЯ СОЛЬ
# --------------------------------------------------------------------------- #
Q("enter", ("Salt Breath", "Соляное дыхание"), section="salt",
  deps=["overworld:deepdark"], icon="galosphere:pink_salt_cluster",
  shape="hexagon", size=1.6,
  desc=[("The Galosphere mod populated the depths: three cave biomes, two "
         "structures, the metal palladium, sterling armor, moles with pouches "
         "and something ancient under the salt. The way in is below the Deep "
         "Dark — dig even deeper and look for the pink glow.",
         "Мод Galosphere населил глубины: три пещерных биома, две структуры, "
         "металл палладий, стерлинговая броня, кроты с мешочками и нечто "
         "древнее под солью. Вход — ниже Глубокой тьмы: копай ещё глубже и "
         "ищи розовое свечение."),
        ("Every item of the mod is in JEI. This chapter walks you through "
         "all of it.",
         "Каждый предмет мода есть в JEI. Эта глава проведёт тебя по всем.")],
  tasks=[biome("galosphere:pink_salt_caves"),
         item("galosphere:pink_salt_shard", 16)],
  rewards=[lvl(4), give("galosphere:pink_salt_lamp", 4),
           toast("Добро пожаловать в Галосферу.")]),

Q("shades", ("Three Shades of Salt", "Три оттенка соли"), section="salt",
  deps=["enter"], icon="galosphere:pastel_pink_salt",
  desc=[("Salt in the caves comes in three colors: pink, rose and pastel. "
         "Mine whole blocks, not just shards — they will be needed for "
         "building.",
         "Соль в пещерах трёх цветов: розовая, роуз и пастельная. Добывай "
         "целые блоки, а не только осколки — они пригодятся для стройки.")],
  tasks=[item("galosphere:pink_salt", 16),
         item("galosphere:rose_pink_salt", 16),
         item("galosphere:pastel_pink_salt", 16)],
  rewards=[xpr(120), give("galosphere:polished_pink_salt", 16),
           give("galosphere:polished_rose_pink_salt", 16),
           give("galosphere:polished_pastel_pink_salt", 16)]),

Q("saltlight", ("Salt and Light", "Соль и свет"), section="salt",
  deps=["shades"], icon="galosphere:chandelier",
  desc=[("A pink salt lamp is crafted from shards, a chandelier hangs from "
         "the ceiling, and a light stand holds the floor. Soul versions are "
         "made with soul soil — the same recipes.",
         "Лампа из розовой соли крафтится из осколков, канделябр подвешивается "
         "к потолку, а стойка света держит пол. Душевные версии делаются с "
         "почвой душ — рецепты те же.")],
  tasks=[item("galosphere:pink_salt_lamp", 2),
         item("galosphere:chandelier", 2),
         item("galosphere:light_stand", 2)],
  rewards=[xpr(120), give("minecraft:lantern", 4),
           give("galosphere:soul_chandelier", 2),
           give("galosphere:soul_light_stand", 2)]),

Q("straw", ("Pink Straws", "Розовые соломинки"), section="salt",
  deps=["enter"], icon="galosphere:pink_salt_straw", optional=True,
  desc=[("On the floor and ceiling of the salt caves grow pink salt straws — "
         "hollow crystal tubes. Break them and take a few: they look great "
         "in builds.",
         "На полу и потолке соляных пещер растут розовые соляные соломинки — "
         "полые кристальные трубки. Сломай и забери пару: в постройках они "
         "смотрятся отлично.")],
  tasks=[item("galosphere:pink_salt_straw", 4)],
  rewards=[give("galosphere:salted_jerky", 4), xpr(80)]),

Q("preserved", ("The Preserved", "Консервированные"), section="salt",
  deps=["enter"], icon="galosphere:preserved_flesh", shape="diamond",
  desc=[("The salt caves are guarded by the Preserved — undead in salty "
         "bandages. They come in groups of four and drop nothing: the "
         "valuable things stay inside them. Or not.",
         "Соляные пещеры охраняют консервированные — нежить в соляных бинтах. "
         "Ходят группами по четверо и не роняют ничего: ценности остаются "
         "внутри. Или нет.")],
  tasks=[kill("galosphere:preserved", 4)],
  rewards=[lvl(5), xpr(150)]),

Q("saline", ("Saline Solution", "Соляной раствор"), section="salt",
  deps=["enter"], icon="galosphere:pink_salt_shard", optional=True,
  desc=[("Somewhere in the salt caves there is a saline composter — throw a "
         "pink salt shard into it and get coarse dirt. The advancement "
         "\"Saline Solution\" will confirm it.",
         "Где-то в соляных пещерах стоит соляной компостер — брось в него "
         "осколок розовой соли и получи каменистую землю. Достижение "
         "«Соляной раствор» это засвидетельствует.")],
  tasks=[adv("galosphere:husbandry/coarse_dirt_compost")],
  rewards=[give("minecraft:coarse_dirt", 16), xpr(100),
           give("galosphere:saline_composter")]),

Q("saltbuild1", ("Salt Mason", "Соляной зодчий"), section="salt",
  deps=["shades"], icon="galosphere:pink_salt_bricks",
  desc=[("Craft bricks and polished salt — and the stairs, slabs and walls "
         "from them. The rest of the variants are cut in the stonecutter: "
         "any block of the family gives all the others.",
         "Скрафти кирпичи и полированную соль — а из них лестницы, плиты и "
         "стены. Остальные варианты режутся в камнерезе: любой блок семейства "
         "даёт все остальные.")],
  tasks=[item("galosphere:pink_salt_bricks", 32),
         item("galosphere:polished_pink_salt", 16)],
  rewards=[lvl(4), give("galosphere:pink_salt_stairs", 16),
           give("galosphere:pink_salt_slab", 16),
           give("galosphere:pink_salt_wall", 16),
           give("galosphere:pink_salt_brick_stairs", 16),
           give("galosphere:pink_salt_brick_slab", 16),
           give("galosphere:pink_salt_brick_wall", 16),
           give("galosphere:polished_pink_salt_stairs", 16),
           give("galosphere:polished_pink_salt_slab", 16),
           give("galosphere:polished_pink_salt_wall", 16),
           give("galosphere:chiseled_pink_salt", 4)]),

Q("saltbuild2", ("Rose and Pastel", "Роуз и пастель"), section="salt",
  deps=["saltbuild1"], icon="galosphere:rose_pink_salt_bricks",
  desc=[("The same set for the other two colors. Craft what you need, cut "
         "the rest in the stonecutter — and build yourself a salt palace.",
         "Тот же набор для двух остальных цветов. Скрафти нужное, остальное "
         "нарежь в камнерезе — и строй себе соляной дворец.")],
  tasks=[item("galosphere:rose_pink_salt_bricks", 16),
         item("galosphere:pastel_pink_salt_bricks", 16)],
  rewards=[give("galosphere:polished_rose_pink_salt", 16),
           give("galosphere:polished_pastel_pink_salt", 16),
           give("galosphere:rose_pink_salt_brick_stairs", 16),
           give("galosphere:pastel_pink_salt_brick_stairs", 16),
           give("galosphere:rose_pink_salt_wall", 16),
           give("galosphere:pastel_pink_salt_slab", 16),
           give("galosphere:chiseled_rose_pink_salt", 4),
           give("galosphere:chiseled_pastel_pink_salt", 4)]),

Q("saltbuild3", ("Salt Pantry", "Соляная кладовая"), section="salt",
  deps=["saltbuild2"], icon="galosphere:polished_rose_pink_salt",
  optional=True,
  desc=[("The final set of salt blocks for the collector: all the slabs, "
         "stairs and walls of the rose and pastel families. Mine more salt "
         "and craft the rest — or cut it in the stonecutter.",
         "Последний набор соляных блоков для коллекционера: все плиты, "
         "лестницы и стены семейства роуз и пастель. Накопай ещё соли и "
         "скрафти недостающее — или нарежь в камнерезе.")],
  tasks=[item("galosphere:rose_pink_salt", 32),
         item("galosphere:pastel_pink_salt", 32)],
  rewards=[give("galosphere:rose_pink_salt_slab", 16),
           give("galosphere:rose_pink_salt_stairs", 16),
           give("galosphere:rose_pink_salt_brick_slab", 16),
           give("galosphere:rose_pink_salt_brick_wall", 16),
           give("galosphere:pastel_pink_salt_stairs", 16),
           give("galosphere:pastel_pink_salt_wall", 16),
           give("galosphere:pastel_pink_salt_brick_slab", 16),
           give("galosphere:pastel_pink_salt_brick_wall", 16),
           give("galosphere:polished_rose_pink_salt_slab", 16),
           give("galosphere:polished_rose_pink_salt_stairs", 16),
           give("galosphere:polished_rose_pink_salt_wall", 16),
           give("galosphere:polished_pastel_pink_salt_slab", 16),
           give("galosphere:polished_pastel_pink_salt_stairs", 16),
           give("galosphere:polished_pastel_pink_salt_wall", 16)]),

# --------------------------------------------------------------------------- #
#  2. ЛИШАЙНИКОВЫЙ САД
# --------------------------------------------------------------------------- #
Q("lichen", ("Lichen Gardens", "Лишайниковый сад"), section="lichen",
  deps=["enter"], icon="galosphere:lichen_moss", shape="hexagon", size=1.3,
  desc=[("The second biome of the depths: hanging gardens of lichen. Moss "
         "covers the floor, bowls of lichen hang on the walls — collect "
         "everything.",
         "Второй биом глубин: висячие сады лишайника. Мох укрывает пол, чаши "
         "лишайника висят на стенах — собери всё.")],
  tasks=[biome("galosphere:lichen_caves"),
         item("galosphere:lichen_moss", 8),
         item("galosphere:bowl_lichen", 4)],
  rewards=[lvl(5), give("galosphere:salted_jerky", 4)]),

Q("lightway", ("Glowing Path", "Светящаяся тропа"), section="lichen",
  deps=["lichen"], icon="galosphere:lichen_moss",
  desc=[("Walk across lichen moss — the soft green light under your feet "
         "gives the advancement \"Light the Way!\".",
         "Пройдись по лишайниковому мху — мягкий зелёный свет под ногами "
         "выдаст достижение «Освети путь!».")],
  tasks=[adv("galosphere:adventure/light_the_way")],
  rewards=[xpr(100)]),

Q("cordyceps", ("Edible Air", "Съедобный воздух"), section="lichen",
  deps=["lightway"], icon="galosphere:golden_lichen_cordyceps",
  desc=[("Cordyceps grow in columns through the whole biome. Eat one while "
         "standing underwater — the advancement is called \"Edible Air\" for "
         "a reason. The golden version is crafted and fills you much better.",
         "Кордицепсы растут колоннами через весь биом. Съешь один, стоя под "
         "водой, — достижение «Съедобный воздух» называется так не просто "
         "так. Золотой кордицепс крафтится и насыщает куда лучше.")],
  tasks=[item("galosphere:lichen_cordyceps", 6),
         adv("galosphere:adventure/edible_air")],
  rewards=[lvl(4), give("galosphere:golden_lichen_cordyceps", 2)]),

Q("shelf", ("Shelves, Roots and Vines", "Полки, корни и лозы"),
  section="lichen", deps=["lichen"], icon="galosphere:lichen_shelf",
  desc=[("Lichen shelves are the favorite food of spectres; roots decorate "
         "the walls, and vines are climbable — like ladders, but alive.",
         "Полки лишайника — любимая еда спектров; корни украшают стены, а по "
         "лозам можно карабкаться — как по лестницам, только живым.")],
  tasks=[item("galosphere:lichen_shelf", 8),
         item("galosphere:lichen_roots", 8),
         item("galosphere:lichen_vines", 8)],
  rewards=[xpr(120), give("minecraft:glow_lichen", 8)]),

Q("spectre", ("Spectre in a Bottle", "Спектр в бутылке"), section="lichen",
  deps=["lichen"], icon="galosphere:bottle_of_spectre", shape="diamond",
  desc=[("Spectres drift through the lichen caves — harmless ghostly birds "
         "that spawn on lichen moss. Lure one with an allurite shard or a "
         "lichen shelf, then catch it with an empty glass bottle: the "
         "advancement is called \"Watchfly?\".",
         "Спектры парят в лишайниковых пещерах — безобидные призрачные птицы, "
         "нерестятся на лишайниковом мху. Примани одного осколком аллюрита "
         "или полкой лишайника, а затем поймай пустой стеклянной бутылкой: "
         "достижение так и называется — «Watchfly?».")],
  tasks=[obs("galosphere:spectre", "entity_type", 20),
         adv("galosphere:adventure/watchfly"),
         item("galosphere:bottle_of_spectre")],
  rewards=[xpr(200), lvl(5)]),

Q("eye", ("Eye for an Eye", "Око за око"), section="lichen", deps=["spectre"],
  icon="galosphere:spectre_bound_spyglass", optional=True,
  desc=[("Give a spectre an allurite shard — it becomes bound. Now look at "
         "it through a spyglass and you will get the advancement \"Eye for "
         "an Eye\"... and something more.",
         "Дай спектру осколок аллюрита — он станет связанным. Теперь "
         "посмотри на него в подзорную трубу и получи достижение «Око за "
         "око»... и кое-что ещё.")],
  tasks=[adv("galosphere:adventure/eye_for_eye")],
  rewards=[give("galosphere:spectre_bound_spyglass"), xpr(200)]),

Q("pillar", ("Caterpillars", "Гусеницы"), section="lichen", deps=["lichen"],
  icon="galosphere:specterpillar_spawn_egg",
  desc=[("Spectres lay specterpillars — small crawling larvae. Frogs adore "
         "them: vanilla frog food, right from the mod.",
         "Спектры откладывают спектерпилларов — мелких ползучих личинок. "
         "Лягушки их обожают: фирменная еда из ванили прямо из мода.")],
  tasks=[obs("galosphere:specterpillar", "entity_type", 20)],
  rewards=[xpr(80)]),

Q("flare", ("Spectre Flare", "Спектральная шашка"), section="lichen",
  deps=["lichen"], icon="galosphere:spectre_flare",
  desc=[("A thrown flare of spectral light — the mod's own way to see what "
         "hides in the dark. Craft a few before long cave trips.",
         "Брошенная шашка спектрального света — фирменный способ мода "
         "увидеть, что таится в темноте. Скрафти пару штук перед долгими "
         "вылазками.")],
  tasks=[item("galosphere:spectre_flare", 4)],
  rewards=[lvl(4), give("minecraft:glow_ink_sac", 4)]),

# --------------------------------------------------------------------------- #
#  3. КРИСТАЛЬНЫЕ КАНЬОНЫ
# --------------------------------------------------------------------------- #
Q("canyons", ("Crystal Canyons", "Кристальные каньоны"), section="crystal",
  deps=["enter"], icon="galosphere:opal", shape="hexagon", size=1.4,
  desc=[("The rarest and most beautiful biome of the mod: canyons overgrown "
         "with crystals. Allurite is blue, lumiere glows yellow-green, opal "
         "shimmers with all colors. Large palladium veins are only here.",
         "Самый редкий и красивый биом мода: каньоны, заросшие кристаллами. "
         "Аллюрит синий, люмьер светится жёлто-зелёным, опал переливается "
         "всем сразу. Крупные жилы палладия — только здесь.")],
  tasks=[biome("galosphere:crystal_canyons"),
         item("galosphere:allurite_shard", 12),
         item("galosphere:lumiere_shard", 12),
         item("galosphere:opal", 6)],
  rewards=[lvl(6), give("galosphere:opal_block", 2)]),

Q("clusters", ("Blocks and Clusters", "Блоки и кластеры"), section="crystal",
  deps=["canyons"], icon="galosphere:allurite_block",
  desc=[("Nine shards make a block. Allurite blocks have a secret: they "
         "muffle sound waves — sculk sensors through them do not hear you.",
         "Девять осколков дают блок. У блоков аллюрита есть секрет: они "
         "глушат звуковые волны — скалк-сенсоры сквозь них тебя не слышат.")],
  tasks=[item("galosphere:allurite_block", 4),
         item("galosphere:lumiere_block", 4),
         item("galosphere:opal_block", 4)],
  rewards=[xpr(150), give("galosphere:glinted_allurite_cluster", 2),
           give("galosphere:glinted_lumiere_cluster", 2),
           give("galosphere:allurite_cluster", 2),
           give("galosphere:lumiere_cluster", 2)]),

Q("lamps", ("Crystal Light", "Кристальный свет"), section="crystal",
  deps=["clusters"], icon="galosphere:lumiere_lamp",
  desc=[("A lamp for each crystal: allurite, lumiere and even amethyst — "
         "the mod gives vanilla amethyst bricks, slabs, stairs and a lamp.",
         "Лампа для каждого кристалла: аллюритовая, люмьеровая и даже "
         "аметистовая — мод даёт ванильному аметисту кирпичи, плиты, "
         "лестницы и лампу.")],
  tasks=[item("galosphere:allurite_lamp", 2),
         item("galosphere:lumiere_lamp", 2),
         item("galosphere:amethyst_lamp", 2)],
  rewards=[xpr(120), give("minecraft:amethyst_shard", 8)]),

Q("sparkle", ("Sparkles", "Искорки"), section="crystal", deps=["canyons"],
  icon="galosphere:sparkle_spawn_egg",
  desc=[("Sparkles flit over calcite and crystal blocks in the canyons. "
         "They breathe underwater, love glow lichen and pollinate the "
         "crystals — that is why the canyons bloom.",
         "Искорки порхают над кальцитом и кристаллами в каньонах. Дышат под "
         "водой, любят светящийся лишайник и опыляют кристаллы — поэтому "
         "каньоны и цветут.")],
  tasks=[obs("galosphere:sparkle", "entity_type", 20)],
  rewards=[xpr(120), give("galosphere:glow_ink_clumps", 4),
           give("minecraft:glow_lichen", 8)]),

Q("glowflare", ("Light the Way!", "Свети ярко!"), section="crystal",
  deps=["canyons"], icon="galosphere:glow_flare",
  desc=[("A glow flare lights up the cave where it lands. Better than "
         "torches: throw it ahead of you into the dark.",
         "Световая шашка освещает пещеру там, где упадёт. Лучше факелов: "
         "бросай её в темноту впереди себя.")],
  tasks=[item("galosphere:glow_flare", 4)],
  rewards=[lvl(4), give("minecraft:torch", 32)]),

Q("monstrometer", ("Monstrometer", "Монстрометр"), section="crystal",
  deps=["canyons"], icon="galosphere:monstrometer",
  desc=[("Insert a lumiere shard as fuel — and the device will tell you "
         "that monsters are near. Lumiere shards also work as fuel for the "
         "echo bell... the mod loves lumiere.",
         "Вставь осколок люмьера как топливо — и прибор подскажет, что рядом "
         "монстры. Осколки люмьера вообще в ходу: ими питается и "
         "монстрометр, и эхо-колокол.")],
  tasks=[item("galosphere:monstrometer"),
         item("galosphere:lumiere_shard", 4)],
  rewards=[xpr(150)]),

Q("lumcomp", ("Fragility of Light", "Хрупкость света"), section="crystal",
  deps=["monstrometer"], icon="galosphere:lumiere_shard", optional=True,
  desc=[("Somewhere in the depths there is a lumiere composter — a lumiere "
         "shard in it turns into glowstone dust. The advancement \"Fragility "
         "of Light\" will confirm it.",
         "Где-то в глубинах стоит люмьеровый компостер — осколок люмьера в "
         "нём превращается в светокаменную пыль. Достижение «Хрупкость "
         "света» это засвидетельствует.")],
  tasks=[adv("galosphere:husbandry/lumiere_compost")],
  rewards=[give("minecraft:glowstone_dust", 8), xpr(100),
           give("galosphere:lumiere_composter")]),

Q("cbuild1", ("Crystal Mason", "Кристальный зодчий"), section="crystal",
  deps=["canyons"], icon="galosphere:allurite_bricks",
  desc=[("Bricks, smooth blocks and chiseled variants for allurite and "
         "lumiere. Slabs, stairs and the rest — in the stonecutter.",
         "Кирпичи, гладкие блоки и точёные варианты для аллюрита и люмьера. "
         "Плиты, лестницы и остальное — в камнерезе.")],
  tasks=[item("galosphere:allurite_bricks", 16),
         item("galosphere:lumiere_bricks", 16),
         item("galosphere:chiseled_allurite", 2),
         item("galosphere:chiseled_lumiere", 2)],
  rewards=[lvl(5), give("galosphere:smooth_allurite", 16),
           give("galosphere:allurite_slab", 16),
           give("galosphere:allurite_stairs", 16),
           give("galosphere:allurite_brick_slab", 16),
           give("galosphere:allurite_brick_stairs", 16),
           give("galosphere:smooth_allurite_slab", 16),
           give("galosphere:smooth_allurite_stairs", 16),
           give("galosphere:smooth_lumiere", 16),
           give("galosphere:lumiere_slab", 16),
           give("galosphere:lumiere_stairs", 16),
           give("galosphere:lumiere_brick_slab", 16),
           give("galosphere:lumiere_brick_stairs", 16),
           give("galosphere:smooth_lumiere_slab", 16),
           give("galosphere:smooth_lumiere_stairs", 16)]),

Q("cbuild2", ("Opal and Amethyst", "Опал и аметист"), section="crystal",
  deps=["cbuild1"], icon="galosphere:opal_bricks",
  desc=[("The same for opal and modded amethyst. Opal bricks even have "
         "walls. Everything else — stonecutter.",
         "То же для опала и модового аметиста. У опаловых кирпичей есть даже "
         "стены. Всё остальное — камнерез.")],
  tasks=[item("galosphere:opal_bricks", 16),
         item("galosphere:amethyst_bricks", 16),
         item("galosphere:chiseled_opal_bricks", 2),
         item("galosphere:chiseled_amethyst", 2)],
  rewards=[lvl(5), give("galosphere:opal_block", 8),
           give("galosphere:opal_brick_wall", 16),
           give("galosphere:opal_brick_slab", 16),
           give("galosphere:opal_brick_stairs", 16),
           give("galosphere:amethyst_slab", 16),
           give("galosphere:amethyst_stairs", 16),
           give("galosphere:amethyst_brick_slab", 16),
           give("galosphere:amethyst_brick_stairs", 16),
           give("galosphere:smooth_amethyst", 16),
           give("galosphere:smooth_amethyst_slab", 16),
           give("galosphere:smooth_amethyst_stairs", 16),
           give("galosphere:glinted_amethyst_cluster", 2)]),

# --------------------------------------------------------------------------- #
#  4. ПАЛЛАДИЙ И СТЕРЛИНГ
# --------------------------------------------------------------------------- #
Q("palladium", ("Palladium", "Палладий"), section="palladium",
  deps=["canyons"], icon="galosphere:palladium_ingot", shape="diamond",
  desc=[("The metal of the depths. Small veins are everywhere in the "
         "Overworld from the bedrock up to Y=48, large ones — only in the "
         "crystal canyons up to Y=112. A stone pickaxe is enough. Smelt the "
         "raw ore into ingots.",
         "Металл глубин. Мелкие жилы — везде в Верхнем мире от коренной "
         "породы до Y=48, крупные — только в кристальных каньонах до Y=112. "
         "Хватит каменной кирки. Переплавь сырую руду в слитки.")],
  tasks=[item("galosphere:raw_palladium", 12),
         item("galosphere:palladium_ingot", 8)],
  rewards=[lvl(6), xpr(150), give("galosphere:palladium_ore", 4),
           give("galosphere:deepslate_palladium_ore", 4)]),

Q("pallablocks", ("Palladium Blocks", "Палладиевые блоки"),
  section="palladium", deps=["palladium"], icon="galosphere:palladium_block",
  desc=[("A palladium block is a valid beacon base — the mod quietly gives "
         "you a cheap pyramid. Nuggets, dust, lattice (glow berries hang on "
         "it), panels and tiles round out the family.",
         "Палладиевый блок — годное основание маяка: мод тихо даёт тебе "
         "дешёвую пирамиду. Самородки, пыль, решётка (на ней висят светящиеся "
         "ягоды), панели и плитка дополняют семейство.")],
  tasks=[item("galosphere:palladium_block", 2),
         item("galosphere:raw_palladium_block", 2),
         item("galosphere:palladium_nugget", 9),
         item("galosphere:palladium_dust", 4),
         item("galosphere:palladium_lattice", 4)],
  rewards=[xpr(150), give("galosphere:palladium_panel", 8),
           give("galosphere:palladium_tiles", 8),
           give("galosphere:palladium_panel_slab", 8),
           give("galosphere:palladium_panel_stairs", 8),
           give("galosphere:palladium_tiles_slab", 8),
           give("galosphere:palladium_tiles_stairs", 8)]),

Q("sterling", ("Sterling Armor", "Стерлинговая броня"), section="palladium",
  deps=["pallablocks"], icon="galosphere:sterling_chestplate",
  shape="octagon", size=1.5,
  desc=[("The full sterling set: crafted from palladium, repaired with "
         "palladium ingots, protects from freezing. The pride of one who "
         "has mastered the depths.",
         "Полный стерлинговый комплект: крафтится из палладия, чинится "
         "палладиевыми слитками, защищает от замерзания. Гордость того, кто "
         "освоил глубины.")],
  tasks=[item("galosphere:sterling_helmet"),
         item("galosphere:sterling_chestplate"),
         item("galosphere:sterling_leggings"),
         item("galosphere:sterling_boots")],
  rewards=[lvl(10), toast("Стерлинг блестит в темноте.")]),

Q("banner", ("Looking Good, Partner!", "Выглядишь здорово, партнёр!"),
  section="palladium", deps=["sterling"], icon="minecraft:white_banner",
  desc=[("A sterling helmet can hold a banner — attach any and wear it with "
         "pride. The advancement is called \"Looking Good Partner!\".",
         "Стерлинговый шлем умеет держать знамя — прикрепи любое и носи с "
         "гордостью. Достижение так и называется: «Выглядишь здорово, "
         "партнёр!».")],
  tasks=[item("minecraft:white_banner"),
         adv("galosphere:adventure/attached_sterling")],
  rewards=[lvl(5), give("minecraft:red_banner", 2)]),

Q("horse", ("Fancy Seeing You Here!", "Кого я вижу!"), section="palladium",
  deps=["banner"], icon="galosphere:sterling_horse_armor", optional=True,
  desc=[("Sterling horse armor is crafted like the rest — and it does not "
         "sink in water. Put it on a horse with a banner: the mod has an "
         "advancement for that too.",
         "Стерлинговая конская броня крафтится как остальная — и не тонет в "
         "воде. Надень её на коня со знаменем: на это тоже есть достижение.")],
  tasks=[item("galosphere:sterling_horse_armor"),
         adv("galosphere:husbandry/attached_sterling_horse")],
  rewards=[lvl(5), give("minecraft:golden_carrot", 8)]),

Q("bomb", ("Palladium Bomb", "Палладиевая бомба"), section="palladium",
  deps=["palladium"], icon="galosphere:palladium_bomb",
  desc=[("A thrown bomb blasts stone. It can be tuned in the crafting grid: "
         "slime ball makes it bounce, string lengthens the fuse, gunpowder "
         "makes the blast stronger.",
         "Брошенная бомба взрывает камень. Её можно настроить в верстаке: "
         "слизь заставляет её прыгать, нить удлиняет запал, порох усиливает "
         "взрыв.")],
  tasks=[item("galosphere:palladium_bomb", 4)],
  rewards=[xpr(150), give("minecraft:gunpowder", 8)]),

# --------------------------------------------------------------------------- #
#  5. КРОТЫ И МЕШОЧКИ
# --------------------------------------------------------------------------- #
Q("mole", ("Moles of the Depths", "Кроты глубин"), section="mole",
  deps=["enter"], icon="galosphere:mole_spawn_egg",
  desc=[("Fat blind moles dig through the salt caves. They fear alliums — "
         "plant one and the mole will not come near. Watch one at work.",
         "Толстые слепые кроты роют соляные пещеры. Боятся лука-аллиума — "
         "посади один, и крот не подойдёт. Понаблюдай за работой одного.")],
  tasks=[obs("galosphere:mole", "entity_type", 20)],
  rewards=[xpr(120), give("minecraft:allium", 4)]),

Q("burrow", ("Mole Burrow", "Кротовья нора"), section="mole", deps=["mole"],
  icon="galosphere:mole_burrow",
  desc=[("Moles dig burrows — dig one up with a shovel and take it with "
         "you. Tuff dirt is crafted and moles happily dig it too.",
         "Кроты роют норы — выкопай такую лопатой и забери с собой. Туфовая "
         "земля крафтится, и кроты её тоже охотно роют.")],
  tasks=[item("galosphere:mole_burrow"),
         item("galosphere:tuff_dirt", 8)],
  rewards=[lvl(4), give("minecraft:tuff", 16)]),

Q("pouch", ("Mining Pouch", "Мешочек старателя"), section="mole",
  deps=["burrow"], icon="galosphere:mining_pouch", shape="hexagon", size=1.3,
  desc=[("Every time a mole returns home, the burrow gets a new mining "
         "pouch. Put a pouch into the burrow — and the mole will start "
         "taking orders: it asks for dirt, ores, salt... and brings gifts in "
         "return. Gifts are random: tuff and torches, rarely — bombs, opal "
         "flakes and a broken bell, epically — golden apples, enchanted "
         "books, the trim \"Faith\" and maps to the ruins.",
         "Каждый раз, когда крот возвращается домой, в норе появляется новый "
         "мешочек старателя. Вставь мешочек в нору — и крот начнёт брать "
         "заказы: просит землю, руды, соль... а взамен приносит подарки. "
         "Подарки случайны: туф и факелы, редко — бомбы, опаловые хлопья и "
         "сломанный колокол, эпически — золотые яблоки, чародейские книги, "
         "отделка «Вера» и карты к руинам.")],
  tasks=[item("galosphere:mining_pouch"),
         adv("galosphere:adventure/questful")],
  rewards=[lvl(6), xpr(200), give("minecraft:golden_carrot", 4),
           give("galosphere:broken_echo_bell"),
           toast("Крот принял заказ.")]),

Q("flakes", ("Opal Flakes", "Опаловые хлопья"), section="mole",
  deps=["pouch"], icon="galosphere:opal_flakes", optional=True,
  desc=[("A rare gift from the moles. Needed for the next quest — wait for "
         "the burrow to give you a couple.",
         "Редкий подарок кротов. Нужен для следующего квеста — дождись от "
         "норы пары штук.")],
  tasks=[item("galosphere:opal_flakes", 2)],
  rewards=[give("galosphere:opal_block", 2), xpr(150)]),

Q("opalising", ("Opal Trees", "Опаловые деревья"), section="mole",
  deps=["flakes"], icon="galosphere:opal_sapling", optional=True,
  desc=[("Hit any sapling with opal flakes in hand — it turns into an opal "
         "sapling. Plant it and grow an opal tree: shimmering leaves and "
         "opal logs.",
         "Ударь по любому саженцу с опаловыми хлопьями в руке — он "
         "превратится в опаловый. Посади и вырасти опаловое дерево: "
         "переливающиеся листья и опаловые брёвна.")],
  tasks=[adv("galosphere:adventure/opalising"),
         item("galosphere:opal_sapling"),
         item("galosphere:opal_log", 8)],
  rewards=[lvl(6), give("galosphere:opal_leaves", 16)]),

# --------------------------------------------------------------------------- #
#  6. РУИНЫ И АРХЕОЛОГИЯ
# --------------------------------------------------------------------------- #
Q("ruins", ("Forgotten Ruins", "Забытые руины"), section="ruins",
  deps=["enter"], icon="galosphere:thirst_pottery_sherd", shape="diamond",
  desc=[("The mod generates forgotten ruins along rivers, in mountains, "
         "hills and taiga — ancient buildings of stone and tuff. Inside "
         "there is suspicious gravel, and in it — new sherds and sometimes "
         "an enchanted book with \"Sifting\".",
         "Мод генерирует забытые руины вдоль рек, в горах, холмах и тайге — "
         "древние постройки из камня и туфа. Внутри — подозрительный гравий, "
         "а в нём новые черепки и иногда чародейская книга с «Просеиванием».")],
  tasks=[struct("galosphere:forgotten_ruins"),
         adv("galosphere:adventure/find_forgotten_ruins")],
  rewards=[lvl(6), give("minecraft:brush")]),

Q("sherds", ("Thirst and Wave", "Жажда и волна"), section="ruins",
  deps=["ruins"], icon="galosphere:wave_pottery_sherd",
  desc=[("Brush the suspicious gravel in the ruins: the mod adds two sherds "
         "— \"Thirst\" and \"Wave\". They go on a decorated pot like "
         "vanilla ones. And you can brush the same block again — there is "
         "an advancement for that.",
         "Расчисти подозрительный гравий в руинах: мод добавляет два черепка "
         "— «Жажда» и «Волна». Они ставятся на декоративный горшок как "
         "ванильные. А ещё один и тот же блок можно почистить повторно — на "
         "это есть достижение.")],
  tasks=[item("galosphere:thirst_pottery_sherd"),
         item("galosphere:wave_pottery_sherd"),
         adv("galosphere:adventure/rebrushing")],
  rewards=[lvl(5), give("minecraft:decorated_pot"), xpr(150)]),

Q("faith", ("Trim \"Faith\"", "Отделка «Вера»"), section="ruins",
  deps=["pouch"], icon="galosphere:faith_armor_trim_smithing_template",
  optional=True,
  desc=[("An epic gift from the moles — the smithing template \"Faith\". "
         "Apply it to any armor at the smithing table with any trim "
         "material.",
         "Эпический подарок кротов — кузнечный шаблон «Вера». Примени его к "
         "любой броне на кузнечном столе с любым материалом отделки.")],
  tasks=[item("galosphere:faith_armor_trim_smithing_template"),
         adv("galosphere:misc/faith_armor_trim_smithing_template_smithing_trim")],
  rewards=[lvl(8), give("minecraft:emerald", 8)]),

# --------------------------------------------------------------------------- #
#  7. МАСТЕРСКАЯ ГЛУБИН
# --------------------------------------------------------------------------- #
Q("ropedart", ("Rope Dart", "Верёвочный дротик"), section="workshop",
  deps=["palladium"], icon="galosphere:rope_dart",
  desc=[("Throw the dart — it sticks and reels the loot or an unlucky mob "
         "straight to you. The fisherman's rod of the underground.",
         "Брось дротик — он вонзается и подтягивает добычу или неудачливого "
         "моба прямо к тебе. Удочка подземелья.")],
  tasks=[item("galosphere:rope_dart")],
  rewards=[lvl(4), xpr(100)]),

Q("saltbound", ("Saltbound Tablet", "Соляная табличка"), section="workshop",
  deps=["ropedart"], icon="galosphere:saltbound_tablet", shape="diamond",
  desc=[("A magic weapon of the mod: charges up and fires a salt volley, "
         "then recharges. Can be enchanted like a bow. Illagers hate it.",
         "Магическое оружие мода: заряжается и бьёт соляным залпом, затем "
         "перезаряжается. Зачаровывается как лук. Разбойники его ненавидят.")],
  tasks=[item("galosphere:saltbound_tablet")],
  rewards=[xpr(200), give("galosphere:pink_salt_shard", 16)]),

Q("evoker", ("Finally a Worthy Opponent", "Наконец-то достойный соперник"),
  section="workshop", deps=["saltbound"], icon="minecraft:totem_of_undying",
  optional=True,
  desc=[("Find an evoker — in a woodland mansion or during a raid — and "
         "finish him with the saltbound tablet. The mod has a personal "
         "advancement for exactly this kill.",
         "Найди заклинателя — в лесном особняке или во время рейда — и "
         "прикончи его соляной табличкой. На этот случай у мода есть личное "
         "достижение.")],
  tasks=[adv("galosphere:adventure/saltbound_kill_evoker")],
  rewards=[lvl(15), xpr(500), give("minecraft:totem_of_undying")]),

Q("combustion", ("Combustion Table", "Стол горения"), section="workshop",
  deps=["ropedart"], icon="galosphere:combustion_table",
  desc=[("The workbench of the depths — crafted from salt and crystals. "
         "Looks great in a cave base and opens its own window.",
         "Верстак глубин — крафтится из соли и кристаллов. Отлично смотрится "
         "в пещерной базе и открывает собственное окно.")],
  tasks=[item("galosphere:combustion_table")],
  rewards=[lvl(4), give("minecraft:crafting_table", 2)]),

Q("decor", ("Decor of the Depths", "Декор глубин"), section="workshop",
  deps=["combustion"], icon="galosphere:weapon_rack",
  desc=[("A weapon rack holds your swords and pickaxes like a museum "
         "exhibit; a shadow frame darkens the walls; gilded beads tinkle "
         "quietly. All of it is crafted.",
         "Оружейная стойка держит мечи и кирки как музейный экспонат; "
         "теневая рама затемняет стены; позолоченные бусы тихо звенят. Всё "
         "это крафтится.")],
  tasks=[item("galosphere:weapon_rack", 2),
         item("galosphere:shadow_frame", 4),
         item("galosphere:gilded_beads", 8)],
  rewards=[xpr(120), give("galosphere:light_stand", 4)]),

Q("membrane", ("Cured Membrane", "Обработанная мембрана"),
  section="workshop", deps=["decor"], icon="galosphere:cured_membrane",
  desc=[("Phantom membranes are cured with salt — they stop being slippery "
         "and become a building material: membranes, membrane blocks and "
         "\"stranded\" blocks.",
         "Мембраны фантома обрабатываются солью — перестают скользить и "
         "становятся стройматериалом: мембраны, блоки мембран и «пляжные» "
         "блоки.")],
  tasks=[item("galosphere:cured_membrane", 4),
         item("galosphere:cured_membrane_block", 4),
         item("galosphere:stranded_membrane_block", 4)],
  rewards=[lvl(4), give("minecraft:phantom_membrane", 4)]),

Q("anchor", ("Burrow Anchor", "Норный якорь"), section="workshop",
  deps=["burrow"], icon="galosphere:burrow_anchor",
  desc=[("The personal teleport of the mod — crafted from salt and "
         "crystals. How exactly it anchors to the burrow — find out "
         "yourself, the mod does not like spoilers.",
         "Личный телепорт мода — крафтится из соли и кристаллов. Как именно "
         "он привязывается к норе — выясни сам, мод не любит спойлеров.")],
  tasks=[item("galosphere:burrow_anchor"), check()],
  rewards=[xpr(150), lvl(4)]),

# --------------------------------------------------------------------------- #
#  8. СВЯТИЛИЩЕ И БЕРСЕРК
# --------------------------------------------------------------------------- #
Q("shrine", ("Shrine of Salt", "Святилище соли"), section="shrine",
  deps=["enter"], icon="galosphere:pink_salt", shape="hexagon", size=1.4,
  desc=[("Only in the pink salt caves the mod generates a shrine of salt — "
         "a quiet hall with an echo altar in the center, chests with jerky, "
         "leather, membranes, sometimes a name tag and a golden apple, and a "
         "library with books.",
         "Только в розовых соляных пещерах мод генерирует святилище соли — "
         "тихий зал с эхо-алтарём в центре, сундуками с вяленым мясом, "
         "кожей, мембранами, иногда биркой и золотым яблоком, и библиотекой "
         "с книгами.")],
  tasks=[struct("galosphere:pink_salt_shrine"),
         adv("galosphere:adventure/find_pink_salt_shrine")],
  rewards=[lvl(8), xpr(200), give("galosphere:salted_jerky", 8)]),

Q("bell", ("Echo Bell", "Эхо-колокол"), section="shrine",
  deps=["shrine", "pouch"], icon="galosphere:echo_bell",
  desc=[("A broken echo bell is brought by moles (one you already have). "
         "Craft the whole bell: broken bell, two echo shards from an ancient "
         "city, an allurite shard and a stick. Insert an allurite charge — "
         "and the bell will ring near ores. Except ancient debris: that one "
         "it does not hear.",
         "Сломанный эхо-колокол приносят кроты (один у тебя уже есть). "
         "Собери целый колокол: сломанный колокол, два осколка эха из "
         "древнего города, осколок аллюрита и палка. Вставь аллюритовый "
         "заряд — и колокол зазвучит рядом с рудами. Кроме древних обломков: "
         "их он не слышит.")],
  tasks=[item("galosphere:echo_bell"),
         item("minecraft:echo_shard", 2),
         item("galosphere:allurite_shard", 4)],
  rewards=[xpr(200), lvl(6)]),

Q("berserker", ("Reign of Terror", "Царство ужаса"), section="shrine",
  deps=["bell"], icon="galosphere:berserker_spawn_egg", shape="gear",
  size=1.6,
  desc=[("Return to the shrine. Ring the charged bell at the echo altar in "
         "the center of the hall — and the Berserker wakes up. He smashes "
         "the ground, shakes off debris, pierces with salt pillars and "
         "summons the Preserved. Bring good armor.",
         "Вернись в святилище. Позвони заряженным колоколом у эхо-алтаря в "
         "центре зала — и Берсерк проснётся. Он бьёт по земле, стряхивает "
         "обломки, пронзает соляными столбами и призывает консервированных. "
         "Принеси хорошую броню.")],
  tasks=[adv("galosphere:adventure/summon_berserker")],
  rewards=[lvl(12), toast("Царство ужаса началось.")]),

Q("slay", ("Berserker Slayer", "Убийца берсерка"), section="shrine",
  deps=["berserker"], icon="galosphere:preserved_template", shape="octagon",
  size=1.4,
  desc=[("Survive his reign and put him down. The Berserker drops a "
         "preserved template and preserved flesh — the flesh is edible, the "
         "template is for the smithing table.",
         "Переживи его царство и положи его. С берсерка падают "
         "консервированный шаблон и консервированная плоть — плоть съедобна, "
         "шаблон — для кузнечного стола.")],
  tasks=[kill("galosphere:berserker"),
         item("galosphere:preserved_flesh", 2),
         item("galosphere:preserved_template", 2)],
  rewards=[lvl(10), xpr(400)]),

Q("preservedup", ("Preserved Upgrade", "Консервированное улучшение"),
  section="shrine", deps=["slay"], icon="galosphere:preserved_template",
  desc=[("At the smithing table: preserved template + any tool, armor or "
         "shulker box + pink salt shard. The thing becomes preserved — the "
         "depths respect such things.",
         "На кузнечном столе: консервированный шаблон + любой инструмент, "
         "броня или шалкеровый ящик + осколок розовой соли. Вещь становится "
         "консервированной — глубины уважают такие.")],
  tasks=[item("galosphere:pink_salt_shard", 8), check()],
  rewards=[xpr(300), give("galosphere:pink_salt_shard", 16)]),

Q("master", ("Master of the Galosphere", "Мастер Галосферы"),
  section="shrine", deps=["sterling", "decor", "slay"], icon="galosphere:opal_block",
  shape="gear", size=2.0,
  desc=[("You have seen all three biomes and both structures, raised "
         "sterling armor, befriended the moles, woken up and put down the "
         "Berserker. The depths are yours.",
         "Ты видел все три биома и обе структуры, поднял стерлинговую броню, "
         "подружился с кротами, разбудил и уложил Берсерка. Глубины — твои.")],
  tasks=[check()],
  rewards=[lvl(20), xpr(800), give("galosphere:opal_block", 16),
           give("galosphere:chandelier", 4),
           toast("Глубины покорились тебе.")]),
]

# --------------------------------------------------------------------------- #
#  Картинки главы
# --------------------------------------------------------------------------- #
def build_images():
    imgs = [
        # ореолы вех
        halo("enter", SALTL, 3.6),
        halo("canyons", CRYSTAL, 3.2),
        halo("sterling", PALLAD, 3.4),
        halo("shrine", SHRINE, 3.2),
        halo("berserker", 0xFF5A5A, 3.8, 200),
        halo("master", GOLD, 4.4, 200),
        # кликабельный розовый портал обратно — к «Глубокой тьме»
        portal("enter", "overworld:deepdark", dx=-2.4, dy=0.0, size=1.9,
               color=SALTL, title=("To the Dawnlands", "В Земли Рассвета")),
        # отметка мода у входа
        {
            "at": "enter", "dx": 0.0, "dy": -1.35, "w": 4.4, "h": 0.7,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x2A1622, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Mod: Galosphere 1.5.5", "Мод: Galosphere 1.5.5"),
        },
        # подсказка у кротовьей норы
        {
            "at": "pouch", "dx": 0.0, "dy": 1.35, "w": 4.6, "h": 0.75,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x241A12, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Gifts are random!", "Подарки случайны!"),
        },
        # предупреждение у берсерка
        {
            "at": "berserker", "dx": 0.0, "dy": -1.35, "w": 5.2, "h": 0.75,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x2A0E14, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Ring the bell at the altar", "Звони в колокол у алтаря"),
        },
    ]
    return imgs


CHAPTER = {
    "id": 0xC004, "filename": "galosphere",
    "layout": "blocks", "cols": 2, "dx": 2.1, "dy": 1.45,
    "pad_x": 4.5, "pad_y": 6.5,
    "shape": "hexagon", "icon": "galosphere:pink_salt_cluster",
    "banner": "banner_galosphere", "banner_w": 13.0, "banner_h": 3.25,
    "banner_gap": 2.9,
    "title": ("Galosphere", "Галосфера"),
    "subtitle": [
        ("The mod Galosphere: three cave biomes, two structures, palladium, "
         "sterling armor, moles with pouches and a berserker under the salt.",
         "Мод Galosphere: три пещерных биома, две структуры, палладий, "
         "стерлинговая броня, кроты с мешочками и берсерк под солью."),
        ("The entrance is below the Deep Dark in the Dawnlands — through the "
         "pink portal. Everything the mod has is covered here.",
         "Вход — ниже Глубокой тьмы в Землях Рассвета, через розовый портал. "
         "Здесь раскрыто всё, что есть в моде."),
    ],
    "sections": SECTIONS,
    "quests": QUESTS,
    "images": build_images(),
    "links": [
        # «откуда мы пришли»: квест Глубокая тьма из Земель Рассвета
        {"quest": "overworld:deepdark"},
    ],
}
