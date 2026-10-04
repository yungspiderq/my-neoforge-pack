# scripts/quests/ — квестовая линейка FTB Quests

Квесты пишутся **на Python**, а не руками в SNBT. Данные глав лежат в
`chapters/*.py`, мини-DSL для записи — в `qdsl.py`, точка входа —
`questline.py`; `scripts/gen_quests.py` генерирует из них файлы в
`config/ftbquests/quests/`, а `scripts/check_quests.py` проверяет результат
без Minecraft.

```bash
python scripts/gen_quests.py              # перегенерировать
python scripts/gen_quests.py --check      # только проверить данные, не писать
python scripts/check_quests.py --registry # валидация готовых .snbt + реестр MC
python scripts/gen_textures.py --check    # картинки глав актуальны
```

CI делает и то и другое: валится, если закоммиченные `.snbt` не совпадают
с данными глав, если валидатор нашёл ошибку или если текстура из квеста
не найдена на диске.

Линейка сейчас: **4 главы / 194 квеста / 432 задачи / 396 наград** —
«Земли Рассвета» (Верхний мир, 8 секций), «Багровое Пекло» (Нижний мир,
6 секций), «Грань Пустоты» (Край, 4 секции) и «Галосфера» (мод Galosphere,
8 секций — весь контент мода: биомы, структуры, палладий, стерлинг, кроты,
археология, берсерк; вход — розовый портал у «Глубокой тьмы»).

---

## Зачем генератор, а не ручные .snbt

Потому что в формате FTB Quests легко ошибиться так, что **ничего не упадёт** —
квесты просто молча не появятся или будут с пустыми названиями:

| Ловушка | Последствие |
|---|---|
| ID — не 16-символьный uppercase hex | `readID()` молча перегенерирует ID → все связи рвутся |
| ID равен 0 или 1 | то же самое: эти значения мод считает невалидными |
| Два объекта с одним ID | второй перезапишет первый |
| `dependencies` указывает на несуществующий квест | `removeInvalidDependencies()` молча удалит связь |
| lang-ключ не совпадает с ID | заголовок квеста пустой |
| `quest_desc` написан строкой, а не списком | FTB бросит `IllegalArgumentException` |
| `.packwizignore` содержит некорневой паттерн | go-gitignore матчит его на любом уровне — так `quests/**` вырезал `config/ftbquests/quests/` |
| `ItemTask.count` написан как int, а не long | задача может не определиться |
| `ItemReward.count` написан как long | то же, но в другую сторону |
| Поле `levels` вместо `xp_levels` | награда выдаст 0 уровней |
| У картинки главы нет `id` | мод выдаст случайный → заголовок из lang потеряется |
| Картинка с `text_on_image`, но без `title` | рисовать нечего, молча пусто |

Генератор исключает весь этот класс ошибок: ID выдаются из схемы, lang-ключи
строятся из тех же ID, а типы полей проверяются по схеме, выверенной по
исходникам мода.

---

## Формат выверен по исходникам, а не по догадкам

