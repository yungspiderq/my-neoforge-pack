// =====================================================================
//  Кастомные предметы модпака
// ---------------------------------------------------------------------
//  startup_scripts выполняются ОДИН РАЗ при загрузке игры (и на клиенте,
//  и на сервере) — именно здесь регистрируются новые предметы и блоки.
//
//  Зарегистрированный ID = "kubejs:" + имя ниже.
//  Эти же ID используются в квестах (scripts/quests/chapters/*.py ->
//  config/ftbquests/quests/chapters/*.snbt) и в рецептах:
//  kubejs/server_scripts/recipes.js
//
//  Текстуры — СОБСТВЕННЫЕ, рисуются скриптом scripts/gen_textures.py и лежат в
//      kubejs/assets/kubejs/textures/item/<имя>.png
//  KubeJS подхватывает их через .texture('kubejs:item/<имя>') и сам генерирует
//  модель item/generated с layer0 = эта текстура. Перегенерировать картинки:
//      python scripts/gen_textures.py
// =====================================================================

StartupEvents.registry('item', event => {

    // Бронзовая медаль: базовая награда за главы.
    event.create('quest_token')
        .displayName('Quest Token')
        .texture('kubejs:item/quest_token')
        .tooltip('Медаль квеста. Выдаётся за пройденные главы.')
        .maxStackSize(64)

    // Незеритовая медаль: улучшенная, крафтится из трёх обычных.
    event.create('quest_token_premium')
        .displayName('Premium Quest Token')
        .texture('kubejs:item/quest_token_premium')
        .tooltip('Улучшенная медаль. Скрафти из трёх обычных.')
        .maxStackSize(64)

    // Финальная медаль: требует звезду Нижнего мира.
    event.create('quest_medal')
        .displayName('Medal of the Quest Master')
        .texture('kubejs:item/quest_medal')
        .tooltip('Финальная награда пака. Требует звезду Нижнего мира.')
        .rarity('epic')
        .maxStackSize(16)

    // Предмет-фишка пака: фонарь звездочёта (см. server_scripts/star_lantern.js).
    // Правый клик — короткое ночное зрение и сноп звёздных искр.
    event.create('star_lantern')
        .displayName('Stargazer\'s Lantern')
        .texture('kubejs:item/star_lantern')
        .tooltip('Правый клик: 20 секунд ночного зрения и сноп звёздных искр.')
        .tooltip('Оправа из звездопала вокруг звёздного алмаза — рецепт в верстаке.')
        .rarity('rare')
        .maxStackSize(1)

    // Самопроверка: если здесь не четыре предмета, квесты со своими
    // наградами будут невыполнимы — и об этом скажет лог, а не пустая книга.
    console.info('[modpack] кастомных предметов зарегистрировано: 4 ' +
                 '(quest_token, quest_token_premium, quest_medal, star_lantern)')
})
