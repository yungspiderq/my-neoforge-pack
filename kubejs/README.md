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
├── client_scripts/    выполняются только на клиенте (JEI-подсказки, HUD)
└── assets/            работает как РЕСУРСПАК (приоритет выше jar'ов модов!)
    ├── kubejs/textures/…          картинки глав квестов и кастомных предметов
    └── galosphere/lang/ru_ru.json полный русский перевод Galosphere (см. ниже)
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
(главы «Земли Рассвета», «Багровое Пекло» и «Грань Пустоты»;
данные — `scripts/quests/chapters/*.py`).

Текстуры взяты из ванили (`gold_ingot`, `netherite_ingot`, `nether_star`) —
это гарантирует, что предмет отрисуется сразу. Свои png:

```
kubejs/assets/kubejs/textures/item/quest_token.png
```

и в `custom_items.js` замените `.texture('minecraft:item/gold_ingot')`
на `.texture('kubejs:item/quest_token')`.

---

## Перевод Galosphere (`assets/galosphere/lang/ru_ru.json`)

Родной `ru_ru.json` внутри Galosphere 1.21.1-1.5.5 устарел ещё с 1.20.x: из
297 ключей `en_us.json` переведено лишь 73 (и ещё 34 — мёртвые ключи старой
номенклатуры: `silver_*` → `palladium_*`, `warped_anchor` → `burrow_anchor`,
`advancements.story.*` → `advancements.galosphere.*`). В игре это выглядело
как английские названия почти всех блоков, предметов, мобов, достижений и
субтитров мода.

Наш файл `kubejs/assets/galosphere/lang/ru_ru.json` — **полный оверрайд на
297/297 ключей**. Это работает, потому что `kubejs/assets/` подключается как
ресурс-пак с приоритетом выше jar'ов модов, а языковые файлы Minecraft
мержит **по ключам** (наши значения перекрывают модовые). Терминология сведена
1-в-1 с главой квестов «Галосфера» (`scripts/quests/chapters/galosphere.py`):
«Стол горения», «Мешочек старателя», «Световая шашка», «Консервированный»,
«Норный якорь», «Спектерпиллар», «Искорка»…; достижения, которые квесты
цитируют по имени, в игре теперь называются ровно так же.

Полноту перевода стережёт чекер (подключён в CI, в шаг Validate):

```bash
python scripts/check_lang.py                            # офлайн: по снимку ключей jar'а
python scripts/check_lang.py --online                   # сверка с живым jar'ом с Modrinth
python scripts/check_lang.py --online --update-snapshot # переснять ключи после обновления мода
```

Он проверяет: покрытие всех ключей `en_us`, отсутствие лишних ключей (опечатка
в имени = тихий пропуск), непустые значения, значения, оставленные
английскими, и совпадение `%s`-плейсхолдеров. Снимок ключей лежит в
`scripts/lang/galosphere_en_us.json` (в пак не входит — `scripts/` исключён
`.packwizignore`). **После обновления версии Galosphere** обязательно:
`--online --update-snapshot`, затем доперевести новые ключи.

Тот же перевод собирается в **ресурс-пак `GalosphereRU.zip`**, который
включён в пак и **скачивается игрокам автоматически** в
`.minecraft/resourcepacks/` (при установке/обновлении любым способом:
однострочник packwiz, Modpack Manager, .mrpack через `overrides/`):

```bash
python scripts/gen_resourcepack.py          # → resourcepacks/GalosphereRU.zip
                                            #   + ../GalosphereRU.zip (запасная копия)
python scripts/gen_resourcepack.py --check  # CI: упакованная копия актуальна?
```

Внутри zip — байт-в-байт тот же `ru_ru.json` + `pack.mcmeta`
(pack_format 34 = MC 1.21.1) + рисованная `pack.png`; сборка
детерминирована (фиксированные метки времени в zip), поэтому `--check`
сверяет файл побайтово. После любой правки `ru_ru.json` перезапустите
генератор — иначе CI упадёт.

**Включать ресурспак в настройках не нужно**: в сборке перевод и так
применяется автоматически через `kubejs/assets/`. Упакованный zip —
портативная копия того же перевода: её можно унести в любой клиент
1.21.1 без KubeJS (положить в `resourcepacks/` и включить в «Настройки →
Наборы ресурсов») или раздать друзьям вручную — запасная копия лежит в
корне workspace и на Pages (`<base>/resourcepacks/GalosphereRU.zip`).

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
| В чате «KubeJS errors found», в логе `Tried to register event handler 'StartupEvents.…' for invalid script type SERVER` | обработчик StartupEvents попал в `server_scripts` — ему место только в `startup_scripts` (см. `startup_scripts/diagnostics.js`) |

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
// ТОЛЬКО в startup_scripts (в server_scripts KubeJS откажет с ошибкой):
StartupEvents.registry('item',  e => { e.create('id').displayName('Name') })
StartupEvents.registry('block', e => { e.create('id').material('metal') })
StartupEvents.init(e => { /* ранняя инициализация */ })
StartupEvents.postInit(e => { /* после закрытия реестров */ })

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
