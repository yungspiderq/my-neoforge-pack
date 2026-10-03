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
├── config/ resourcepacks/ shaderpacks/   ← синхронизируемые файлы
├── packsync/                     ← механизм автосинхронизации (см. packsync/README.md)
│   ├── packwiz-installer.jar
│   ├── packwiz-installer-bootstrap.jar
│   ├── sync.cmd  sync.sh
│   └── pack-url.txt
├── instance-template/            ← шаблон инстанса для Prism/Freesm
├── scripts/
│   ├── pw.py                     ← ведение пака (моды, индекс, артефакты)
│   └── setup-github.py           ← публикация на GitHub одной командой
├── docs/                         ← подробные инструкции
└── .github/workflows/
    ├── validate.yml              ← проверка на PR
    ├── pages.yml                 ← публикация на GitHub Pages (каждый push в main)
    └── release.yml               ← .mrpack + instance.zip (по тегу v*)
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
