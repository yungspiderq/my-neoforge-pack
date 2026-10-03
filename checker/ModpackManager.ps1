<#
.SYNOPSIS
    Modpack Manager — окно для проверки и починки модпака.

.DESCRIPTION
    Что умеет:
      • выбрать папку сборки вручную или найти её автоматически
        (AstralRinth, Modrinth App, Freesm, Prism, MultiMC, .minecraft)
      • сверить с сервером ВСЁ содержимое пака по категориям:
        моды / конфиги / ресурспаки / шейдеры / прочее
      • проверить каждый файл ПО ХЭШУ — ловит «файл есть, но битый или старый»
      • ПОЧИНИТЬ: докачать отсутствующее и заменить несовпавшее
        собственным загрузчиком на PowerShell. Java для этого НЕ нужна —
        в отличие от packwiz-installer, которого дёргал предыдущий вариант.
      • найти и (по желанию) удалить лишние файлы, которых нет в паке
      • помнить последнюю папку и адрес пака между запусками

    Игру не запускает и аккаунты не трогает — это инструмент обслуживания сборки.

.NOTES
    Чистый PowerShell 5.1 + WinForms. Никаких зависимостей ставить не нужно.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -STA -File ModpackManager.ps1
    powershell -ExecutionPolicy Bypass -STA -File ModpackManager.ps1 -GameDir "C:\...\profiles\MyPack"
    powershell -ExecutionPolicy Bypass -STA -File ModpackManager.ps1 -Side server
#>

[CmdletBinding()]
param(
    [string] $GameDir = '',
    [string] $BaseUrl = '',
    [ValidateSet('client', 'server', 'both')]
    [string] $Side = 'client'
)

$ErrorActionPreference = 'Stop'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$script:APP_NAME    = 'Modpack Manager'
$script:APP_VERSION = '2.0.0'
$script:SETTINGS_DIR  = Join-Path $env:LOCALAPPDATA 'ModpackManager'
$script:SETTINGS_FILE = Join-Path $script:SETTINGS_DIR 'settings.json'
$script:FALLBACK_BASE = 'https://yungspiderq.github.io/my-neoforge-pack'

$script:Model   = $null    # что требует пак
$script:State   = @()      # сверка с диском
$script:Recent  = @()      # недавние папки сборки
$script:Notes   = @()
$script:CurDir  = $GameDir
$script:CurBase = $BaseUrl

# --------------------------------------------------------------------------- #
#  Настройки (помнить последнюю папку)
# --------------------------------------------------------------------------- #

function Load-Settings {
    $d = @{ GameDir = ''; BaseUrl = ''; Side = 'client'; Recent = @() }
    try {
        if (Test-Path -LiteralPath $script:SETTINGS_FILE) {
            $j = Get-Content -LiteralPath $script:SETTINGS_FILE -Raw | ConvertFrom-Json
            if ($j.GameDir) { $d.GameDir = $j.GameDir }
            if ($j.BaseUrl) { $d.BaseUrl = $j.BaseUrl }
            if ($j.Side)    { $d.Side    = $j.Side }
            if ($j.Recent)  { $d.Recent  = @($j.Recent) }
        }
    } catch {}
    return $d
}

function Save-Settings {
    try {
        if (-not (Test-Path -LiteralPath $script:SETTINGS_DIR)) {
            New-Item -ItemType Directory -Path $script:SETTINGS_DIR -Force | Out-Null
        }
        [pscustomobject]@{
            GameDir = $script:CurDir
            BaseUrl = $script:CurBase
            Side    = $cmbSide.SelectedItem
            Recent  = @($script:Recent | Select-Object -First 8)
        } | ConvertTo-Json | Set-Content -LiteralPath $script:SETTINGS_FILE -Encoding UTF8
    } catch {}
}

# --------------------------------------------------------------------------- #
#  Мини-парсер TOML
# --------------------------------------------------------------------------- #

function ConvertFrom-SimpleToml([string]$Text) {
    $root = @{}
    $cur = $root
    $arrays = @{}
    foreach ($raw in ($Text -split "`r?`n")) {
        $line = $raw.Trim()
        if ($line -eq '' -or $line.StartsWith('#')) { continue }
        if ($line -match '^\[\[(.+)\]\]$') {
            $name = $Matches[1].Trim()
            if (-not $arrays.ContainsKey($name)) { $arrays[$name] = New-Object System.Collections.ArrayList }
            $h = @{}
            [void]$arrays[$name].Add($h)
            $cur = $h
            continue
        }
        if ($line -match '^\[(.+)\]$') {
            $cur = $root
            foreach ($part in ($Matches[1].Trim() -split '\.')) {
                $k = $part.Trim()
                if (-not $cur.ContainsKey($k)) { $cur[$k] = @{} }
                $cur = $cur[$k]
            }
            continue
        }
        if ($line -match '^([A-Za-z0-9_\-]+)\s*=\s*(.*)$') {
            $k = $Matches[1]; $v = $Matches[2].Trim()
            if ($v.StartsWith('[')) {
                $items = @()
                foreach ($i in ($v.Trim('[', ']') -split ',')) {
                    $t = $i.Trim().Trim('"')
                    if ($t -ne '') { $items += $t }
                }
                $cur[$k] = $items
            } elseif ($v.StartsWith('"')) { $cur[$k] = $v.Trim('"') }
            elseif ($v -eq 'true')  { $cur[$k] = $true }
            elseif ($v -eq 'false') { $cur[$k] = $false }
            else { $cur[$k] = $v }
        }
    }
    foreach ($k in $arrays.Keys) { $root[$k] = $arrays[$k] }
    return $root
}

# --------------------------------------------------------------------------- #
#  HTTP
# --------------------------------------------------------------------------- #

function Get-RemoteText([string]$Url) {
    return (Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 60).Content
}

function Get-HashAlg([string]$Fmt) {
    switch (($Fmt + '').ToLower()) {
        'sha256' { return 'SHA256' }
        'sha512' { return 'SHA512' }
        'md5'    { return 'MD5' }
        default  { return 'SHA1' }
    }
}

function Get-FileHashOf([string]$Path, [string]$Fmt) {
    try { return (Get-FileHash -LiteralPath $Path -Algorithm (Get-HashAlg $Fmt)).Hash.ToLower() }
    catch { return '' }
}

function Write-Log([string]$Msg, [string]$Level = 'info') {
    $ts = (Get-Date).ToString('HH:mm:ss')
    $line = "[$ts] $Msg"
    if ($Log) {
        $Log.AppendText($line + "`r`n")
        if ($Log.TextLength -gt 200000) { $Log.Clear(); $Log.AppendText($line + "`r`n") }
    }
}

