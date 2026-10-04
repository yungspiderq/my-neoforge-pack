# Модпак с автосинхронизацией через GitHub

Приватный модпак, который **сам обновляется у игроков**. Вы добавляете мод одной
командой, пушите в GitHub — и при следующем запуске игры лаунчер сам докачивает
изменения всем, кто установил пак.

**Стек:** `packwiz` (формат пака) + GitHub Pages (раздача) + `packwiz-installer`
(синхронизация на стороне игрока) + GitHub Actions (сборка).

**Лаунчеры:** Freesm Launcher (форк Prism), AstralRinth (форк Modrinth App),
а также Prism Launcher, MultiMC и обычный Modrinth App.

**Загрузчик по умолчанию:** NeoForge `21.1.252` / Minecraft `1.21.1`.

---

## Главная идея

В git-репозитории **нет ни одного `.jar` файла модов**. Хранятся только:

```
mods/jei.pw.toml          ← «ссылка» на мод: URL, sha1, id на Modrinth
index.toml                ← список всех файлов пака с sha256-хэшами
pack.toml                 ← имя пака, версия MC и загрузчика
config/, resourcepacks/, shaderpacks/   ← ваши общие файлы (эти уже реально хранятся)
```

Отсюда три приятных следствия:

1. **Легально.** Файлы модов не переиздаются — игрок качает их напрямую с
   `cdn.modrinth.com`, как и всегда. Лицензии модов не нарушаются.
2. **Лёгкий репозиторий.** ~5 МБ вместо гигабайтов.
3. **Дешёвое обновление.** При запуске сверяются sha256-хэши — докачивается
   только то, что реально изменилось.

---

## Установка у игроков — одной командой

Игроку не нужно ничего скачивать и настраивать. В PowerShell:

```powershell
irm https://<user>.github.io/<repo>/install.ps1 | iex
```

или двойной клик по `install.bat`, или на Linux/macOS:

```bash
curl -fsSL https://<user>.github.io/<repo>/install.sh | bash
```

Установщик сам найдёт лаунчер (Freesm, Prism, MultiMC, AstralRinth, Modrinth App),
а если его нет — предложит поставить Freesm (`-WithLauncher`). Для Freesm/Prism
установка полностью автоматическая: лаунчеру передаётся
`--import <url>/latest/instance.zip`, и он сам качает инстанс, Minecraft,
NeoForge, Java и моды. Для AstralRinth импорт тоже автоматический, а hook
вписывается за 4 клика (строка уже лежит в буфере обмена) — подробности и
обоснование в [`installer/README.md`](installer/README.md).

Артефакты публикуются по **стабильным адресам** `latest/instance.zip` и
`latest/pack.mrpack`, поэтому переустанавливать пак при добавлении модов не
нужно никогда — уже установленный инстанс обновляется сам.

---

## Как это выглядит в жизни

```
ВЫ                                     GITHUB                        ДРУЗЬЯ
──────────────────────────────────     ──────────────────────        ─────────────────
python scripts/pw.py add oculus
git add -A && git commit && git push ─► Actions: packwiz refresh
                                        → GitHub Pages опубликован
                                                                       запуск игры
                                                                       └─ pre-launch hook
                                                                          └─ packwiz-installer
                                                                             читает pack.toml
                                                                             сверяет хэши
                                                                             качает oculus.jar  ✔
```

Никаких «скинь новый архив в дискорд».

---

## Быстрый старт

### Вариант 1 — одной командой (рекомендуется)

`scripts/setup-github.py` делает **всё**: создаёт репозиторий, включает GitHub
Pages, проставляет имя пака, пушит, ставит тег, дожидается сборки и проверяет,
что `pack.toml` реально отдаётся.

```bash
# токен — только через переменную окружения, в файлы и в чат он не попадает
export GITHUB_TOKEN=github_pat_xxxxxxxxxxxx

python scripts/setup-github.py \
    --repo my-neoforge-pack --public \
    --pack-name "Наш Пак" \
    --mc 1.21.1 --neoforge 21.1.252

unset GITHUB_TOKEN          # и сразу отзываем токен на github.com/settings/tokens
```

Сначала можно посмотреть план, ничего не меняя:

```bash
GITHUB_OWNER=ваш-ник python scripts/setup-github.py --repo my-pack --dry-run
```

**Какой токен нужен:** fine-grained PAT, *только на этот репозиторий*,
`Contents: Read and write` + `Administration: Read and write` + `Metadata: Read-only`,
срок — 1 день. Подробности и ручные шаги — в [`docs/SETUP.md`](docs/SETUP.md).

