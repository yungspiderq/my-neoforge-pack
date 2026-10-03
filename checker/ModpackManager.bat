@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Modpack Manager

rem =====================================================================
rem  Двойной клик = открыть Modpack Manager.
rem  Проверяет папку сборки (mods, config, resourcepacks, shaderpacks)
rem  против сервера и докачивает всё, что не совпало. Java не нужна.
rem
rem  Аргументы передаются скрипту как есть:
rem      ModpackManager.bat -GameDir "C:\путь\к\сборке"
rem      ModpackManager.bat -Side server
rem =====================================================================

set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"

set "SCRIPT=%HERE%\ModpackManager.ps1"
if not exist "%SCRIPT%" set "SCRIPT=%TEMP%\ModpackManager.ps1"

if not exist "%SCRIPT%" (
    echo.
    echo   [X]  ModpackManager.ps1 не найден.
    echo        Положите ModpackManager.bat и ModpackManager.ps1 в одну папку
    echo        или скачайте их командой из INSTALL.md.
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%SCRIPT%" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
    echo.
    echo   окно закрылось с кодом %RC%
    pause
)
endlocal
exit /b %RC%
