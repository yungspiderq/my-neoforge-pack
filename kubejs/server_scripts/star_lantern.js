// =====================================================================
//  Фонарь звездочёта (kubejs:star_lantern) — предмет-фишка пака.
//  Регистрация и текстура: startup_scripts/custom_items.js и
//  scripts/gen_textures.py; рецепт: server_scripts/recipes.js;
//  квест: глава «Вечное Звездосветье», секция «Жемчужины и финал».
//
//  Правый клик: 20 секунд ночного зрения (400 тиков, без частиц эффекта
//  в инвентаре) + сноп искр end_rod + тихий звон аметиста. Работает и в
//  одиночной игре, и на сервере: событие серверное, эффекты и команды
//  исполняются от имени игрока.
// =====================================================================

// В KubeJS 2101 (MC 1.21.1) правый клик предметом — это ItemEvents.rightClicked;
// первым аргументом принимаем фильтр по ID, чтобы не дёргать событие попусту.
ItemEvents.rightClicked('kubejs:star_lantern', event => {
    const p = event.entity
    if (!p || !p.potionEffects) return
    p.potionEffects.add('minecraft:night_vision', 400, 0, false, true)
    p.runCommandSilent('particle minecraft:end_rod ~ ~1.2 ~ 0.35 0.5 0.35 0.04 20')
    p.runCommandSilent('playsound minecraft:block.amethyst_block.chime master @s ~ ~ ~ 0.5 1.3')
})