### Вариант 2 — руками

```bash
# 1. Клонируйте/создайте репозиторий и перейдите в него
cd modpack

# 2. Впишите своё имя пака и ник в pack.toml (строки name / author)

# 3. Создайте пустой репозиторий на GitHub и подключите его
git init && git add -A && git commit -m "init modpack"
git branch -M main
git remote add origin https://github.com/<ваш-ник>/<имя-репо>.git

# 4. Задайте адрес пака (он же получится автоматически в CI)
python scripts/pw.py set-url https://<ваш-ник>.github.io/<имя-репо>/pack.toml

# 5. Запушьте
git push -u origin main
```

После первого пуша:

- **Settings → Pages → Build and deployment → Source = GitHub Actions**
  (workflow пытается включить это сам через `configure-pages`, но проверьте).
- Через 1–2 минуты пак будет доступен по адресу из `packsync/pack-url.txt`.
- Проверьте: откройте в браузере `<адрес>` — должен скачаться/показаться TOML.

Затем создайте первый релиз с установочными файлами:

```bash
# поднимите версию в pack.toml (version = "1.0.0") и:
git tag v1.0.0
git push origin v1.0.0
```

В **Releases** появятся два файла — их и раздаёте друзьям (см. [`INSTALL.md`](INSTALL.md)).

---

## Повседневная работа с паком

Все команды — из корня репозитория. Скрипт `scripts/pw.py` работает на Python 3.8+
без зависимостей; официальный `packwiz` (Go) при этом остаётся «истиной в последней
инстанции» — CI прогоняет его перед каждой публикацией.

### Добавить мод

```bash
python scripts/pw.py add jei jade oculus embeddium
```

Принимает slug или ID с Modrinth (`https://modrinth.com/mod/<slug>`). Скрипт сам:

- подбирает версию под ваш загрузчик и версию MC из `pack.toml`;
- **докачивает обязательные зависимости** (например, для JEI подтянет MezzConfig);
- определяет `side` (client / server / both);
- пишет `mods/<имя>.pw.toml` и пересобирает `index.toml`.

Полезные флаги:

| Флаг | Что делает |
|---|---|
| `--side client` | принудительно только клиент (например, шейдеры, миникарта) |
| `--optional` | мод станет «опциональным» — packwiz-installer спросит игрока |
| `--no-deps` | не тянуть зависимости |
| `--loader forge` / `--mc 1.21.4` | переопределить выбор версии |

### Обновить / удалить / посмотреть

```bash
python scripts/pw.py update --all      # обновить все моды до последних версий
python scripts/pw.py update jei        # только один
python scripts/pw.py remove journeymap
python scripts/pw.py list
python scripts/pw.py check             # целостность пака
python scripts/check_mods.py           # совместимость модов (оффлайн, см. ниже)
```

Чтобы зафиксировать мод на текущей версии и не обновлять его — добавьте в
`mods/<имя>.pw.toml` строку `pin = true`.

### Мод, которого нет на Modrinth

Положите `.jar` в **GitHub Releases** своего же репозитория и подключите ссылкой:

```bash
python scripts/pw.py add-url "Мой приватный мод" \
  https://github.com/<ник>/<репо>/releases/download/v1/my-mod-1.0.jar \
  --side both --hash
```

Или (если лицензия мода разрешает распространение) просто положите `.jar`
в папку `mods/` — packwiz отправит его игрокам как обычный файл.

### Общие конфиги, ресурспаки, шейдеры

Просто кидайте файлы в соответствующие папки — они уедут игрокам в `.minecraft/`:

| Папка в репозитории | Куда попадёт игроку |
|---|---|
| `config/…` | `.minecraft/config/…` |
| `resourcepacks/foo.zip` | `.minecraft/resourcepacks/foo.zip` |
| `shaderpacks/Complementary.zip` | `.minecraft/shaderpacks/Complementary.zip` |
| `kubejs/…`, `defaultconfigs/…` | аналогично, 1:1 |
| `options.txt` | `.minecraft/options.txt` |

После добавления файлов выполните `python scripts/pw.py refresh` (или просто
закоммитьте — CI сам сделает `packwiz refresh`).

> ⚠️ **Любой** файл в корне репозитория, не исключённый в `.packwizignore`,
> считается частью пака и скачается игрокам. Перед коммитом проверяйте
> `python scripts/pw.py check`.

