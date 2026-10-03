<#
.SYNOPSIS
    «Проверены ли моды?» — окно, которое показывает, что реально стоит
    в папке игры и чего не хватает. Без зависимостей: чистый PowerShell + WinForms.

.DESCRIPTION
    Что делает:
      • сам находит папки игры всех известных лаунчеров
        (AstralRinth, Modrinth App, Freesm, Prism, MultiMC, .minecraft)
      • читает адрес пака из <папка игры>/packsync/pack-url.txt
      • скачивает pack.toml -> index.toml -> mods/*.pw.toml (ровно как
        packwiz-installer) и сверяет каждый ожидаемый .jar с тем, что на диске
      • проверяет sha1 каждого установленного файла — ловит «файл есть, но битый»
      • показывает статус: НА МЕСТЕ / ОТСУТСТВУЕТ / ПОВРЕЖДЁН / ОТКЛЮЧЁН / ЛИШНИЙ
      • кнопка «Синхронизировать» запускает packwiz-installer и показывает вывод
      • кнопка «Показать прогресс» создаёт packsync/SHOW_GUI — после этого
        синхронизация идёт с видимым окном прогресса вместо тихого режима

    Игру НЕ запускает и аккаунты не трогает — это диагностическое окно.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File CheckMods.ps1
    powershell -ExecutionPolicy Bypass -File CheckMods.ps1 -GameDir "C:\...\profiles\MyPack"
    powershell -ExecutionPolicy Bypass -File CheckMods.ps1 -BaseUrl https://user.github.io/repo
#>

[CmdletBinding()]
param(
    [string] $GameDir = '',
    [string] $BaseUrl = ''
)

$ErrorActionPreference = 'Stop'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$FALLBACK_BASE = 'https://yungspiderq.github.io/my-neoforge-pack'

# script-scope: обработчики событий выполняются позже, чем тело скрипта,
# поэтому параметры надёжнее держать в $script:
$script:ArgBaseUrl = $BaseUrl
$script:ArgGameDir = $GameDir

# --------------------------------------------------------------------------- #
#  Поиск папок игры
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
        @{ Label = 'AstralRinth';  Base = "$env:APPDATA\AstralRinthApp\profiles" },
        @{ Label = 'Modrinth App'; Base = "$env:APPDATA\ModrinthApp\profiles" },
        @{ Label = 'Freesm';       Base = "$env:APPDATA\FreesmLauncher\instances" },
        @{ Label = 'Freesm';       Base = "$env:LOCALAPPDATA\FreesmLauncher\instances" },
        @{ Label = 'Prism';        Base = "$env:APPDATA\PrismLauncher\instances" },
        @{ Label = 'Prism';        Base = "$env:LOCALAPPDATA\PrismLauncher\instances" },
        @{ Label = 'MultiMC';      Base = "$env:APPDATA\MultiMC\instances" },
        @{ Label = 'MultiMC';      Base = 'C:\MultiMC\instances' }
    )
    foreach ($r in $roots) {
        if (-not (Test-Path -LiteralPath $r.Base)) { continue }
        Get-ChildItem -LiteralPath $r.Base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $gd = Get-PrismGameDir $_.FullName
            if (Test-Path -LiteralPath (Join-Path $gd 'packsync')) {
                [void]$out.Add([pscustomobject]@{
                    Label = '{0}: {1}' -f $r.Label, $_.Name
                    Path  = $gd
                })
            }
        }
    }
    # обычный .minecraft — только если там есть packsync
    if (Test-Path -LiteralPath "$env:APPDATA\.minecraft\packsync") {
        [void]$out.Add([pscustomobject]@{ Label = 'Vanilla: .minecraft'; Path = "$env:APPDATA\.minecraft" })
    }
    # всё, что нашлось по packsync, даже без mods — полезно для диагностики
    foreach ($r in $roots) {
        if (-not (Test-Path -LiteralPath $r.Base)) { continue }
        Get-ChildItem -LiteralPath $r.Base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $gd = Get-PrismGameDir $_.FullName
            $dup = $false
            foreach ($o in $out) { if ($o.Path -eq $gd) { $dup = $true } }
            if (-not $dup -and (Test-Path -LiteralPath $gd)) {
                [void]$out.Add([pscustomobject]@{
                    Label = '{0}: {1} (нет packsync)' -f $r.Label, $_.Name
                    Path  = $gd
                })
            }
        }
    }
    return $out
}

# --------------------------------------------------------------------------- #
#  Мини-парсер TOML (то же подмножество, что в scripts/*.py)
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

function Get-TextFrom([string]$Url) {
    return (Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 60).Content
}

# --------------------------------------------------------------------------- #
#  Логика проверки
# --------------------------------------------------------------------------- #

function Read-PackUrl([string]$gd) {
    $f = Join-Path $gd 'packsync\pack-url.txt'
    if (Test-Path -LiteralPath $f) {
        $u = (Get-Content -LiteralPath $f -TotalCount 1).Trim()
        if ($u) { return $u }
    }
    return $null
}

function Invoke-Check {
    param([string]$Gd, [string]$Base, $Grid, $StatusBox, $Log)

    $Grid.Items.Clear()
    $Log.Clear()
    $add = {
        param($n, $e, $d, $s, $c)
        $it = New-Object System.Windows.Forms.ListViewItem($n)
        [void]$it.SubItems.Add($e)
        [void]$it.SubItems.Add($d)
        [void]$it.SubItems.Add($s)
        $it.ForeColor = $c
        [void]$Grid.Items.Add($it)
    }

    if (-not $Gd -or -not (Test-Path -LiteralPath $Gd)) {
        $StatusBox.Text = 'Папка игры не найдена'
        & $add '(папка игры)' '-' $Gd 'НЕТ' ([System.Drawing.Color]::Red)
        return
    }

    # --- адрес пака ---
    $packTomlUrl = Read-PackUrl $Gd
    if ($packTomlUrl) {
        $Base = ($packTomlUrl -replace '/pack\.toml$', '')
        $Log.AppendText("адрес пака (из packsync/pack-url.txt): $packTomlUrl`r`n")
    } elseif ($Base) {
        $Log.AppendText("pack-url.txt не найден, использую заданный адрес: $Base`r`n")
    } else {
        $Base = $FALLBACK_BASE
        $Log.AppendText("адрес не определён, беру по умолчанию: $Base`r`n")
    }

    # --- pack.toml ---
    try {
        $pack = ConvertFrom-SimpleToml (Get-TextFrom "$Base/pack.toml")
    } catch {
        $StatusBox.Text = 'Не удалось получить pack.toml'
        & $add 'pack.toml' '-' '-' "ОШИБКА: $($_.Exception.Message)" ([System.Drawing.Color]::Red)
        return
    }
    $mc = $pack.versions.minecraft
    $ldr = ''
    foreach ($k in @('neoforge', 'forge', 'fabric', 'quilt')) { if ($pack.versions.$k) { $ldr = "$k $($pack.versions.$k)" } }
    $Log.AppendText("пак: $($pack.name) $($pack.version) | Minecraft $mc | $ldr`r`n")

    # --- index.toml + контроль целостности ---
    $idxFile = $pack.index.file
    if (-not $idxFile) { $idxFile = 'index.toml' }
    try {
        $idxRaw = (Invoke-WebRequest -Uri "$Base/$idxFile" -UseBasicParsing -TimeoutSec 60).Content
    } catch {
        $StatusBox.Text = 'Не удалось получить index.toml'
        & $add 'index.toml' '-' '-' "ОШИБКА: $($_.Exception.Message)" ([System.Drawing.Color]::Red)
        return
    }
    $declared = $pack.index.hash
    if ($declared) {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $actual = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($idxRaw))) -replace '-', '').ToLower()
        if ($actual -eq $declared.ToLower()) {
            $Log.AppendText("целостность index.toml: OK (sha256 сходится)`r`n")
        } else {
            $Log.AppendText("ВНИМАНИЕ: sha256 index.toml НЕ сходится с pack.toml!`r`n")
            & $add 'index.toml' $declared.Substring(0, 12) $actual.Substring(0, 12) 'РАССИНХРОН' ([System.Drawing.Color]::Red)
        }
    }
    $idx = ConvertFrom-SimpleToml $idxRaw

    # --- собираем ожидания ---
    $expected = @()
    foreach ($e in $idx.files) {
        $rel = $e.file
        if ($rel -like '*.pw.toml') {
            try { $m = ConvertFrom-SimpleToml (Get-TextFrom "$Base/$rel") } catch { continue }
            $expected += [pscustomobject]@{
                Name = $m.name; FileName = $m.filename; Side = $m.side
                Hash = $m.download.hash; HashFmt = $m.download.'hash-format'
                Rel = $rel; Kind = 'mod'
            }
        } else {
            $expected += [pscustomobject]@{
                Name = $rel; FileName = $rel; Side = 'both'
                Hash = $e.hash; HashFmt = 'sha256'
                Rel = $rel; Kind = 'file'; Preserve = $e.preserve
            }
        }
    }

    if ($expected.Count -eq 0) {
        $StatusBox.Text = 'В паке нет ни одного файла'
        & $add '(пусто)' '-' '-' 'ПАК ПУСТ' ([System.Drawing.Color]::Orange)
        $Log.AppendText("в index.toml нет записей — проверять нечего`r`n")
        return
    }

    # --- сверяем с диском ---
    $okN = 0; $missN = 0; $badN = 0
    $seen = @{}
    $GREEN = [System.Drawing.Color]::FromArgb(0, 130, 0)
    $RED = [System.Drawing.Color]::Red
    $ORANGE = [System.Drawing.Color]::DarkOrange
    $GRAY = [System.Drawing.Color]::Gray

    foreach ($x in $expected) {
        if ($x.Kind -eq 'mod') {
            $path = Join-Path (Join-Path $Gd 'mods') $x.FileName
        } else {
            $path = Join-Path $Gd ($x.FileName -replace '/', '\')
        }
        $seen[$x.FileName] = $true

        if (-not (Test-Path -LiteralPath $path)) {
            $dis = Join-Path $path '.disabled'
            if (Test-Path -LiteralPath $dis) {
                & $add $x.Name $x.FileName 'есть, но .disabled' 'ОТКЛЮЧЁН' $ORANGE
            } elseif ($x.Preserve) {
                & $add $x.Name $x.FileName 'нет' 'НЕТ (preserve)' $GRAY
            } else {
                & $add $x.Name $x.FileName 'нет' 'ОТСУТСТВУЕТ' $RED
                $missN++
            }
            continue
        }

        $fi = Get-Item -LiteralPath $path
        $sizeMb = [math]::Round($fi.Length / 1MB, 2)
        $alg = if ($x.HashFmt -eq 'sha256') { 'SHA256' } elseif ($x.HashFmt -eq 'sha512') { 'SHA512' } else { 'SHA1' }
        try {
            $h = (Get-FileHash -LiteralPath $path -Algorithm $alg).Hash.ToLower()
        } catch { $h = '' }
        if ($x.Hash -and $h -and ($h -ne $x.Hash.ToLower())) {
            & $add $x.Name $x.FileName "$sizeMb МБ, хэш НЕ совпал" 'ПОВРЕЖДЁН' $RED
            $badN++
        } else {
            & $add $x.Name $x.FileName "$sizeMb МБ, $alg верен" 'НА МЕСТЕ' $GREEN
            $okN++
        }
    }

    # --- лишние файлы в mods/ ---
    $modsDir = Join-Path $Gd 'mods'
    if (Test-Path -LiteralPath $modsDir) {
        Get-ChildItem -LiteralPath $modsDir -File -ErrorAction SilentlyContinue | ForEach-Object {
            $n = $_.Name
            if (-not $seen.ContainsKey($n) -and $n -notlike '*.disabled') {
                & $add '(не из пака)' $n "$([math]::Round($_.Length/1MB,2)) МБ" 'ЛИШНИЙ' $GRAY
            }
        }
    }

    # --- служебные признаки ---
    $pwj = Join-Path $Gd 'packwiz.json'
    if (Test-Path -LiteralPath $pwj) {
        $age = [math]::Round(((Get-Date) - (Get-Item -LiteralPath $pwj).LastWriteTime).TotalMinutes)
        $Log.AppendText("packwiz.json: есть, обновлён $age мин назад -> синхронизация работала`r`n")
    } else {
        $Log.AppendText("packwiz.json: НЕТ -> packwiz-installer ни разу не отработал`r`n")
        & $add 'packwiz.json' 'должен появиться после синка' 'нет' 'СИНК НЕ ШЁЛ' $RED
    }
    $sl = Join-Path $Gd 'packsync\sync.log'
    if (Test-Path -LiteralPath $sl) {
        $Log.AppendText("packsync/sync.log: есть, изменён $((Get-Item -LiteralPath $sl).LastWriteTime)`r`n")
    } else {
        $Log.AppendText("packsync/sync.log: нет -> hook, скорее всего, не запускался`r`n")
    }

    $StatusBox.Text = 'На месте: {0}   Отсутствует: {1}   Повреждено: {2}' -f $okN, $missN, $badN
    $StatusBox.ForeColor = if (($missN -eq 0) -and ($badN -eq 0)) { $GREEN } else { $RED }
    $Log.AppendText("`r`n$($StatusBox.Text)`r`n")
    $Log.ScrollToCaret()
}

# --------------------------------------------------------------------------- #
#  Форма
# --------------------------------------------------------------------------- #

$form = New-Object System.Windows.Forms.Form
$form.Text = 'Проверка модпака'
$form.Size = New-Object System.Drawing.Size(1040, 700)
$form.MinimumSize = New-Object System.Drawing.Size(820, 520)
$form.StartPosition = 'CenterScreen'
$form.Font = New-Object System.Drawing.Font('Segoe UI', 9)

$top = New-Object System.Windows.Forms.Panel
$top.Dock = 'Top'; $top.Height = 74
$form.Controls.Add($top)

$lblDir = New-Object System.Windows.Forms.Label
$lblDir.Text = 'Папка игры:'; $lblDir.Location = New-Object System.Drawing.Point(10, 12); $lblDir.AutoSize = $true
$top.Controls.Add($lblDir)

$cmbDir = New-Object System.Windows.Forms.ComboBox
$cmbDir.Location = New-Object System.Drawing.Point(90, 8)
$cmbDir.Size = New-Object System.Drawing.Size(620, 24)
$cmbDir.DropDownStyle = 'DropDown'
$top.Controls.Add($cmbDir)

$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = 'Обзор…'; $btnBrowse.Location = New-Object System.Drawing.Point(718, 7); $btnBrowse.Size = New-Object System.Drawing.Size(80, 26)
$top.Controls.Add($btnBrowse)

$btnCheck = New-Object System.Windows.Forms.Button
$btnCheck.Text = 'Проверить'; $btnCheck.Location = New-Object System.Drawing.Point(806, 7); $btnCheck.Size = New-Object System.Drawing.Size(100, 26)
$btnCheck.Font = New-Object System.Drawing.Font('Segoe UI', 9, [System.Drawing.FontStyle]::Bold)
$top.Controls.Add($btnCheck)

$btnSync = New-Object System.Windows.Forms.Button
$btnSync.Text = 'Синхронизировать'; $btnSync.Location = New-Object System.Drawing.Point(90, 40); $btnSync.Size = New-Object System.Drawing.Size(150, 26)
$top.Controls.Add($btnSync)

$btnGui = New-Object System.Windows.Forms.Button
$btnGui.Text = 'Показывать прогресс'; $btnGui.Location = New-Object System.Drawing.Point(248, 40); $btnGui.Size = New-Object System.Drawing.Size(160, 26)
$top.Controls.Add($btnGui)

$btnMods = New-Object System.Windows.Forms.Button
$btnMods.Text = 'Открыть mods/'; $btnMods.Location = New-Object System.Drawing.Point(416, 40); $btnMods.Size = New-Object System.Drawing.Size(120, 26)
$top.Controls.Add($btnMods)

$btnLog = New-Object System.Windows.Forms.Button
$btnLog.Text = 'Открыть sync.log'; $btnLog.Location = New-Object System.Drawing.Point(544, 40); $btnLog.Size = New-Object System.Drawing.Size(130, 26)
$top.Controls.Add($btnLog)

$StatusBox = New-Object System.Windows.Forms.Label
$StatusBox.Location = New-Object System.Drawing.Point(690, 45)
$StatusBox.Size = New-Object System.Drawing.Size(320, 20)
$StatusBox.TextAlign = 'MiddleLeft'
$top.Controls.Add($StatusBox)

$split = New-Object System.Windows.Forms.SplitContainer
$split.Dock = 'Fill'
$split.Orientation = 'Horizontal'
$form.Controls.Add($split)
$split.BringToFront()

$Grid = New-Object System.Windows.Forms.ListView
$Grid.View = 'Details'; $Grid.FullRowSelect = $true; $Grid.GridLines = $true
$Grid.Dock = 'Fill'
$Grid.HideSelection = $false
[void]$Grid.Columns.Add('Мод / файл', 250)
[void]$Grid.Columns.Add('Ожидаемый файл', 300)
[void]$Grid.Columns.Add('На диске', 190)
[void]$Grid.Columns.Add('Статус', 130)
$split.Panel1.Controls.Add($Grid)

$Log = New-Object System.Windows.Forms.TextBox
$Log.Multiline = $true; $Log.ReadOnly = $true; $Log.ScrollBars = 'Both'
$Log.WordWrap = $false; $Log.Dock = 'Fill'
$Log.Font = New-Object System.Drawing.Font('Consolas', 8.5)
$Log.BackColor = [System.Drawing.Color]::FromArgb(248, 248, 248)
$split.Panel2.Controls.Add($Log)

# --------------------------------------------------------------------------- #
#  Обработчики
# --------------------------------------------------------------------------- #

function Selected-GameDir {
    $t = $cmbDir.Text
    if ($t -match '\|(.+)$') { return $Matches[1].Trim() }
    if ($t -and (Test-Path -LiteralPath $t)) { return $t }
    return ''
}

function Reload-Dirs {
    $cmbDir.Items.Clear()
    $dirs = @(Find-GameDirs)
    foreach ($d in $dirs) { [void]$cmbDir.Items.Add(('{0}  |  {1}' -f $d.Label, $d.Path)) }
    if ($script:ArgGameDir) {
        $found = $false
        foreach ($d in $dirs) { if ($d.Path -eq $script:ArgGameDir) { $found = $true } }
        if (-not $found) { [void]$cmbDir.Items.Add("(указана вручную)  |  $($script:ArgGameDir)") }
    }
    if ($dirs.Count -eq 0 -and $script:ArgGameDir) { $cmbDir.Text = "(указана вручную)  |  $($script:ArgGameDir)" }
    elseif ($dirs.Count -gt 0) { $cmbDir.SelectedIndex = 0 }
    $Log.AppendText("найдено папок игры: $($dirs.Count)`r`n")
}

$btnCheck.Add_Click({
    $gd = Selected-GameDir
    $form.Cursor = 'WaitCursor'
    try { Invoke-Check -Gd $gd -Base $script:ArgBaseUrl -Grid $Grid -StatusBox $StatusBox -Log $Log }
    catch { $Log.AppendText("ОШИБКА: $($_.Exception.Message)`r`n") }
    finally { $form.Cursor = 'Default' }
})

$btnBrowse.Add_Click({
    $d = New-Object System.Windows.Forms.FolderBrowserDialog
    $d.Description = 'Выберите папку игры (профиль лаунчера или .minecraft)'
    if ($d.ShowDialog() -eq 'OK') {
        [void]$cmbDir.Items.Add("(вручную)  |  $($d.SelectedPath)")
        $cmbDir.Text = "(вручную)  |  $($d.SelectedPath)"
    }
})

$btnSync.Add_Click({
    $gd = Selected-GameDir
    if (-not $gd) { [void][System.Windows.Forms.MessageBox]::Show('Сначала выберите папку игры'); return }
    $cmd = Join-Path $gd 'packsync\sync.cmd'
    $sh  = Join-Path $gd 'packsync/sync.sh'
    $Log.AppendText("`r`n=== запуск синхронизации ===`r`n")
    $form.Cursor = 'WaitCursor'
    try {
        if ($IsWindows -or $env:OS -eq 'Windows_NT') {
            if (-not (Test-Path -LiteralPath $cmd)) { throw "нет $cmd" }
            $out = & cmd.exe /c "`"$cmd`"" 2>&1 | Out-String
        } else {
            if (-not (Test-Path -LiteralPath $sh)) { throw "нет $sh" }
            $out = & sh $sh 2>&1 | Out-String
        }
        $Log.AppendText($out)
        $Log.AppendText("=== синхронизация завершена, перепроверяю ===`r`n")
        Invoke-Check -Gd $gd -Base $script:ArgBaseUrl -Grid $Grid -StatusBox $StatusBox -Log $Log
    } catch {
        $Log.AppendText("ОШИБКА: $($_.Exception.Message)`r`n")
    } finally { $form.Cursor = 'Default' }
})

$btnGui.Add_Click({
    $gd = Selected-GameDir
    if (-not $gd) { [void][System.Windows.Forms.MessageBox]::Show('Сначала выберите папку игры'); return }
    $flag = Join-Path $gd 'packsync\SHOW_GUI'
    if (Test-Path -LiteralPath $flag) {
        Remove-Item -LiteralPath $flag -Force
        $btnGui.Text = 'Показывать прогресс'
        $Log.AppendText("SHOW_GUI удалён -> синхронизация снова тихая`r`n")
    } else {
        New-Item -ItemType File -Path $flag -Force | Out-Null
        $btnGui.Text = 'Прогресс: ВКЛ'
        $Log.AppendText("SHOW_GUI создан -> при следующем запуске откроется окно packwiz-installer с прогрессом`r`n")
    }
})

$btnMods.Add_Click({
    $gd = Selected-GameDir
    if (-not $gd) { return }
    $m = Join-Path $gd 'mods'
    if (Test-Path -LiteralPath $m) { Start-Process -FilePath $m } else { Start-Process -FilePath $gd }
})

$btnLog.Add_Click({
    $gd = Selected-GameDir
    if (-not $gd) { return }
    $l = Join-Path $gd 'packsync\sync.log'
    if (Test-Path -LiteralPath $l) { Start-Process -FilePath 'notepad.exe' -ArgumentList $l }
    else { [void][System.Windows.Forms.MessageBox]::Show("sync.log ещё нет: $l`r`nЗначит hook ни разу не запускался.") }
})

# --------------------------------------------------------------------------- #

$form.Add_Shown({
    Reload-Dirs
    if ($cmbDir.Items.Count -eq 0) {
        $Log.AppendText("лаунчеры не найдены. Укажите папку игры кнопкой «Обзор…»`r`n")
        $Log.AppendText("обычно это:`r`n")
        $Log.AppendText("  AstralRinth : %APPDATA%\AstralRinthApp\profiles\<имя>`r`n")
        $Log.AppendText("  Modrinth App: %APPDATA%\ModrinthApp\profiles\<имя>`r`n")
        $Log.AppendText("  Freesm/Prism: %APPDATA%\FreesmLauncher\instances\<имя>\.minecraft`r`n")
    } else {
        $btnCheck.PerformClick()
    }
})

[void]$form.ShowDialog()
