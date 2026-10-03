# quests/ — квестовая линейка FTB Quests

Квесты пишутся **на Python**, а не руками в SNBT. `questline.py` — это данные,
`scripts/gen_quests.py` генерирует из них файлы в `config/ftbquests/quests/`.

```bash
python scripts/gen_quests.py            # перегенерировать
python scripts/gen_quests.py --check    # только проверить, ничего не писать
python scripts/check_quests.py --registry   # валидация готовых файлов
```

CI делает и то и другое: валится, если закоммиченные `.snbt` не совпадают
с `questline.py`, и если валидатор нашёл ошибку.

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
| `ItemTask.count` написан как int, а не long | задача может не определиться |
| `ItemReward.count` написан как long | то же, но в другую сторону |
| Поле `levels` вместо `xp_levels` | награда выдаст 0 уровней |

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
| `quest/Quest.java` → `writeData` | `x`/`y`/`size` — **double**; `dependencies` — список строк |
| `quest/task/ItemTask.java` | `item` (compound), `count` — **long**, пишется только если > 1 |
| `quest/reward/ItemReward.java` | `item`, `count` — **int** (не long!), `random_bonus` — int |
| `quest/reward/XPLevelsReward.java` | поле называется **`xp_levels`**, а не `levels` |
| `quest/task/TaskTypes.java` | `item`, `checkmark`, `xp`, `dimension`, `kill`, `stat`, `location`, `advancement`, `observation`, `biome`, `structure`, `gamestage`, `fluid`, `custom` |
| `quest/reward/RewardTypes.java` | `item`, `xp`, `xp_levels`, `command`, `toast`, `loot`, `random`, `choice`, `advancement`, `currency`, `gamestage`, `custom`, `all_table` |
| `quest/task/TaskType.java` → `getTypeForNBT` | для неймспейса `ftbquests` пишется только path, т.е. `type: "item"`, а не `"ftbquests:item"` |
| `quest/translation/TranslationManager.java` → `makeKey` | ключ = `<objectType>.<ID>.<поле>` |
| `quest/translation/TranslationKey.java` | `title` (строка), `quest_subtitle` (строка), `quest_desc` (**список**), `chapter_subtitle` (**список**) |
| `quest/QuestObjectType.java` | `chapter`, `quest`, `task`, `reward`, `reward_table`, `chapter_group`, `quest_link`, `image` |
| `TranslationManager.DEFAULT_FALLBACK_LOCALE` | `en_us` — грузится и отправляется игроку всегда |

**Важное следствие:** начиная с этой версии FTB Quests заголовки и описания
**не хранятся** в файлах глав. Они живут в `config/ftbquests/quests/lang/<локаль>.snbt`
и привязаны к ID через ключ `<тип>.<ID>.<поле>`. Поэтому правка `title:` прямо
в `chapters/*.snbt` не даст ничего — её затрёт, а текст не появится.

---

## Структура результата

```
config/ftbquests/quests/
├── data.snbt                 version: 13, default_quest_shape
├── chapter_groups.snbt       chapter_groups: [ ]   (пусто = группа по умолчанию)
├── chapters/
│   ├── beginning.snbt        Начало            6 квестов
│   ├── food_and_farm.snbt    Еда и ферма       4 квеста
│   ├── exploration.snbt      Исследование      6 квестов
│   └── kubejs_custom.snbt    Кастомный контент 3 квеста (предметы KubeJS)
└── lang/
    ├── en_us.snbt            fallback-локаль, грузится всегда
    └── ru_ru.snbt            подхватится, если в клиенте выбран русский
```

Ключи сортируются при записи — FTB Quests делает то же самое
(`SNBT.setShouldSortKeysOnWrite(true)`), поэтому правки квестов в игре
не создают лишний diff.

---

## Схема ID

Младший байт ID квеста **должен быть нулевым** — туда генератор пишет индекс
задачи или награды. Отсюда ограничение: максимум 15 задач и 15 наград на квест.