Чтобы файл **не перезаписывал** личные настройки игрока, поставьте ему
`preserve = true` в `index.toml` (или `packwiz manual add options.txt --preserve`).

---

## Структура репозитория

```
.
├── pack.toml                     ← имя/версия пака, MC + NeoForge
├── index.toml                    ← генерируется: список файлов и sha256
├── .packwizignore                ← что НЕ входит в пак
├── mods/*.pw.toml                ← метаданные модов (ссылки, не jar-ы!)
├── config/                       ← общие конфиги (в т.ч. ftbquests/quests/*.snbt)
├── kubejs/                       ← кастомные предметы и рецепты
├── scripts/quests/questline.py   ← квесты НА PYTHON (генератор -> .snbt)
├── resourcepacks/ shaderpacks/   ← синхронизируемые файлы
├── packsync/                     ← механизм автосинхронизации (см. packsync/README.md)
│   ├── packwiz-installer.jar
│   ├── packwiz-installer-bootstrap.jar
│   ├── sync.cmd  sync.sh
│   └── pack-url.txt
├── installer/                    ← однокнопочная установка у игроков
│   ├── install.ps1  install.bat  install.sh
├── app/                          ← Modpack Manager (Python + Tkinter -> .exe)
│   ├── packlib.py                ← ядро: пак, сверка, синхронизация (без GUI)
│   └── modpack_app.py            ← интерфейс: меню, вкладки, прогресс
├── instance-template/            ← шаблон инстанса для Prism/Freesm
├── scripts/
│   ├── pw.py                     ← ведение пака (моды, индекс, артефакты)
│   ├── verify.py                 ← проверка, что автосинк реально работает
│   ├── check_mods.py             ← совместимость модов между собой (оффлайн)
│   ├── gen_quests.py check_quests.py gen_textures.py preview_book.py
│   └── setup-github.py           ← публикация на GitHub одной командой
├── docs/                         ← подробные инструкции
└── .github/workflows/
    ├── validate.yml              ← проверка на PR
    ├── pages.yml                 ← публикация на GitHub Pages (каждый push в main)
    └── release.yml               ← .mrpack + instance.zip (по тегу v*)
```

---

## Проверка, что автосинк действительно работает

`scripts/verify.py` прогоняет **ровно ту же цепочку**, что и `packwiz-installer`
при запуске игры, но без Minecraft и без лаунчера — за пару секунд:

```bash
python scripts/verify.py                    # полная проверка, реально качает jar-ы
python scripts/verify.py --fast             # только HTTP-заголовки, без закачки
python scripts/verify.py --dest /tmp/mc     # разложить скачанное как при установке
python scripts/verify.py --side server      # проверить серверную сторону
```

Что проверяется:

| # | Проверка |
|---|---|
| 1 | `pack.toml` доступен по HTTP, версии MC/загрузчика читаются |
| 2 | `index.toml` скачан и его **sha256 совпадает** с заявленным в `pack.toml` |
| 3 | каждый `mods/*.pw.toml` доступен и его sha256 совпадает с индексом |
| 4 | каждый `.jar` реально скачивается и его **sha1 совпадает** с заявленным |
| 5 | `latest/instance.zip` и `latest/pack.mrpack` доступны, внутри них `packsync/pack-url.txt` указывает на этот же пак |
| 6 | в `instance.cfg` есть корректная `PreLaunchCommand` и `OverrideCommands=true`; в `modrinth.index.json` — правильное число модов и зависимостей |

Любое расхождение — это ровно та причина, по которой у игрока «моды не скачиваются»,
поэтому скрипт падает с ненулевым кодом и печатает список провалов.
Удобно гонять в CI и после каждого пуша.

---

## Modpack Manager — приложение на Python

`app/modpack_app.py` — оконное приложение: **меню, вкладки, таблица статусов,
прогресс-бар**. Python 3.8+ и Tkinter, оба в стандартной поставке, сторонних
зависимостей нет. В CI собирается в один `ModpackManager.exe` через PyInstaller,
так что игрокам Python не нужен.

Готовое приложение (Windows):

```
https://<user>.github.io/<repo>/latest/ModpackManager.exe
```

Что умеет:

- **Выбрать папку сборки** — вручную или автопоиском у AstralRinth, Modrinth App,
  Freesm, Prism, MultiMC и в `.minecraft`. Последняя папка запоминается.
