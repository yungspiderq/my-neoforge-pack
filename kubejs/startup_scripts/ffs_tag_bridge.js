// =====================================================================
//  Мост FTB Filter System <-> FTB Quests для MC 1.21.1 (v6).
//
//  На 1.21.1 ни FFS 21.1.x, ни FTB Quests 2101.1.36 не несут интеграцию
//  друг к другу (проверено сканированием jar): FTB Quests даёт API
//  адаптеров и экран выбора тега, FFS — предмет-фильтр и парсер строк,
//  а соединяет их пак (как в RLCMC). Это и есть мост.
//
//  Поддержка строк фильтра: ftbfiltersystem:item_tag(<тег>),
//  ftbfiltersystem:item(<предмет>), ftbfiltersystem:or(...) — как их
//  сериализует GUI рабочих сборок.
//
//  Стиль файла — осознанно варварский: ТОЛЬКО var и function-декларации.
//  Rhino в KubeJS переиспользует scope скрипта между проходами, и
//  const/let внутри обработчика дают "TypeError: redeclaration of var X"
//  (проверено боем: v1 упал на Platform.isModLoaded, v2/v3 на const).
//  Повторную регистрацию исключает guard global.swFfsBridgeDone.
//  v5: матчинг тега без класса TagKey (он не грузится Java.loadClass в этом
//  окружении) — через builtInRegistryHolder().tags() держателя предмета.
//  v6: сигнатуры по исходникам FTB-Quests 1.21.1/main: вход через
//  FTBQuestsAPI.api() (не .instance()), getName возвращает String,
//  getMatcher принимает (filterStack, registryAccess).
//
//  Проверка: logs/kubejs/startup.log:
//    "[starlight] FFS tag bridge: адаптер зарегистрирован"
//    "[starlight] FFS tag bridge self-test: OK"
// =====================================================================

function swParseFilter(str, ctx) {
    if (!str) return null
    var s = String(str).trim()
    if (s.indexOf('ftbfiltersystem:') === 0) s = s.slice('ftbfiltersystem:'.length)
    var m = /^item_tag\(([^)]+)\)$/.exec(s)
    if (m) {
        var tagId = m[1].trim()
        // TagKey не создаём: Java.loadClass('...TagKey') в этом окружении не
        // грузится, а держатель предмета сам отдаёт все свои теги.
        return function (stack) {
            if (!stack || stack.isEmpty()) return false
            return stack.getItem().builtInRegistryHolder().tags().anyMatch(function (t) {
                return t.location().toString() === tagId
            })
        }
    }
    m = /^item\(([^)]+)\)$/.exec(s)
    if (m) {
        var item = ctx.builtIn.ITEM.get(ctx.rl.parse(m[1].trim()))
        return function (stack) { return !stack.isEmpty() && stack.getItem() === item }
    }
    m = /^or\((.+)\)$/.exec(s)
    if (m) {
        var inner = []
        var re = /(?:[a-z0-9_.-]+:)?([a-zA-Z_]+)\(([^()]*(?:\([^()]*\))?[^()]*)\)/g
        var part
        while ((part = re.exec(m[1])) !== null) {
            var sub = swParseFilter(part[1] + '(' + part[2] + ')', ctx)
            if (sub) inner.push(sub)
        }
        if (inner.length) {
            return function (stack) {
                for (var i = 0; i < inner.length; i++) if (inner[i](stack)) return true
                return false
            }
        }
    }
    return null
}

function swRegisterBridge() {
    if (global.swFfsBridgeDone) return
    global.swFfsBridgeDone = true
    var ctx = {}
    try {
        ctx.components = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModDataComponents')
        ctx.items = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModItems')
    } catch (e) {
        console.info('[starlight] FFS tag bridge: мод ftbfiltersystem не установлен — мост не нужен')
        return
    }
    ctx.stack = Java.loadClass('net.minecraft.world.item.ItemStack')
    ctx.registries = Java.loadClass('net.minecraft.core.registries.Registries')
    ctx.builtIn = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
    ctx.rl = Java.loadClass('net.minecraft.resources.ResourceLocation')
    ctx.component = Java.loadClass('net.minecraft.network.chat.Component')
    ctx.api = Java.loadClass('dev.ftb.mods.ftbquests.api.FTBQuestsAPI')
    ctx.iface = Java.loadClass('dev.ftb.mods.ftbquests.api.ItemFilterAdapter')
    ctx.FILTER_TYPE = ctx.components.FILTER_STRING.get()
    ctx.SMART_FILTER = ctx.items.SMART_FILTER.get()

    ctx.filterString = function (stack) {
        if (!stack || stack.isEmpty() || stack.getItem() !== ctx.SMART_FILTER) return null
        var v = stack.get(ctx.FILTER_TYPE)
        return v == null ? null : String(v)
    }
    ctx.matcherOf = function (stack) {
        return swParseFilter(ctx.filterString(stack), ctx)
    }

    var adapter = new JavaAdapter(ctx.iface, {
        getName: function () { return 'Starlight Tag Bridge' },
        isFilterStack: function (stack) { return ctx.filterString(stack) != null },
        doesItemMatch: function (filterStack, toCheck, registries) {
            var f = ctx.matcherOf(filterStack)
            return f != null && f(toCheck)
        },
        getMatcher: function (filterStack, registryAccess) {
            var f = ctx.matcherOf(filterStack)
            if (f == null) return function (stack) { return false }
            return f
        },
        hasItemTagFilter: function () { return true },
        makeTagFilterStack: function (tagKey) {
            var stack = new ctx.stack(ctx.SMART_FILTER, 1)
            stack.set(ctx.FILTER_TYPE, 'ftbfiltersystem:item_tag(' + tagKey.location().toString() + ')')
            return stack
        },
    })
    ctx.api.api().registerFilterAdapter(adapter)
    console.info('[starlight] FFS tag bridge: адаптер зарегистрирован — теги в задачах FTB Quests работают')
    try {
        var matching = Java.loadClass('dev.ftb.mods.ftbquests.integration.item_filtering.ItemMatchingSystem')
        var testFilter = new ctx.stack(ctx.SMART_FILTER, 1)
        testFilter.set(ctx.FILTER_TYPE, 'ftbfiltersystem:item_tag(minecraft:logs)')
        var testLog = new ctx.stack(ctx.builtIn.ITEM.get(ctx.rl.parse('minecraft:oak_log')), 1)
        var ok = matching.INSTANCE.doesItemMatch(
            testFilter, testLog, matching.ComponentMatchType.NONE, null)
        console.info('[starlight] FFS tag bridge self-test: ' + (ok ? 'OK' : 'FAIL'))
    } catch (e2) {
        console.warn('[starlight] FFS tag bridge self-test не запустился: ' + e2)
    }
}

StartupEvents.postInit(function (event) {
    try {
        swRegisterBridge()
    } catch (err) {
        console.error('[starlight] FFS tag bridge не смог зарегистрироваться: ' + err)
    }
})
