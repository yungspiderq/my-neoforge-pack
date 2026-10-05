# -*- coding: utf-8 -*-
"""
Глава 1 — «Земли Рассвета» (Верхний мир).

Самая большая глава: от первого дерева до зажжённого портала в Незер.
Разбита на 8 секций-блоков, каждая рисуется своей подложкой с подписью
(layout="blocks" в gen_quests.py). У «Глубокой тьмы» — кликабельный портал
в отдельную главу «Галосфера» (контент мода Galosphere).

Правила, по которым написаны данные:
  • у каждого квеста есть icon — иначе глава выглядит набором одинаковых кружков;
  • deps задают дерево: без deps квест продолжает предыдущего (цепочка),
    с deps — ветвится. Ключи глобальны в пределах главы, поэтому связь между
    секциями пишется просто deps=["diamonds"];
  • size/shape выделяют вехи; ореол (halo) рисует картинка главы;
  • optional=True — необязательный квест (FTB рисует его другим цветом);
  • числа в задачах подобраны так, чтобы квест занимал 5–20 минут игры.
"""

from qdsl import (CUSTOM, Q, SEC, adv, biome, check, dim, give, halo, item, tag,
                  kill, lvl, loc, obs, portal, say, stat, struct, toast, xp,
                  xpr)

GREEN   = 0x3E7A3A
STONE   = 0x59627A
TEAL    = 0x2F7F72
WHEAT   = 0x9A8A2E
BLOOD   = 0x96403C
ARCANE  = 0x6A4A9E
REDST   = 0xA83A2C
PORTALC = 0x8A3FCF
GOLD    = 0xFFD75E
SALTL   = 0xF2A6D2   # розовый — портал в главу «Галосфера»

SECTIONS = [
    SEC("awaken",     ("Awakening",        "Пробуждение"),      GREEN),
    SEC("underground",("Under the Ground", "Под землёй"),       STONE),
    SEC("wilds",      ("Wild Lands",       "Дикие земли"),      TEAL),
    SEC("farm",       ("Farm and Food",    "Ферма и еда"),      WHEAT),
    SEC("combat",     ("Steel and Fang",   "Сталь и клык"),     BLOOD),
    SEC("arcane",     ("Enchanting",       "Чары и зелья"),     ARCANE),
    SEC("redstone",   ("Contraptions",     "Механизмы"),        REDST),
    SEC("gate",       ("The Gate",         "Врата"),            PORTALC),
]

