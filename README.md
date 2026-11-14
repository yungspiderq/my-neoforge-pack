# My NeoForge Pack v0.2.0

Minecraft 1.21.1 / NeoForge 21.1.252 / Java 21.

**Exactly one gameplay content mod: Create.** Additional mods provide questing, menus, scripting, performance, UI and shaders. Modrinth dependencies are resolved automatically, but no extra gameplay content mods are intended.

## Included framework
- **Create**: only gameplay content mod
- **FTB Quests**, FTB Library, FTB Teams, FTB Filter System: quest engine
- **FancyMenu**: custom title screen, buttons and background
- **KubeJS / Rhino**: future scripts
- **Cubes Without Borders**: borderless fullscreen
- **Sodium / Iris**: performance and shader support
- **JEI, Jade, AppleSkin and other QoL** when compatible
- **Bare Bones resource pack** and **Complementary Reimagined / BSL shaders** are downloaded as client-side optional visual packs where a compatible distribution exists

## Updates
Github Pages: https://yungspiderq.github.io/my-neoforge-pack/pack.toml

For Prism/Freesm import latest/instance.zip with pre-launch sync; for Modrinth App import latest/pack.mrpack and configure a pre-launch hook (see INSTALL.md).

Changing pack-selection.json and pushing main causes GitHub Actions to fetch compatible Modrinth versions, pin hashes, publish site/latest artifacts and save generated metadata. The 4 FTB Maven entries are retained manually.

To build locally run:

    python scripts/resolve_modrinth.py
    python scripts/pack.py refresh
    python scripts/pack.py validate
    python scripts/pack.py site

**Do not put JAR/ZIP archives in Git.** Only references are committed. Resource/shader packs are not forced on players; enable them in the Minecraft graphics/resource-pack menus.

Prior pack backup: backup/pre-rebuild-2026-11-14. Back up worlds; this rebuild is not compatible with old saves by default.

## Questbook

14 illustrated chapters and 253 quests in Russian and English, including Create progression, 3 interconnected quest lanes per chapter, KubeJS custom rewards and an optional stormwatch custom task. See [QUESTS.md](docs/QUESTS.md). KubeJS content is included in this same pack; no separate content mod is added.


## Chronicles 0.4 redesign

The questbook has been rebuilt to **24 chapters / 626 quests** (16 vanilla, 8 Create) with 12 distinctive visual layouts, individual chapter art and expanded objectives, including custom KubeJS challenges and rewards. The old title screen was replaced with a clockwork-atlas FancyMenu with styled action buttons. See [Quest Atlas](docs/QUESTS.md) and [FancyMenu](docs/MENU.md).
