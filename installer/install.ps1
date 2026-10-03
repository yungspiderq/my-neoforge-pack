<#
.SYNOPSIS
    Однокнопочный установщик модпака. Сам находит лаунчер и ставит пак.

.DESCRIPTION
    Что делает:
      1. Ищет установленные лаунчеры (Freesm, Prism, MultiMC, AstralRinth, Modrinth App)
         — через PATH, реестр (Uninstall), ярлыки в меню Пуск и типичные каталоги.
      2. Если ничего не нашёл и указан -WithLauncher — скачивает и ставит Freesm Launcher.
      3. Freesm / Prism / MultiMC:
             <launcher>.exe --import <BASE>/latest/instance.zip
         Лаунчер сам скачает инстанс, Minecraft, NeoForge и пропишет Pre-Launch
         Command для автосинхронизации. Ручных действий — ноль.
      4. AstralRinth / Modrinth App:
             скачивает .mrpack, кладёт строку hook'а в буфер обмена и запускает
             лаунчер с этим файлом (auto-import). Остаётся вставить строку
             в Options -> Hooks -> Pre-launch (Ctrl+V).
         База данных лаунчера НЕ трогается — это принципиально.

.PARAMETER Launcher
    auto (по умолчанию) | freesm | prism | multimc | astralrinth | modrinth
    При auto предпочтение отдаётся Freesm/Prism: там установка полностью
    автоматическая и не требует настройки hook'а.

.PARAMETER WithLauncher
    Если лаунчер не найден — скачать и установить Freesm Launcher автоматически.

.EXAMPLE
    irm https://<user>.github.io/<repo>/install.ps1 | iex

.EXAMPLE
    .\install.ps1 -Launcher astralrinth -WithLauncher
#>

[CmdletBinding()]
param(
    [string] $BaseUrl = '@@BASE_URL@@',
    [ValidateSet('auto', 'freesm', 'prism', 'multimc', 'astralrinth', 'modrinth')]
    [string] $Launcher = 'auto',
    [switch] $WithLauncher,
    [string] $InstanceName = ''
)

$ErrorActionPreference = 'Stop'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

# --------------------------------------------------------------------------- #
#  Вывод
# --------------------------------------------------------------------------- #

function Write-Title([string]$t) {
    Write-Host ''
    Write-Host ('=' * 68) -ForegroundColor DarkCyan
    Write-Host "  $t" -ForegroundColor Cyan
    Write-Host ('=' * 68) -ForegroundColor DarkCyan
}
function Write-Step([string]$t) { Write-Host ''; Write-Host "  -> $t" -ForegroundColor Yellow }
function Write-Ok([string]$t)   { Write-Host "     [OK]   $t" -ForegroundColor Green }
function Write-Info([string]$t) { Write-Host "     [..]   $t" -ForegroundColor Gray }
function Write-Warn2([string]$t){ Write-Host "     [!]    $t" -ForegroundColor Magenta }
function Write-Bad([string]$t)  { Write-Host "     [X]    $t" -ForegroundColor Red }

# --------------------------------------------------------------------------- #
#  Описание известных лаунчеров
# --------------------------------------------------------------------------- #

