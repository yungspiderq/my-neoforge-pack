# app/ — Modpack Manager (Python)

Приложение для проверки и починки сборки. **Python 3.8+ и Tkinter** — оба входят
в стандартную поставку Python, сторонних зависимостей нет вообще. Именно поэтому
оно собирается в один `.exe` через PyInstaller без каких-либо ухищрений.

| Файл | Что это |
|---|---|
| `packlib.py` | Ядро: чтение пака, сверка с диском, синхронизация, создание инстанса. **GUI здесь нет** — поэтому модуль тестируется headless и используется из CI. |
| `modpack_app.py` | Tkinter-обёртка: меню, вкладки, таблица, прогресс, диалоги. |

---

## Запуск

```bash
python app/modpack_app.py
python app/modpack_app.py --game-dir "C:\...\profiles\MyPack"
python app/modpack_app.py --base-url https://user.github.io/repo
```

Готовый `.exe` (Windows, Python ставить не нужно):

```
https://<user>.github.io/<repo>/latest/ModpackManager.exe
```

Собирается в CI job'ом `build-app` на `windows-latest`:

```
pyinstaller --onefile --windowed --clean --noconfirm \
    --name ModpackManager --add-data "app/packlib.py;." app/modpack_app.py
```

---

## Синхронизация без Java

Главное отличие от `packwiz-installer`: загрузка своя, на `urllib`.

```
http_get(url) -> bytes
  -> hashlib.new(sha1/sha256).hexdigest()
  -> сверка с ожидаемым
  -> ТОЛЬКО ПОТОМ os.replace(tmp, dest)
```

Порядок принципиален: скачивание идёт в `<файл>.download`, хэш проверяется
**до** подмены. Оборвавшаяся закачка не оставит вместо мода огрызок, который
в следующий запуск выглядел бы как «файл есть». Заменяемый файл предварительно
копируется в `.modpack-backup/`.

Java нужна только для запасного пути — меню *Синхронизация → Запустить
packwiz-installer*, который дёргает штатный `packsync/sync.cmd`. Оставлен,
чтобы можно было сравнить поведение двух механизмов.

---

## Создание инстанса без zip-файла

*Файл → Установить пак с нуля* создаёт инстанс Prism/Freesm **прямо на диске**:

```
<instances>/<имя>/
├── instance.cfg        ConfigVersion, InstanceType, OverrideCommands,
│                       PreLaunchCommand со всеми нужными флагами
├── mmc-pack.json       net.minecraft + net.neoforged (uid/version/cachedRequires)
└── .minecraft/
    └── packsync/       pack-url.txt + оба jar-а + sync.cmd + sync.sh
```

Prism сканирует каталог `instances/` и подхватывает новый инстанс сам —
ни `--import`, ни zip, ни диалог импорта не нужны. Jar-ы берутся с сервера
из `packsync/` (этот каталог публикуется на Pages отдельным шагом `pw.py site`,
в индекс пака он намеренно не входит).

Версия Java для `mmc-pack.json` вычисляется по версии Minecraft
(`java_major_for`): 1.17–1.20.4 → 17 (`java-runtime-gamma`),
1.20.5+ → 21 (`java-runtime-delta`), 26.x → 25 (`java-runtime-epsilon`).

**Для AstralRinth этот путь не работает**: его профили регистрируются в SQLite
(`%APPDATA%\AstralRinthApp\app.db`, таблица `profiles`), а не сканированием
каталога. Писать в чужую базу — неоправданный риск, поэтому для AstralRinth
остаётся импорт `.mrpack` и ручной hook (4 клика, строка копируется в буфер
установщиком).

---

## Что проверяется

Цепочка ровно та же, что у `packwiz-installer`:

```
pack.toml   -> имя, версия, MC, загрузчик, sha256 индекса
index.toml  -> sha256 сверяется с pack.toml (защита от рассинхрона)
mods/*.pw.toml -> URL на Modrinth, sha1, side
каждый файл -> сравнение с диском ПО ХЭШУ
```

Проверяется не только `mods/`, но и `config/`, `defaultconfigs/`, `kubejs/`,
`resourcepacks/`, `shaderpacks/` — всё, что есть в индексе пака.

### Статусы

| Статус | Значение | Чинится? |
|---|---|---|
| `НА МЕСТЕ` | файл есть и хэш совпал | — |
| `ОТСУТСТВУЕТ` | файла нет | да |
| `НЕ СОВПАДАЕТ` | хэш другой (битый или старый) | да |
| `ОТКЛЮЧЁН` | лежит как `<имя>.disabled` | нет — это сделал игрок |
| `НЕТ (preserve)` | в `index.toml` стоит `preserve = true` | нет — намеренно |
| `ДРУГАЯ СТОРОНА` | мод серверный, выбрана сторона `client` | нет |
| `ЛИШНИЙ` | файла нет в паке | да, по запросу |

`ОТКЛЮЧЁН` и `НЕТ (preserve)` намеренно не считаются ошибками. Первое — игрок
сам выключил мод (в меню есть «Включить .disabled»), второе — файл запрещено
перезаписывать, чтобы не затирать личные настройки.

---

## Интерфейс

**Меню**

| | |
|---|---|
| **Файл** | Выбрать папку сборки… · Недавние · Установить пак с нуля… · Сохранить отчёт… (txt/csv) · Выход |
| **Проверка** | Проверить сейчас (F5) · Все стороны · Только проблемные · Показать все |
| **Синхронизация** | Починить всё (Ctrl+R) · Починить только выбранное · Убрать лишние… · Включить/снять `.disabled` · Запустить packwiz-installer |
| **Инструменты** | Открыть `mods/` · `config/` · папку сборки · `.modpack-backup` · `sync.log` · `SHOW_GUI` |
| **Справка** | Как это работает · Адрес пака · Репозиторий · О программе |

**Вкладки:** Моды · Конфиги и файлы · Лишние · Журнал.
В таблицах работает мультивыделение — можно чинить или отключать группу модов.

Настройки (последняя папка, адрес, сторона, список недавних) хранятся в
`%LOCALAPPDATA%\ModpackManager\settings.json`
(Linux: `~/.config/modpack-manager/settings.json`).

---

## Потоки и Tk

Tkinter **не потокобезопасен**: трогать виджеты не из главного потока нельзя.
Поэтому вся сетевая работа (`load_pack`, `scan_local`, `sync_rows`,
`install_prism_instance`) уходит в `threading.Thread(daemon=True)`, а результаты
приходят обратно через `queue.Queue`. Главный поток разбирает очередь в
`_drain()` по `root.after(60, ...)`.

Типы событий в очереди: `log`, `status`, `progress`, `render`, `guivar`,
`info`, `recheck`, `reloaddirs`, `done`, `error`. Все обрабатываются в одном
`_drain` — раньше здесь была обёртка, которая потерянно проглатывала события.

---

## Кроссплатформенный аналог для CI

`scripts/verify.py` делает ту же проверку из командной строки и возвращает
ненулевой код при любом провале:

```bash
python scripts/verify.py --game-dir <папка игры>     # сверка с диском
python scripts/verify.py                             # проверка сервера и артефактов
python scripts/verify.py --fast                      # без скачивания jar-ов
```

`packlib.py` и `verify.py` намеренно дублируют часть логики: первое — ядро
приложения, второе — автономная проверка для CI, которую можно запускать
без установленного Tkinter.
