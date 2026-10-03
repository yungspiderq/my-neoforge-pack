@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Проверка модпака

rem =====================================================================
rem  Двойной клик = открыть окно «Проверка модпака».
rem  Показывает, какие моды реально стоят в папке игры и чего не хватает.
rem =====================================================================

set "HERE=%~dp0"
if "%HERE:~-1%"=="\" set "HERE=%HERE:~0,-1%"

if exist "%HERE%\CheckMods.ps1" (
    set "SCRIPT=%HERE%\CheckMods.ps1"
) else (
    set "SCRIPT=%TEMP%\CheckMods.ps1"
    if not exist "%SCRIPT%" (
        echo.
        echo   [X]  CheckMods.ps1 не найден ни рядом, ни во временной папке.
        echo        Скачайте оба файла в одну папку:
        echo          CheckMods.bat
        echo          CheckMods.ps1
        echo.
        pause
        exit /b 1
    )
)

powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%SCRIPT%" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" echo.
if not "%RC%"=="0" echo   окно закрылось с кодом %RC%
endlocal
exit /b %RC%
