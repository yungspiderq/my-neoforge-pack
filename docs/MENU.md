# FancyMenu — Chronicles / Clockwork Atlas

Replaced the previous Starlight menu (old background and vanilla-looking buttons)
with a self-contained design created specifically for this pack.

- Dark blue/bronze atlas background with cogwheels, map contours and build motifs.
- Five interactive custom buttons with separate idle/hover textures.
- Proper mimic-vanilla actions for singleplayer, multiplayer, options, mods and quit.
- Repository shortcut, version footer and custom title branding.
- Original 1920x1080 PNG artwork; no external image dependencies or fonts shipped.

All assets are generated with python scripts/gen_menu.py by Pillow.
FancyMenu layout: config/fancymenu/customization/chronicles_title_layout.txt.

Buttons use FancyMenu's mimicbutton action, targeting the vanilla title_screen
widget IDs so they remain functional after the visual redesign.

If an action differs in a future Minecraft/FancyMenu release, use FancyMenu editor
inside the game to pick the corresponding vanilla button and update its identifier.
No launcher hook or Java code changes are necessary.