- **Проверить** mods, config, defaultconfigs, kubejs, resourcepacks, shaderpacks
  и всё прочее содержимое пака — каждый файл **по хэшу**, поэтому ловится и
  «файл есть, но битый», и «есть, но старый».
- **Починить** — собственный загрузчик на `urllib`, **Java не нужна**. Качает во
  временный файл, сверяет хэш и только потом подменяет; старое уходит в
  `.modpack-backup`.
- **Установить пак с нуля** — создаёт инстанс Prism/Freesm **прямо на диске**:
  `instance.cfg` с Pre-Launch Command, `mmc-pack.json` с Minecraft и NeoForge,
  `.minecraft/packsync/`. Ни zip-файла, ни диалога импорта — лаунчер подхватывает
  инстанс сам.
- Включать/выключать моды через `.disabled`, убирать лишние файлы, сохранять
  отчёт в txt/csv, смотреть `sync.log`, включать видимый прогресс (`SHOW_GUI`).

Статусы: `НА МЕСТЕ` · `ОТСУТСТВУЕТ` · `НЕ СОВПАДАЕТ` · `ОТКЛЮЧЁН` ·
`НЕТ (preserve)` · `ДРУГАЯ СТОРОНА` · `ЛИШНИЙ`. Подробности —
в [`app/README.md`](app/README.md).

Ядро (`app/packlib.py`) намеренно отделено от GUI: оно тестируется headless,
и именно его CI прогоняет перед сборкой `.exe`.

Дополнительно `packsync/sync.cmd` и `sync.sh` пишут `packsync/sync.log`, а
файл-флаг `packsync/SHOW_GUI` включает видимое окно прогресса при запуске игры.

**Для автора и CI** — `scripts/verify.py --game-dir <папка>`: та же проверка
из командной строки, с ненулевым кодом возврата при любом провале.

---

## Квесты (FTB Quests) и кастомный контент (KubeJS)

В паке **141 квест в 3 главах** (321 задача, 215 наград) — по одной главе на
измерение. Каждая глава — это не список, а **витрина секций**: внутри главы
квесты собраны в цветные блоки с подписями, связаны стрелками зависимостей
и снабжены иконками, подсказками и вехами.

| Глава | Квестов | Секции | О чём |
|---|---|---|---|
| Земли Рассвета | 84 | 8 | от первого дерева до портала: пещеры, биомы, ферма, бой, чары, механизмы |
| Багровое Пекло | 35 | 6 | крепость, бартер с пиглинами, незерит, Иссушитель, маяк, выход в Край |
| Грань Пустоты | 22 | 4 | дракон, внешние острова, город Края, элитры, медаль мастера пака |

Оформление главы: **баннер** 256x64 сверху (рисуется `scripts/gen_textures.py`),
цветная **подложка и пластинка-заголовок** у каждой секции (текст рисуется
шрифтом игры и переведён на русский и английский), **ореолы** позади вех,
кликабельные **порталы** между главами (`click_action: open_quest`), ссылки на
квесты соседних глав (`quest_links`). Раскладку (`blocks` — секции полками,
внутри — дерево по зависимостям) считает генератор, координаты руками не
пишутся. Используются 11 типов задач FTB Quests, включая `stat`, `location`,
`observation`, `biome`, `structure` и `advancement`.

Кастомные предметы имеют **собственные текстуры 16x16**
(`kubejs/assets/kubejs/textures/item/*.png`), а не ванильные заглушки:
золотая медаль, незеритовая медаль и финальная медаль с лентами.

Квесты пишутся **на Python** (`scripts/quests/questline.py`), а SNBT генерирует
`scripts/gen_quests.py`. Так сделано намеренно: в формате FTB Quests легко
ошибиться так, что ничего не упадёт — квесты просто молча не появятся.
Например, lang-ключ жёстко привязан к ID (`quest.0000000000001110.title`),
а `readID()` молча перегенерирует ID, равный 0 или 1.

Формат выверен **по исходникам мода** (ветка `1.21.1/main`, соответствует
FTB Quests 2101.1.36), а не по чужим примерам. Оттуда же взяты неочевидные
детали — например, что `ItemTask.count` это **long** (`8L`), а
`ItemReward.count` — **int** (`8`), и что поле награды называется `xp_levels`,
а не `levels`. Полная таблица источников — в [`scripts/quests/README.md`](scripts/quests/README.md).

`scripts/check_quests.py` валидирует результат **без Minecraft**: парсит SNBT
обратно, проверяет ID, зависимости, типы полей, lang-ключи, соответствие
`kubejs:*`-предметов скриптам регистрации и (с `--registry`) существование всех
`minecraft:*` в 1.21.1. Обе проверки встроены в CI.