$LAUNCHERS = @(
    @{
        Key = 'freesm'; Product = 'Freesm Launcher'; Family = 'prism'
        ExeNames = @('FreesmLauncher.exe')
        Guess = @(
            "$env:LOCALAPPDATA\Programs\FreesmLauncher\FreesmLauncher.exe",
            "$env:LOCALAPPDATA\FreesmLauncher\FreesmLauncher.exe",
            "$env:ProgramFiles\FreesmLauncher\FreesmLauncher.exe",
            "${env:ProgramFiles(x86)}\FreesmLauncher\FreesmLauncher.exe"
        )
        Repo = 'FreesmTeam/FreesmLauncher'
        AssetPattern = 'FreesmLauncher-Windows-MSVC-Setup-.*\.exe$'
        ArmPattern = 'FreesmLauncher-Windows-MSVC-arm64-Setup-.*\.exe$'
        Url = 'https://freesmlauncher.org/'
    },
    @{
        Key = 'prism'; Product = 'Prism Launcher'; Family = 'prism'
        ExeNames = @('prismlauncher.exe', 'PrismLauncher.exe')
        Guess = @(
            "$env:LOCALAPPDATA\Programs\PrismLauncher\prismlauncher.exe",
            "$env:ProgramFiles\PrismLauncher\prismlauncher.exe",
            "${env:ProgramFiles(x86)}\PrismLauncher\PrismLauncher.exe"
        )
        Repo = 'PrismLauncher/PrismLauncher'
        AssetPattern = 'PrismLauncher-Windows-MSVC-Setup-.*\.exe$'
        ArmPattern = 'PrismLauncher-Windows-MSVC-arm64-Setup-.*\.exe$'
        Url = 'https://prismlauncher.org/'
    },
    @{
        Key = 'multimc'; Product = 'MultiMC'; Family = 'prism'
        ExeNames = @('MultiMC.exe')
        Guess = @("$env:LOCALAPPDATA\Programs\MultiMC\MultiMC.exe", "C:\MultiMC\MultiMC.exe")
        Repo = ''; AssetPattern = ''; ArmPattern = ''; Url = 'https://multimc.org/'
    },
    @{
        Key = 'astralrinth'; Product = 'AstralRinth App'; Family = 'theseus'
        # mainBinaryName в tauri.conf.json = "AstralRinth App" (с пробелом!)
        ExeNames = @('AstralRinth App.exe', 'AstralRinth.exe', 'astralrinth.exe')
        Guess = @(
            "$env:ProgramFiles\AstralRinth App\AstralRinth App.exe",
            "$env:LOCALAPPDATA\Programs\AstralRinth App\AstralRinth App.exe",
            "$env:LOCALAPPDATA\AstralRinth App\AstralRinth App.exe"
        )
        DataDir = "$env:APPDATA\AstralRinthApp"
        Repo = ''; AssetPattern = ''; ArmPattern = ''; Url = 'https://git.astralium.su/didirus/AstralRinth'
    },
    @{
        Key = 'modrinth'; Product = 'Modrinth App'; Family = 'theseus'
        ExeNames = @('Modrinth App.exe', 'modrinth-app.exe', 'ModrinthApp.exe')
        Guess = @(
            "$env:LOCALAPPDATA\Programs\Modrinth App\Modrinth App.exe",
            "$env:ProgramFiles\Modrinth App\Modrinth App.exe"
        )
        DataDir = "$env:APPDATA\ModrinthApp"
        Repo = ''; AssetPattern = ''; ArmPattern = ''; Url = 'https://modrinth.com/app'
    }
)

# --------------------------------------------------------------------------- #
#  Поиск исполняемого файла
# --------------------------------------------------------------------------- #

function Resolve-Shortcut([string]$lnk) {
    try {
        $sh = New-Object -ComObject WScript.Shell
        $s = $sh.CreateShortcut($lnk)
        if ($s.TargetPath -and (Test-Path -LiteralPath $s.TargetPath)) { return $s.TargetPath }
    } catch {}
    return $null
}

function Find-LauncherExe($def) {
    # 1) PATH
    foreach ($n in $def.ExeNames) {
        $c = Get-Command $n -ErrorAction SilentlyContinue
        if ($c -and $c.Source) { return $c.Source }
    }
    # 2) известные каталоги
    foreach ($p in $def.Guess) {
        if ($p -and (Test-Path -LiteralPath $p)) { return (Resolve-Path -LiteralPath $p).Path }
    }
    # 3) реестр: ключи удаления программ
    $roots = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )
    foreach ($r in $roots) {
        $items = Get-ItemProperty $r -ErrorAction SilentlyContinue
        foreach ($it in $items) {
            if (-not $it.DisplayName) { continue }
            $match = $false
            foreach ($n in $def.ExeNames) { if ($it.DisplayName -like "*$($n -replace '\.exe$','')*") { $match = $true } }
            if ($it.DisplayName -like "*$($def.Product)*") { $match = $true }
            if ($def.Key -eq 'freesm' -and $it.DisplayName -like '*Freesm*') { $match = $true }
            if (-not $match) { continue }

            foreach ($cand in @($it.InstallLocation, $it.DisplayIcon)) {
                if (-not $cand) { continue }
                $cand = ($cand -split ',')[0].Trim('"')
                if ((Test-Path -LiteralPath $cand) -and $cand -like '*.exe') { return $cand }
                foreach ($n in $def.ExeNames) {
                    $try = Join-Path $cand $n
                    if (Test-Path -LiteralPath $try) { return (Resolve-Path -LiteralPath $try).Path }
                }
            }
        }
    }
    # 4) ярлыки в меню Пуск
    $menus = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs",
        "$env:ProgramData\Microsoft\Windows\Start Menu\Programs"
    )
    foreach ($m in $menus) {
        if (-not (Test-Path -LiteralPath $m)) { continue }
        $lnks = Get-ChildItem -LiteralPath $m -Recurse -Filter '*.lnk' -ErrorAction SilentlyContinue
        foreach ($l in $lnks) {
            $tgt = Resolve-Shortcut $l.FullName
            if (-not $tgt) { continue }
            $leaf = Split-Path $tgt -Leaf
            foreach ($n in $def.ExeNames) {
                if ($leaf -ieq $n) { return $tgt }
            }
        }
    }
    return $null
}

