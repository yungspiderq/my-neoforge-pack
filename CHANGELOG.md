# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
версионирование — [SemVer](https://semver.org/lang/ru/).

Версия пака задаётся в `pack.toml` (`version = "…"`) и соответствует git-тегам `v*`.

## [Unreleased]

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

[Unreleased]: https://github.com/REPLACE_ME/REPLACE_ME/commits/main
