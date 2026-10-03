# Changelog

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
версионирование — [SemVer](https://semver.org/lang/ru/).

Версия пака задаётся в `pack.toml` (`version = "…"`) и соответствует git-тегам `v*`.

## [Unreleased]

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
