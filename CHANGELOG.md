# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
версионирование — [SemVer](https://semver.org/lang/ru/).

Версия пака задаётся в `pack.toml` (`version = "…"`) и соответствует git-тегам `v*`.

## [Unreleased]

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
