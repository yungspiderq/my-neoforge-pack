// =====================================================================
//  Мост FTB Filter System <-> FTB Quests для MC 1.21.1 (v2).
//
//  Зачем: FTB Quests 2101.1.36 матчит задачи через адаптеры
//  (ItemMatchingSystem + ItemFilterAdapter) и показывает экран выбора
//  тега, но адаптер регистрирует мод-фильтр, а FFS 21.1.x на 1.21.1 этого
//  не делает (интеграция есть в 1.20.1 и в новых линейках MC — между ними
//  дыра). Без адаптера smart_filter в задаче требует сам себя.
//
//  Мост регистрирует минимальный адаптер: понимает фильтры
//    ftbfiltersystem:item_tag(<тег>)
//    ftbfiltersystem:item(<предмет>)
//    ftbfiltersystem:or(<фильтр> <фильтр> ...)   (как их пишет GUI)
//  матчит любой предмет тега/список предметов, отдаёт display-стаки и
//  создаёт стек фильтра для встроенного экрана выбора тега.
//
//  Проверка: logs/kubejs/startup.log ->
//    "[starlight] FFS tag bridge: адаптер зарегистрирован"
// =====================================================================

StartupEvents.postInit(event => {
    try {
        let ModDataComponents, ModItems
        try {
            ModDataComponents = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModDataComponents')
            ModItems = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModItems')
        } catch (e) {
            console.info('[starlight] FFS tag bridge: мод ftbfiltersystem не установлен — мост не нужен')
            return
        }
        const ItemStack = Java.loadClass('net.minecraft.world.item.ItemStack')
        const Registries = Java.loadClass('net.minecraft.core.registries.Registries')
        const TagKey = Java.loadClass('net.minecraft.core.registries.TagKey')
        const ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
        const Component = Java.loadClass('net.minecraft.network.chat.Component')
        const FTBQuestsAPI = Java.loadClass('dev.ftb.mods.ftbquests.api.FTBQuestsAPI')
        const FILTER_TYPE = ModDataComponents.FILTER_STRING.get()
        const SMART_FILTER = ModItems.SMART_FILTER.get()
        const NS = 'ftbfiltersystem:'

        function filterString(stack) {
            if (!stack || stack.isEmpty() || stack.getItem() !== SMART_FILTER) return null
            const v = stack.get(FILTER_TYPE)
            return v == null ? null : String(v)
        }
        // разбирает строку фильтра в функцию-предикат над ItemStack
        function compileFilter(str) {
            if (!str) return null
            let s = str.trim()
            if (s.startsWith(NS)) s = s.slice(NS.length)
            let m = /^item_tag\(([^)]+)\)$/.exec(s)
            if (m) {
                const key = TagKey.create(Registries.ITEM, ResourceLocation.parse(m[1].trim()))
                return stack => !stack.isEmpty() && stack.is(key)
            }
            m = /^item\(([^)]+)\)$/.exec(s)
            if (m) {
                const id = m[1].trim()
                return stack => !stack.isEmpty() && stack.getItem() === Java.loadClass('net.minecraft.core.registries.BuiltInRegistries').ITEM.get(ResourceLocation.parse(id))
            }
            m = /^or\((.+)\)$/.exec(s)
            if (m) {
                const inner = []
                const re = /([a-z0-9_.-]+:)?([a-zA-Z_]+)\(([^()]*(?:\([^()]*\))?[^()]*)\)/g
                let part
                while ((part = re.exec(m[1])) !== null) {
                    const sub = compileFilter((part[1] || '') + part[2] + '(' + part[3] + ')')
                    if (sub) inner.push(sub)
                }
                if (inner.length) return stack => inner.some(f => f(stack))
            }
            return null
        }
        function matcherOf(stack) {
            return compileFilter(filterString(stack))
        }

        const adapter = new JavaAdapter(dev.ftb.mods.ftbquests.api.ItemFilterAdapter, {
            getName: () => Component.literal('Starlight Tag Bridge'),
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
                const stack = new ItemStack(SMART_FILTER, 1)
                stack.set(FILTER_TYPE, NS + 'item_tag(' + tagKey.location().toString() + ')')
                return stack
            },
        })
        FTBQuestsAPI.instance().registerFilterAdapter(adapter)
        console.info('[starlight] FFS tag bridge: адаптер зарегистрирован — теги в задачах FTB Quests работают')
    } catch (err) {
        console.error('[starlight] FFS tag bridge не смог зарегистрироваться: ' + err)
    }
})
