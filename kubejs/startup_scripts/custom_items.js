// =====================================================================
//  Кастомные предметы модпака
// ---------------------------------------------------------------------
//  startup_scripts выполняются ОДИН РАЗ при загрузке игры (и на клиенте,
//  и на сервере) — именно здесь регистрируются новые предметы и блоки.
//
//  Зарегистрированный ID = "kubejs:" + имя ниже.
//  Эти же ID используются в квестах: config/ftbquests/quests/chapters/kubejs_custom.snbt
//  и в рецептах: kubejs/server_scripts/recipes.js
//
//  Текстуры намеренно взяты из ванили — это гарантирует, что предмет
//  отрисуется сразу. Свои png кладите в
//      kubejs/assets/kubejs/textures/item/<имя>.png
//  и меняйте .texture('kubejs:item/<имя>').
// =====================================================================

StartupEvents.registry('item', event => {

    event.create('quest_token')
        .displayName('Quest Token')
        .texture('minecraft:item/gold_ingot')
        .tooltip('Выдается за выполнение квестов.')
        .maxStackSize(64)

    event.create('quest_token_premium')
        .displayName('Premium Quest Token')
        .texture('minecraft:item/netherite_ingot')
        .tooltip('Улучшенная медаль. Скрафти из обычной.')
        .maxStackSize(64)

    event.create('quest_medal')
        .displayName('Medal of the Quest Master')
        .texture('minecraft:item/nether_star')
        .tooltip('Финальная награда. Требует звезду Нижнего мира.')
        .maxStackSize(16)
})