QUESTS = [
# --------------------------------------------------------------------------- #
#  1. ПРОБУЖДЕНИЕ
# --------------------------------------------------------------------------- #
Q("wood", ("First Wood", "Первое дерево"), section="awaken",
  icon="minecraft:oak_log",
  desc=[("Hold the left mouse button on a tree trunk. Sixteen logs is enough "
         "to start; the rest you will get from saplings.",
         "Зажми левую кнопку мыши на стволе. Шестнадцати брёвен хватит, чтобы "
         "начать; остальное дадут саженцы."),
        ("Everything in this book starts here.",
         "Всё в этой книге начинается отсюда."),
        ("Any wood counts - oak, spruce, even Starlight timber: the counter "
         "accepts whatever logs you carry.",
         "Засчитывается любая древесина — дуб, ель, даже из Звездосветья: "
         "счётчик примет любые брёвна из инвентаря.")],
  tasks=[tag("minecraft:logs", 16)],
  rewards=[give("minecraft:bread", 4)]),

Q("bench", ("Workbench", "Верстак"), section="awaken",
  icon="minecraft:crafting_table",
  desc=[("Planks in the inventory crafting grid, then four planks into a table. "
         "From now on 3x3 recipes are available. Any planks count (one stack "
         "of 32).",
         "Доски — в сетку крафта в инвентаре, затем четыре доски в стол. "
         "С этого момента доступны рецепты 3x3. Доски — любые.")],
  tasks=[tag("minecraft:planks", 32), item("minecraft:crafting_table")],
  rewards=[give("minecraft:stick", 16)]),

Q("tools", ("Wooden Set", "Деревянный набор"), section="awaken",
  icon="minecraft:wooden_pickaxe",
  desc=[("A wooden pickaxe digs stone, a wooden axe chops twice as fast. "
         "They break quickly — that is normal.",
         "Деревянная кирка копает камень, деревянный топор рубит вдвое быстрее. "
         "Ломаются они быстро — это нормально.")],
  tasks=[item("minecraft:wooden_pickaxe"), item("minecraft:wooden_axe")],
  rewards=[give("minecraft:coal", 8)]),

Q("stoneage", ("Stone Age", "Каменный век"), section="awaken",
  icon="minecraft:stone_pickaxe",
  tasks=[tag("c:cobblestones", 64), item("minecraft:stone_pickaxe")],
  rewards=[give("minecraft:furnace"), give("minecraft:torch", 16)]),

Q("oven", ("Furnace", "Печь"), section="awaken",
  icon="minecraft:furnace",
  desc=[("Coal from a vein or from a charcoal kiln: put logs on top, fuel "
         "underneath. Interact with the furnace at least once.",
         "Уголь из жилы или из угольщика: брёвна сверху, топливо снизу. "
         "Хотя бы раз открой печь.")],
  tasks=[item("minecraft:furnace"), stat("minecraft:interact_with_furnace", 1),
         item("minecraft:coal", 16)],
  rewards=[give("minecraft:campfire")]),

Q("walls", ("Four Walls", "Четыре стены"), section="awaken",
  icon="minecraft:oak_door",
  desc=[("A door stops zombies, a chest stores the loot, a ladder gets you out "
         "of the hole. The house can be a hole in a hill.",
         "Дверь не пускает зомби, сундук хранит добычу, лестница выводит из ямы. "
         "Домом может быть нора в склоне холма.")],
  tasks=[tag("minecraft:wooden_doors"), item("minecraft:chest"),
         item("minecraft:ladder", 4)],
  rewards=[give("minecraft:lantern", 4)]),

Q("bed", ("Good Night", "Спокойной ночи"), section="awaken",
  icon="minecraft:white_bed",
  desc=[("Three wool and three planks. Sleeping skips the night and moves the "
         "spawn point — you will not walk back across the map after dying. "
         "Any bed colour counts.",
         "Три шерсти и три доски. Сон пропускает ночь и переносит точку "
         "возрождения — после смерти не придётся идти через всю карту. "
         "Кровать — любого цвета.")],
  tasks=[tag("minecraft:beds"), stat("minecraft:sleep_in_bed", 1)],
  rewards=[lvl(2)]),

Q("light", ("Light in the Dark", "Свет в темноте"), section="awaken",
  icon="minecraft:torch",
  desc=[("Mobs spawn where the light level is zero. Torches are the cheapest "
         "way to keep your house and your mine empty.",
         "Мобы появляются там, где уровень света нулевой. Факелы — самый дешёвый "
         "способ держать дом и шахту пустыми.")],
  tasks=[item("minecraft:torch", 64)],
  rewards=[give("minecraft:lantern", 8)]),

Q("iron", ("Iron Age", "Железный век"), section="awaken",
  icon="minecraft:iron_ingot",
  desc=[("Raw iron is smelted in a furnace. Eight ingots is a full set of tools "
         "and a bucket.",
         "Железо-сырец переплавляется в печи. Восемь слитков — это полный набор "
         "инструментов и ведро.")],
  tasks=[item("minecraft:iron_ingot", 8), adv("minecraft:story/smelt_iron")],
  rewards=[give("minecraft:iron_pickaxe")]),

Q("kit", ("Full Kit", "Полный комплект"), section="awaken",
  icon="minecraft:iron_sword", shape="gear", size=1.35,
  desc=[("Sword, pickaxe, axe, shovel and a shield. The shield blocks arrows and "
         "creeper explosions — hold it in the off-hand and crouch.",
         "Меч, кирка, топор, лопата и щит. Щит отражает стрелы и взрыв крипера — "
         "держи его во второй руке и приседай.")],
  tasks=[item("minecraft:iron_sword"), item("minecraft:iron_pickaxe"),
         item("minecraft:iron_axe"), item("minecraft:iron_shovel"),
         item("minecraft:shield")],
  rewards=[give("minecraft:golden_apple", 2), lvl(4)]),

Q("armor", ("Armor", "Броня"), section="awaken",
  icon="minecraft:iron_chestplate",
  tasks=[item("minecraft:iron_helmet"), item("minecraft:iron_chestplate"),
         item("minecraft:iron_leggings"), item("minecraft:iron_boots"),
         adv("minecraft:story/obtain_armor")],
  rewards=[give("minecraft:iron_block", 2)]),

Q("bucket", ("Bucket", "Ведро"), section="awaken",
  icon="minecraft:bucket",
  desc=[("Water turns lava into obsidian, lava melts sand into glass. A bucket "
         "is the most useful tool after the pickaxe.",
         "Вода превращает лаву в обсидиан, лава плавит песок в стекло. Ведро — "
         "самый полезный инструмент после кирки.")],
  tasks=[item("minecraft:bucket"), item("minecraft:water_bucket")],
  rewards=[give("minecraft:lava_bucket")]),

# --------------------------------------------------------------------------- #
#  2. ПОД ЗЕМЛЁЙ
# --------------------------------------------------------------------------- #
Q("deep", ("Down We Go", "Вниз"), section="underground", deps=["kit"],
  icon="minecraft:deepslate",
  desc=[("Below Y=0 stone turns into deepslate. Dig a staircase, not a shaft: "
         "you cannot jump out of a 1x1 hole.",
         "Ниже Y=0 камень переходит в глубинный сланец. Копай лестницу, а не "
         "колодец: из ямы 1x1 не выпрыгнуть.")],
  tasks=[item("minecraft:deepslate", 64), stat("minecraft:walk_one_cm", 100000)],
  rewards=[give("minecraft:torch", 64)]),

Q("coalseam", ("Black Gold", "Чёрное золото"), section="underground",
  icon="minecraft:coal",
  tasks=[item("minecraft:coal", 32)],
  rewards=[give("minecraft:coal_block", 2)]),

Q("copper", ("Copper", "Медь"), section="underground",
  icon="minecraft:copper_ingot",
  desc=[("Copper is needed for a lightning rod, a spyglass and the copper bulb. "
         "It oxidises, but that is only cosmetic.",
         "Медь нужна для громоотвода, подзорной трубы и медной лампы. "
         "Она окисляется, но это только внешний вид.")],
  tasks=[item("minecraft:raw_copper", 24), item("minecraft:copper_ingot", 16)],
  rewards=[give("minecraft:lightning_rod")]),

Q("dust", ("Red Dust", "Красная пыль"), section="underground",
  icon="minecraft:redstone",
  tasks=[item("minecraft:redstone", 32)],
  rewards=[give("minecraft:redstone_torch", 8)]),

Q("lapis", ("Lapis Lazuli", "Лазурит"), section="underground",
  icon="minecraft:lapis_lazuli",
  desc=[("Save it: enchanting consumes lapis by the handful.",
         "Копи: зачарование ест лазурит горстями.")],
  tasks=[item("minecraft:lapis_lazuli", 32)],
  rewards=[give("minecraft:lapis_block", 2)]),

Q("goldvein", ("Gold", "Золото"), section="underground",
  icon="minecraft:gold_ingot",
  tasks=[item("minecraft:gold_ingot", 8)],
  rewards=[give("minecraft:golden_apple")]),

Q("diamonds", ("Diamonds!", "Алмазы!"), section="underground", deps=["deep"],
  icon="minecraft:diamond", shape="diamond", size=1.5,
  desc=[("Best height is Y=-59, and always dig sideways with a two-block "
         "ceiling. Five diamonds: a pickaxe plus two spares.",
         "Лучшая высота — Y=-59, копай вбок с потолком в два блока. "
         "Пять алмазов: кирка и два запасных.")],
  tasks=[item("minecraft:diamond", 5), adv("minecraft:story/mine_diamond")],
  rewards=[give("minecraft:diamond_pickaxe"), lvl(3)]),

Q("abyss", ("Bottom of the World", "Дно мира"), section="underground",
  deps=["diamonds"], icon="minecraft:bedrock",
  desc=[("Get down to Y=-60. Bedrock is at -64, lava oceans are between. "
         "Take a water bucket.",
         "Спустись до Y=-60. Коренная порода на -64, между ними лавовые океаны. "
         "Возьми ведро воды.")],
  tasks=[loc("minecraft:overworld", [-20000000, -64, -20000000],
             [40000000, 6, 40000000])],
  rewards=[give("minecraft:diamond", 3)]),

Q("amethyst", ("Amethyst Geode", "Аметистовая жеода"), section="underground",
  deps=["deep"], icon="minecraft:amethyst_shard",
  desc=[("A dark sphere of smooth basalt hides amethyst. Listen: the blocks "
         "chime when you walk on them.",
         "В тёмной сфере из гладкого базальта спрятан аметист. Прислушайся: "
         "блоки звенят под ногами.")],
  tasks=[item("minecraft:amethyst_shard", 12)],
  rewards=[give("minecraft:spyglass"), give("minecraft:tinted_glass", 8)]),

Q("emeralds", ("Emeralds", "Изумруды"), section="underground", deps=["deep"],
  icon="minecraft:emerald",
  desc=[("Emerald ore only generates under mountains. Villagers will pay for "
         "everything else anyway.",
         "Изумрудная руда встречается только под горами. Жители всё равно "
         "заплатят за что угодно другое.")],
  tasks=[item("minecraft:emerald", 4)],
  rewards=[give("minecraft:emerald_block")]),

Q("caves", ("Crystal and Moss", "Хрусталь и мох"), section="underground",
  deps=["deep"], icon="minecraft:moss_block",
  desc=[("Dripstone caves stab you from above, lush caves glow with berries. "
         "Both are worth a look.",
         "Карстовые пещеры колют тебя сверху, пышные светятся ягодами. "
         "Обе стоят того, чтобы заглянуть.")],
  tasks=[biome("minecraft:dripstone_caves"), biome("minecraft:lush_caves")],
  rewards=[give("minecraft:glow_berries", 8), lvl(3)]),

Q("deepdark", ("Deep Dark", "Глубокая тьма"), section="underground",
  deps=["caves"], icon="minecraft:sculk_sensor", shape="octagon", size=1.4,
  desc=[("Sculk hears you. Sneak, do not run, do not place blocks on the "
         "sensors. Wool muffles vibrations.",
         "Скалк слышит тебя. Крадись, не бегай, не ставь блоки на сенсоры. "
         "Шерсть гасит вибрации.")],
  tasks=[biome("minecraft:deep_dark"), item("minecraft:echo_shard", 2)],
  rewards=[give("minecraft:sculk_catalyst", 2), lvl(6)]),

Q("ancientcity", ("Ancient City", "Древний город"), section="underground",
  deps=["deepdark"], icon="minecraft:echo_shard",
  desc=[("A huge dark structure under the deep dark. Chests hold the Swift "
         "Sneak book and the disc fragments. Do not break the portal frame.",
         "Огромное тёмное сооружение под глубокой тьмой. В сундуках — книга "
         "«Проворство» и обломки пластинки. Не ломай раму портала.")],
  tasks=[struct("minecraft:ancient_city"), item("minecraft:echo_shard", 6)],
  rewards=[lvl(10), give("minecraft:golden_carrot", 8)]),

Q("warden", ("Do Not Breathe", "Не дыши"), section="underground",
  deps=["deepdark"], icon="minecraft:sculk_shrieker", optional=True,
  desc=[("Sneak within 8 blocks of a sculk sensor and stay alive. The Warden is "
         "not meant to be killed: it drops nothing.",
         "Прокрадись вплотную к скалк-сенсору и останься жив. Хранителя не "
         "нужно убивать: с него ничего не падает.")],
  tasks=[adv("minecraft:adventure/avoid_vibration")],
  rewards=[give("minecraft:echo_shard", 4), toast("Ты слышал его шаги и выжил.")]),

Q("trial", ("Trial Chamber", "Пробная камера"), section="underground",
  deps=["deep"], icon="minecraft:trial_key", shape="hexagon", size=1.4,
  desc=[("A copper-and-tuff structure with vaults. A trial key opens a normal "
         "vault, an ominous key — the good ones.",
         "Структура из меди и туфа с хранилищами. Обычный ключ открывает простое "
         "хранилище, зловещий — хорошее.")],
  tasks=[struct("minecraft:trial_chambers"), item("minecraft:trial_key")],
  rewards=[give("minecraft:ominous_bottle"), lvl(6)]),

Q("obsidian", ("Obsidian", "Обсидиан"), section="underground",
  deps=["diamonds"], icon="minecraft:obsidian", shape="rsquare", size=1.4,
  desc=[("Pour water over a lava lake, then mine it with a diamond pickaxe. "
         "Fourteen blocks: ten for the portal, four for an enchanting table.",
         "Вылей воду на озеро лавы и копай алмазной киркой. Четырнадцать блоков: "
         "десять на портал, четыре на стол зачарования.")],
  tasks=[item("minecraft:obsidian", 14), adv("minecraft:story/form_obsidian")],
  rewards=[give("minecraft:flint_and_steel")]),

# --------------------------------------------------------------------------- #
#  3. ДИКИЕ ЗЕМЛИ
# --------------------------------------------------------------------------- #
Q("explore", ("First Step Out", "Первый выход"), section="wilds", deps=["kit"],
  icon="minecraft:compass",
  desc=[("The compass always points at the world spawn. Walk until the "
         "landscape stops repeating.",
         "Компас всегда указывает на точку появления в мире. Иди, пока пейзаж "
         "не перестанет повторяться.")],
  tasks=[item("minecraft:compass"), stat("minecraft:sprint_one_cm", 200000)],
  rewards=[give("minecraft:map"), give("minecraft:bread", 8)]),

Q("village", ("Village", "Деревня"), section="wilds", deps=["explore"],
  icon="minecraft:emerald",
  desc=[("Talk to a villager with the trade key (right-click). The librarian "
         "sells enchanted books for emeralds — find him first.",
         "Поговори с жителем (правая кнопка). Библиотекарь продаёт зачарованные "
         "книги за изумруды — сначала найди его.")],
  tasks=[stat("minecraft:talked_to_villager", 3), item("minecraft:emerald", 4)],
  rewards=[give("minecraft:emerald", 8)]),

Q("trade", ("Merchant", "Торговец"), section="wilds", deps=["village"],
  icon="minecraft:emerald_block",
  desc=[("Five trades of any kind. Trading also refreshes the villager's stock.",
         "Пять любых сделок. Торговля заодно обновляет ассортимент жителя.")],
  tasks=[stat("minecraft:traded_with_villager", 5),
         adv("minecraft:adventure/trade")],
  rewards=[give("minecraft:emerald_block", 2)]),

Q("outpost", ("Pillager Outpost", "Аванпост разбойников"), section="wilds",
  deps=["explore"], icon="minecraft:crossbow",
  desc=[("A dark oak tower with cages. Killing the captain gives Bad Omen — "
         "do not walk into a village with it.",
         "Башня из тёмного дуба с клетками. Смерть капитана даёт «Дурное знамение» "
         "— не заходи с ним в деревню.")],
  tasks=[struct("minecraft:pillager_outpost"), kill("minecraft:pillager", 5)],
  rewards=[give("minecraft:crossbow"), give("minecraft:arrow", 32)]),

Q("raid", ("Hero of the Village", "Герой деревни"), section="wilds",
  deps=["outpost", "trade"], icon="minecraft:totem_of_undying",
  shape="heart", size=1.5,
  desc=[("Bring Bad Omen into a village and survive all waves. Vindicators and "
         "a ravager come at the end.",
         "Принеси «Дурное знамение» в деревню и переживи все волны. В конце "
         "придут поборники и разоритель.")],
  tasks=[stat("minecraft:raid_win", 1),
         adv("minecraft:adventure/hero_of_the_village")],
  rewards=[give("minecraft:totem_of_undying"), lvl(8)]),

Q("fivelands", ("Five Lands", "Пять земель"), section="wilds", deps=["explore"],
  icon="minecraft:map", shape="octagon", size=1.4,
  desc=[("Desert, taiga, jungle, swamp and savanna. Biomes count when you stand "
         "in them, the map is not enough.",
         "Пустыня, тайга, джунгли, болото и саванна. Биом засчитывается, когда "
         "ты в нём стоишь, карты недостаточно.")],
  tasks=[biome("minecraft:desert"), biome("minecraft:taiga"),
         biome("minecraft:jungle"), biome("minecraft:swamp"),
         biome("minecraft:savanna")],
  rewards=[lvl(8), give("minecraft:map", 2)]),

Q("ocean", ("To the Sea", "К морю"), section="wilds", deps=["explore"],
  icon="minecraft:kelp",
  tasks=[biome("minecraft:ocean"), item("minecraft:kelp", 16),
         tag("minecraft:boats")],
  rewards=[give("minecraft:cod", 8)]),

Q("monument", ("Ocean Monument", "Подводная крепость"), section="wilds",
  deps=["ocean"], icon="minecraft:sponge", shape="hexagon", size=1.4,
  desc=[("Guardians do not let you mine. Drink a water-breathing potion or "
         "drain the monument; the elder guardian is inside.",
         "Стражи не дают копать. Выпей зелье подводного дыхания или осуши "
         "крепость; древний страж — внутри.")],
  tasks=[struct("minecraft:monument"), kill("minecraft:elder_guardian", 1),
         item("minecraft:sponge", 4)],
  rewards=[give("minecraft:sponge", 8), lvl(10)]),

Q("shipwreck", ("Shipwreck", "Кораблекрушение"), section="wilds", deps=["ocean"],
  icon="minecraft:heart_of_the_sea",
  desc=[("A map from a wreck leads to buried treasure: dig where the red cross "
         "is. The heart of the sea is inside.",
         "Карта с обломков ведёт к зарытому кладу: копай под красным крестом. "
         "Сердце моря — внутри.")],
  tasks=[struct("minecraft:shipwreck"), item("minecraft:heart_of_the_sea")],
  rewards=[give("minecraft:gold_block", 2)]),

Q("peaks", ("Peaks", "Вершины"), section="wilds", deps=["explore"],
  icon="minecraft:goat_horn",
  desc=[("Goats drop a horn when they ram a block. Snowy slopes and stony peaks "
         "are where to look.",
         "Козы роняют рог, когда таранят блок. Искать надо на снежных склонах "
         "и каменистых пиках.")],
  tasks=[biome("minecraft:stony_peaks"), kill("minecraft:goat", 1),
         item("minecraft:goat_horn")],
  rewards=[lvl(5)]),

Q("cherry", ("Cherry Grove", "Вишнёвая роща"), section="wilds", deps=["explore"],
  icon="minecraft:cherry_log",
  desc=[("Pink trees on top of mountains. Petals fall from the leaves.",
         "Розовые деревья на вершинах гор. С листьев падают лепестки.")],
  tasks=[biome("minecraft:cherry_grove"), item("minecraft:cherry_log", 16),
         item("minecraft:pink_petals", 8)],
  rewards=[give("minecraft:cherry_sapling", 4)]),

Q("mansion", ("Woodland Mansion", "Лесной особняк"), section="wilds",
  deps=["fivelands"], icon="minecraft:totem_of_undying",
  desc=[("A cartographer villager sells the map. Inside: evokers, and every one "
         "of them drops a totem.",
         "Житель-картограф продаёт карту. Внутри — заклинатели, и каждый роняет "
         "тотем.")],
  tasks=[struct("minecraft:mansion"), kill("minecraft:evoker", 1)],
  rewards=[give("minecraft:totem_of_undying"), lvl(12)]),

Q("tame", ("Companions", "Друзья"), section="wilds", deps=["explore"],
  icon="minecraft:lead",
  desc=[("Bones for a wolf, fish for a cat, a saddle for a horse. A tamed animal "
         "follows you and can be healed with meat.",
         "Кости для волка, рыба для кошки, седло для лошади. Приручённое животное "
         "ходит за тобой и лечится мясом.")],
  tasks=[adv("minecraft:husbandry/tame_an_animal"), item("minecraft:lead", 2)],
  rewards=[give("minecraft:name_tag")]),

# --------------------------------------------------------------------------- #
#  4. ФЕРМА И ЕДА
# --------------------------------------------------------------------------- #
Q("seeds", ("Seeds", "Семена"), section="farm", deps=["bench"],
  icon="minecraft:wheat_seeds",
  desc=[("Break tall grass for seeds, hoe the dirt next to water and plant. "
         "Bone meal speeds everything up.",
         "Ломай высокую траву ради семян, вспаши землю у воды и посади. "
         "Костная мука ускоряет всё.")],
  tasks=[adv("minecraft:husbandry/plant_seed"), tag("c:seeds", 16)],
  rewards=[give("minecraft:bone_meal", 16), give("minecraft:iron_hoe")]),

Q("wheat", ("Bread", "Хлеб"), section="farm", deps=["seeds"],
  icon="minecraft:bread",
  tasks=[item("minecraft:wheat", 24), item("minecraft:bread", 12)],
  rewards=[give("minecraft:hay_block", 3)]),

Q("garden", ("Kitchen Garden", "Огород"), section="farm", deps=["seeds"],
  icon="minecraft:carrot",
  desc=[("Carrots and potatoes come from village farms and zombies. Beetroot "
         "is fast but not very filling.",
         "Морковь и картофель — с деревенских грядок и с зомби. Свёкла растёт "
         "быстро, но сытость даёт невысокую.")],
  tasks=[item("minecraft:carrot", 12), item("minecraft:potato", 12),
         item("minecraft:beetroot", 8)],
  rewards=[give("minecraft:bone_meal", 32)]),

Q("breed", ("Breeding", "Разведение"), section="farm", deps=["wheat"],
  icon="minecraft:wheat",
  desc=[("Feed two animals of the same kind their favourite food and they will "
         "produce a baby. Ten of any kind counts.",
         "Скорми двум животным одного вида их любимую еду — появится детёныш. "
         "Засчитаются десять любых.")],
  tasks=[stat("minecraft:animals_bred", 10),
         adv("minecraft:husbandry/breed_an_animal")],
  rewards=[give("minecraft:golden_carrot", 4)]),

Q("yard", ("Full Yard", "Полный двор"), section="farm", deps=["breed"],
  icon="minecraft:cooked_beef",
  tasks=[item("minecraft:cooked_beef", 8), item("minecraft:cooked_porkchop", 8),
         item("minecraft:cooked_chicken", 8), item("minecraft:egg", 8)],
  rewards=[give("minecraft:hay_block", 4), give("minecraft:lead", 2)]),

Q("sheep", ("Wool", "Шерсть"), section="farm", deps=["breed"],
  icon="minecraft:white_wool",
  desc=[("Shears do not hurt the sheep and regrow after feeding. Dye changes "
         "the colour of the wool. Any wool colour counts.",
         "Ножницы не калечат овцу, шерсть отрастает после кормления. Краситель "
         "меняет цвет шерсти. В задаче засчитывается шерсть любого цвета.")],
  tasks=[item("minecraft:shears"), tag("minecraft:wool", 24)],
  rewards=[give("minecraft:white_bed", 2)]),

Q("fishing", ("Fishing", "Рыбалка"), section="farm", deps=["wood"],
  icon="minecraft:fishing_rod",
  desc=[("Treasure comes from an open water surface at least 5x4x5. Enchant the "
         "rod with Luck of the Sea to get it faster.",
         "Сокровища ловятся с открытой воды не меньше 5x4x5. Зачаруй удочку на "
         "«Морскую удачу», чтобы получать их быстрее.")],
  tasks=[item("minecraft:fishing_rod"), stat("minecraft:fish_caught", 10),
         adv("minecraft:husbandry/fishy_business")],
  rewards=[give("minecraft:nautilus_shell"), lvl(3)]),

Q("bees", ("Apiary", "Пасека"), section="farm", deps=["garden"],
  icon="minecraft:honey_bottle",
  desc=[("Look at a bee nest for a few seconds — the task counts the glance. "
         "Shears give honeycomb, a bottle gives honey.",
         "Посмотри на пчелиное гнездо пару секунд — задача засчитывает взгляд. "
         "Ножницы дают соты, бутылочка — мёд.")],
  tasks=[obs("minecraft:bee_nest", "block", 20), item("minecraft:honeycomb", 6),
         item("minecraft:honey_bottle", 2)],
  rewards=[give("minecraft:honey_block", 2)]),

Q("melon", ("Melon and Pumpkin", "Арбуз и тыква"), section="farm", deps=["garden"],
  icon="minecraft:melon_slice",
  tasks=[item("minecraft:melon_slice", 8), item("minecraft:carved_pumpkin", 2)],
  rewards=[give("minecraft:jack_o_lantern", 4)]),

Q("carrotgold", ("Golden Carrot", "Золотая морковь"), section="farm",
  deps=["breed", "goldvein"], icon="minecraft:golden_carrot",
  desc=[("Eight nuggets around a carrot. The best saturation in the game — "
         "take a stack into the Nether.",
         "Восемь самородков вокруг моркови. Лучшая насыщенность в игре — "
         "возьми стек в Незер.")],
  tasks=[item("minecraft:golden_carrot", 12)],
  rewards=[give("minecraft:golden_apple", 2)]),

Q("cake", ("Cake", "Торт"), section="farm", deps=["yard"],
  icon="minecraft:cake",
  tasks=[item("minecraft:cake"), stat("minecraft:eat_cake_slice", 1)],
  rewards=[give("minecraft:pumpkin_pie", 4)]),

Q("balanced", ("Balanced Diet", "Сбалансированное питание"), section="farm",
  deps=["cake", "melon"], icon="minecraft:enchanted_golden_apple",
  shape="heart", size=1.4, optional=True,
  desc=[("Eat everything edible in the game, including pufferfish and spider "
         "eyes. Long, dull, and worth the achievement.",
         "Съешь всё съедобное в игре, включая иглобрюха и паучьи глаза. "
         "Долго, нудно и стоит своего достижения.")],
  tasks=[adv("minecraft:husbandry/balanced_diet")],
  rewards=[give("minecraft:enchanted_golden_apple"), lvl(15)]),

# --------------------------------------------------------------------------- #
#  5. СТАЛЬ И КЛЫК
# --------------------------------------------------------------------------- #
Q("firstblood", ("First Blood", "Первая кровь"), section="combat", deps=["kit"],
  icon="minecraft:rotten_flesh",
  desc=[("Zombies burn in the sun and drop rotten flesh. Five of them is one "
         "night of standing your ground.",
         "Зомби сгорают на солнце и роняют гнилую плоть. Пять штук — это одна "
         "ночь удержания позиции.")],
  tasks=[adv("minecraft:adventure/kill_a_mob"), kill("minecraft:zombie", 5)],
  rewards=[give("minecraft:arrow", 32)]),

Q("bones", ("Bones", "Кости"), section="combat", deps=["firstblood"],
  icon="minecraft:bone",
  desc=[("A skeleton shoots from 16 blocks. Use a shield and a corner, or dig "
         "down and hit from below.",
         "Скелет стреляет с 16 блоков. Используй щит и угол, либо копай вниз "
         "и бей снизу.")],
  tasks=[kill("minecraft:skeleton", 10), item("minecraft:bone", 16)],
  rewards=[give("minecraft:bow")]),

Q("spiders", ("Eight Legs", "Восемь ног"), section="combat", deps=["firstblood"],
  icon="minecraft:string",
  desc=[("Cave spiders are smaller and poisonous, they live in abandoned mines "
         "wrapped in cobwebs.",
         "Пещерные пауки меньше и ядовиты, живут в заброшенных шахтах, "
         "затянутых паутиной.")],
  tasks=[kill("minecraft:spider", 8), kill("minecraft:cave_spider", 4),
         item("minecraft:string", 16)],
  rewards=[give("minecraft:fishing_rod")]),

Q("creepers", ("Do Not Hiss", "Не шипи"), section="combat", deps=["firstblood"],
  icon="minecraft:gunpowder",
  desc=[("Hit and step back, or lure a skeleton to kill it. Charged creepers "
         "spawn from lightning and drop heads.",
         "Ударь и отступи, либо натрави скелета. Заряженный крипер рождается "
         "от молнии и роняет голову.")],
  tasks=[kill("minecraft:creeper", 10), item("minecraft:gunpowder", 16)],
  rewards=[give("minecraft:tnt", 4)]),

Q("archer", ("Marksman", "Стрелок"), section="combat", deps=["bones"],
  icon="minecraft:bow",
  desc=[("A fully drawn bow flies further. Hold the shield in the off-hand while "
         "shooting to survive the return fire.",
         "Полностью натянутый лук бьёт дальше. Держи щит во второй руке, "
         "чтобы пережить ответный залп.")],
  tasks=[adv("minecraft:adventure/shoot_arrow"), item("minecraft:arrow", 64),
         stat("minecraft:damage_dealt", 5000)],
  rewards=[give("minecraft:bow"), lvl(4)]),

Q("enderman_ow", ("Tall Guest", "Высокий гость"), section="combat",
  deps=["firstblood"], icon="minecraft:ender_pearl",
  desc=[("Do not look at his face. Fight under a roof two blocks high — he "
         "cannot reach you there.",
         "Не смотри ему в лицо. Дерись под навесом высотой в два блока — "
         "там он до тебя не дотянется.")],
  tasks=[kill("minecraft:enderman", 5), item("minecraft:ender_pearl", 8)],
  rewards=[give("minecraft:ender_chest")]),

Q("slimes", ("Slime", "Слизь"), section="combat", deps=["firstblood"],
  icon="minecraft:slime_ball",
  desc=[("Slimes spawn in swamps at night and in slime chunks below Y=40. "
         "Big ones split into smaller ones.",
         "Слизни появляются ночью на болотах и в «слизневых» чанках ниже Y=40. "
         "Большие делятся на маленьких.")],
  tasks=[kill("minecraft:slime", 8), item("minecraft:slime_ball", 12)],
  rewards=[give("minecraft:sticky_piston", 2)]),

Q("shieldwall", ("Shield Wall", "Щит"), section="combat", deps=["kit"],
  icon="minecraft:shield",
  tasks=[adv("minecraft:story/deflect_arrow"),
         stat("minecraft:damage_blocked_by_shield", 500)],
  rewards=[give("minecraft:iron_ingot", 6)]),

Q("hunter", ("Hunter", "Охотник"), section="combat",
  deps=["bones", "spiders", "creepers"], icon="minecraft:iron_sword",
  shape="gear", size=1.4,
  desc=[("250 kills of any mobs. Counted by the game statistic, not by this "
         "quest book.",
         "250 убийств любых мобов. Считается по игровой статистике, а не по "
         "этой книге.")],
  tasks=[stat("minecraft:mob_kills", 250)],
  rewards=[give("minecraft:diamond_sword"), lvl(6)]),

Q("golem", ("Iron Guardian", "Железный защитник"), section="combat",
  deps=["hunter"], icon="minecraft:iron_block",
  desc=[("Four iron blocks in a T and a carved pumpkin on top. He defends the "
         "village and you.",
         "Четыре железных блока буквой Т и вырезанная тыква сверху. "
         "Он защищает деревню и тебя.")],
  tasks=[adv("minecraft:adventure/summon_iron_golem"),
         item("minecraft:iron_block", 4), item("minecraft:carved_pumpkin")],
  rewards=[lvl(6)]),

Q("allmobs", ("Head Collection", "Коллекция голов"), section="combat",
  deps=["hunter"], icon="minecraft:zombie_head", shape="gear", size=1.5,
  optional=True,
  desc=[("Kill one of every hostile mob in the game, including the Wither and "
         "the Ender Dragon. This is a season of play.",
         "Убей по одному каждому враждебному мобу в игре, включая Иссушителя "
         "и Дракона Края. Это сезон игры.")],
  tasks=[adv("minecraft:adventure/kill_all_mobs")],
  rewards=[give("minecraft:enchanted_golden_apple", 2), lvl(20)]),

Q("trident", ("Trident", "Трезубец"), section="combat", deps=["monument"],
  icon="minecraft:trident",
  desc=[("Drowned carry tridents rarely; farms on the ocean work better. "
         "A trident with Loyalty returns to your hand.",
         "Утопленники носят трезубцы редко; фермы в океане работают лучше. "
         "Трезубец с «Верностью» возвращается в руку.")],
  tasks=[item("minecraft:trident"), adv("minecraft:adventure/throw_trident")],
  rewards=[give("minecraft:nautilus_shell", 2)]),

# --------------------------------------------------------------------------- #
#  6. ЧАРЫ И ЗЕЛЬЯ
# --------------------------------------------------------------------------- #
Q("levels", ("Experience", "Опыт"), section="arcane", deps=["kit"],
  icon="minecraft:experience_bottle",
  desc=[("The task CONSUMES ten levels: experience is the currency of "
         "enchanting. Bottle it later, or grind mobs now.",
         "Задача ЗАБИРАЕТ десять уровней: опыт — это валюта зачарования. "
         "Запаси его заранее или фарми мобов.")],
  tasks=[xp(levels=10)],
  rewards=[give("minecraft:experience_bottle", 8)]),

Q("etable", ("Enchanting Table", "Стол зачарования"), section="arcane",
  deps=["levels", "diamonds", "obsidian"], icon="minecraft:enchanting_table",
  shape="gear", size=1.5,
  desc=[("Four obsidian, two diamonds, one book. Look at the table for a couple "
         "of seconds to complete the observation task.",
         "Четыре обсидиана, два алмаза, книга. Посмотри на стол пару секунд, "
         "чтобы закрыть задачу наблюдения.")],
  tasks=[item("minecraft:enchanting_table"),
         obs("minecraft:enchanting_table", "block", 20)],
  rewards=[give("minecraft:lapis_lazuli", 32)]),

Q("library", ("Library", "Библиотека"), section="arcane", deps=["etable"],
  icon="minecraft:bookshelf",
  desc=[("Fifteen bookshelves one block away from the table unlock level 30 "
         "enchantments. Air must be between them.",
         "Пятнадцать книжных полок в блоке от стола открывают чары 30 уровня. "
         "Между ними должен быть воздух.")],
  tasks=[item("minecraft:bookshelf", 15), item("minecraft:book", 8),
         item("minecraft:lectern")],
  rewards=[give("minecraft:writable_book", 2), lvl(3)]),

Q("firstenchant", ("First Enchantment", "Первые чары"), section="arcane",
  deps=["library"], icon="minecraft:enchanted_book",
  desc=[("Third slot, three levels of luck, and hope for Fortune or Silk Touch.",
         "Третья строка, три уровня и надежда на «Удачу» или «Шёлковое касание».")],
  tasks=[adv("minecraft:story/enchant_item"),
         stat("minecraft:enchant_item", 3)],
  rewards=[lvl(5)]),

Q("diamondbar", ("Diamond Bar", "Алмазный комплект"), section="arcane",
  deps=["firstenchant"], icon="minecraft:diamond_chestplate",
  shape="diamond", size=1.4,
  tasks=[item("minecraft:diamond_sword"), item("minecraft:diamond_pickaxe"),
         item("minecraft:diamond_helmet"), item("minecraft:diamond_chestplate"),
         adv("minecraft:story/shiny_gear")],
  rewards=[lvl(8), give("minecraft:diamond", 4)]),

Q("anvil", ("Anvil", "Наковальня"), section="arcane", deps=["diamondbar"],
  icon="minecraft:anvil",
  desc=[("Merges enchantments and repairs gear. Each use makes the next repair "
         "more expensive.",
         "Объединяет чары и чинит снаряжение. Каждое использование делает "
         "следующий ремонт дороже.")],
  tasks=[item("minecraft:anvil"), stat("minecraft:interact_with_anvil", 1)],
  rewards=[give("minecraft:iron_block", 3)]),

Q("brewing", ("Brewing Stand", "Зельеварение"), section="arcane", deps=["levels"],
  icon="minecraft:brewing_stand",
  desc=[("Three blaze rods and a nether wart make the base potion. Until then "
         "you can brew awkward potions from water bottles.",
         "Три стержня ифрита и незерский нарост дают базовое зелье. Пока их нет, "
         "можно варить «странные» зелья из бутылок с водой.")],
  tasks=[item("minecraft:brewing_stand"), item("minecraft:glass_bottle", 6),
         stat("minecraft:interact_with_brewingstand", 1)],
  rewards=[give("minecraft:redstone", 8), give("minecraft:glowstone_dust", 4)]),

Q("smithing", ("Smithing", "Кузнечное дело"), section="arcane", deps=["anvil"],
  icon="minecraft:smithing_table",
  desc=[("A smithing table upgrades diamond gear to netherite, a grindstone "
         "strips enchantments and returns some experience.",
         "Кузнечный стол улучшает алмазное снаряжение до незеритового, "
         "точило снимает чары и возвращает часть опыта.")],
  tasks=[item("minecraft:smithing_table"), item("minecraft:grindstone"),
         stat("minecraft:interact_with_smithing_table", 1)],
  rewards=[lvl(4)]),

Q("token", ("Quest Token", "Медаль квеста"), section="arcane",
  deps=["diamondbar", "emeralds", "goldvein"], icon=CUSTOM["token"],
  shape="gear", size=1.4,
  desc=[("A custom item of this pack: a diamond, a gold ingot and an emerald in "
         "any arrangement. The recipe is in JEI.",
         "Свой предмет этого пака: алмаз, золотой слиток и изумруд в любом "
         "порядке. Рецепт есть в JEI."),
        ("Tokens are collected, not used. The premium token needs netherite.",
         "Медали коллекционируются, а не расходуются. Для улучшенной нужен "
         "незерит.")],
  tasks=[item(CUSTOM["token"], 3)],
  rewards=[lvl(6), give("minecraft:gold_ingot", 4)]),

# --------------------------------------------------------------------------- #
#  7. МЕХАНИЗМЫ
# --------------------------------------------------------------------------- #
Q("wiring", ("Wiring", "Проводка"), section="redstone", deps=["dust"],
  icon="minecraft:repeater",
  desc=[("A signal travels 15 blocks; a repeater refreshes it. A comparator "
         "reads the fullness of a chest.",
         "Сигнал идёт 15 блоков, повторитель его обновляет. Компаратор читает "
         "наполненность сундука.")],
  tasks=[item("minecraft:redstone", 64), item("minecraft:repeater", 4),
         item("minecraft:comparator", 2)],
  rewards=[give("minecraft:redstone_block", 2)]),

Q("pistons", ("Pistons", "Поршни"), section="redstone", deps=["wiring"],
  icon="minecraft:piston",
  tasks=[item("minecraft:piston", 4), item("minecraft:sticky_piston", 2)],
  rewards=[give("minecraft:slime_ball", 8)]),

Q("observer", ("Observers and Hoppers", "Наблюдатели и воронки"),
  section="redstone", deps=["pistons"], icon="minecraft:observer",
  desc=[("An observer sees a block change, a hopper moves items. Together they "
         "build every automatic farm.",
         "Наблюдатель видит изменение блока, воронка перемещает предметы. "
         "Вместе они строят любую автоферму.")],
  tasks=[item("minecraft:observer", 4), item("minecraft:hopper", 4)],
  rewards=[give("minecraft:hopper", 4)]),

Q("rails", ("Railway", "Железная дорога"), section="redstone", deps=["pistons"],
  icon="minecraft:minecart",
  desc=[("A powered rail needs gold and a redstone torch. Ride two kilometres "
         "to complete the statistic.",
         "Энергорельсы требуют золота и красного факела. Проедь два километра, "
         "чтобы закрыть статистику.")],
  tasks=[item("minecraft:rail", 32), item("minecraft:minecart"),
         stat("minecraft:minecart_one_cm", 200000)],
  rewards=[give("minecraft:powered_rail", 8)]),

Q("music", ("Music", "Музыка"), section="redstone", deps=["wiring"],
  icon="minecraft:note_block",
  desc=[("Right-click tunes a note block, a record in a jukebox plays until it "
         "ends. Records drop from creepers killed by skeletons.",
         "Правая кнопка настраивает нотный блок, пластинка в проигрывателе "
         "играет до конца. Пластинки падают с криперов, убитых скелетами.")],
  tasks=[item("minecraft:note_block"), item("minecraft:jukebox"),
         stat("minecraft:play_noteblock", 1), item("minecraft:music_disc_cat")],
  rewards=[give("minecraft:music_disc_cat", 1)]),

Q("boom", ("Boom", "Взрыв"), section="redstone", deps=["wiring"],
  icon="minecraft:tnt",
  desc=[("Gunpowder and sand. Useful for digging down fast and for waking the "
         "whole neighbourhood.",
         "Порох и песок. Полезно, чтобы быстро копать вниз и будить "
         "всю округу.")],
  tasks=[item("minecraft:tnt", 8), item("minecraft:flint_and_steel")],
  rewards=[give("minecraft:gunpowder", 16)]),

Q("autofarm", ("Own Contraption", "Свой механизм"), section="redstone",
  deps=["observer", "music"], icon="minecraft:dispenser", shape="gear",
  size=1.4,
  desc=[("Build any automatic farm: iron, gold, crops or mob grinder. There is "
         "no item to hand in — tick the box yourself when it works.",
         "Построй любую автоферму: железную, золотую, урожайную или "
         "мободробилку. Предмет сдавать не нужно — поставь галочку сам, "
         "когда заработает.")],
  tasks=[item("minecraft:dispenser", 2), item("minecraft:observer", 8), check()],
  rewards=[lvl(10), toast("Твой первый механизм работает.")]),

# --------------------------------------------------------------------------- #
#  8. ВРАТА
# --------------------------------------------------------------------------- #
Q("flint", ("Flint and Steel", "Огниво"), section="gate", deps=["obsidian"],
  icon="minecraft:flint_and_steel",
  desc=[("Flint from gravel, iron ingot. It lights the portal and the TNT.",
         "Кремень из гравия плюс железный слиток. Оно поджигает портал и TNT.")],
  tasks=[item("minecraft:flint_and_steel"), item("minecraft:gravel", 16)],
  rewards=[lvl(3)]),

Q("ready", ("Pick Your Path", "Выбор пути"), section="gate", deps=["armor"],
  icon="minecraft:golden_carrot", shape="hexagon", size=1.3,
  dependency_requirement="one_completed",
  desc=[("One of three is enough: full iron armor, enchanted diamond gear or a "
         "brewing stand. The Nether does not care which one you chose.",
         "Достаточно одного из трёх: полный комплект железной брони, "
         "зачарованное алмазное снаряжение или зельеварка. Незеру всё равно, "
         "что ты выбрал.")],
  tasks=[check()],
  rewards=[lvl(5), give("minecraft:golden_carrot", 8)]),

Q("portalow", ("The Nether Gate", "Врата в Незер"), section="gate",
  deps=["flint", "ready"], icon="minecraft:netherrack", shape="gear", size=2.0,
  desc=[("Ten obsidian minimum: a 4x5 frame without corners works. Light it "
         "with flint and steel and step in.",
         "Минимум десять обсидиана: рама 4x5 без углов работает. Подожги "
         "огнивом и войди."),
        ("One block in the Nether is eight blocks in the Overworld. That is how "
         "you travel fast.",
         "Один блок в Незере — это восемь блоков в Верхнем мире. Так "
         "путешествуют быстро.")],
  tasks=[dim("minecraft:the_nether"), adv("minecraft:story/enter_the_nether")],
  rewards=[lvl(8), give("minecraft:golden_carrot", 8),
           say('tellraw @s {"text":"Незер открыт. Вернись, когда будешь готов.",'
               '"color":"red"}', silent=True)]),
]

