# My NeoForge Pack - clean starter

This is a new baseline, not the old story-driven pack.
Minecraft 1.21.1 / NeoForge 21.1.252 / Java 21.
Currently: zero mods, no quests, no KubeJS scripts.

The previous complete repository is preserved in the branch:
backup/pre-rebuild-2026-11-14
Original commit: ed5647097ade7f69992ac57d58d7d3bda9c76e2b

## Auto updates

Prism/Freesm imports from:
https://yungspiderq.github.io/my-neoforge-pack/latest/instance.zip

The Windows instance has a pre-launch command that runs packwiz-installer.
On every start it compares hashes with GitHub Pages and downloads changed files.

Modrinth App or AstralRinth:
https://yungspiderq.github.io/my-neoforge-pack/latest/pack.mrpack
Requires manually configuring a pre-launch hook as described in INSTALL.md.

## Add mods

Install packwiz: https://packwiz.infra.link/installation/

Run:
    packwiz modrinth add <slug>
    python scripts/pack.py refresh
    python scripts/pack.py validate
    git add . && git commit -m "Add mods" && git push

The repository stores mods/*.pw.toml reference files, not mod JARs.
Put shared config files in config/; KubeJS scripts in kubejs/.
Every push to main deploys the new pack. A release is optional.
For a tagged GitHub Release use a v-prefixed tag.

Test locally:
    python scripts/pack.py site

## Safety

This is a new pack, NOT a migration of the previous pack.
Back up your worlds. Do not load old modded saves into the empty starter.
The updater does not track your personal saves/ directory.