function Get-InstalledLaunchers {
    $found = @()
    foreach ($def in $LAUNCHERS) {
        $exe = Find-LauncherExe $def
        if ($exe) { $found += [pscustomobject]@{ Def = $def; Exe = $exe } }
    }
    return $found
}

# --------------------------------------------------------------------------- #
#  Скачивание
# --------------------------------------------------------------------------- #

function Get-Text([string]$url) {
    return (Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 60).Content
}

function Save-File([string]$url, [string]$dest) {
    $tmp = "$dest.part"
    Invoke-WebRequest -Uri $url -UseBasicParsing -OutFile $tmp -TimeoutSec 900
    Move-Item -LiteralPath $tmp -Destination $dest -Force
    return $dest
}

function Install-Freesm {
    Write-Step 'Скачиваю Freesm Launcher с GitHub'
    $def = $LAUNCHERS | Where-Object { $_.Key -eq 'freesm' }
    $rel = Get-Text 'https://api.github.com/repos/FreesmTeam/FreesmLauncher/releases/latest' | ConvertFrom-Json
    $isArm = $env:PROCESSOR_ARCHITECTURE -eq 'ARM64'
    $pattern = if ($isArm) { $def.ArmPattern } else { $def.AssetPattern }
    $asset = $rel.assets | Where-Object { $_.name -match $pattern } | Select-Object -First 1
    if (-not $asset) { throw 'не нашёл установщик Freesm Launcher в релизе' }
    Write-Info ("версия {0}, файл {1} ({2:N1} МБ)" -f $rel.tag_name, $asset.name, ($asset.size / 1MB))
    $dst = Join-Path $env:TEMP $asset.name
    Save-File $asset.browser_download_url $dst | Out-Null
    Write-Info 'запускаю установщик — пройдите его окна, затем нажмите Enter здесь'
    Start-Process -FilePath $dst -Wait
    $exe = Find-LauncherExe $def
    if (-not $exe) { throw 'Freesm Launcher установился, но exe не найден. Перезапустите установщик пака.' }
    Write-Ok "Freesm Launcher: $exe"
    return $exe
}

# --------------------------------------------------------------------------- #
#  Установка в Prism-подобный лаунчер
# --------------------------------------------------------------------------- #

function Install-ViaPrism([string]$exe, [string]$product) {
    $zipUrl = "$BaseUrl/latest/instance.zip"
    Write-Step "Проверяю, что инстанс доступен: $zipUrl"
    try {
        $h = Invoke-WebRequest -Uri $zipUrl -UseBasicParsing -Method Head -TimeoutSec 60
        $len = 0
        try { $len = [int64]($h.Headers['Content-Length']) } catch { $len = 0 }
        if ($len -gt 0) { Write-Ok ("instance.zip найден ({0:N0} КБ)" -f ($len / 1KB)) }
        else { Write-Ok 'instance.zip доступен' }
    } catch {
        Write-Warn2 "HEAD-запрос не прошёл ($($_.Exception.Message)) — пробую скачать напрямую"
    }

    Write-Step "Передаю лаунчеру: $product --import <url>"
    Write-Info 'Лаунчер сам скачает инстанс, Minecraft, NeoForge и Java.'
    Write-Info 'При первом запуске packwiz-installer докачает моды — это может занять несколько минут.'
    Start-Process -FilePath $exe -ArgumentList @('--import', $zipUrl)
    Write-Ok 'Команда передана лаунчеру. Дальше он всё сделает сам.'
    return $true
}

# --------------------------------------------------------------------------- #
#  Установка в AstralRinth / Modrinth App
# --------------------------------------------------------------------------- #