```bash
python scripts/gen_quests.py              # questline.py -> .snbt
python scripts/check_quests.py --registry # валидация
```

### Моды пака

| Мод | Версия | Откуда |
|---|---|---|
| FTB Quests | 2101.1.36 | `maven.ftb.dev` |
| FTB Library | 2101.1.36 | `maven.ftb.dev` (зависимость) |
| FTB Teams | 2101.1.9 | `maven.ftb.dev` (зависимость) |
| Architectury API | 13.0.11+neoforge | Modrinth (требуется ≥13.0.8) |
| KubeJS | 2101.7.2-build.377 | Modrinth |
| Rhino | 2101.2.7-build.85 | Modrinth (зависимость KubeJS) |
| Better Advanced Tooltips | 2101.1.0-build.5 | Modrinth (зависимость KubeJS) |
| JEI / Jade / JourneyMap | см. `pw.py list` | Modrinth |
| FTB Quests Optimizer | 3.2.0-1.21.1 | Modrinth (производительность FTB Quests) |
| FTB Quests Entity Visualization | 1.11.0 | Modrinth (мобы в задачах рендерятся в 3D) |

**Certain Questing Additions убран из пака**: сборка 1.2.0.4 сделана под
FTB Quests 2101.1.15…20 и на FTB Quests 2101.1.21+ роняет игру при открытии
книги квестов (`MixinApplyError: @Shadow field val$name was not located in
ChapterImageButton$3`). Подробности — `docs/TROUBLESHOOTING.md`.
Проверка зашита в `scripts/check_mods.py` и в CI, поэтому случайно вернуть
мод в пак не получится.

FTB-модов **нет на Modrinth** — только на CurseForge, чей API требует ключ.
Поэтому добавлена команда `pw.py add-maven`: она читает POM, рекурсивно
разрешает зависимости, при конфликте версий берёт максимальную и достаёт
готовый sha1 из соседнего файла `.sha1` (jar при этом не скачивается).

```bash
python scripts/pw.py add-maven ftb-quests-neoforge --mc-prefix 2101
```

---

## Локальная проверка до публикации

```bash
python scripts/pw.py serve --port 8080
```

Откроется локальный сервер на `http://localhost:8080/pack.toml`. Временно укажите
этот адрес в pre-launch команде своего тестового инстанса — и убедитесь, что
синхронизация работает, **до** пуша в GitHub.

Собрать артефакты руками (без CI):

```bash
python scripts/pw.py site --out site              # payload для Pages
python scripts/pw.py mrpack                       # .mrpack в dist/
python scripts/pw.py instance                     # instance.zip в dist/
```

---

## Документация

| Файл | О чём |
|---|---|
| [`INSTALL.md`](INSTALL.md) | **Инструкция для игроков** — можно просто отдать ссылку |
| [`installer/README.md`](installer/README.md) | Как работает однокнопочный установщик |
| [`app/README.md`](app/README.md) | Modpack Manager: меню, вкладки, статусы, починка и установка инстанса без Java |
| [`docs/SETUP.md`](docs/SETUP.md) | Первичная настройка GitHub, Pages, релизов + `setup-github.py` |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Как всё устроено под капотом |
| [`docs/SERVER.md`](docs/SERVER.md) | Выделенный сервер с тем же паком |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Типовые проблемы и решения |
| [`packsync/README.md`](packsync/README.md) | Про `packwiz-installer` и hook-и лаунчеров |

---

## Смена версии Minecraft / загрузчика

Отредактируйте `pack.toml`:

```toml
[versions]
minecraft = "1.21.4"
neoforge  = "21.4.158"

[options]
acceptable-game-versions = ["1.21.2", "1.21.3", "1.21.4"]
```

Затем `python scripts/pw.py update --all` — все моды переподберутся под новую
версию. Что не найдётся, скрипт сообщит. Актуальные версии NeoForge:
`https://neoforged.net/` → *Download* → список на maven.

---

## Лицензии

- [`packwiz`](https://github.com/packwiz/packwiz) — MIT
- [`packwiz-installer`](https://github.com/packwiz/packwiz-installer) — MIT
  (jar-файлы лежат в `packsync/`, текст лицензии — `packsync/LICENSE-packwiz-installer.txt`)
- Моды принадлежат их авторам; этот репозиторий хранит только **ссылки** на них.
