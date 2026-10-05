// =====================================================================
//  Мост FTB Filter System <-> FTB Quests для MC 1.21.1.
//
//  Зачем: FTB Quests 2101.1.36 умеет матчить задачи через адаптеры
//  (ItemMatchingSystem + ItemFilterAdapter) и даже показывает экран
//  выбора тега, но адаптер должен зарегистрировать мод-фильтр. FFS 21.1.4
//  на 1.21.1 этого не делает (интеграция появилась только в новых MC),
//  поэтому smart_filter в задаче требовал сам себя. Этот скрипт
//  регистрирует минимальный адаптер: понимает фильтры вида
//  item_tag(<тег>) и матчит любой предмет тега; заодно оживает
//  встроенный экран выбора тега в редакторе квестов.
//
//  Проверка: в logs/kubejs/startup.log должна быть строка
//  "[starlight] FFS tag bridge: адаптер зарегистрирован".
// =====================================================================

StartupEvents.postInit(event => {
    try {
        if (!Platform.isModLoaded('ftbfiltersystem')) {
            console.info('[starlight] FFS tag bridge: мод ftbfiltersystem не стоит — мост не нужен')
            return
        }
        const ItemStack = Java.loadClass('net.minecraft.world.item.ItemStack')
        const Registries = Java.loadClass('net.minecraft.core.registries.Registries')
        const TagKey = Java.loadClass('net.minecraft.core.registries.TagKey')
        const ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
        const ModDataComponents = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModDataComponents')
        const ModItems = Java.loadClass('dev.ftb.mods.ftbfiltersystem.registry.ModItems')
        const FTBQuestsAPI = Java.loadClass('dev.ftb.mods.ftbquests.api.FTBQuestsAPI')
        const FILTER_TYPE = ModDataComponents.FILTER_STRING.get()
        const SMART_FILTER = ModItems.SMART_FILTER.get()

        function filterTagString(stack) {
            if (!stack || stack.isEmpty() || stack.getItem() !== SMART_FILTER) return null
            const v = stack.get(FILTER_TYPE)
            return v == null ? null : String(v)
        }
        function parseTag(str) {
            // поддерживаем фильтры вида item_tag(<namespace>:<path>)
            const m = /^item_tag\(([^)]+)\)$/.exec(str || '')
            return m ? m[1] : null
        }
        function matches(filterStack, toCheck) {
            const tagId = parseTag(filterTagString(filterStack))
            if (!tagId || !toCheck || toCheck.isEmpty()) return false
            const key = TagKey.create(Registries.ITEM, ResourceLocation.parse(tagId))
            return toCheck.is(key)
        }

        const adapter = new JavaAdapter(dev.ftb.mods.ftbquests.api.ItemFilterAdapter, {
            getName: () => 'Starlight Tag Bridge',
            isFilterStack: stack => filterTagString(stack) != null,
            doesItemMatch: (filterStack, toCheck, _registries) => matches(filterStack, toCheck),
            getMatcher: filterStack => (toCheck => matches(filterStack, toCheck)),
            hasItemTagFilter: () => true,
            makeTagFilterStack: tagKey => {
                const stack = new ItemStack(SMART_FILTER, 1)
                stack.set(FILTER_TYPE, 'item_tag(' + tagKey.location().toString() + ')')
                return stack
            },
        })
        FTBQuestsAPI.instance().registerFilterAdapter(adapter)
        console.info('[starlight] FFS tag bridge: адаптер зарегистрирован — теги в задачах FTB Quests работают')
    } catch (err) {
        console.error('[starlight] FFS tag bridge не смог зарегистрироваться: ' + err)
    }
})
