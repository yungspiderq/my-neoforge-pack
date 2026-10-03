# Как это устроено

## Схема целиком

```
┌──────────────────────────── ВАШ КОМПЬЮТЕР ────────────────────────────┐
│  pack.toml          mods/*.pw.toml       config/…  resourcepacks/…     │
│  (имя, MC, NeoForge) (ссылки на Modrinth) (ваши файлы)                  │
│                    │                                                   │
│                    ▼  pw.py refresh / packwiz refresh                  │
│              index.toml  ← sha256 каждого файла пака                   │
└────────────────────┬──────────────────────────────────────────────────┘
                     │ git push
                     ▼
┌──────────────────────────── GITHUB ───────────────────────────────────┐
│  Actions: go install packwiz → packwiz refresh → pw.py site            │
│                                                                        │
│  ┌── GitHub Pages ──────────────┐   ┌── Releases (по тегу v*) ──────┐  │
│  │ <user>.github.io/<repo>/     │   │ pack-1.0.0.mrpack             │  │
│  │   pack.toml                  │   │ pack-1.0.0-instance.zip       │  │
│  │   index.toml                 │   └───────────────────────────────┘  │
│  │   mods/*.pw.toml             │                                      │
│  │   config/…  resourcepacks/…  │                                      │
│  └──────────────────────────────┘                                      │
└────────────────────┬──────────────────────────────────────────────────┘
                     │ HTTP при каждом запуске игры
                     ▼
┌──────────────────── КОМПЬЮТЕР ИГРОКА ─────────────────────────────────┐
│  лаунчер → pre-launch hook                                             │
│    Freesm/Prism : "$INST_JAVA" -jar …/packwiz-installer-bootstrap.jar  │
│    AstralRinth  : cmd /c packsync\sync.cmd                             │
│                                                                        │
│  packwiz-installer:                                                    │
│    1. GET pack.toml      → узнать имя index-файла и его sha256         │
│    2. GET index.toml     → получить список файлов и хэшей               │
│    3. сравнить с packwiz.json (что уже стоит локально)                 │
│    4. для *.pw.toml      → GET их, прочитать [download].url            │
│    5. скачать только недостающее/изменившееся                          │
│    6. удалить то, чего больше нет в паке                               │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Формат packwiz

Придуман специально для «modpack as code». Правила простые:

- Корень репозитория **отождествляется с папкой игры** (`.minecraft/`).
- Файлы `pack.toml`, `index.toml` и всё с расширением `.pw.toml` — **метафайлы**,
  игрокам они не скачиваются.
- Всё остальное — **обычные файлы**, они попадают игроку 1:1 по тому же
  относительному пути. Поэтому конфиги лежат в `config/`, а не в `overrides/config/`.
- Что считать «остальным» — регулируется `.packwizignore` (gitignore-синтаксис).
  Туда же добавлены `scripts/`, `docs/`, `.github/`, `instance-template/`,
  `packsync/` и все `.md`-документы.

### `mods/<имя>.pw.toml`

```toml
name = "Just Enough Items (JEI)"
filename = "jei-1.21.1-neoforge-19.57.0.450.jar"   # куда положить в mods/
side = "both"                                       # both | client | server

[download]
url = "https://cdn.modrinth.com/data/u6dRKJwZ/versions/Tn0dgwL0/jei-…jar"
hash-format = "sha1"
hash = "129a0aa982cd520ef8a35abddf592dc4d5655bd9"

[update]
[update.modrinth]
mod-id  = "u6dRKJwZ"      # чтобы `pw.py update` находил новые версии
version = "Tn0dgwL0"
```

### `index.toml`

```toml
hash-format = "sha256"

[[files]]
file = "mods/just-enough-items.pw.toml"
hash = "e448786fd180a89c…"
metafile = true

[[files]]
file = "config/journeymap.cfg"
hash = "9a1c…"
preserve = true          # ← не перезаписывать, если игрок уже менял файл
```

`pack.toml` хранит sha256 самого `index.toml` — защита от подмены индекса.

---

## Почему `packsync/` исключён из пака

`packwiz-installer.jar` во время работы **заблокирован** операционной системой
(Windows держит файл открытым). Если бы jar лежал в индексе пака, попытка
обновить его на новую версию закончилась бы ошибкой записи.

Поэтому `packsync/` игнорируется packwiz'ом и раскладывается CI-ем напрямую:

- в `…-instance.zip` → `minecraft/packsync/`
- в `.mrpack` → `overrides/packsync/`

Оба пути приводят в корень папки игры, так что sync-скрипты и jar-ы
всегда оказываются в `<папка игры>/packsync/`.

Обновление версии installer'а = замена jar-а в репозитории + новый релиз.

---

## Разница в hook-ах лаунчеров

Это самый неочевидный момент всей схемы.

### Prism Launcher / Freesm Launcher

Freesm — форк Prism Launcher, поэтому наследует всю его механику.
Pre-launch command выполняется **через парсер аргументов с поддержкой кавычек**
и с подстановкой переменных:

| Переменная | Значение |
|---|---|
| `$INST_JAVA` | путь к Java, выбранной для инстанса |
| `$INST_DIR` | папка инстанса |
| `$INST_DIR/minecraft` | папка игры |
| `$INST_MC_DIR` | то же |

Рабочая папка команды — `$INST_DIR`, а игра живёт в `$INST_DIR/minecraft`,
поэтому обязательно передаём `--pack-folder "$INST_DIR/minecraft"`
(по умолчанию packwiz-installer считает папкой пака текущий каталог).

```
"$INST_JAVA" -jar "$INST_DIR/minecraft/packsync/packwiz-installer-bootstrap.jar" \
  --bootstrap-no-update \
  --bootstrap-main-jar "$INST_DIR/minecraft/packsync/packwiz-installer.jar" \
  --pack-folder "$INST_DIR/minecraft" \
  -g "https://<user>.github.io/<repo>/pack.toml"
