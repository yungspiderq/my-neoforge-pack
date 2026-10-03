@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem =====================================================================
rem  packsync - avtosinhronizaciya modpaka (Windows)
rem  ---------------------------------------------------------------------
rem  Zapusketsya launserom PERED startom igry.
rem  Nikogda ne valit start igry: pri lyuboy oshibke vozvrashchaem 0.
rem
rem  V AstralRinth / Modrinth App hook propisyvaetsya tak:
rem      cmd /c packsync\sync.cmd
rem  (hook tam rezhet stroku po probelam i NE podstavlyaet peremennye,
rem   poetomu imenno tak - tri tokena bez probelov)
rem =====================================================================

set "PACKSYNC_DIR=%~dp0"
if "%PACKSYNC_DIR:~-1%"=="\" set "PACKSYNC_DIR=%PACKSYNC_DIR:~0,-1%"
for %%I in ("%PACKSYNC_DIR%\..") do set "GAME_DIR=%%~fI"

set "BOOT_JAR=%PACKSYNC_DIR%\packwiz-installer-bootstrap.jar"
set "MAIN_JAR=%PACKSYNC_DIR%\packwiz-installer.jar"
set "URLFILE=%PACKSYNC_DIR%\pack-url.txt"

if not exist "%BOOT_JAR%" goto :done
if not exist "%MAIN_JAR%" goto :done
if not exist "%URLFILE%"    goto :done

set "PACK_URL="
set /p PACK_URL=<"%URLFILE%"
if not defined PACK_URL goto :done

rem ---------------- poisk java.exe ----------------
set "JAVA_EXE="
if defined JAVA_HOME if exist "%JAVA_HOME%\bin\java.exe" set "JAVA_EXE=%JAVA_HOME%\bin\java.exe"
if not defined JAVA_EXE for /f "delims=" %%i in ('where java.exe 2^>nul') do if not defined JAVA_EXE set "JAVA_EXE=%%i"
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\AstralRinth\java_runtimes"
if not defined JAVA_EXE call :findjava "%APPDATA%\AstralRinth\java_runtimes"
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\ModrinthApp\java_runtimes"
if not defined JAVA_EXE call :findjava "%APPDATA%\ModrinthApp\java_runtimes"
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\PrismLauncher\java"
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\FreesmLauncher\java"
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Eclipse Adoptium"
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Microsoft"
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Java"
if not defined JAVA_EXE call :findjava "%PROGRAMFILES(X86)%\Java"
if not defined JAVA_EXE call :findjava "%USERPROFILE%\.jdks"
if not defined JAVA_EXE goto :done

rem ---------------- sinhronizaciya ----------------
echo [packsync] %JAVA_EXE%
echo [packsync] %PACK_URL%
"%JAVA_EXE%" -jar "%BOOT_JAR%" --bootstrap-no-update --bootstrap-main-jar "%MAIN_JAR%" --pack-folder "%GAME_DIR%" -g "%PACK_URL%"
echo [packsync] exit code %ERRORLEVEL%

:done
endlocal
exit /b 0

:findjava
if not defined JAVA_EXE if exist "%~1" for /f "delims=" %%f in ('dir /b /s /a-d "%~1\java.exe" 2^>nul') do if not defined JAVA_EXE set "JAVA_EXE=%%f"
goto :eof