Все имена полей и типы взяты из ветки
[`FTBTeam/FTB-Quests` @ `1.21.1/main`](https://github.com/FTBTeam/FTB-Quests/tree/1.21.1/main),
что соответствует FTB Quests **2101.1.36**:

| Источник | Что оттуда взято |
|---|---|
| `quest/BaseQuestFile.java` | `VERSION = 13`, структура `chapters/`, `reward_tables/`, `lang/`, `data.snbt`, `chapter_groups.snbt` |
| `quest/BaseQuestFile.java` → `readDataFull` | **квесты лежат ИНЛАЙНОМ в файле главы**, списком `quests` — не отдельными файлами |
| `quest/BaseQuestFile.java` → `writeChapterFiles` | `id`, `group` (`""` = группа по умолчанию), `order_index`, `quests`, `quest_links`, `images` |
| `quest/QuestObjectBase.java` → `getCodeString` | `String.format("%016X", id)` — 16 символов uppercase hex |
| `quest/QuestObjectBase.java` → `writeData` | `icon` — ItemStack SNBT; `tags` — список строк |
| `quest/Quest.java` → `writeData` | `x`/`y`/`size`/`icon_scale` — **double**; `dependencies` — список строк; `dependency_requirement`, `progression_mode`, `min_required_dependencies`, `optional`, `can_repeat`, … |
| `quest/ChapterImage.java` | `x/y/width/height/rotation` — double, `image` — строка-иконка, `color` — int RGB, `alpha`/`order` — int, `click_action`, `dev`, `corner`, `dependency`, `position_locked`, `text_on_image`, `text_shadow`, `text_inset`, `text_h_align`, `text_v_align` |
| `quest/ImageClickAction.java` | типы клика: `none`, `open_uri`, `open_quest`, `run_command`, `custom_event`, `show_recipe`, `show_docs`; формат в NBT — `"<тип>:<данные>"` |
| `client/gui/quests/ChapterImageButton.java` | картинки рисуются слоем **BACKGROUND**, то есть всегда ПОД линиями и квестами; порядок между собой задаёт `order`; `text_on_image` рисует заголовок **шрифтом игры** внутри рамки картинки |
| `quest/QuestLink.java` | `linked_quest` — code-строка квеста, `x`/`y`, `shape`, `size` |
| `quest/task/ItemTask.java` | `item` (compound), `count` — **long**, пишется только если > 1 |
| `quest/task/XPTask.java` | `value` — **long**; `points` — bool; задача **забирает** опыт у игрока |
| `quest/task/LocationTask.java` | `position` — **IntArray** `[x,y,z]` = МИН-угол, `size` — `[w,h,d]` |
| `quest/task/ObservationTask.java` | `observation_type` — имя из enum, `observe_type` — его ordinal, `timer` — long |
| `quest/reward/ItemReward.java` | `item`, `count` — **int** (не long!), `random_bonus` — int |
| `quest/reward/XPLevelsReward.java` | поле называется **`xp_levels`**, а не `levels` |
| `quest/reward/CommandReward.java` | `command`, `permission_level`, `silent`, `feedback_message`; `{p}`, `{x}`, `{y}`, `{z}`, `{team}` подставляются, команда идёт через `performPrefixedCommand` |
| `quest/QuestObjectType.java` | `chapter`, `quest`, `task`, `reward`, `reward_table`, `chapter_group`, `quest_link`, `image` |
| `quest/translation/TranslationManager.java` → `makeKey` | ключ = `<objectType>.<ID>.<поле>` — работает и для `image.*` |
| `quest/translation/TranslationKey.java` | `title` (строка), `quest_subtitle` (строка), `quest_desc` (**список**), `chapter_subtitle` (**список**) |
| `TranslationManager.DEFAULT_FALLBACK_LOCALE` | `en_us` — грузится и отправляется игроку всегда |

**Важное следствие:** начиная с этой версии FTB Quests заголовки и описания
**не хранятся** в файлах глав. Они живут в `config/ftbquests/quests/lang/<локаль>.snbt`
и привязаны к ID через ключ `<тип>.<ID>.<поле>`. Поэтому правка `title:` прямо
в `chapters/*.snbt` не даст ничего — её затрёт, а текст не появится.

---

## Структура данных

```
scripts/quests/
├── questline.py          точка входа: порядок глав, FILE_SETTINGS, FILE_VERSION
├── qdsl.py               helpers: Q, SEC, item/kill/stat/adv/biome/struct/…,
│                         give/lvl/xpr/say/toast, halo/portal/backdrop
├── chapters/
│   ├── overworld.py      глава 1 — «Земли Рассвета»   (84 квеста, 8 секций)
│   ├── nether.py         глава 2 — «Багровое Пекло»   (35 квестов, 6 секций)
│   ├── end.py            глава 3 — «Грань Пустоты»    (22 квеста, 4 секции)
│   └── galosphere.py     глава 4 — «Галосфера»        (53 квеста, 8 секций,
│                                                       мод Galosphere)
└── mc_registry_1.21.1.json   реестр MC + модов (секция "mods")
                            для check_quests.py --registry
```

```
config/ftbquests/quests/          (генерируется, руками не правится)
├── data.snbt                 version 13, default_quest_shape, fallback_locale
├── chapter_groups.snbt       chapter_groups: [ ]   (пусто = группа по умолчанию)
├── chapters/
│   ├── overworld.snbt
│   ├── nether.snbt
│   └── end.snbt
└── lang/
    ├── en_us.snbt            fallback-локаль, грузится всегда
    └── ru_ru.snbt            подхватится, если в клиенте выбран русский
```

Ключи сортируются при записи — FTB Quests делает то же самое
(`SNBT.setShouldSortKeysOnWrite(true)`), поэтому правки квестов в игре
не создают лишний diff.

---

## Схема ID

Младший полубайт ID квеста **должен быть нулевым** — туда генератор пишет
индекс задачи или награды. Отсюда ограничение: максимум 15 задач и 15 наград
на квест. Диапазоны не пересекаются, поэтому коллизий не бывает by construction:

| Объект | Шаблон | Пример |
|---|---|---|
| глава | `0xC000 + ci` | `000000000000C001` |
| квест | `0x100000 + ci*0x1000 + qi*0x10` | `0x101540` → `0000000000101540` |
| задача | `0x200000 + slot + t` (slot = id квеста & 0xFFFFF) | `0000000000201540` |
| награда | `0x300000 + slot + r` | `0000000000301540` |
| картинка главы | `0x400000 + ci*0x1000 + i` | `0000000000401002` |
| quest_link | `0x500000 + ci*0x1000 + l` | `0000000000502001` |

До 255 глав, до 255 квестов в главе, до 255 картинок на главу. ID задач,
наград, картинок и ссылок в данных писать **не нужно** — генератор проставляет
их сам и проверяет уникальность.

---

## Раскладки и секции

| layout | Как расставляет |
|---|---|
| `blocks` | глава делится на секции (`SEC(...)`); внутри секции — `flow` по её зависимостям, а сами секции укладываются полками по `cols` штук в ряд. Каждая секция получает **подложку** (`panel_soft.png`, красится цветом секции) и **пластинку-заголовок** (`plate.png` + `text_on_image`) — текст рисуется шрифтом игры и переводится |
| `flow` | слоистое дерево по графу зависимостей: слой узла = 1 + максимум слоёв родителей; внутри слоя узлы сортируются медианой позиций соседей (8 проходов вверх-вниз), поэтому линии почти не пересекаются |
| `line`, `zigzag`, `grid`, `ring`, `spiral`, `tree` | геометрические: порядок квестов в списке = порядок на экране |

Координаты руками задавать не нужно; если очень хочется, поля `x`/`y` квеста
перекрывают раскладку. Генератор дополнительно проверяет, что два квеста одной
главы не оказались в одной точке (иначе иконки наложатся).

### Зависимости (`deps`)

```python
deps=[3]                    # квест №3 этой же главы (нумерация с 1)
deps=["diamonds"]           # квест с key="diamonds" в этой главе
deps=["nether:stronghold"]  # квест из другой главы
# нет deps                  # наследует предыдущего квеста главы (цепочка)
```

Связи между главами работают как обычные ID: FTB Quests не требует, чтобы
зависимости жили в одной главе. `dependency_requirement="one_completed"` +
несколько `deps` дают узел «выбери один путь».

### Картинки главы (`images`)

Рисуются **под** квестами (слой BACKGROUND), порядок между собой — поле
`order` (у подложек -200, у заголовков -40, у ореолов -50, баннер -100).
Позиция задаётся одним из способов:

```python
{"at": "wither", "dy": 1.6, ...}          # относительно квеста (+dx/dy)
{"at": "levels", "align_y": "top", ...}   # x квеста, y = верх главы - offset
{"fit": "quests", "margin": 6.0, ...}     # под всё дерево квестов главы
{"x": 4.0, "y": -6.0, ...}                # абсолютные координаты
```

`image` — строка-иконка FTB Library: `kubejs:textures/gui/<имя>.png`,
`item:minecraft:diamond`, `color:#RRGGBB`, несколько иконок через `" + "`.
Поле `color` (int RGB) и `alpha` красят текстуру, поэтому все оформительские
текстуры рисуются белыми (`scripts/gen_textures.py`).

`click_quest` делает картинку кликабельной: в NBT попадёт
`click_action: "open_quest:<ID>"`, и клик по порталу откроет квест нужной
главы. `dependency` (в данных — `dep`) прячет картинку до завершения квеста.

### Ссылки (`links`)

`{"quest": "overworld:portalow"}` рисует в главе иконку квеста из ДРУГОЙ
главы (тот же прогресс, тот же квест) — «откуда мы пришли». Позиция по
умолчанию: слева от первого столбца, на уровне квестов-наследников.

---

## Как добавить квест

Правится только `scripts/quests/chapters/<глава>.py`:

```python
Q("firstenchant", ("First Enchantment", "Первые чары"),
  section="arcane",                      # секция главы (layout="blocks")
  icon="minecraft:enchanted_book",       # иконка квеста
  desc=[("Third slot, three levels of luck.",
         "Третья строка, три уровня и надежда на удачу.")],
  tasks=[adv("minecraft:story/enchant_item"),
         stat("minecraft:enchant_item", 3),
         item("minecraft:lapis_lazuli", 32)],
  rewards=[lvl(5), give("minecraft:bookshelf", 4)],
  deps=["etable"],                       # без deps — цепочка от предыдущего
  ),
```

Helpers в `qdsl.py` (`item`, `kill`, `stat`, `adv`, `biome`, `struct`, `dim`,
`xp`, `loc`, `obs`, `check` для задач; `give`, `lvl`, `xpr`, `say`, `toast`
для наград) — это только сокращения для словарей: генератор по-прежнему
проверяет каждое поле по схеме и отвергнет неизвестное явной ошибкой.

Затем:

```bash
python scripts/gen_quests.py
python scripts/check_quests.py --registry
git add -A && git commit -m "feat(quests): новая веха в главе Чары" && git push
```

Игроки получат квест при следующем запуске игры — переустанавливать пак
не нужно.

### Тексты

Каждая строка — либо просто `"текст"` (пойдёт в обе локали), либо пара
`("english", "русский")`. Пара предпочтительнее: `en_us` — fallback-локаль
FTB Quests, она отправляется игроку всегда, поэтому без неё заголовки
пропадут у всех, кто не на русской локали.

### Доступные типы

**Задачи:** `item` (`item`, `count`), `checkmark`, `kill` (`entity`, `value`),
`dimension`, `xp` (`value`, `points`), `stat` (`stat`, `value`), `location`
(`dimension`, `position`, `size`), `advancement` (`advancement`, `criterion`),
`observation` (`to_observe`, `observation_type`, `timer`), `biome`, `structure`.

**Награды:** `item` (`item`, `count`), `xp_levels`, `xp`, `command` (`command`,
`permission_level`, `silent`, `feedback_message`), `toast` (`description`).

Не используются и почему: задачи `fluid`/`energy` (нужны моды с жидкостями и
энергией), `gamestage` (нужен Game Stages), `custom` (без обработчика задачу
нельзя завершить — интеграции KubeJS↔FTB Quests в KubeJS-core нет); награды
`loot`/`random`/`choice`/`all_table` (нужны таблицы наград), `currency`,
`advancement`, `gamestage`.

Хотите добавить тип или поле — сначала посмотрите `writeData`/`readData`
соответствующего класса в репозитории FTB и допишите поле в схему
`gen_quests.py`. Непроверенное поле генератор отклонит явной ошибкой, а не
молча испортит квест.

---

## Что проверяет `check_quests.py`

Запускается без Minecraft и без Java:

1. **синтаксис SNBT** — каждый файл парсится обратно настоящим парсером
   (рекурсивный спуск);
2. **ID** — 16 символов uppercase hex, уникальны во всём файле квестов
   (включая задачи, награды, картинки и ссылки), не 0 и не 1;
3. **`filename`** в главе совпадает с именем файла (иначе поедут переводы);
4. **`x`/`y`** — double, **`order_index`** — int, **`version`** — int и равен 13;
5. **`count`** — long у задач, int у наград;
6. **типы** задач и наград существуют, обязательные поля на месте;
7. **`dependencies`**, `dependency` картинок и `linked_quest` ссылок — список
   строк, каждая указывает на существующий **квест**, не на себя;
8. **lang** — ключ вида `<тип>.<ID>.<поле>`, тип совпадает с реальным типом
   объекта (`image` тоже поддерживается), `quest_desc`/`chapter_subtitle` —
   списки, у каждой главы и квеста есть `title` в `en_us`;
9. **картинки глав** — типы полей по `ChapterImage.java`, `click_action` из
   enum, `text_h_align`/`text_v_align` из enum, у `text_on_image` есть `id`,
   а текстура `kubejs:textures/...` **существует на диске**;
10. **KubeJS** — каждый `kubejs:*` предмет из квестов зарегистрирован в
    `startup_scripts` и имеет рецепт в `server_scripts`;
11. **`--registry`** — все `minecraft:*` существуют в 1.21.1, а ID модов
    (`galosphere:*`, …) — в секции `mods.<неймспейс>` того же реестра
    (`mc_registry_1.21.1.json`, собирается из jar-ов модов, CI сверяет
    оффлайн; `kubejs:*` проверяется пунктом 10).

Код возврата nonzero при любой ошибке — можно вешать в CI, что и сделано.
