# Install clean NeoForge pack

Minecraft 1.21.1 / NeoForge 21.1.252; use Java 21.

## Windows - Prism Launcher / Freesm

Download https://yungspiderq.github.io/my-neoforge-pack/latest/instance.zip
Import the ZIP as a new instance in Prism/Freesm and launch Minecraft.
The included pre-launch command runs packsync/sync.cmd before Minecraft.
The pack installer fetches changed files by their checksums from Pages.
If Java is not found or the network fails, the game may still launch
without the update. Inspect the game-folder packsync/sync.log.

## Modrinth App / AstralRinth

Import https://yungspiderq.github.io/my-neoforge-pack/latest/pack.mrpack
Configure the instance pre-launch hook manually:
Windows: cmd /c packsync\sync.cmd
Linux/macOS: sh packsync/sync.sh

Without this hook, a downloaded MRPACK is only a snapshot and does NOT auto-update.

## Linux/macOS Prism

Set a platform-specific pre-launch command invoking sh on
the game-folder packsync/sync.sh (the bundled command targets Windows).

## Caution

This rebuild contains NO mods yet. Old modded worlds may fail or lose
content if loaded without their old mods. Back up saves before use.
Only manifest-tracked config/mod files are synchronized, not saves/.
The previous pack remains in branch backup/pre-rebuild-2026-11-14.