function Install-ViaTheseus($found) {
    $exe = $found.Exe
    $def = $found.Def
    $mrUrl = "$BaseUrl/latest/pack.mrpack"
    $dst = Join-Path $env:TEMP 'modpack-latest.mrpack'

    Write-Step "Скачиваю пак: $mrUrl"
    Save-File $mrUrl $dst | Out-Null
    Write-Ok ("сохранено: {0} ({1:N1} МБ)" -f $dst, ((Get-Item -LiteralPath $dst).Length / 1MB))

    $hook = 'cmd /c packsync\sync.cmd'
    Write-Step 'Кладу строку hook''а в буфер обмена'
    try {
        Set-Clipboard -Value $hook
        Write-Ok "в буфере: $hook"
    } catch {
        Write-Warn2 "не удалось положить в буфер обмена. Строка: $hook"
    }

    Write-Step "Запускаю $($def.Product) с файлом пака (auto-import)"
    Start-Process -FilePath $exe -ArgumentList @("`"$dst`"")

    Write-Host ''
    Write-Host '  Осталось 4 действия (один раз):' -ForegroundColor Cyan
    Write-Host "    1. Дождитесь окончания импорта профиля в $($def.Product)" -ForegroundColor White
    Write-Host '    2. Откройте настройки профиля: Options' -ForegroundColor White
    Write-Host '    3. Раздел Hooks -> поле Pre-launch -> вставьте из буфера (Ctrl+V)' -ForegroundColor White
    Write-Host "       должно получиться ровно: $hook" -ForegroundColor DarkGray
    Write-Host '    4. Сохраните и запустите профиль' -ForegroundColor White
    Write-Host ''
    Write-Host '  Почему так: AstralRinth выполняет hook без shell, режет строку по пробелам' -ForegroundColor DarkGray
    Write-Host '  и не подставляет переменные, поэтому кавычки и $INST_DIR там не работают.' -ForegroundColor DarkGray
    Write-Host '  Вся логика (поиск Java, адрес пака) спрятана в packsync\sync.cmd.' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host "  База данных лаунчера ($($def.DataDir)\app.db) намеренно НЕ изменяется." -ForegroundColor DarkGray
    return $true
}

# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #

Write-Title 'Установщик модпака'
Write-Info "адрес пака: $BaseUrl"

if ($BaseUrl -like '*@@BASE_URL@@*') {
    Write-Bad 'BaseUrl не задан. Запустите скрипт с GitHub Pages или передайте -BaseUrl явно:'
    Write-Host '        .\install.ps1 -BaseUrl https://<user>.github.io/<repo>' -ForegroundColor White
    exit 1
}

Write-Step 'Ищу установленные лаунчеры'
$installed = @(Get-InstalledLaunchers)
if ($installed.Count -eq 0) {
    Write-Warn2 'ни один известный лаунчер не найден'
} else {
    foreach ($i in $installed) { Write-Ok ("{0,-18} {1}" -f $i.Def.Product, $i.Exe) }
}

# --- выбор лаунчера ---
$target = $null
if ($Launcher -ne 'auto') {
    $target = $installed | Where-Object { $_.Def.Key -eq $Launcher } | Select-Object -First 1
    if (-not $target) { Write-Bad "лаунчер '$Launcher' не найден в системе"; }
} else {
    #auto: предпочитаем prism-семейство (там полностью автоматически)
    foreach ($pref in @('freesm', 'prism', 'multimc', 'astralrinth', 'modrinth')) {
        $target = $installed | Where-Object { $_.Def.Key -eq $pref } | Select-Object -First 1
        if ($target) { break }
    }
}

# --- если ничего нет: ставим Freesm ---
if (-not $target) {
    if ($WithLauncher) {
        try {
            $exe = Install-Freesm
            $def = $LAUNCHERS | Where-Object { $_.Key -eq 'freesm' }
            $target = [pscustomobject]@{ Def = $def; Exe = $exe }
        } catch {
            Write-Bad "не удалось установить Freesm Launcher: $($_.Exception.Message)"
        }
    }
    if (-not $target) {
        Write-Host ''
        Write-Host '  Сначала нужен лаунчер. Рекомендуемый — Freesm Launcher (бесплатный,' -ForegroundColor Cyan
        Write-Host '  оффлайн-аккаунты, полная поддержка нашего авто-синка):' -ForegroundColor Cyan
        Write-Host '      https://freesmlauncher.org/' -ForegroundColor White
        Write-Host ''
        Write-Host '  Затем перезапустите установщик. Или поставьте лаунчер автоматически:' -ForegroundColor Cyan
        Write-Host '      irm <адрес>/install.ps1 -WithLauncher | iex' -ForegroundColor White
        Write-Host ''
        exit 1
    }
}

Write-Step "Выбран лаунчер: $($target.Def.Product)"

if ($target.Def.Family -eq 'prism') {
    Install-ViaPrism $target.Exe $target.Def.Product | Out-Null
} else {
    Install-ViaTheseus $target | Out-Null
}

Write-Title 'Готово'
Write-Host '  Дальше моды будут обновляться САМИ при каждом запуске игры:' -ForegroundColor Green
Write-Host "  вы пушите изменения в git -> $BaseUrl/pack.toml -> лаунчер докачивает разницу." -ForegroundColor DarkGray
Write-Host ''
Write-Host '  Проверить, что синк работает: в папке игры должен появиться packwiz.json' -ForegroundColor DarkGray
Write-Host '  и строки [packsync] в консоли лаунчера.' -ForegroundColor DarkGray
Write-Host ''
