# FancyMenu — Chronicles 0.4.1 UI hotfix

## Reported regression and fix

At 1664×916, the old FancyMenu 0.4 layout drew custom overlays **on top of**
the vanilla Minecraft logo, Realms icon, branding and native buttons.
The custom buttons also extended outside the left-hand panel.

**Root cause:** the previous generated `vanilla_button` declarations
omitted `element_type = vanilla_button`. FancyMenu did not apply their
`is_hidden` rules. In addition, the overlay buttons used a centered anchor
which placed them in the middle of the screen, across the background.

### Changes

- Restored the proper FancyMenu 3.x syntax for every styled and hidden widget.
- Hide the Minecraft logo, splash, branding, Realms button and Realms icons.
- **Style the actual original title-screen buttons** (Singleplayer,
  Multiplayer, Settings, Mods, Quit) instead of creating overlapping
  controls that mimic them. Original Minecraft actions still work.
- Anchor the five buttons to `mid-left`, within the illustration's left panel.
  Designed for the supplied 1664×916 screenshot and responsive anchoring.
- Keep Language and Accessibility available in the lower-right.
- Keep a separately styled custom repository button.
- Remove the extra bottom-center version label so it doesn't collide with
  Minecraft's unavoidable copyright display.
- Set `show_customization_overlay=false` and `modpack_mode=true` to hide
  FancyMenu editor chrome for ordinary pack players.
- Validate hidden elements, accessible native buttons and approximate
  1664×916 layout geometry in CI.

## Files

- `scripts/gen_menu.py` — deterministic design/layout generator
- `config/fancymenu/customization/chronicles_title_layout.txt` — generated layout
- `config/fancymenu/assets/chronicles_background.png` — original 1920×1080 background
- `config/fancymenu/assets/chronicles_button.png` — button (normal)
- `config/fancymenu/assets/chronicles_button_hover.png` — button (hover)
- `config/fancymenu/options.txt` — overlay/modpack mode controls

This hotfix keeps the rest of the pack and all quest progress unchanged.

**Testing:** CI checks layout syntax, geometry, dependencies and distributable
archives. It does not render the Minecraft GUI, so verify with an in-game
screenshot after the pack updates.