function Set-Status([string]$Msg) { if ($StatusLbl) { $StatusLbl.Text = $Msg } }
function Set-Progress([int]$Pct, [string]$Msg) {
    if ($Progress) {
        if ($Pct -lt 0) { $Progress.Style = 'Marquee'; $Progress.Value = 0 }
        else { $Progress.Style = 'Continuous'; $Progress.Value = [Math]::Max(0, [Math]::Min(100, $Pct)) }
    }
    if ($Msg) { Set-Status $Msg }
    [System.Windows.Forms.Application]::DoEvents()
}

# --------------------------------------------------------------------------- #
#  Поиск папок сборки
# --------------------------------------------------------------------------- #

function Get-PrismGameDir([string]$inst) {
    foreach ($sub in @('.minecraft', 'minecraft')) {
        $p = Join-Path $inst $sub
        if (Test-Path -LiteralPath $p) { return $p }
    }
    return $inst
}

function Find-GameDirs {
    $out = New-Object System.Collections.ArrayList
    $roots = @(
        @{ L = 'AstralRinth';  B = "$env:APPDATA\AstralRinthApp\profiles" },
        @{ L = 'Modrinth App'; B = "$env:APPDATA\ModrinthApp\profiles" },
        @{ L = 'Freesm';       B = "$env:APPDATA\FreesmLauncher\instances" },
        @{ L = 'Freesm';       B = "$env:LOCALAPPDATA\FreesmLauncher\instances" },
        @{ L = 'Prism';        B = "$env:APPDATA\PrismLauncher\instances" },
        @{ L = 'Prism';        B = "$env:LOCALAPPDATA\PrismLauncher\instances" },
        @{ L = 'MultiMC';      B = "$env:APPDATA\MultiMC\instances" },
        @{ L = 'MultiMC';      B = 'C:\MultiMC\instances' }
    )
    $seen = @{}
    foreach ($r in $roots) {
        if (-not (Test-Path -LiteralPath $r.B)) { continue }
        foreach ($d in (Get-ChildItem -LiteralPath $r.B -Directory -ErrorAction SilentlyContinue)) {
            $gd = Get-PrismGameDir $d.FullName
            if ($seen.ContainsKey($gd.ToLower())) { continue }
            $seen[$gd.ToLower()] = $true
            $hasPack = Test-Path -LiteralPath (Join-Path $gd 'packsync')
            $hasMods = Test-Path -LiteralPath (Join-Path $gd 'mods')
            $tag = if ($hasPack) { '' } elseif ($hasMods) { ' — нет packsync' } else { ' — пустой инстанс' }
            [void]$out.Add([pscustomobject]@{
                Label = '{0}: {1}{2}' -f $r.L, $d.Name, $tag
                Path  = $gd
                HasPack = $hasPack
            })
        }
    }
    if (Test-Path -LiteralPath "$env:APPDATA\.minecraft") {
        $gd = "$env:APPDATA\.minecraft"
        if (-not $seen.ContainsKey($gd.ToLower())) {
            $hasPack = Test-Path -LiteralPath (Join-Path $gd 'packsync')
            [void]$out.Add([pscustomobject]@{
                Label = 'Vanilla: .minecraft{0}' -f $(if ($hasPack) { '' } else { ' — нет packsync' })
                Path = $gd; HasPack = $hasPack
            })
        }
    }
    # сортируем: сначала те, где packsync уже есть
    return @($out | Sort-Object @{ Expression = { -not $_.HasPack } }, Label)
}

# --------------------------------------------------------------------------- #
#  Модель пака (что должно быть)
# --------------------------------------------------------------------------- #

function Resolve-BaseUrl([string]$Gd) {
    if ($script:CurBase) { return $script:CurBase }
    if ($Gd) {
        $f = Join-Path $Gd 'packsync\pack-url.txt'
        if (Test-Path -LiteralPath $f) {
            $u = (Get-Content -LiteralPath $f -TotalCount 1).Trim()
            if ($u) { return ($u -replace '/pack\.toml$', '') }
        }
    }
    return $script:FALLBACK_BASE
}

function Load-PackModel([string]$Base) {
    Set-Progress -1 "Читаю $Base/pack.toml"
    $pack = ConvertFrom-SimpleToml (Get-RemoteText "$Base/pack.toml")

    $idxFile = if ($pack.index.file) { $pack.index.file } else { 'index.toml' }
    Set-Progress -1 "Читаю $idxFile"
    $idxRaw = Get-RemoteText "$Base/$idxFile"

    $integrity = 'не задан'
    if ($pack.index.hash) {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $actual = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($idxRaw))) -replace '-', '').ToLower()
        $integrity = if ($actual -eq $pack.index.hash.ToLower()) { 'OK' } else { 'РАССИНХРОН' }
    }
    $idx = ConvertFrom-SimpleToml $idxRaw

    $ldr = ''; $ldrVer = ''
    foreach ($k in @('neoforge', 'forge', 'fabric', 'quilt')) {
        if ($pack.versions.$k) { $ldr = $k; $ldrVer = $pack.versions.$k }
    }

    $items = New-Object System.Collections.ArrayList
    # ВАЖНО: @($null) дало бы массив из одного $null, поэтому фильтруем.
    # На пустом паке (index.toml без [[files]]) это единственная защита.
    $files = @($idx.files | Where-Object { $_ })
    $n = 0
    foreach ($e in $files) {
        $n++
        Set-Progress ([int](40 * $n / [Math]::Max(1, $files.Count))) "Разбираю метаданные: $n / $($files.Count)"
        $rel = $e.file
        if (-not $rel) { continue }
        if ($rel -like '*.pw.toml') {
            try { $m = ConvertFrom-SimpleToml (Get-RemoteText "$Base/$rel") } catch { continue }
            $destRel = 'mods/' + $m.filename
            # .pw.toml может лежать не в mods/ — тогда файл кладётся рядом с метаданными
            $dir = [System.IO.Path]::GetDirectoryName($rel) -replace '\\', '/'
            if ($dir -and $dir -ne '.') { $destRel = "$dir/$($m.filename)" }
            [void]$items.Add([pscustomobject]@{
                Kind = 'mod'; Category = 'Моды'; Name = $m.name
                Rel = $rel; DestRel = $destRel
                Url = $m.download.url; Hash = $m.download.hash
                HashFmt = $(if ($m.download.'hash-format') { $m.download.'hash-format' } else { 'sha1' })
                Side = $(if ($m.side) { $m.side } else { 'both' })
                Preserve = $false
            })
        } else {
            $cat = 'Прочее'
            $first = ($rel -split '/')[0].ToLower()
            switch -Regex ($first) {
                '^config$|^defaultconfigs$|^kubejs$' { $cat = 'Конфиги'; break }
                '^resourcepacks$'                    { $cat = 'Ресурспаки'; break }
                '^shaderpacks$'                      { $cat = 'Шейдеры'; break }
                default                              { $cat = 'Прочее'; break }
            }
            [void]$items.Add([pscustomobject]@{
                Kind = 'file'; Category = $cat; Name = $rel
                Rel = $rel; DestRel = $rel
                Url = "$Base/$rel"; Hash = $e.hash
                HashFmt = $(if ($e.'hash-format') { $e.'hash-format' } else { 'sha256' })
                Side = 'both'; Preserve = [bool]$e.preserve
            })
        }
    }

    return [pscustomobject]@{
        Base = $Base; Name = $pack.name; Version = $pack.version
        MC = $pack.versions.minecraft; Loader = $ldr; LoaderVersion = $ldrVer
        Integrity = $integrity; Items = $items
    }
}

