// =====================================================================
//  Рецепты кастомных предметов
// ---------------------------------------------------------------------
//  server_scripts выполняются на сервере (в одиночной игре — на встроенном).
//  Здесь добавляются/меняются рецепты.
//
//  Все три рецепта соответствуют квестам со своими медалями:
//  «Медаль квеста» — глава «Земли Рассвета», секция «Чары и зелья»;
//  «Улучшенная медаль» — глава «Багровое Пекло», секция «Хозяева пекла»;
//  «Медаль мастера» — глава «Грань Пустоты», секция «Мастер пака».
//  Данные квестов живут в scripts/quests/chapters/*.py; меняете рецепт —
//  меняйте описание и перегенерируйте:  python scripts/gen_quests.py
// =====================================================================

ServerEvents.recipes(event => {

    // --- Медаль квеста: бесформенный рецепт ---
    event.shapeless('kubejs:quest_token', [
        'minecraft:diamond',
        'minecraft:gold_ingot',
        'minecraft:emerald'
    ])

    // --- Улучшенная медаль: форменный рецепт ---
    //     N N N
    //     N T N        T = обычная медаль
    //     G G G
    event.shaped('kubejs:quest_token_premium', [
        'NNN',
        'NTN',
        'GGG'
    ], {
        N: 'minecraft:netherite_scrap',
        T: 'kubejs:quest_token',
        G: 'minecraft:gold_ingot'
    })

    // --- Медаль мастера квестов ---
    //     D E D
    //     P S P        S = звезда Нижнего мира, P = улучшенная медаль
    //     D E D
    event.shaped('kubejs:quest_medal', [
        'DED',
        'PSP',
        'DED'
    ], {
        D: 'minecraft:diamond_block',
        E: 'minecraft:emerald_block',
        P: 'kubejs:quest_token_premium',
        S: 'minecraft:nether_star'
    })

    // --- Пример обратной стороны: убираем ванильный рецепт, если он мешает ---
    // event.remove({ output: 'minecraft:tnt' })
})
