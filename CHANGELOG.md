# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
версионирование — [SemVer](https://semver.org/lang/ru/).

Версия пака задаётся в `pack.toml` (`version = "…"`) и соответствует git-тегам `v*`.

## [Unreleased] — 1.3.2

### Fixed
- **Устаревшие файлы больше не выживают при обновлении у игроков.** Отчёт
  `crash-2026-10-04_10.28.53-client.txt`: в профиле AstralRinth (theseus)
  по-прежнему грузился `certain_questing_additions` — мод, исключённый из
  пака в v1.3.1, — и клиент крашился тем же `MixinApplyError` при открытии
  книги квестов. Причина: лаунчеры Theseus-семейства (AstralRinth, Modrinth
  App) при импорте/обновлении `.mrpack` только добавляют и заменяют файлы,
  но никогда ничего не удаляют. Так же выживали и главы старой 13-главной
  книги квестов в `config/ftbquests/quests/chapters/`.

### Added
- **Modpack Manager 3.1: «Починить всё» теперь делает ЧИСТУЮ ПЕРЕУСТАНОВКУ.**
  Каталог `mods/`, `config/`, `defaultconfigs/`, `kubejs/`, `resourcepacks/`,
  `shaderpacks/` целиком уезжают в `.modpack-backup/clean-<дата-время>/`,
  затем весь пак скачивается с сервера заново — устаревшие моды и главы
  исчезают гарантированно. Личное не трогается: `saves/`, `local/` (прогресс
  квестов), `journeymap/`, `options.txt`, `logs/`, `crash-reports/`,
  `packsync/`, `packwiz.json`; файлы с `preserve = true` возвращаются из
  бэкапа. Если очистка не удалась (игра запущена и держит jar-ы), починка
  прерывается ДО скачивания. Прежний инкрементальный режим сохранён в меню
  как «Быстрая починка».
- **Вкладка «Лишние»: рекурсивный скан поддеревьев, полностью подконтрольных
  паку** (`config/ftbquests`, `kubejs/startup_scripts`,
  `kubejs/server_scripts`, `kubejs/assets`, `defaultconfigs`) — старые главы
  квестов и удалённые скрипты видны сразу, без чистой переустановки. Корень
  `config/` вглубь не сканируется намеренно: иначе рантайм-конфиги модов
  (sodium, jade, fml.toml…) засыпали бы список сотнями ложных строк.
- `app/test_packlib.py` — headless-тесты ядра на локальном фейковом
  pack-сервере (устаревший мод и старая глава → «ЛИШНИЙ»; `clean_reinstall`
  → бэкап + свежая закачка + сохранность `saves/`, `local/`, `journeymap/`,
  `options.txt`, `packsync/`; восстановление `preserve`-файла). Подключены
  в CI (`pages.yml`, `release.yml`) перед сборкой `.exe`; в воркфлоу включён
  UTF-8-режим Python (`PYTHONUTF8=1`) — Windows-раннеры по умолчанию
  печатают в cp1252 и падают на кириллице с `UnicodeEncodeError`.

### Changed
- `docs/TROUBLESHOOTING.md`: раздел про краш CQA дополнен сценарием «пак
  обновлён, а мод всё равно на месте» — с объяснением про Theseus и лечением
  чистой переустановкой.

## [1.3.1] — 2026-10-04

Реворк квестовой книги по отзыву «выглядит скучно и пусто»: вместо тринадцати
небольших глав — три большие, по одной на измерение, с секциями-витринами.

### Changed
- **Линейка пересобрана: 3 главы / 141 квест / 321 задача / 215 наград.**
  «Земли Рассвета» (Верхний мир, 8 секций, 84 квеста), «Багровое Пекло»
  (Нижний мир, 6 секций, 35 квестов), «Грань Пустоты» (Край, 4 секции,
  22 квеста). У каждого квеста иконка предмета, у большинства — подсказка
  в 1–4 строки (RU + EN).
- **Новая раскладка `blocks`**: глава делится на секции (`SEC`), каждая
  рисуется своим цветным блоком с подложкой и пластинкой-заголовком; внутри
  секции — дерево `flow` по графу зависимостей (слой = 1 + максимум слоёв
  родителей, порядок внутри слоя по медиане позиций соседей). Секции
  укладываются полками, координаты по-прежнему считает генератор.
- **Новая схема ID**: квест `0x100000 + ci*0x1000 + qi*0x10`, картинки
  `0x400000 + …`, ссылки `0x500000 + …` — до 255 квестов на главу вместо 15.
- **Оформление глав**: подложки секций и заголовки рисуются шрифтом игры из
  lang-таблицы (`text_on_image` + ключ `image.<ID>.title`), ореолы позади вех,
  кликабельные порталы между главами (`click_action: "open_quest:<ID>"`),
  ссылки `quest_links` на квесты соседних глав, плашки-предупреждения
  («Босс. Сначала подготовься», «Крадись. Не беги»).
- **Данные глав разложены по файлам**: `scripts/quests/chapters/{overworld,
  nether,end}.py` + мини-DSL `scripts/quests/qdsl.py` (`Q`, `SEC`, `item/kill/
  stat/adv/biome/struct/dim/xp/loc/obs/check`, `give/lvl/xpr/say/toast`,
  `halo/portal/backdrop`). `questline.py` остался точкой входа: порядок глав
  и `FILE_SETTINGS`.
- `scripts/gen_textures.py`: вместо 13 баннеров — 3 сюжетных баннера 256x64
  (рассвет над холмами, крепость над лавой, острова Края) плюс оформительские
  текстуры, которые FTB красит полем `color`: `plate`, `panel_soft`, `halo`,
  `portal`, `portal_end`.

### Fixed
- **Краш клиента при открытии книги квестов** (`Rendering screen` →
  `MixinApplyError: @Shadow field val$name was not located in …
  ChapterImageButton$3`, отчёт `crash-2026-10-04_09.33.55-client.txt`).
  Виновник — **Certain Questing Additions 1.2.0.4**: сборка сделана под
  FTB Quests 2101.1.15…20, где `ChapterImageButton$3` был анонимным классом с
  синтетическим полем `val$name`; в FTB Quests 2101.1.21+ на его месте
  `$SwitchMap…ChapterImage$TextAlign`, и миксин `ChapterImageConfigGroupMixin`
  не применяется. Мод **удалён из пака** (12 модов вместо 13): новой сборки
  под 2101.1.21+ у автора нет (последняя — 2026-08-06), а понижать FTB Quests
  нельзя — `text_on_image`/`click_action` у картинок глав появились только в
  2101.1.28, и FTB Quests Entity Visualization требует `>= 2101.1.29`.
  На книгу квестов удаление не влияет: баннеры, подложки секций, ореолы и
  порталы рисует сам FTB Quests, а `text_on_image` — встроенная возможность
  2101.1.28+, а не функция аддона.
- **KubeJS**: обработчик `StartupEvents.init` убран из
  `server_scripts/diagnostics.js` в новый `startup_scripts/diagnostics.js`.
  Ушла ошибка «Tried to register event handler 'StartupEvents.init' for
  invalid script type SERVER!» и сообщение «KubeJS errors found [1]!» в чате.
- Баннер главы центрируется над деревом квестов: у `ChapterImage` координаты —
  центр картинки, а не угол, из-за чего старый баннер уезжал влево.

### Added
- `scripts/check_mods.py` — оффлайн-проверка состава модов: восстанавливает
  modid и версию по имени jar, сверяет со списком заведомо несовместимых пар
  (`BLOCKED`, первым пунктом туда занесён CQA) и обязательных модов
  (`REQUIRED`), ищет дубли jar-ов. Подключён в CI (`validate.yml`, `pages.yml`),
  так что вернуть сломанный аддон в пак случайно больше не получится.
- `docs/TROUBLESHOOTING.md`: раздел про краш `MixinApplyError` при открытии
  книги квестов — как выглядит, почему возникает и что делать.
- `check_quests.py`: полная проверка картинок глав по `ChapterImage.java`
  (типы полей, `click_action`, `text_h_align`/`text_v_align`, наличие `id`
  у `text_on_image`), существование текстуры `kubejs:textures/…` на диске,
  проверка `quest_links` (`linked_quest` → существующий квест), ID и
  lang-ключи картинок и ссылок.
- Генератор ругается, если два квеста главы попали в одну точку, если у
  картинки `text_on_image` без `title`, если секция не объявлена, если в
  зависимостях цикл или ссылка сама на себя.

### Removed
- Десять неиспользуемых баннеров глав из `kubejs/assets/kubejs/textures/gui/`.

## [1.2.0] — 2026-10-04

Большое расширение квестовой линейки и оформления.

### Added
- **Квестовая линейка выросла с 4 глав / 19 квестов до 13 глав / 117 квестов
  / 196 задач / 141 награды.** Ванильные главы полностью переработаны
  (Основы, Пещеры и руда, Бой и мобы, Еда и ферма, Чары и зелья, Редстоун,
  Нижний мир, Край, Исследование, Строительство, Ванильные достижения),
  плюс главы Кастомный контент и Мастерство.
- **Используются 11 из 14 типов задач FTB Quests**: `item`, `checkmark`,
  `kill`, `dimension`, `xp`, `stat`, `location`, `advancement`, `observation`,
  `biome`, `structure`. Схемы всех полей выверены по исходникам
  (включая `IntArray`-поля `position`/`size` у `location` и пару
  `observation_type` + `observe_type` у `observation`).
  Не используются `fluid`/`energy` (нужны моды с жидкостями/энергией),
  `gamestage` (нужен Game Stages) и `custom` (без обработчика квест
  невыполним — KubeJS-core не содержит интеграции с FTB Quests).
- **Собственные текстуры** (скрипт `scripts/gen_textures.py`, Pillow):
  3 предмета 16x16 (`kubejs/assets/kubejs/textures/item/*.png`) и 13 баннеров
  глав 256x64 (`.../textures/gui/*.png`). Баннеры подключаются как
  `ChapterImage` через `image: "kubejs:textures/gui/<имя>.png"` — формат
  строки иконки (`*.png` → `ImageIcon`) подтверждён по `Icon.getIcon0`.
- **Оформление каждой главы своё**: форма квестов (`default_quest_shape` —
  9 разных), иконка главы и квестов (`icon`, ItemStack), баннер-картинка и
  раскладка (`line / zigzag / grid / ring / spiral / tree`, считается
  генератором — координаты руками не проставляются).
- **Три аддона FTB Quests** с Modrinth: FTB Quests Optimizer 3.2.0-1.21.1,
  FTB Quests Entity Visualization 1.11.0, Certain Questing Additions 1.2.0.4.
  Всего модов: 13.
- `scripts/quests/mc_registry_1.21.1.json` — реестр для валидации, собранный
  из клиентского jar 1.21.1: 2385 предметов/блоков, 181 моб, 78 custom-статов,
  64 биома, 34 структуры, 1399 достижений, 3 измерения. Лежит в репозитории —
  CI сверяет ID без интернета.

### Changed
- `check_quests.py`: сверка с реестром включена по умолчанию и расширена на
  биомы/структуры/достижения/статы/измерения; добавлена проверка типов
  числовых полей задач и наград и полей `ChapterImage`.
- `gen_quests.py`: зависимости можно не проставлять — по умолчанию квест
  зависит от предыдущего в главе, а глава с `gate: true` начинается с
  последнего квеста предыдущей главы.
- CI (`validate.yml`): шаг «Textures must be up to date» (`gen_textures.py
  --check`, требует Pillow).

### Fixed
- Валидатор ловил две реальные ошибки данных: у `XPTask` поле называется
  `value` (long), а не `xp` (int — это поле `XPReward`); и ID достижения
  «Следуй за очами» — `minecraft:story/follow_ender_eye`, а не
  `follow_eyes`/`follow_the_eye`. Обе найдены сверкой с реестром.

## [1.1.0] — 2026-10-04

### Added
- **FTB Quests 2101.1.36** + зависимости (FTB Library 2101.1.36, FTB Teams
  2101.1.9) с `maven.ftb.dev`, **Architectury API 13.0.11**, **KubeJS
  2101.7.2-build.377** + Rhino 2101.2.7 и Better Advanced Tooltips 2101.1.0.
  Всего модов в паке: 10.
- `pw.py add-maven` — установка модов с Maven с разрешением транзитивных
  зависимостей из POM, выбором максимальной версии при конфликте и чтением
  готового sha1 из соседнего `.sha1`-файла (без скачивания jar). Нужно потому,
  что FTB-модов нет на Modrinth, а CurseForge API требует ключ.
- `scripts/quests/questline.py` — квестовая линейка как данные: 4 главы, 19 квестов,
  32 задачи, 33 награды. Тексты парами (en, ru).
- `scripts/gen_quests.py` — генератор SNBT с типизированной схемой полей,
  выверенной по исходникам FTB Quests (ветка 1.21.1/main). Непроверенное поле
  или тип — ошибка генерации, а не молча битый квест.
- `scripts/check_quests.py` — валидация без Minecraft: собственный SNBT-парсер
  (рекурсивный спуск, 15 позитивных + 6 негативных тестов), проверка ID
  (16-hex, уникальность, не 0/1), зависимостей, типов числовых полей,
  lang-ключей, соответствия `kubejs:*` скриптам, и `--registry` для сверки
  всех `minecraft:*` с реальным реестром 1.21.1.
- `kubejs/` — 3 кастомных предмета (`quest_token`, `quest_token_premium`,
  `quest_medal`), рецепты к ним и диагностика загрузки в лог.
- CI: шаги «Quest files must be up to date» (diff сгенерированного против
  закоммиченного) и «Validate quests» в validate.yml; `check_quests.py
  --registry` и `gen_quests.py --check` в pages.yml.

### Fixed
- **go-gitignore (которую использует packwiz) трактует паттерн со слэшем в
  середине как НЕпривязанный к корню** — вопреки спецификации gitignore.
  Из-за этого `quests/**` в `.packwizignore` матчил `config/ftbquests/quests/**`,
  и все 8 файлов квестов молча выпадали из пака: `packwiz refresh` собирал
  индекс без них. Поймал только CI, где `packwiz refresh` и `pw.py check`
  дали разный состав пака.
  Исправлено в две стороны: все паттерны в `.packwizignore` теперь начинаются
  с `/` (единственная однозначная привязка к корню), а матчер в `pw.py`
  намеренно повторяет поведение go-gitignore вместо спецификации git — иначе
  локальная проверка и packwiz расходятся. Исходная папка `quests/` переехала
  в `scripts/quests/`, чтобы не иметь одноимённого компонента пути.
  Регресс-тест: 44 кейса, расхождений 0.
- **Матчер `_match` в `pw.py` стал строже, чем нужно**: предыдущая правка
  привела его к спецификации gitignore, а надо было к поведению packwiz.
- **`write_mod()` писал дубль секции `[update]` для модов без апдейтера**
  (maven / прямая ссылка). packwiz на этом падал:
  `toml: line 11: Key 'update' has already been defined`, из-за чего
  `packwiz modrinth export` в релизе v1.1.0 завершился ошибкой.
  Локально не ловилось, потому что мини-парсер в `pw.py` молча перезаписывал
  дубликаты, а packwiz использует строгий BurntSushi TOML.
- **`read_toml` теперь строгий**: дубликат ключа, дубликат секции и секция,
  конфликтующая со скаляром, — это `TomlError`. Добавлено 6 регресс-тестов.
  Смысл ровно в том, чтобы падать там же, где падает packwiz, а не позже в CI.
- **`.packwizignore`-матчер в `pw.py` нарушал gitignore-семантику**, из-за чего
  паттерн `quests/**` (исключающий `quests/questline.py`) заодно вырезал
  `config/ftbquests/quests/**` — квесты не попадали в пак. Паттерн со слэшем
  в начале или середине теперь привязан к корню.
- **`_match` использовал `fnmatch`, где `*` -> `.*` и пересекает `/`**, поэтому
  дефолтное правило `/*.zip` (только корень) ловило `resourcepacks/*.zip` и
  `shaderpacks/*.zip` — ресурспаки и шейдеры перестали бы синхронизироваться.
  Переписано на regex с `*` = `[^/]*`. Добавлено 36 тест-кейсов, расхождений 0.
- `pw.py check`: пустой `[update]` у maven-модов больше не ошибка, а
  предупреждение (кастомный `[update.maven]` уронил бы packwiz с
  «Update plugin maven not found!»).
- `pw.py add-maven`: конфликт версий (FTB Library 2101.1.36 от quests против
  2101.1.25 от teams) разрешается в пользу максимальной — раньше вторая запись
  молча перезаписывала первую, оставляя устаревшую версию.


_(пусто)_

## [1.0.3] — 2026-10-04

### Added
- `app/` — **Modpack Manager на Python + Tkinter** вместо PowerShell-версии.
  `packlib.py` (ядро без GUI, тестируется headless) + `modpack_app.py`
  (интерфейс). Сторонних зависимостей нет, поэтому PyInstaller собирает
  один `ModpackManager.exe`.
- Job `build-app` (windows-latest) в `pages.yml` и `release.yml`: smoke-test
  ядра, `py_compile`, сборка `--onefile --windowed`, публикация по стабильному
  адресу `latest/ModpackManager.exe` и вложение в релиз.
- **«Установить пак с нуля»** — создание инстанса Prism/Freesm прямо на диске
  (`instance.cfg` + `mmc-pack.json` + `.minecraft/packsync/`). Zip-файл и
  диалог импорта больше не нужны: Prism сканирует `instances/` сам.
- Публикация `packsync/` на GitHub Pages — приложение берёт jar-ы оттуда.
- Включение/отключение модов через `.disabled` прямо из меню, мультивыделение
  в таблицах, отчёт в txt/csv, запоминание недавних папок.

### Changed
- Синхронизация в приложении — собственная, на `urllib`. PowerShell-версия
  дёргала `sync.cmd`, то есть требовала установленную Java.
- Скачивание идёт в `<файл>.download`, хэш проверяется ДО `os.replace`,
  заменяемый файл копируется в `.modpack-backup`.

### Removed
- `checker/` (`CheckMods.ps1`, `ModpackManager.ps1`, `ModpackManager.bat`) —
  PowerShell-версия полностью заменена приложением на Python.


### Added
- `checker/ModpackManager.ps1` + `ModpackManager.bat` — оконное приложение
  для проверки и починки сборки (PowerShell 5.1 + WinForms, ноль зависимостей).
  Меню Файл/Проверка/Синхронизация/Инструменты/Справка, вкладки
  «Моды» / «Конфиги и файлы» / «Лишние» / «Журнал», автопоиск папки сборки
  у шести лаунчеров, запоминание последней папки и адреса в
  `%LOCALAPPDATA%\ModpackManager\settings.json`, экспорт отчёта в txt/csv.
- **Собственный загрузчик без Java**: `Invoke-Sync` качает через
  `Invoke-WebRequest` во временный файл, сверяет хэш и только затем подменяет;
  заменяемое копируется в `.modpack-backup`. Предыдущий вариант дёргал
  `sync.cmd`, то есть требовал установленную Java.
- Проверка не только `mods/`, но и `config/`, `defaultconfigs/`, `kubejs/`,
  `resourcepacks/`, `shaderpacks/` и прочих файлов пака, с группировкой по
  вкладкам и статусом `НЕТ (preserve)` для файлов с `preserve = true`.
- Фильтр по стороне (`client` / `server` / `both`) и статус `ДРУГАЯ СТОРОНА`.
- `config/modpack-info.txt` — первый реально синхронизируемый файл пака,
  заодно пример того, как в пак попадают конфиги.

### Removed
- `checker/CheckMods.ps1` / `CheckMods.bat` — заменены на ModpackManager.


### Added
- `checker/CheckMods.ps1` + `CheckMods.bat` — диагностическое окно на чистом
  PowerShell + WinForms (ноль зависимостей). Автопоиск папок игры AstralRinth,
  Modrinth App, Freesm, Prism, MultiMC и `.minecraft`; сверка каждого ожидаемого
  файла с диском по sha1/sha256; статусы НА МЕСТЕ / ОТСУТСТВУЕТ / ПОВРЕЖДЁН /
  ОТКЛЮЧЁН / ЛИШНИЙ / СИНК НЕ ШЁЛ; кнопки «Синхронизировать», «Открыть mods/»,
  «Открыть sync.log» и «Показывать прогресс».
- `packsync/SHOW_GUI` — файл-флаг: с ним `sync.cmd`/`sync.sh` запускают
  packwiz-installer БЕЗ `-g`, то есть с видимым окном прогресса.
- `packsync/sync.log` — обе обёртки теперь логируют найденную Java, адрес пака,
  папку игры, вывод установщика и код возврата. Раньше синхронизация была
  полностью немой, и «не работает» невозможно было диагностировать.
- `verify.py --game-dir <папка игры>` — та же проверка кроссплатформенно,
  с ненулевым кодом возврата при любом провале (пригодно для CI).
- `verify.py --force-download` — вместе с `--game-dir` дополнительно скачать
  jar-ы и сверить их с Modrinth.

### Changed
- `pw.py site` публикует на Pages не только `install.*`, но и `CheckMods.*`,
  так что игроки берут проверялку короткой ссылкой.


### Fixed
- `pw.py add`/`update` подбирали версию под **неверную версию Minecraft**:
  `acceptable-game-versions` шёл первым, и «точным совпадением» считалась `1.21`
  вместо `1.21.1`. Теперь `[versions].minecraft` всегда первый в списке.
- `primary_loader()` возвращал строку, а `pick_version()` делал из неё `list()`,
  из-за чего в Modrinth API уезжал фильтр `loaders=["n","e","o","f",...]`.
  Добавлен `_as_list()`.

### Changed
- Выбор версии мода теперь предпочитает `release` > `beta` > `alpha`.
  Если существует более свежая pre-release-сборка, `add` печатает явную подсказку
  с готовой командой `--pre-release` вместо молчаливого решения за автора.
- Стартовый набор модов: JEI 19.51.0.418 (release), Jade 15.10.6,
  JourneyMap 1.21.1-6.0.9 — все под NeoForge 1.21.1.

### Added
- `scripts/verify.py` — автономная проверка автосинхронизации: повторяет цепочку
  packwiz-installer (pack.toml -> sha256(index.toml) -> mods/*.pw.toml -> sha1 jar-ов),
  проверяет артефакты на Pages и содержимое `instance.cfg` / `modrinth.index.json`.
  Флаги `--fast`, `--dest`, `--side`, `--url`.
- `pw.py add/update --pre-release`.


### Added
- Каркас репозитория: `packwiz`-пак на NeoForge 21.1.252 / Minecraft 1.21.1.
- Пак намеренно **пустой** (`mods/` без модов) — чистый старт, наполняется
  командой `python scripts/pw.py add <slug>`.
- `scripts/setup-github.py` — публикация на GitHub одной командой: создание репо,
  включение Pages, правка `pack.toml`, push, тег, ожидание Actions и проверка
  доступности `pack.toml`. Токен передаётся гиту через `GIT_CONFIG_*` как
  HTTP-заголовок и не попадает ни в `.git/config`, ни на диск.
- `scripts/pw.py` — автономный инструмент ведения пака (Python 3.8+, без зависимостей):
  `add`, `add-url`, `remove`, `update`, `list`, `refresh`, `check`,
  `set-url`, `show-url`, `versions`, `site`, `mrpack`, `inject-packsync`,
  `instance`, `serve`.
- Автоподбор версии мода под основной загрузчик: сначала строго `neoforge`
  и точная версия MC, затем запасные варианты; при нескольких файлах в одной
  версии Modrinth выбирается файл под нужный загрузчик.
- Автоматическое подтягивание обязательных зависимостей с Modrinth.
- `packsync/` — механизм автосинхронизации: `packwiz-installer` v0.5.14
  и `packwiz-installer-bootstrap` v0.0.3 (оба MIT), обёртки `sync.cmd` / `sync.sh`
  с самостоятельным поиском Java и гарантированным кодом возврата 0.
- `installer/` — однокнопочная установка у игроков: `install.ps1` (Windows,
  PowerShell 5.1+), `install.bat` (двойной клик), `install.sh` (Linux/macOS).
  Скрипты ищут лаунчер четырьмя способами (PATH, типичные каталоги, реестр
  `Uninstall`, ярлыки меню Пуск + flatpak), для Prism-семейства вызывают
  `--import <url>` (полностью автоматически), для Theseus-семейства —
  автоимпорт `.mrpack` аргументом командной строки + строка hook'а в буфере
  обмена. Есть `-WithLauncher`: сам скачает и поставит Freesm Launcher.
- Публикация артефактов по стабильным адресам `latest/instance.zip` и
  `latest/pack.mrpack` на GitHub Pages — переустановка пака больше не нужна.
- GitHub Actions:
  - `validate.yml` — проверка на PR и push в побочные ветки, падает при устаревшем `index.toml`;
  - `pages.yml` — публикация пака на GitHub Pages на каждый push в `main`;
  - `release.yml` — сборка `.mrpack` и `…-instance.zip` по тегу `v*`.
- Шаблон инстанса Prism/MultiMC (`instance-template/`) с заранее прописанной
  Pre-Launch Command для полного авто-синка.
- Документация: `README.md`, `INSTALL.md` (для игроков), `docs/SETUP.md`,
  `docs/ARCHITECTURE.md`, `docs/SERVER.md`, `docs/TROUBLESHOOTING.md`,
  `packsync/README.md`.
- `.gitattributes` с форсированным `eol=lf` для текстовых файлов — без этого
  sha256-хэши в `index.toml` расходятся между Windows и CI, и packwiz-installer
  перекачивает файлы заново при каждом запуске.
- `.packwizignore`, исключающий из пака всю инфраструктуру репозитория.

[1.0.3]: https://github.com/yungspiderq/my-neoforge-pack/releases/tag/v1.0.3