# --------------------------------------------------------------------------- #
#  Картинки главы
# --------------------------------------------------------------------------- #
def build_images():
    imgs = [
        # ореолы вокруг ключевых вех
        halo("diamonds", GOLD, 3.4),
        halo("deepdark", 0x7FD4FF, 3.2),
        halo("raid", 0xFF9A6A, 3.2),
        halo("portalow", PORTALC, 4.2, 200),
        # кликабельный портал: переносит в первую страницу главы про Незер
        portal("portalow", "nether:enter", dx=2.4, dy=0.0, size=1.9,
               title=("To the Nether", "В Незер")),
        # розовый портал у «Глубокой тьмы» — в главу «Галосфера» (мод Galosphere)
        portal("deepdark", "galosphere:enter", dx=-2.4, dy=0.0, size=1.9,
               color=SALTL, title=("To the Galosphere", "В Галосферу")),
        # табличка-памятка у квеста про опыт
        {
            "at": "levels", "dy": -1.15, "w": 3.6, "h": 0.7,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x1E1E28, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 9,
            "title": ("XP is consumed!", "Опыт сгорает!"),
        },
        # подпись-подсказка у «Глубокой тьмы»
        {
            "at": "deepdark", "dx": 0.0, "dy": 1.35, "w": 4.6, "h": 0.75,
            "image": "kubejs:textures/gui/plate.png",
            "color": 0x0E2233, "alpha": 235, "order": -35, "lock": True,
            "text": True, "text_shadow": True, "text_inset": 8,
            "title": ("Sneak. Do not run.", "Крадись. Не беги."),
        },
    ]
    return imgs


CHAPTER = {
    "id": 0xC001, "filename": "overworld",
    "layout": "blocks", "cols": 2, "dx": 2.1, "dy": 1.45,
    "pad_x": 4.5, "pad_y": 6.5,
    "shape": "circle", "icon": "minecraft:grass_block",
    "banner": "banner_overworld", "banner_w": 13.0, "banner_h": 3.25,
    "banner_gap": 2.9,
    "title": ("Dawnlands", "Земли Рассвета"),
    "subtitle": [
        ("One world, one life, one book. Everything you need is under your feet.",
         "Один мир, одна жизнь, одна книга. Всё нужное — у тебя под ногами."),
        ("Sections are read left to right, top to bottom; the arrows show what "
         "unlocks what.",
         "Секции читаются слева направо и сверху вниз; стрелки показывают, "
         "что что открывает."),
    ],
    "sections": SECTIONS,
    "quests": QUESTS,
    "images": build_images(),
}
