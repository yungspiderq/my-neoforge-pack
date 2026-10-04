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
rem
rem  LOG: vsyo pishetsya v packsync\sync.log - esli chto-to ne tak,
rem       smotrite snachala ego.
rem  DEBUG: sozdayte fayl packsync\SHOW_GUI - i umesto tihogo rejima
rem       otkroetsya okno packwiz-installer s progressom skachivaniya.
rem =====================================================================

set "PACKSYNC_DIR=%~dp0"
if "%PACKSYNC_DIR:~-1%"=="\" set "PACKSYNC_DIR=%PACKSYNC_DIR:~0,-1%"
for %%I in ("%PACKSYNC_DIR%\..") do set "GAME_DIR=%%~fI"

set "BOOT_JAR=%PACKSYNC_DIR%\packwiz-installer-bootstrap.jar"
set "MAIN_JAR=%PACKSYNC_DIR%\packwiz-installer.jar"
set "URLFILE=%PACKSYNC_DIR%\pack-url.txt"
set "LOGFILE=%PACKSYNC_DIR%\sync.log"

for /f "tokens=1-3 delims=/- " %%a in ("%date%") do set "D=%%c-%%a-%%b"
set "T=%time:~0,8%"
set "STAMP=[%D% %T%]"

if not exist "%BOOT_JAR%" goto :nojar
if not exist "%MAIN_JAR%" goto :nojar
if not exist "%URLFILE%"    goto :nojar

set "PACK_URL="
set /p PACK_URL=<"%URLFILE%"
if not defined PACK_URL goto :nojar

rem ---------------- poisk java (java.exe, zatem javaw.exe) ----------------
set "JAVA_EXE="
if defined JAVA_HOME if exist "%JAVA_HOME%\bin\java.exe" set "JAVA_EXE=%JAVA_HOME%\bin\java.exe"
if not defined JAVA_EXE for /f "delims=" %%i in ('where java.exe 2^>nul') do if not defined JAVA_EXE set "JAVA_EXE=%%i"
rem --- prohod 1: java.exe ---
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\AstralRinth\java_runtimes" java.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\AstralRinth\java_runtimes" java.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\AstralRinthApp\java_runtimes" java.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\AstralRinthApp\java_runtimes" java.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\ModrinthApp\java_runtimes" java.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\ModrinthApp\java_runtimes" java.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\PrismLauncher\java" java.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\PrismLauncher\java" java.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\FreesmLauncher\java" java.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\FreesmLauncher\java" java.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Eclipse Adoptium" java.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Microsoft" java.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Java" java.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES(X86)%\Java" java.exe
if not defined JAVA_EXE call :findjava "%USERPROFILE%\.jdks" java.exe
rem --- prohod 2: javaw.exe --- upravlyaemye runtime Freesm/Prism mogut
rem     ne imet java.exe; javaw.exe dlya sinhronizacii dostatochen.
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\AstralRinth\java_runtimes" javaw.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\AstralRinth\java_runtimes" javaw.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\AstralRinthApp\java_runtimes" javaw.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\AstralRinthApp\java_runtimes" javaw.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\ModrinthApp\java_runtimes" javaw.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\ModrinthApp\java_runtimes" javaw.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\PrismLauncher\java" javaw.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\PrismLauncher\java" javaw.exe
if not defined JAVA_EXE call :findjava "%LOCALAPPDATA%\FreesmLauncher\java" javaw.exe
if not defined JAVA_EXE call :findjava "%APPDATA%\FreesmLauncher\java" javaw.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Eclipse Adoptium" javaw.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Microsoft" javaw.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES%\Java" javaw.exe
if not defined JAVA_EXE call :findjava "%PROGRAMFILES(X86)%\Java" javaw.exe
if not defined JAVA_EXE call :findjava "%USERPROFILE%\.jdks" javaw.exe

if not defined JAVA_EXE (
    echo %STAMP% JAVA NOT FOUND - sinhronizaciya propushena, igra zapustitsya bez mods>>"%LOGFILE%"
    echo [packsync] java.exe ne najden - mods ne budut obnovleny. Sm. %LOGFILE%
    goto :done
)

rem ---------------- rezhim: tiho ili s oknom ----------------
set "GUIFLAG=-g"
if exist "%PACKSYNC_DIR%\SHOW_GUI" set "GUIFLAG="

echo %STAMP% start>>"%LOGFILE%"
echo %STAMP% java=%JAVA_EXE%>>"%LOGFILE%"
echo %STAMP% url=%PACK_URL%>>"%LOGFILE%"
echo %STAMP% game_dir=%GAME_DIR%>>"%LOGFILE%"
echo %STAMP% mode=%GUIFLAG%>>"%LOGFILE%"
echo [packsync] %PACK_URL%

"%JAVA_EXE%" -jar "%BOOT_JAR%" --bootstrap-no-update --bootstrap-main-jar "%MAIN_JAR%" --pack-folder "%GAME_DIR%" %GUIFLAG% "%PACK_URL%" >>"%LOGFILE%" 2>&1
set "RC=%ERRORLEVEL%"
echo %STAMP% exit_code=%RC%>>"%LOGFILE%"

if "%RC%"=="0" (
    echo [packsync] sinhronizaciya zavershena uspeshno
) else (
    echo [packsync] VNIAMANIE: kod vozvrata %RC% - sm. %LOGFILE%
    echo [packsync] igra zapustitsya, no mods mogli ne obnovitsya
)

:done
endlocal
exit /b 0

:nojar
echo %STAMP% SKIP: net jar-ov ili pack-url.txt v %PACKSYNC_DIR%>>"%LOGFILE%" 2>nul
echo [packsync] packsync ne polnostiu ustanovlen - propusk
endlocal
exit /b 0

:findjava
if not defined JAVA_EXE if exist "%~1" for /f "delims=" %%f in ('dir /b /s /a-d "%~1\%~2" 2^>nul') do if not defined JAVA_EXE set "JAVA_EXE=%%f"
goto :eof
