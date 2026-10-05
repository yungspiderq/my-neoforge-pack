// =====================================================================
//  Мост FTB Filter System <-> FTB Quests для MC 1.21.1 (v3).
//
//  На 1.21.1 ни FFS 21.1.0-21.1.4, ни FTB Quests 2101.1.36 не несут
//  интеграцию друг к другу (проверено сканированием jar): FTB Quests
//  даёт API адаптеров и экран выбора тега, но адаптер регистрирует
//  pack/vendor. В рабочих сборках (например RLCMC) этот мост живёт в
//  самих паках. Здесь — наша версия моста.
//
//  Поддерживаются фильтры: ftbfiltersystem:item_tag(<тег>),
//  ftbfiltersystem:item(<предмет>), ftbfiltersystem:or(...) — то, что
//  создаёт встроенный GUI.
//
//  Проверка: logs/kubejs/startup.log:
//    "[starlight] FFS tag bridge: адаптер зарегистрирован"
//    "[starlight] FFS tag bridge self-test: OK" (дубовое бревно матчится
//    фильтром #minecraft:logs)
//  ВАЖНО: имена классов держим в переменных с префиксом Mc*/Ffs*,
//  потому что ItemStack/Component/ResourceLocation — глобалки KubeJS,
//  и const с таким же именем роняет скрипт (TypeError: redeclaration).
// =====================================================================

StartupEvents.postInit(event => {
    try {
        let FfsComponents, FfsItems
        try {
            FfsComponents = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModDataComponents')
            FfsItems = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModItems')
        } catch (e) {
            console.info('[starlight] FFS tag bridge: мод ftbfiltersystem не установлен — мост не нужен')
            return
        }
        const McStack = Java.loadClass('net.minecraft.world.item.ItemStack')
        const McRegistries = Java.loadClass('net.minecraft.core.registries.Registries')
        const McBuiltIn = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
        const McTagKey = Java.loadClass('net.minecraft.core.registries.TagKey')
        const McRL = Java.loadClass('net.minecraft.resources.ResourceLocation')
        const McComponent = Java.loadClass('net.minecraft.network.chat.Component')
        const QuestsAPI = Java.loadClass('dev.ftb.mods.ftbquests.api.FTBQuestsAPI')
        const AdapterIface = Java.loadClass('dev.ftb.mods.ftbquests.api.ItemFilterAdapter')
        const FILTER_TYPE = FfsComponents.FILTER_STRING.get()
        const SMART_FILTER = FfsItems.SMART_FILTER.get()
        const NS = 'ftbfiltersystem:'

        function filterString(stack) {
            if (!stack || stack.isEmpty() || stack.getItem() !== SMART_FILTER) return null
            const v = stack.get(FILTER_TYPE)
            return v == null ? null : String(v)
        }
        function compileFilter(str) {
            if (!str) return null
            let s = String(str).trim()
            if (s.startsWith(NS)) s = s.slice(NS.length)
            let m = /^item_tag\(([^)]+)\)$/.exec(s)
            if (m) {
                const key = McTagKey.create(McRegistries.ITEM, McRL.parse(m[1].trim()))
                return stack => !stack.isEmpty() && stack.is(key)
            }
            m = /^item\(([^)]+)\)$/.exec(s)
            if (m) {
                const item = McBuiltIn.ITEM.get(McRL.parse(m[1].trim()))
                return stack => !stack.isEmpty() && stack.getItem() === item
            }
            m = /^or\((.+)\)$/.exec(s)
            if (m) {
                const inner = []
                const re = /(?:[a-z0-9_.-]+:)?([a-zA-Z_]+)\(([^()]*(?:\([^()]*\))?[^()]*)\)/g
                let part
                while ((part = re.exec(m[1])) !== null) {
                    const sub = compileFilter(part[1] + '(' + part[2] + ')')
                    if (sub) inner.push(sub)
                }
                if (inner.length) return stack => inner.some(f => f(stack))
            }
            return null
        }
        function matcherOf(stack) {
            return compileFilter(filterString(stack))
        }

        const adapter = new JavaAdapter(AdapterIface, {
            getName: () => McComponent.literal('Starlight Tag Bridge'),
            isFilterStack: stack => filterString(stack) != null,
            doesItemMatch: (filterStack, toCheck, _registries) => {
                const f = matcherOf(filterStack)
                return f != null && f(toCheck)
            },
            getMatcher: filterStack => {
                const f = matcherOf(filterStack)
                return f == null ? (stack => false) : f
            },
            hasItemTagFilter: () => true,
            makeTagFilterStack: tagKey => {
                const stack = new McStack(SMART_FILTER, 1)
                stack.set(FILTER_TYPE, NS + 'item_tag(' + tagKey.location().toString() + ')')
                return stack
            },
        })
        QuestsAPI.instance().registerFilterAdapter(adapter)
        console.info('[starlight] FFS tag bridge: адаптер зарегистрирован — теги в задачах FTB Quests работают')
        try {
            const McMatching = Java.loadClass('dev.ftb.mods.ftbquests.integration.item_filtering.ItemMatchingSystem')
            const testFilter = adapter.makeTagFilterStack(
                McTagKey.create(McRegistries.ITEM, McRL.parse('minecraft:logs')))
            const testLog = new McStack(McBuiltIn.ITEM.get(McRL.parse('minecraft:oak_log')), 1)
            const ok = McMatching.INSTANCE.doesItemMatch(
                testFilter, testLog, McMatching.ComponentMatchType.NONE, null)
            console.info('[starlight] FFS tag bridge self-test: ' + (ok ? 'OK' : 'FAIL'))
        } catch (e2) {
            console.warn('[starlight] FFS tag bridge self-test не запустился: ' + e2)
        }
    } catch (err) {
        console.error('[starlight] FFS tag bridge не смог зарегистрироваться: ' + err)
    }
})