# --------------------------------------------------------------------------- #
#  Сверка с диском
# --------------------------------------------------------------------------- #

function Test-LocalState([string]$Gd) {
    $side = $cmbSide.SelectedItem
    $res = New-Object System.Collections.ArrayList
    $all = @($script:Model.Items)
    $n = 0
    foreach ($it in $all) {
        $n++
        Set-Progress ([int](100 * $n / [Math]::Max(1, $all.Count))) "Сверяю с диском: $n / $($all.Count)"
        $rel = $it.DestRel -replace '/', '\'
        $path = Join-Path $Gd $rel

        $row = [pscustomobject]@{
            Item = $it; Name = $it.Name; Category = $it.Category
            DestRel = $it.DestRel; Path = $path
            Status = ''; Detail = ''; Size = 0; Actionable = $false
        }

        if ($side -ne 'both' -and $it.Side -ne 'both' -and $it.Side -ne $side) {
            $row.Status = 'ДРУГАЯ СТОРОНА'; $row.Detail = "side=$($it.Side), выбран $side"
            [void]$res.Add($row); continue
        }

        if (-not (Test-Path -LiteralPath $path)) {
            if (Test-Path -LiteralPath ($path + '.disabled')) {
                $row.Status = 'ОТКЛЮЧЁН'; $row.Detail = 'лежит как .disabled'
            } elseif ($it.Preserve) {
                $row.Status = 'НЕТ (preserve)'; $row.Detail = 'файл не перезаписывается намеренно'
            } else {
                $row.Status = 'ОТСУТСТВУЕТ'; $row.Detail = 'нужно скачать'
                $row.Actionable = $true
            }
            [void]$res.Add($row); continue
        }

        $fi = Get-Item -LiteralPath $path
        $row.Size = $fi.Length
        $h = Get-FileHashOf $path $it.HashFmt
        if ($it.Hash -and $h -and ($h -ne $it.Hash.ToLower())) {
            $row.Status = 'НЕ СОВПАДАЕТ'
            $row.Detail = '{0}: ждём {1}…, файл {2}…' -f $it.HashFmt, $it.Hash.Substring(0, [Math]::Min(10, $it.Hash.Length)), $h.Substring(0, [Math]::Min(10, $h.Length))
            $row.Actionable = $true
        } else {
            $row.Status = 'НА МЕСТЕ'
            $row.Detail = '{0} верен, {1} МБ' -f $it.HashFmt, [math]::Round($fi.Length / 1MB, 2)
        }
        [void]$res.Add($row)
    }

    # лишние файлы
    $expected = @{}
    foreach ($it in $all) { $expected[($it.DestRel -replace '/', '\').ToLower()] = $true }
    foreach ($sub in @('mods', 'config', 'resourcepacks', 'shaderpacks')) {
        $d = Join-Path $Gd $sub
        if (-not (Test-Path -LiteralPath $d)) { continue }
        foreach ($f in (Get-ChildItem -LiteralPath $d -File -ErrorAction SilentlyContinue)) {
            $rel = ($sub + '\' + $f.Name).ToLower()
            if ($expected.ContainsKey($rel)) { continue }
            # файл вида <ожидаемый>.disabled — это отключённый мод из пака,
            # а не мусор: player сам его выключил, синхронизатор такие не трогает
            $isDisabledOfExpected = $false
            foreach ($k in $expected.Keys) { if (($k + '.disabled') -eq $rel) { $isDisabledOfExpected = $true } }
            if ($isDisabledOfExpected) { continue }
            [void]$res.Add([pscustomobject]@{
                Item = $null; Name = $f.Name; Category = 'Лишние'
                DestRel = "$sub/$($f.Name)"; Path = $f.FullName
                Status = 'ЛИШНИЙ'; Detail = '{0} МБ, в паке не значится' -f [math]::Round($f.Length / 1MB, 2)
                Size = $f.Length; Actionable = $true
            })
        }
    }

    # служебные признаки
    $notes = @()
    $pwj = Join-Path $Gd 'packwiz.json'
    if (Test-Path -LiteralPath $pwj) {
        $age = [math]::Round(((Get-Date) - (Get-Item -LiteralPath $pwj).LastWriteTime).TotalMinutes)
        $notes += "packwiz.json есть, обновлён $age мин назад — packwiz-installer отрабатывал"
    } else {
        $notes += 'packwiz.json НЕТ — packwiz-installer ни разу не отработал (hook не прописан?)'
    }
    $sl = Join-Path $Gd 'packsync\sync.log'
    if (Test-Path -LiteralPath $sl) {
        $notes += "packsync/sync.log: изменён $((Get-Item -LiteralPath $sl).LastWriteTime)"
    } else {
        $notes += 'packsync/sync.log нет — hook, скорее всего, не запускался'
    }
    $script:Notes = $notes
    return $res
}

# --------------------------------------------------------------------------- #
#  Собственный загрузчик (без Java)
# --------------------------------------------------------------------------- #

function Invoke-Sync {
    param([object[]]$Rows)

    $todo = @($Rows | Where-Object { $_.Actionable -and $_.Status -ne 'ЛИШНИЙ' })
    if ($todo.Count -eq 0) {
        [void][System.Windows.Forms.MessageBox]::Show(
            'Чинить нечего: все файлы на месте и хэши сходятся.',
            $script:APP_NAME, 'OK', 'Information')
        return
    }

    $mb = [System.Windows.Forms.MessageBox]::Show(
        "Будет скачано/заменено файлов: $($todo.Count)`r`n`r`nПапка: $($script:CurDir)`r`nИсточник: $($script:Model.Base)`r`n`r`nПродолжить?",
        $script:APP_NAME, 'YesNo', 'Question')
    if ($mb -ne 'Yes') { return }

    $bak = Join-Path $script:CurDir '.modpack-backup'
    $done = 0; $fail = 0; $bytes = 0
    $n = 0
    foreach ($r in $todo) {
        $n++
        Set-Progress ([int](100 * $n / $todo.Count)) "Скачиваю $($n)/$($todo.Count): $($r.Name)"
        $dest = $r.Path
        try {
            $dir = Split-Path $dest -Parent
            if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

            # бэкап заменяемого файла
            if (Test-Path -LiteralPath $dest) {
                if (-not (Test-Path -LiteralPath $bak)) { New-Item -ItemType Directory -Path $bak -Force | Out-Null }
                $rel = $r.DestRel -replace '/', '\'
                $bp = Join-Path $bak ($rel -replace '[:\\]', '_')
                try { Copy-Item -LiteralPath $dest -Destination $bp -Force } catch {}
            }

            $tmp = "$dest.download"
            Invoke-WebRequest -Uri $r.Item.Url -UseBasicParsing -OutFile $tmp -TimeoutSec 600
            $h = Get-FileHashOf $tmp $r.Item.HashFmt
            if ($r.Item.Hash -and $h -and ($h -ne $r.Item.Hash.ToLower())) {
                Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
                throw 'хэш скачанного файла не совпал (ждём {0}, получили {1})' -f $r.Item.Hash.Substring(0,10), $h.Substring(0,10)
            }
            Move-Item -LiteralPath $tmp -Destination $dest -Force
            $bytes += (Get-Item -LiteralPath $dest).Length
            $done++
            Write-Log "скачан $($r.DestRel)"
        } catch {
            $fail++
            Write-Log "ОШИБКА $($r.DestRel): $($_.Exception.Message)" 'error'
        }
    }
    Set-Progress 100 ('Готово: {0} скачано, {1} ошибок, {2} МБ' -f $done, $fail, [math]::Round($bytes / 1MB, 1))
    Write-Log ("синхронизация: {0} скачано, {1} ошибок, {2} МБ" -f $done, $fail, [math]::Round($bytes / 1MB, 1))
    if ($fail -gt 0) {
        [void][System.Windows.Forms.MessageBox]::Show(
            "Скачано: $done`r`nС ошибками: $fail`r`n`r`nПодробности во вкладке «Журнал».",
            $script:APP_NAME, 'OK', 'Warning')
    }
    Invoke-Refresh -Silent
}

function Remove-Extras {
    $rows = @($script:State | Where-Object { $_.Status -eq 'ЛИШНИЙ' })
    if ($rows.Count -eq 0) {
        [void][System.Windows.Forms.MessageBox]::Show('Лишних файлов нет.', $script:APP_NAME, 'OK', 'Information')
        return
    }
    $list = ($rows | ForEach-Object { $_.DestRel }) -join "`r`n"
    $mb = [System.Windows.Forms.MessageBox]::Show(
        "Удалить файлов, которых нет в паке: $($rows.Count)?`r`n`r`n$list`r`n`r`nФайлы будут перемещены в .modpack-backup, а не удалены навсегда.",
        $script:APP_NAME, 'YesNo', 'Warning')
    if ($mb -ne 'Yes') { return }
    $bak = Join-Path $script:CurDir '.modpack-backup'
    if (-not (Test-Path -LiteralPath $bak)) { New-Item -ItemType Directory -Path $bak -Force | Out-Null }
    foreach ($r in $rows) {
        try {
            $bp = Join-Path $bak (($r.DestRel -replace '/', '\') -replace '[:\\]', '_')
            Move-Item -LiteralPath $r.Path -Destination $bp -Force
            Write-Log "убран лишний: $($r.DestRel)"
        } catch { Write-Log "не удалось убрать $($r.DestRel): $($_.Exception.Message)" 'error' }
    }
    Invoke-Refresh -Silent
}

# --------------------------------------------------------------------------- #
#  Отрисовка таблицы
# --------------------------------------------------------------------------- #

$COLORS = @{
    'НА МЕСТЕ'        = [System.Drawing.Color]::FromArgb(0, 128, 0)
    'ОТСУТСТВУЕТ'     = [System.Drawing.Color]::Red
    'НЕ СОВПАДАЕТ'    = [System.Drawing.Color]::Red
    'ОТКЛЮЧЁН'        = [System.Drawing.Color]::DarkOrange
    'НЕТ (preserve)'  = [System.Drawing.Color]::Gray
    'ДРУГАЯ СТОРОНА'  = [System.Drawing.Color]::Gray
    'ЛИШНИЙ'          = [System.Drawing.Color]::FromArgb(150, 90, 0)
}

function Show-Rows {
    foreach ($lv in @($lvMods, $lvFiles, $lvExtra)) {
        $lv.BeginUpdate()
        $lv.Items.Clear()
    }
    $counts = @{}
    foreach ($r in $script:State) {
        $lv = switch ($r.Category) {
            'Моды'   { $lvMods; break }
            'Лишние' { $lvExtra; break }
            default  { $lvFiles; break }
        }
        $it = New-Object System.Windows.Forms.ListViewItem($r.Name)
        [void]$it.SubItems.Add($r.DestRel)
        [void]$it.SubItems.Add($r.Status)
        [void]$it.SubItems.Add($r.Detail)
        if ($COLORS.ContainsKey($r.Status)) { $it.ForeColor = $COLORS[$r.Status] }
        $it.Tag = $r
        [void]$lv.Items.Add($it)
        $counts[$r.Status] = 1 + $(if ($counts.ContainsKey($r.Status)) { $counts[$r.Status] } else { 0 })
    }
    foreach ($lv in @($lvMods, $lvFiles, $lvExtra)) { $lv.EndUpdate() }

    $tabMods.Text  = 'Моды ({0})'            -f $lvMods.Items.Count
    $tabFiles.Text = 'Конфиги и файлы ({0})' -f $lvFiles.Items.Count
    $tabExtra.Text = 'Лишние ({0})'          -f $lvExtra.Items.Count

    $bad = 0; foreach ($k in @('ОТСУТСТВУЕТ', 'НЕ СОВПАДАЕТ')) { if ($counts.ContainsKey($k)) { $bad += $counts[$k] } }
    $good = $(if ($counts.ContainsKey('НА МЕСТЕ')) { $counts['НА МЕСТЕ'] } else { 0 })
    if ($bad -eq 0 -and $good -gt 0) {
        Set-Status ('Всё в порядке: {0} файлов на месте, хэши сходятся' -f $good)
        $StatusLbl.ForeColor = $COLORS['НА МЕСТЕ']
    } elseif ($bad -gt 0) {
        Set-Status ('Требуется починка: {0} файлов не в порядке, {1} на месте' -f $bad, $good)
        $StatusLbl.ForeColor = [System.Drawing.Color]::Red
    } else {
        Set-Status 'Нет данных'
        $StatusLbl.ForeColor = [System.Drawing.Color]::Gray
    }
}

# --------------------------------------------------------------------------- #
#  Форма
# --------------------------------------------------------------------------- #

$form = New-Object System.Windows.Forms.Form
$form.Text = $script:APP_NAME
$form.Size = New-Object System.Drawing.Size(1180, 760)
$form.MinimumSize = New-Object System.Drawing.Size(900, 560)
$form.StartPosition = 'CenterScreen'
$form.Font = New-Object System.Drawing.Font('Segoe UI', 9)

# Корневой контейнер: меню сверху, дальше панель выбора, вкладки, статус-бар.
# TableLayoutPanel вместо свободного Dock — иначе порядок докинга зависит от
# z-order (индекса в Controls), и статус-бар остаётся без места.
$root = New-Object System.Windows.Forms.TableLayoutPanel
$root.Dock = 'Fill'
$root.ColumnCount = 1
$root.RowCount = 3
$root.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle('Percent', 100)))
$root.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Absolute', 96)))
$root.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Percent', 100)))
$root.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Absolute', 24)))
$form.Controls.Add($root)

function New-LV {
    param([string[]]$Cols, [int[]]$W)
    $lv = New-Object System.Windows.Forms.ListView
    $lv.View = 'Details'; $lv.FullRowSelect = $true; $lv.GridLines = $true
    $lv.Dock = 'Fill'; $lv.HideSelection = $false
    $lv.MultiSelect = $true
    for ($i = 0; $i -lt $Cols.Count; $i++) { [void]$lv.Columns.Add($Cols[$i], $W[$i]) }
    return $lv
}

# --- меню ---
$menu = New-Object System.Windows.Forms.MenuStrip

$mFile = New-Object System.Windows.Forms.ToolStripMenuItem('&Файл')
$miOpen  = New-Object System.Windows.Forms.ToolStripMenuItem('Выбрать папку сборки…')
$miRecent= New-Object System.Windows.Forms.ToolStripMenuItem('Недавние')
$miSave  = New-Object System.Windows.Forms.ToolStripMenuItem('Сохранить отчёт…')
$miExit  = New-Object System.Windows.Forms.ToolStripMenuItem('Выход')
[void]$mFile.DropDownItems.AddRange(@($miOpen, $miRecent, (New-Object System.Windows.Forms.ToolStripSeparator), $miSave, (New-Object System.Windows.Forms.ToolStripSeparator), $miExit))

$mCheck = New-Object System.Windows.Forms.ToolStripMenuItem('&Проверка')
$miCheck = New-Object System.Windows.Forms.ToolStripMenuItem('Проверить сейчас')
$miCheckAll = New-Object System.Windows.Forms.ToolStripMenuItem('Проверить, игнорируя сторону (both)')
[void]$mCheck.DropDownItems.AddRange(@($miCheck, $miCheckAll))

$mSync = New-Object System.Windows.Forms.ToolStripMenuItem('&Синхронизация')
$miFix   = New-Object System.Windows.Forms.ToolStripMenuItem('Починить всё (скачать недостающее и несовпавшее)')
$miFixSel= New-Object System.Windows.Forms.ToolStripMenuItem('Починить только выбранное')
$miExtra = New-Object System.Windows.Forms.ToolStripMenuItem('Убрать лишние файлы…')
$miLegacy= New-Object System.Windows.Forms.ToolStripMenuItem('Запустить packwiz-installer (через Java)…')
[void]$mSync.DropDownItems.AddRange(@($miFix, $miFixSel, (New-Object System.Windows.Forms.ToolStripSeparator), $miExtra, (New-Object System.Windows.Forms.ToolStripSeparator), $miLegacy))

$mTools = New-Object System.Windows.Forms.ToolStripMenuItem('&Инструменты')
$miMods  = New-Object System.Windows.Forms.ToolStripMenuItem('Открыть папку mods/')
$miConf  = New-Object System.Windows.Forms.ToolStripMenuItem('Открыть папку config/')
$miGame  = New-Object System.Windows.Forms.ToolStripMenuItem('Открыть папку сборки')
$miLog   = New-Object System.Windows.Forms.ToolStripMenuItem('Открыть packsync/sync.log')
$miGui   = New-Object System.Windows.Forms.ToolStripMenuItem('Показывать окно прогресса при запуске игры (SHOW_GUI)')
$miBak   = New-Object System.Windows.Forms.ToolStripMenuItem('Открыть папку бэкапов (.modpack-backup)')
[void]$mTools.DropDownItems.AddRange(@($miMods, $miConf, $miGame, $miLog, (New-Object System.Windows.Forms.ToolStripSeparator), $miGui, (New-Object System.Windows.Forms.ToolStripSeparator), $miBak))

$mHelp = New-Object System.Windows.Forms.ToolStripMenuItem('&Справка')
$miAbout = New-Object System.Windows.Forms.ToolStripMenuItem('О программе')
$miHow   = New-Object System.Windows.Forms.ToolStripMenuItem('Как это работает')
$miUrl   = New-Object System.Windows.Forms.ToolStripMenuItem('Показать адрес пака')
[void]$mHelp.DropDownItems.AddRange(@($miAbout, $miHow, (New-Object System.Windows.Forms.ToolStripSeparator), $miUrl))

[void]$menu.Items.AddRange(@($mFile, $mCheck, $mSync, $mTools, $mHelp))
$form.MainMenuStrip = $menu

# --- верхняя панель ---
$top = New-Object System.Windows.Forms.TableLayoutPanel
$top.Dock = 'Fill'; $top.ColumnCount = 1; $top.RowCount = 3
$top.Padding = New-Object System.Windows.Forms.Padding(8, 4, 8, 4)
$root.Controls.Add($top, 0, 0)

$row1 = New-Object System.Windows.Forms.Panel
$row1.Dock = 'Fill'; $row1.Height = 30
$r1lbl = New-Object System.Windows.Forms.Label
$r1lbl.Text = 'Папка сборки:'; $r1lbl.AutoSize = $false; $r1lbl.Size = New-Object System.Drawing.Size(96, 24)
$r1lbl.Location = New-Object System.Drawing.Point(0, 3)
$cmbDir = New-Object System.Windows.Forms.ComboBox
$cmbDir.Location = New-Object System.Drawing.Point(100, 0)
$cmbDir.Size = New-Object System.Drawing.Size(700, 24)
$cmbDir.Anchor = 'Top,Left,Right'
$cmbDir.DropDownStyle = 'DropDown'
$cmbDir.AutoCompleteMode = 'SuggestAppend'
$cmbDir.AutoCompleteSource = 'ListItems'
$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = 'Обзор…'; $btnBrowse.Location = New-Object System.Drawing.Point(806, 0); $btnBrowse.Size = New-Object System.Drawing.Size(84, 26)
$btnBrowse.Anchor = 'Top,Right'
$btnCheck2 = New-Object System.Windows.Forms.Button
$btnCheck2.Text = 'Проверить'; $btnCheck2.Location = New-Object System.Drawing.Point(896, 0); $btnCheck2.Size = New-Object System.Drawing.Size(110, 26)
$btnCheck2.Font = New-Object System.Drawing.Font('Segoe UI', 9, [System.Drawing.FontStyle]::Bold)
$btnCheck2.Anchor = 'Top,Right'
$btnFix2 = New-Object System.Windows.Forms.Button
$btnFix2.Text = 'Починить всё'; $btnFix2.Location = New-Object System.Drawing.Point(1012, 0); $btnFix2.Size = New-Object System.Drawing.Size(120, 26)
$btnFix2.Anchor = 'Top,Right'
foreach ($c in @($r1lbl, $cmbDir, $btnBrowse, $btnCheck2, $btnFix2)) { $row1.Controls.Add($c) }

$row2 = New-Object System.Windows.Forms.Panel
$row2.Dock = 'Fill'; $row2.Height = 30
$r2lbl = New-Object System.Windows.Forms.Label
$r2lbl.Text = 'Адрес пака:'; $r2lbl.AutoSize = $false; $r2lbl.Size = New-Object System.Drawing.Size(96, 24)
$r2lbl.Location = New-Object System.Drawing.Point(0, 3)
$txtBase = New-Object System.Windows.Forms.TextBox
$txtBase.Location = New-Object System.Drawing.Point(100, 0); $txtBase.Size = New-Object System.Drawing.Size(700, 24)
$txtBase.Anchor = 'Top,Left,Right'
$lblSide = New-Object System.Windows.Forms.Label
$lblSide.Text = 'Сторона:'; $lblSide.Anchor = 'Top,Right'
$lblSide.Location = New-Object System.Drawing.Point(806, 4); $lblSide.AutoSize = $false
$lblSide.Size = New-Object System.Drawing.Size(56, 20)
$cmbSide = New-Object System.Windows.Forms.ComboBox
$cmbSide.Anchor = 'Top,Right'
$cmbSide.Location = New-Object System.Drawing.Point(862, 0); $cmbSide.Size = New-Object System.Drawing.Size(90, 24)
$cmbSide.DropDownStyle = 'DropDownList'
[void]$cmbSide.Items.AddRange(@('client', 'server', 'both'))
$cmbSide.SelectedItem = $Side
$btnReload = New-Object System.Windows.Forms.Button
$btnReload.Text = 'Перечитать пак'; $btnReload.Anchor = 'Top,Right'
$btnReload.Location = New-Object System.Drawing.Point(958, 0); $btnReload.Size = New-Object System.Drawing.Size(174, 26)
foreach ($c in @($r2lbl, $txtBase, $lblSide, $cmbSide, $btnReload)) { $row2.Controls.Add($c) }

$lblInfo = New-Object System.Windows.Forms.Label
$lblInfo.Dock = 'Fill'; $lblInfo.Height = 26; $lblInfo.TextAlign = 'MiddleLeft'
$lblInfo.ForeColor = [System.Drawing.Color]::FromArgb(70, 70, 70)
$lblInfo.Text = 'Папка не выбрана'

[void]$top.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Absolute', 30)))
[void]$top.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Absolute', 30)))
[void]$top.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Absolute', 30)))
[void]$top.Controls.Add($row1, 0, 0)
[void]$top.Controls.Add($row2, 0, 1)
[void]$top.Controls.Add($lblInfo, 0, 2)

# --- вкладки ---
$tabs = New-Object System.Windows.Forms.TabControl
$tabs.Dock = 'Fill'
$root.Controls.Add($tabs, 0, 1)

$tabMods  = New-Object System.Windows.Forms.TabPage; $tabMods.Text = 'Моды'
$tabFiles = New-Object System.Windows.Forms.TabPage; $tabFiles.Text = 'Конфиги и файлы'
$tabExtra = New-Object System.Windows.Forms.TabPage; $tabExtra.Text = 'Лишние'
$tabLog   = New-Object System.Windows.Forms.TabPage; $tabLog.Text = 'Журнал'

$cols = @('Название', 'Файл в папке', 'Статус', 'Подробности')
$wid  = @(300, 330, 150, 340)
$lvMods  = New-LV $cols $wid
$lvFiles = New-LV $cols $wid
$lvExtra = New-LV $cols $wid
$tabMods.Controls.Add($lvMods)
$tabFiles.Controls.Add($lvFiles)
$tabExtra.Controls.Add($lvExtra)

$Log = New-Object System.Windows.Forms.TextBox
$Log.Multiline = $true; $Log.ReadOnly = $true; $Log.ScrollBars = 'Both'
$Log.WordWrap = $false; $Log.Dock = 'Fill'
$Log.Font = New-Object System.Drawing.Font('Consolas', 9)
$Log.BackColor = [System.Drawing.Color]::FromArgb(250, 250, 250)
$tabLog.Controls.Add($Log)

foreach ($t in @($tabMods, $tabFiles, $tabExtra, $tabLog)) { [void]$tabs.TabPages.Add($t) }

# --- статус-бар ---
$status = New-Object System.Windows.Forms.StatusStrip
$StatusLbl = New-Object System.Windows.Forms.ToolStripStatusLabel
$StatusLbl.Spring = $true; $StatusLbl.TextAlign = 'MiddleLeft'
$StatusLbl.Text = 'Готово'
$Progress = New-Object System.Windows.Forms.ToolStripProgressBar
$Progress.Size = New-Object System.Drawing.Size(220, 16)
$Progress.Style = 'Continuous'
[void]$status.Items.AddRange(@($StatusLbl, $Progress))
$root.Controls.Add($status, 0, 2)

# --------------------------------------------------------------------------- #
#  Действия
# --------------------------------------------------------------------------- #

function Selected-GameDir {
    $t = $cmbDir.Text
    if ($t -match '\|(.+)$') { return $Matches[1].Trim() }
    if ($t -and (Test-Path -LiteralPath $t)) { return $t.Trim() }
    return ''
}

function Add-Recent([string]$p) {
    if (-not $p) { return }
    $script:Recent = @(@($script:Recent | Where-Object { $_ -ne $p }) + $p)
    Rebuild-RecentMenu
}

function Rebuild-RecentMenu {
    $miRecent.DropDownItems.Clear()
    if (@($script:Recent).Count -eq 0) {
        $e = New-Object System.Windows.Forms.ToolStripMenuItem('(пусто)'); $e.Enabled = $false
        [void]$miRecent.DropDownItems.Add($e); return
    }
    foreach ($p in @($script:Recent | Select-Object -First 8)) {
        $e = New-Object System.Windows.Forms.ToolStripMenuItem($p)
        $e.Add_Click({ $cmbDir.Text = $this.Text; Invoke-Refresh }.GetNewClosure())
        [void]$miRecent.DropDownItems.Add($e)
    }
}

function Invoke-Refresh {
    param([switch]$Silent)

    $script:CurDir = Selected-GameDir
    if (-not $script:CurDir) {
        if (-not $Silent) {
            [void][System.Windows.Forms.MessageBox]::Show(
                'Выберите папку сборки (кнопка «Обзор…» или список).',
                $script:APP_NAME, 'OK', 'Information')
        }
        Set-Status 'Папка не выбрана'; return
    }
    if (-not (Test-Path -LiteralPath $script:CurDir)) {
        Set-Status 'Папка не существует'; Write-Log "папка не существует: $($script:CurDir)" 'error'; return
    }

    $script:CurBase = $txtBase.Text.Trim()
    if (-not $script:CurBase) { $script:CurBase = Resolve-BaseUrl $script:CurDir; $txtBase.Text = $script:CurBase }
    $script:CurBase = $script:CurBase -replace '/pack\.toml$', '' -replace '/+$', ''

    $form.Cursor = 'WaitCursor'
    try {
        Set-Progress -1 'Читаю пак с сервера…'
        $script:Model = Load-PackModel $script:CurBase
        Write-Log ("пак: {0} {1} | Minecraft {2} | {3} {4} | файлов в индексе: {5} | целостность index.toml: {6}" -f `
            $script:Model.Name, $script:Model.Version, $script:Model.MC, $script:Model.Loader, `
            $script:Model.LoaderVersion, @($script:Model.Items).Count, $script:Model.Integrity)
        $lblInfo.Text = ('{0} {1}   ·   Minecraft {2}   ·   {3} {4}   ·   файлов в паке: {5}   ·   целостность index.toml: {6}' -f `
            $script:Model.Name, $script:Model.Version, $script:Model.MC, $script:Model.Loader, `
            $script:Model.LoaderVersion, @($script:Model.Items).Count, $script:Model.Integrity)
        if ($script:Model.Integrity -eq 'РАССИНХРОН') {
            Write-Log 'ВНИМАНИЕ: sha256 index.toml не совпадает с pack.toml — пак на сервере рассинхронизирован' 'error'
        }

        Set-Progress -1 'Сверяю с диском…'
        $script:State = @(Test-LocalState $script:CurDir)
        Show-Rows
        foreach ($nt in $script:Notes) { Write-Log $nt }
        Add-Recent $script:CurDir
        Save-Settings
        Set-Progress 0 ''
        $Progress.Style = 'Continuous'; $Progress.Value = 0
    } catch {
        Write-Log "ОШИБКА: $($_.Exception.Message)" 'error'
        Set-Status ('Ошибка: ' + $_.Exception.Message)
        $StatusLbl.ForeColor = [System.Drawing.Color]::Red
        if (-not $Silent) {
            [void][System.Windows.Forms.MessageBox]::Show(
                $_.Exception.Message, $script:APP_NAME, 'OK', 'Error')
        }
    } finally {
        $form.Cursor = 'Default'
    }
}

function Get-SelectedRows {
    $out = New-Object System.Collections.ArrayList
    foreach ($lv in @($lvMods, $lvFiles, $lvExtra)) {
        foreach ($i in $lv.SelectedItems) { if ($i.Tag) { [void]$out.Add($i.Tag) } }
    }
    return @($out)
}

function Open-Path([string]$p) {
    if ($p -and (Test-Path -LiteralPath $p)) { Start-Process -FilePath $p }
    else { [void][System.Windows.Forms.MessageBox]::Show("Нет такого пути:`r`n$p", $script:APP_NAME, 'OK', 'Warning') }
}

function Pick-GameDir {
    $d = New-Object System.Windows.Forms.FolderBrowserDialog
    $d.Description = 'Папка сборки (профиль лаунчера или .minecraft)'
    $cur = Selected-GameDir
    if ($cur -and (Test-Path -LiteralPath $cur)) { $d.SelectedPath = $cur }
    if ($d.ShowDialog() -eq 'OK') {
        $cmbDir.Text = "(вручную)  |  $($d.SelectedPath)"
        Invoke-Refresh
    }
}

# --- привязка кнопок и меню ---
$btnBrowse.Add_Click({ Pick-GameDir })
$btnCheck2.Add_Click({ Invoke-Refresh })
$btnFix2.Add_Click({ if ($script:State) { Invoke-Sync -Rows $script:State } else { Invoke-Refresh } })
$btnReload.Add_Click({
    $script:CurBase = $txtBase.Text.Trim() -replace '/pack\.toml$', '' -replace '/+$', ''
    Invoke-Refresh
})
$cmbSide.Add_SelectedIndexChanged({ if ($script:Model) { Invoke-Refresh -Silent } })

$miOpen.Add_Click({ Pick-GameDir })
$miCheck.Add_Click({ Invoke-Refresh })
$miCheckAll.Add_Click({ $cmbSide.SelectedItem = 'both'; Invoke-Refresh })
$miFix.Add_Click({ if ($script:State) { Invoke-Sync -Rows $script:State } else { Invoke-Refresh } })
$miFixSel.Add_Click({
    $rows = Get-SelectedRows
    if ($rows.Count -eq 0) {
        [void][System.Windows.Forms.MessageBox]::Show('Выделите строки в таблице.', $script:APP_NAME, 'OK', 'Information'); return
    }
    Invoke-Sync -Rows $rows
})
$miExtra.Add_Click({ if ($script:State) { Remove-Extras } else { Invoke-Refresh } })
$miLegacy.Add_Click({
    $gd = Selected-GameDir
    if (-not $gd) { [void][System.Windows.Forms.MessageBox]::Show('Сначала выберите папку.', $script:APP_NAME, 'OK', 'Information'); return }
    $cmd = Join-Path $gd 'packsync\sync.cmd'
    if (-not (Test-Path -LiteralPath $cmd)) {
        [void][System.Windows.Forms.MessageBox]::Show("Нет $cmd`r`nЗначит packsync не установлен в эту папку.", $script:APP_NAME, 'OK', 'Warning'); return
    }
    Write-Log 'запускаю packsync\sync.cmd (нужна Java)'
    $out = & cmd.exe /c "`"$cmd`"" 2>&1 | Out-String
    $Log.AppendText($out)
    Invoke-Refresh -Silent
})
$miMods.Add_Click({ Open-Path (Join-Path (Selected-GameDir) 'mods') })
$miConf.Add_Click({ Open-Path (Join-Path (Selected-GameDir) 'config') })
$miGame.Add_Click({ Open-Path (Selected-GameDir) })
$miLog.Add_Click({
    $l = Join-Path (Selected-GameDir) 'packsync\sync.log'
    if (Test-Path -LiteralPath $l) { Start-Process notepad.exe -ArgumentList $l }
    else { [void][System.Windows.Forms.MessageBox]::Show("sync.log ещё нет:`r`n$l", $script:APP_NAME, 'OK', 'Information') }
})
$miBak.Add_Click({ Open-Path (Join-Path (Selected-GameDir) '.modpack-backup') })
$miGui.Add_Click({
    $gd = Selected-GameDir
    if (-not $gd) { [void][System.Windows.Forms.MessageBox]::Show('Сначала выберите папку.', $script:APP_NAME, 'OK', 'Information'); return }
    $f = Join-Path $gd 'packsync\SHOW_GUI'
    if (Test-Path -LiteralPath $f) {
        Remove-Item -LiteralPath $f -Force; $miGui.Checked = $false
        Write-Log 'SHOW_GUI удалён — синхронизация при запуске игры снова тихая'
    } else {
        New-Item -ItemType File -Path $f -Force | Out-Null; $miGui.Checked = $true
        Write-Log 'SHOW_GUI создан — при запуске игры откроется окно packwiz-installer с прогрессом'
    }
})
$miSave.Add_Click({
    $d = New-Object System.Windows.Forms.SaveFileDialog
    $d.Filter = 'Текст (*.txt)|*.txt|CSV (*.csv)|*.csv'
    $d.FileName = 'modpack-report.txt'
    if ($d.ShowDialog() -ne 'OK') { return }
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("$($script:APP_NAME) $script:APP_VERSION  —  $(Get-Date -Format s)")
    [void]$sb.AppendLine("Папка : $($script:CurDir)")
    [void]$sb.AppendLine("Адрес : $($script:CurBase)")
    if ($script:Model) {
        [void]$sb.AppendLine("Пак   : $($script:Model.Name) $($script:Model.Version) | MC $($script:Model.MC) | $($script:Model.Loader) $($script:Model.LoaderVersion)")
        [void]$sb.AppendLine("index.toml целостность: $($script:Model.Integrity)")
    }
    [void]$sb.AppendLine('')
    if ($d.FilterIndex -eq 2) {
        [void]$sb.AppendLine('Категория;Название;Файл;Статус;Подробности')
        foreach ($r in $script:State) {
            [void]$sb.AppendLine(('"{}";"{}";"{}";"{}";"{}"' -f $r.Category, $r.Name, $r.DestRel, $r.Status, $r.Detail))
        }
    } else {
        foreach ($r in $script:State) {
            [void]$sb.AppendLine(('[{0}] {1,-14} {2}  ->  {3}  ({4})' -f $r.Category, $r.Status, $r.Name, $r.DestRel, $r.Detail))
        }
    }
    [void]$sb.AppendLine(''); [void]$sb.AppendLine('--- журнал ---')
    [void]$sb.AppendLine($Log.Text)
    Set-Content -LiteralPath $d.FileName -Value $sb.ToString() -Encoding UTF8
    Write-Log "отчёт сохранён: $($d.FileName)"
})
$miUrl.Add_Click({
    $b = if ($script:CurBase) { $script:CurBase } else { $script:FALLBACK_BASE }
    [void][System.Windows.Forms.MessageBox]::Show(
        "Адрес пака:`r`n$b/pack.toml`r`n`r`nИндекс:`r`n$b/index.toml`r`n`r`nУстановщик:`r`n$b/install.ps1`r`n$b/latest/pack.mrpack`r`n$b/latest/instance.zip",
        $script:APP_NAME, 'OK', 'Information')
})
$miHow.Add_Click({
    [void][System.Windows.Forms.MessageBox]::Show(@'
Программа сравнивает содержимое папки сборки с тем, что опубликовано на сервере.

Цепочка ровно та же, что у packwiz-installer при запуске игры:
  1. pack.toml        — имя пака, версия Minecraft и загрузчика, sha256 индекса
  2. index.toml       — список всех файлов пака с хэшами
  3. mods/*.pw.toml   — для каждого мода: URL на Modrinth и sha1 файла
  4. каждый файл      — сравнивается с тем, что лежит на диске, ПО ХЭШУ

Починка качает файлы напрямую (Invoke-WebRequest), поэтому Java не нужна.
Перед заменой старый файл копируется в .modpack-backup.

Статусы:
  НА МЕСТЕ        файл есть и хэш совпал
  ОТСУТСТВУЕТ     файла нет — будет скачан
  НЕ СОВПАДАЕТ    файл есть, но хэш другой — будет заменён
  ОТКЛЮЧЁН        лежит как <имя>.disabled, синхронизатор его не трогает
  НЕТ (preserve)  в index.toml стоит preserve=true — файл намеренно не
                  перезаписывается, чтобы не затирать личные настройки
  ДРУГАЯ СТОРОНА  мод только для сервера, а выбрана сторона client (или наоборот)
  ЛИШНИЙ          файл в mods/config/…, которого нет в паке
'@, "$($script:APP_NAME) — как это работает", 'OK', 'Information')
})
$miAbout.Add_Click({
    [void][System.Windows.Forms.MessageBox]::Show(
        "$($script:APP_NAME) $script:APP_VERSION`r`n`r`nОбслуживание модпака на packwiz: проверка и починка`r`nбез запуска игры и без Java.`r`n`r`nНастройки: $($script:SETTINGS_FILE)`r`n`r`nЧистый PowerShell 5.1 + WinForms, зависимостей нет.",
        $script:APP_NAME, 'OK', 'Information')
})
$miExit.Add_Click({ $form.Close() })

$form.Add_FormClosing({ Save-Settings })

# --------------------------------------------------------------------------- #

$form.Controls.Add($menu)

$cfg = Load-Settings
$script:Recent = @($cfg.Recent)
if (-not $script:CurBase -and $cfg.BaseUrl) { $script:CurBase = $cfg.BaseUrl }
if ($script:CurBase) { $txtBase.Text = $script:CurBase }
if (-not $Side -and $cfg.Side) { $cmbSide.SelectedItem = $cfg.Side }

$form.Add_Shown({
    Rebuild-RecentMenu
    $dirs = @(Find-GameDirs)
    foreach ($d in $dirs) { [void]$cmbDir.Items.Add(('{0}  |  {1}' -f $d.Label, $d.Path)) }

    $pick = ''
    if ($script:CurDir) { $pick = $script:CurDir }
    elseif ($cfg.GameDir) { $pick = $cfg.GameDir }
    elseif ($dirs.Count -gt 0) { $pick = $dirs[0].Path }

    if ($pick) {
        $cmbDir.Text = "(выбрана)  |  $pick"
        Write-Log "папка сборки: $pick"
        Invoke-Refresh -Silent
    } else {
        Write-Log 'лаунчеры не найдены — укажите папку сборки кнопкой «Обзор…»'
        Write-Log 'обычно это:'
        Write-Log '  AstralRinth  : %APPDATA%\AstralRinthApp\profiles\<имя>'
        Write-Log '  Modrinth App : %APPDATA%\ModrinthApp\profiles\<имя>'
        Write-Log '  Freesm/Prism : %APPDATA%\FreesmLauncher\instances\<имя>\.minecraft'
        Set-Status 'Выберите папку сборки'
    }
})

[void]$form.ShowDialog()
