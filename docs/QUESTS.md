# CHRONICLES 0.4 — a quest atlas

The questbook is a **non-linear adventure** for Minecraft 1.21.1 + Create 6.
There is still only one gameplay content mod: **Create**. Libraries, FancyMenu,
KubeJS and FTB Quests are supporting mods, so they do not receive filler chapters.

## Scale and variety

- **24 chapters, 626 total quests**: 16 vanilla chapters and 8 Create chapters.
- **12 map topologies**, including constellations, spiral routes, climbing mountains,
  railway networks, factory production chains, city districts, circuit boards and islands.
- Each chapter has **26 mandatory progression nodes**, plus optional tasks in
  Wilderness and Create Mastery. Eight additional quests were added to every
  original chapter while keeping its original quest IDs stable.
- **No chapter is a single straight line.** Independent workstreams join at a
  final chapter seal. Vanilla branches unlock at thematic milestones rather than
  forcing everyone to complete the End before beginning Create.
- Item collection, exploration of biomes and structures, vanilla advancements,
  dimensions, experience, creative checkmarks and KubeJS-driven custom events.
- **72 original chapter PNG illustrations:** individually colored chapter
  banner, crest and divider for 24 chapters. All chapter texts are RU/EN.
- **24 custom KubeJS rewards**, a thunderstorm observer challenge, and a bonus
  archivist task that recognizes three collected Create completion seals.
- One custom item: Chronicle Page. XP and small item rewards vary by chapter.

### Vanilla chapters (16)
The First Spark, The Living Homestead, Beneath the Stone, Harvest and Hearth,
City of One, The Wild Compass, Redstone Awakening, The Deep Atlas,
The Arcane Workshop, Through the Fire, Beyond the Horizon,
Village of Trades, Dust and Relics, The Silent Depths,
Atlas of Horizons, Above the Clouds.

### Create chapters (8)
Create: Foundations; Create: Moving Cities; Create: The Grand Factory;
Create: Sorting Networks; Create: Iron Roads; Create: Steam Age;
Create: Moving Worlds; Create: The Masterworks.

## Editable sources

- scripts/quest_chapters.json — original goals and bilingual chapter names
- scripts/quest_expansion.json — new chapters and eight curated goals per original chapter
- scripts/gen_quests.py — deterministic SNBT and PNG creation
- scripts/check_questbook.py — parsable SNBT, dependency graph, item IDs and illustrations
- scripts/registry/mc_registry_1.21.1.json — vanilla item/biome/advancement registry snapshot
- scripts/gen_menu.py — all-new FancyMenu background, buttons and layout
- docs/QUEST_MAP.md — automatically generated topology and unlock map

Run locally:

    python -m pip install "pillow>=11,<13" "nbtlib>=2,<3"
    python scripts/gen_quests.py
    python scripts/gen_menu.py
    python scripts/check_questbook.py
    python scripts/pack.py refresh
    python scripts/pack.py validate

Generated files live in config/ftbquests/quests/ and kubejs/; they are
committed automatically by the GitHub Pages workflow.

**Important:** CI verifies data consistency, not real in-game behavior.
Try a fresh test world before using this update with personal save files.
