# My NeoForge Pack — CHRONICLES 0.4

**Minecraft 1.21.1 • NeoForge 21.1.252 • Java 21**

A Create-centered Minecraft pack with one gameplay content mod (**Create**).
Other mods support questing, scripts, a custom menu, borderless play, optimization,
resource packs and shaders.

## What changed in 0.4

- **626 quests across 24 chapters:** 16 vanilla and 8 Create chapters.
- **12 distinctive quest map layouts**, not identical three-lane trees.
- **72 original quest illustrations** and RU/EN quest localization.
- 24 custom KubeJS completion rewards and two optional custom quests.
- New **FancyMenu Clockwork Atlas** background and styled custom buttons with
  hover states, including vanilla button actions for navigation.
- Quest IDs for the original 14 chapters stay stable for existing progress.
- Kept automatic pack updates, shaders and **Cubes Without Borders**.

## Install (new instance recommended)

**Windows, Prism / Freesm:** import
https://yungspiderq.github.io/my-neoforge-pack/latest/instance.zip

**Modrinth App / AstralRinth:** import
https://yungspiderq.github.io/my-neoforge-pack/latest/pack.mrpack

To enable automatic updates in Modrinth App or AstralRinth, configure the
pre-launch hook in the instance as documented in [INSTALL.md](INSTALL.md).
The Prism/Freesm Windows instance ZIP already contains a pre-launch sync
command. Updates download only manifest-changed content.

**Worlds:** back up saves separately. The pack does not distribute saves and
major modpack changes should be tested in a fresh world first.

## Edit the modpack

Add gameplay mods through packwiz or adjust the managed Modrinth selection
in [pack-selection.json](pack-selection.json). Add dependencies with compatible
NeoForge 1.21.1 versions. Current supporting mods include FTB Quests,
FTB Library, FTB Teams, FTB XMod Compat, Architectury, KubeJS, FancyMenu,
Iris, Sodium and other performance/UI libraries.

Quest sources:
- [Questbook and source data](docs/QUESTS.md)
- [Generated quest route map](docs/QUEST_MAP.md)
- [New FancyMenu design](docs/MENU.md)

Build and validate locally:

    python -m pip install "pillow>=11,<13" "nbtlib>=2,<3"
    python scripts/resolve_modrinth.py
    python scripts/pin_ftb_xmod.py
    python scripts/gen_quests.py
    python scripts/gen_menu.py
    python scripts/check_questbook.py
    python scripts/pack.py refresh
    python scripts/pack.py validate
    python scripts/pack.py site

GitHub Actions repeats these checks on branches and publishes
the updated pack to GitHub Pages after pushes to main.

## Backup

The pre-rebuild modpack remains in
[backup/pre-rebuild-2026-11-14](../../tree/backup/pre-rebuild-2026-11-14).
