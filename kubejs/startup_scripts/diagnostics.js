// =====================================================================
//  Диагностика загрузки (startup_scripts)
// ---------------------------------------------------------------------
//  server_scripts НЕ могут регистрировать обработчики StartupEvents:
//  KubeJS печатает
//      "Tried to register event handler 'StartupEvents.init' for invalid
//       script type SERVER! Valid script types: [STARTUP]"
//  и в игре появляется «KubeJS errors found [1]!». Всё, что связано со
//  стартом мода, живёт здесь, в startup_scripts; в server_scripts остаются
//  только ServerEvents (recipes.js, диагностика сервера).
//
//  Строки ниже попадают в logs/kubejs/start.log ОДИН РАЗ на запуск игры.
//  Нет строки «startup_scripts загружены» = скрипты не подхватились,
//  кастомных предметов не будет.
//
//  Сколько своих предметов зарегистрировано, печатает custom_items.js
//  прямо из события реестра.
//
//  Перезагрузить без перезапуска игры:  /kubejs reload startup_scripts
// =====================================================================

StartupEvents.init(event => {
    console.info('[modpack] startup_scripts загружены: ждём реестры')
})

StartupEvents.postInit(event => {
    console.info('[modpack] startup завершён: реестры закрыты, ' +
                 'предметы и рецепты активны')
})