| Объект | Шаблон | Пример |
|---|---|---|
| глава | `0xC00n` | `000000000000C001` |
| квест | `0x1cq0` — глава `c`, квест `q` | `0x1110` → `0000000000001110` |
| задача | `0x2cqt` — автоматически | `0x2110`, `0x2111` |
| награда | `0x3cqr` — автоматически | `0x3110`, `0x3111` |

ID задач и наград в `questline.py` писать **не нужно** — генератор проставляет
их сам и проверяет уникальность.

---

## Как добавить квест

Правится только `quests/questline.py`:

```python
{
    "id": 0x1170, "x": 4.5, "y": 0.0, "deps": [0x1160],
    "title": ("Enchanting", "Зачарование"),
    "desc": [
        ("Build an enchanting table and get your first enchantment.",
         "Построй стол зачаровывания и получи первые чары."),
    ],
    "tasks": [
        {"type": "item", "item": "minecraft:enchanting_table", "count": 1},
        {"type": "item", "item": "minecraft:lapis_lazuli", "count": 32},
    ],
    "rewards": [
        {"type": "xp_levels", "xp_levels": 10},
        {"type": "item", "item": "minecraft:bookshelf", "count": 15},
    ],
},
```

Затем:

```bash
python scripts/gen_quests.py
python scripts/check_quests.py --registry
git add -A && git commit -m "feat(quests): глава Зачарование" && git push
```

Игроки получат квест при следующем запуске игры — перезапускать пак не нужно.

### Тексты

Каждая строка — либо просто `"текст"` (пойдёт в обе локали), либо пара
`("english", "русский")`. Пара предпочтительнее: `en_us` — fallback-локаль
FTB Quests, она отправляется игроку всегда, поэтому без неё заголовки
пропадут у всех, кто не на русской локали.

### Доступные типы

**Задачи:** `item` (`item`, `count`), `checkmark`, `kill` (`entity`, `value`),
`dimension` (`dimension`), `xp` (`value`, `points`).

**Награды:** `item` (`item`, `count`), `xp_levels` (`xp_levels`), `xp` (`xp`),
`command` (`command`), `toast` (`description`).

В схеме `gen_quests.py` намеренно только те типы и поля, которые проверены по
исходникам. Хотите добавить `stat`, `biome`, `structure`, `observation`,
`loot`, `reward_table` — сначала посмотрите `writeData`/`readData`
соответствующего класса в репозитории FTB и допишите поле в схему.
Генератор отклонит непроверенное поле явной ошибкой, а не молча испортит квест.

---

## Что проверяет `check_quests.py`

Запускается без Minecraft и без Java:

1. **синтаксис SNBT** — каждый файл парсится обратно настоящим парсером
   (рекурсивный спуск, поддержан 15 позитивными и 6 негативными тестами);
2. **ID** — 16 символов uppercase hex, уникальны, не 0 и не 1;
3. **`filename`** в главе совпадает с именем файла (иначе поедут переводы);
4. **`x`/`y`** — double, **`order_index`** — int, **`version`** — int и равен 13;
5. **`count`** — long у задач, int у наград;
6. **типы** задач и наград существуют, обязательные поля на месте;
7. **`dependencies`** — список строк, каждая указывает на существующий **квест**
   (не на задачу и не на награду), не на себя;
8. **lang** — ключ вида `<тип>.<ID>.<поле>`, тип совпадает с реальным типом
   объекта, `quest_desc`/`chapter_subtitle` — списки, у каждой главы и квеста
   есть `title` в `en_us`;
9. **KubeJS** — каждый `kubejs:*` предмет из квестов зарегистрирован в
   `startup_scripts` и имеет рецепт в `server_scripts`;
10. **`--registry`** — все `minecraft:*` существуют в 1.21.1 (реестр берётся
    из `minecraft-assets`, кэшируется в `.cache/`).

Код возврата nonzero при любой ошибке — можно вешать в CI, что и сделано.
