# kubejs/ — скрипты KubeJS

KubeJS позволяет добавлять **свой контент** (предметы, блоки, рецепты, события)
без написания мода на Java. Скрипты — обычный JavaScript (движок Rhino).

Папка синхронизируется игрокам как есть: `kubejs/…` → `.minecraft/kubejs/…`.

```
kubejs/
├── startup_scripts/   выполняются ОДИН раз при загрузке игры (клиент + сервер)
│   └── custom_items.js    регистрация предметов
├── server_scripts/    выполняются на сервере (в одиночной игре — на встроенном)
│   ├── recipes.js         рецепты
│   └── diagnostics.js     строка в лог при загрузке
└── client_scripts/    выполняются только на клиенте (JEI-подсказки, HUD)
```

---

## Что сейчас добавлено

Три кастомных предмета (ID = `kubejs:<имя>`):

| ID | Название | Рецепт |
|---|---|---|
| `kubejs:quest_token` | Quest Token | бесформенный: алмаз + золотой слиток + изумруд |
| `kubejs:quest_token_premium` | Premium Quest Token | форменный: 6 незеритовых обломков, медаль в центре, 3 золота снизу |
| `kubejs:quest_medal` | Medal of the Quest Master | форменный: алмазные/изумрудные блоки, 2 улучшенные медали, звезда Нижнего мира |

Все три используются в главе **«Кастомный контент»**
(`config/ftbquests/quests/chapters/kubejs_custom.snbt`).

Текстуры взяты из ванили (`gold_ingot`, `netherite_ingot`, `nether_star`) —
это гарантирует, что предмет отрисуется сразу. Свои png:

```
kubejs/assets/kubejs/textures/item/quest_token.png
```

и в `custom_items.js` замените `.texture('minecraft:item/gold_ingot')`
на `.texture('kubejs:item/quest_token')`.

---

## Связка «квесты ↔ KubeJS»

Предмет, на который ссылается квест, **обязан** быть зарегистрирован, иначе
задача `item` никогда не выполнится, а иконка будет «отсутствующим предметом».

Порядок правки:

1. `quests/questline.py` — описание квеста (тексты, задачи, награды)
2. `kubejs/startup_scripts/custom_items.js` — регистрация предмета
3. `kubejs/server_scripts/recipes.js` — рецепт
4. `python scripts/gen_quests.py` — перегенерировать SNBT
5. `python scripts/check_quests.py` — **проверит, что все три места согласованы**

`check_quests.py` отдельно сверяет каждый `kubejs:`-предмет в квестах со
скриптами регистрации и с рецептами, так что рассинхрон ловится до запуска игры.

---

## Отладка

| Симптом | Где смотреть |
|---|---|
| Предметов нет в JEI | `logs/kubejs/startup.log` — ошибка регистрации |
| Рецепт не крафтится | `logs/kubejs/server.log` |
| Ничего не загрузилось | `logs/latest.log`: нет строк `[modpack] … загружены` |
| Иконка «missing» | не указан `.texture()` или путь до png неверный |

Перезагрузить скрипты без перезапуска игры:

```
/kubejs reload server_scripts
/kubejs reload startup_scripts     # требует перезапуска клиента для предметов
```

Регистрация новых предметов (`startup_scripts`) **требует полного перезапуска**
игры — и у всех игроков, иначе клиент и сервер разойдутся по реестру и
подключение не пройдёт.

---

## Полезные API (проверено для KubeJS 2101.7.x / MC 1.21.1)

```js
// регистрация
StartupEvents.registry('item',  e => { e.create('id').displayName('Name') })
StartupEvents.registry('block', e => { e.create('id').material('metal') })
StartupEvents.init(e => { /* ранняя инициализация */ })

// рецепты
ServerEvents.recipes(e => {
  e.shapeless('output', ['input1', 'input2'])
  e.shaped('output', ['ABC','DDD'], { A: 'minecraft:stone', B: '#c/logs', ... })
  e.smelting('output', 'input').xp(1.5)
  e.remove({ output: 'minecraft:tnt' })
})

// события
ServerEvents.loaded(e => { })
PlayerEvents.chat(e => { e.message.text })
EntityEvents.death('minecraft:zombie', e => { })
BlockEvents.broken(e => { })
ItemEvents.firstRightClicked(e => { })

// теги
ServerEvents.tags('item', e => { e.add('c:tools', 'kubejs:quest_token') })
```

Полная документация: <https://kubejs.com/wiki>

---

*Этот README не входит в пак — он исключён в `.packwizignore`.*
