# Installing My NeoForge Pack

Minecraft 1.21.1; NeoForge 21.1.252; Java 21.

**Prism / Freesm (Windows):** import https://yungspiderq.github.io/my-neoforge-pack/latest/instance.zip as a new instance. The pre-launch hook runs packwiz-installer from sync.cmd and downloads the selected pack on each launch.

**Modrinth App / AstralRinth:** import https://yungspiderq.github.io/my-neoforge-pack/latest/pack.mrpack and manually add Windows pre-launch hook: cmd /c packsync\\sync.cmd. Without the hook, you only install a snapshot.

**Linux/macOS:** set the launch hook to invoke sh packsync/sync.sh in the instance's game directory.

Use the in-game **Resource Packs** menu to enable Bare Bones and shader selection in Iris video settings. Both are optional and are not forced on by the installer.

Do not reuse an old modded world without a full backup. Check packsync/sync.log if updating fails; the pre-launch helper may allow the game to start after a sync error.