```

Эта строка генерируется CI-ем и зашивается в `instance.cfg` внутри `…-instance.zip`.

### AstralRinth / Modrinth App (Theseus)

Здесь всё иначе. В исходниках (`packages/app-lib/src/api/profile/mod.rs`)
hook выполняется так:

```rust
let mut cmd = hook.split(' ');
if let Some(command) = cmd.next() {
    Command::new(command)
        .args(cmd.collect::<Vec<&str>>())
        .current_dir(&full_path)     // ← папка профиля = папка игры
        .spawn()
}
```

Следствия:

- **нет shell** — пайпы, `&&`, `%VAR%` не работают;
- **нет подстановки переменных** — `$INST_DIR` останется литералом;
- **нет обработки кавычек** — путь с пробелом развалится на два аргумента;
- **рабочая папка = папка профиля**, а в Theseus папка профиля и есть папка игры.

Поэтому единственная рабочая форма — короткая команда без пробелов внутри
аргументов, а всю логику прячем в скрипт:

```
Windows :  cmd /c packsync\sync.cmd
Linux   :  sh packsync/sync.sh
```

`sync.cmd` / `sync.sh` сами находят Java (через `JAVA_HOME`, `PATH`, затем
перебором типичных каталогов — `java_runtimes` AstralRinth/ModrinthApp,
`PrismLauncher/java`, `Eclipse Adoptium`, `/usr/lib/jvm` и т. д.), читают
адрес пака из `pack-url.txt` и запускают installer.

Оба скрипта **всегда возвращают код 0**. Это принципиально: ненулевой код
AstralRinth трактует как ошибку и не запускает игру. Лучше не синхронизироваться,
чем не дать человеку поиграть.

---

## Почему `--bootstrap-no-update`

`packwiz-installer-bootstrap.jar` по умолчанию при каждом запуске обращается
к GitHub API (`repos/comp500/packwiz-installer/releases/latest`), чтобы
самообновиться. Это:

- лишний сетевой запрос на каждый запуск игры;
- зависимость от лимитов GitHub API (60 запросов/час на IP — в общежитии
  или офисе легко упереться);
- плавающая версия installer'а у игроков.

Мы кладём оба jar-а в репозиторий и фиксируем версию флагом
`--bootstrap-no-update`. Запуск становится мгновенным и предсказуемым.

---

## Что делает CI

| Workflow | Триггер | Действия |
|---|---|---|
| `validate.yml` | push в ветку ≠ main, PR | `packwiz refresh` → падает, если `index.toml` в коммите устарел; `pw.py check/list/versions`; пробная сборка site |
| `pages.yml` | push в `main` | `packwiz refresh` → `pw.py site` → деплой на GitHub Pages |
| `release.yml` | тег `v*` | `packwiz refresh` → `packwiz modrinth export` → `pw.py inject-packsync` → `pw.py instance` → GitHub Release |

`index.toml` пересобирается в CI **всегда**, поэтому даже если локально вы
забыли выполнить `refresh` — опубликованный пак будет корректным.
`validate.yml` существует ровно для того, чтобы напомнить об этом до мержа.

---

## Про `.mrpack` и почему он второй сорт

`.mrpack` — формат Modrinth. В нём моды перечислены в `modrinth.index.json`
с прямыми ссылками и sha1. Его импортируют AstralRinth, Modrinth App, Prism.

Но сам по себе `.mrpack` **не умеет обновляться по URL**: Modrinth App
проверяет обновления только для паков, установленных с modrinth.com.
Именно поэтому для AstralRinth мы добавляем hook — он превращает
«статичный импорт» в «живую синхронизацию» поверх уже установленного профиля.

Если hook настроить не удалось — всегда остаётся ручной путь:
скачать новый `.mrpack` из релизов и импортировать заново.
