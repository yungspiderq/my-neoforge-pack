# installer/ — однокнопочная установка у игроков

Три скрипта, которые публикуются на GitHub Pages рядом с `pack.toml`
и позволяют игроку установить пак **одной командой**.

| Файл | Платформа | Как запускают |
|---|---|---|
| `install.ps1` | Windows | `irm <base>/install.ps1 \| iex` |
| `install.bat` | Windows | двойной клик (обёртка над `install.ps1`) |
| `install.sh` | Linux / macOS | `curl -fsSL <base>/install.sh \| bash` |

`@@BASE_URL@@` во всех трёх файлах заменяется на реальный адрес в CI
(шаг *Stamp installer base URL* в `pages.yml`). В репозитории остаётся
плейсхолдер — так скрипты не зависят от имени репозитория.

---

## Что делает установщик

### 1. Ищет лаунчер

Четыре независимых способа, по порядку:

1. `PATH` (`Get-Command` / `command -v`)
2. типичные каталоги установки (`%LOCALAPPDATA%\Programs`, `Program Files`, `/usr/bin`, `~/.local/bin`, `*.AppImage`)
3. реестр Windows: `…\Uninstall\*` → `DisplayName` + `InstallLocation` / `DisplayIcon`
4. ярлыки в меню Пуск (`.lnk` → `WScript.Shell.CreateShortcut`)

Плюс flatpak на Linux. Распознаются: **Freesm Launcher, Prism Launcher, MultiMC,
AstralRinth App, Modrinth App**.

### 2. Ставит пак

**Prism-семейство (Freesm / Prism / MultiMC)** — полностью автоматически:

```
<launcher> --import https://…/latest/instance.zip
```

Prism CLI принимает `--import` с **локальным путём или URL**, поэтому инстанс
даже не скачивается нами — лаунчер тянет его сам. Внутри `instance.zip` уже
лежит `instance.cfg` с прописанной `PreLaunchCommand`, так что автосинк
включается без единого ручного действия.

**Theseus-семейство (AstralRinth / Modrinth App)** — автоимпорт + 4 клика:

```
"AstralRinth App.exe" "C:\…\modpack-latest.mrpack"
```

В `api/handler.rs::parse_command` любой аргумент, не начинающийся с
`modrinth://`, трактуется как путь к `.mrpack` → `CommandPayload::RunMRPack`.
Работает и при холодном старте (`args_os().nth(1)`), и если лаунчер уже запущен
(плагин `single_instance` передаёт `args.get(1)`).

Hook при этом **вписывается вручную**: установщик кладёт строку
`cmd /c packsync\sync.cmd` в буфер обмена и печатает инструкцию.

### 3. `-WithLauncher` (Windows)

Если лаунчера нет вообще — скачивает установщик Freesm Launcher из последнего
релиза (`api.github.com/repos/FreesmTeam/FreesmLauncher/releases/latest`),
запускает его и повторяет поиск. Отдельный паттерн для ARM64.

В однострочнике флаг передаётся оборачиванием скачанного текста в script block:

```powershell
iex "& {$(irm <base>/install.ps1)} -WithLauncher"
```

Вариант `irm <base>/install.ps1 -WithLauncher | iex` **невалиден**: всё до `|`
PowerShell отдаёт командлету `Invoke-RestMethod`, у которого нет параметра
`WithLauncher` → `ParameterBindingException` ещё до скачивания; а `iex` в принципе
выполняет строку без аргументов, поэтому «протолкнуть» флаг через трубу нельзя.

Политика выполнения Windows по умолчанию (`Restricted`) однострочникам с `iex`
не мешает — строка выполняется в памяти. Но она блокирует запуск сохранённого
`.ps1`-файла: `& "$env:TEMP\mp-install.ps1"` → `PSSecurityException /
UnauthorizedAccess` («выполнение сценариев отключено в этой системе») ещё до
первой строки скрипта. Поэтому вариант «скачать файл, затем запустить» годится
только через отдельный процесс с Bypass (настройки системы не меняются):

```powershell
irm <base>/install.ps1 -OutFile "$env:TEMP\mp-install.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File "$env:TEMP\mp-install.ps1" -WithLauncher
```

---

## Почему hook не прописывается в базу AstralRinth автоматически

Технически это возможно: `%APPDATA%\AstralRinthApp\app.db`, таблица `profiles`,
колонка `override_hook_pre_launch` (схема — `packages/app-lib/migrations/20240711194701_init.sql`).

Не делаем сознательно:

- в Windows нет встроенного `sqlite3.exe`, пришлось бы тянуть бинарник со стороны;
- база может быть занята запущенным лаунчером (WAL, `SQLITE_BUSY`), а профиль
  создаётся асинхронно во время импорта — пришлось бы поллить и гоняться за состоянием;
- схема меняется между версиями лаунчера;
- цена ошибки — сломанный лаунчер у игрока, цена успеха — сэкономленные 4 клика.

Если очень захочется: безопасная реализация = копия `app.db` (+ `-wal`, `-shm`)
→ `PRAGMA table_info(profiles)` для проверки схемы → `UPDATE … WHERE path = ?`
с busy-timeout и ретраями → восстановление из копии при любой ошибке.

---

## Как проверить установщик локально

```bash
# поднять локальную копию Pages-пейлоада
python scripts/pw.py site --out /tmp/site
python -m http.server 8080 -d /tmp/site

# в отдельном терминале, с заменённым BASE_URL
sed 's|@@BASE_URL@@|http://localhost:8080|' installer/install.sh | bash -s -- --base-url http://localhost:8080
```

Для PowerShell:

```powershell
(Get-Content installer/install.ps1 -Raw) -replace '@@BASE_URL@@','http://localhost:8080' |
    Set-Content $env:TEMP\install-test.ps1
powershell -ExecutionPolicy Bypass -File $env:TEMP\install-test.ps1 -Launcher freesm
```

---

## Точность имён

| Лаунчер | Имя бинарника | Откуда известно |
|---|---|---|
| Freesm Launcher 2.3.1 | `FreesmLauncher.exe` | ассеты релиза `FreesmLauncher-Windows-MSVC-Setup-2.3.1.exe` |
| Prism Launcher | `prismlauncher.exe` | [CLI-документация Prism](https://prismlauncher.org/wiki/getting-started/command-line-interface/) |
| AstralRinth App 0.9.204 | `AstralRinth App.exe` **с пробелом** | `apps/app/tauri.conf.json`: `productName` / `mainBinaryName` |
| AstralRinth — данные | `%APPDATA%\AstralRinthApp` | `dirs.rs`: `dirs::data_dir().join("AstralRinthApp")`, `identifier = "AstralRinthApp"` |

Пробел в `AstralRinth App.exe` — главная мина: в PowerShell путь обязательно
в кавычках, а в hook'е AstralRinth кавычки использовать **нельзя** (строка
режется по пробелам), поэтому hook указывает на `packsync\sync.cmd`, а не на jar.
