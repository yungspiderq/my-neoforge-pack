@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Установка модпака

rem =====================================================================
rem  Двойной клик по этому файлу = полная установка модпака.
rem  Скачивает install.ps1 с GitHub Pages и запускает его.
rem
rem  Дополнительные флаги можно передать так:
rem      install.bat -WithLauncher        (поставит Freesm Launcher, если его нет)
rem      install.bat -Launcher astralrinth
rem =====================================================================

set "BASE=@@BASE_URL@@"

if not "%BASE:@@BASE=%"=="%BASE%" (
    echo.
    echo   [X]  Адрес пака не задан: этот файл нужно скачать со страницы
    echo        вашего GitHub Pages, а не из репозитория.
    echo.
    pause
    exit /b 1
)

echo.
echo   ====================================================================
echo     Установка модпака
echo     источник: %BASE%
echo   ====================================================================
echo.

set "PS1=%TEMP%\modpack-install.ps1"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;" ^
  "Invoke-WebRequest -UseBasicParsing -Uri '%BASE%/install.ps1' -OutFile '%PS1%';" ^
  "& '%PS1%' -BaseUrl '%BASE%' %*"

set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
    echo   [X]  Установщик завершился с кодом %RC%
) else (
    echo   [OK] Готово. Закройте это окно.
)
echo.
pause
endlocal
exit /b %RC%
