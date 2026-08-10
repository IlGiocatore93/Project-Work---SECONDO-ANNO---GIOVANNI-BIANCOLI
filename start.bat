@echo off


echo.
echo ╔══════════════════════════════════════════╗
echo ║       AVVIO PROGETTO GIOVANNI BIANCOLI   ║
echo ╚══════════════════════════════════════════╝
echo.

set DOCKER_EXE=
set DOCKER_FOUND=0

if exist "%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe" (
    set DOCKER_EXE="%PROGRAMFILES%\Docker\Docker\Docker Desktop.exe"
    set DOCKER_FOUND=1
)
if "%DOCKER_FOUND%"=="0" if exist "%PROGRAMFILES(X86)%\Docker\Docker\Docker Desktop.exe" (
    set DOCKER_EXE="%PROGRAMFILES(X86)%\Docker\Docker\Docker Desktop.exe"
    set DOCKER_FOUND=1
)
if "%DOCKER_FOUND%"=="0" if exist "%LOCALAPPDATA%\Docker\Docker Desktop.exe" (
    set DOCKER_EXE="%LOCALAPPDATA%\Docker\Docker Desktop.exe"
    set DOCKER_FOUND=1
)
if "%DOCKER_FOUND%"=="0" if exist "%APPDATA%\Docker\Docker Desktop.exe" (
    set DOCKER_EXE="%APPDATA%\Docker\Docker Desktop.exe"
    set DOCKER_FOUND=1
)

if "%DOCKER_FOUND%"=="0" (
    for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Docker Inc.\Docker Desktop" /v AppPath 2^>NUL') do (
        if exist "%%B\Docker Desktop.exe" (
            set DOCKER_EXE="%%B\Docker Desktop.exe"
            set DOCKER_FOUND=1
        )
    )
)

if "%DOCKER_FOUND%"=="0" (
    for /f "tokens=2*" %%A in ('reg query "HKLM\Software\Docker Inc.\Docker Desktop" /v AppPath 2^>NUL') do (
        if exist "%%B\Docker Desktop.exe" (
            set DOCKER_EXE="%%B\Docker Desktop.exe"
            set DOCKER_FOUND=1
        )
    )
)

if "%DOCKER_FOUND%"=="1" (
    echo ✅ Docker Desktop trovato: %DOCKER_EXE%
) else (
    echo ⚠️  Percorso Docker Desktop non trovato, tento avvio tramite PATH...
)

tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>NUL | find /I "Docker Desktop.exe" >NUL
if errorlevel 1 (
    echo 🐳 Avvio Docker Desktop...
    if "%DOCKER_FOUND%"=="1" (
        start "" %DOCKER_EXE%
    ) else (
        echo ❌ Impossibile avviare Docker Desktop automaticamente.
        echo    Aprilo manualmente e riprova.
        pause
        exit /b 1
    )
) else (
    echo ✅ Docker Desktop già attivo
)


echo ⏳ Attendo che Docker sia pronto...
:WAIT_DOCKER
docker info >NUL 2>&1
if errorlevel 1 (
    timeout /t 3 /nobreak >NUL
    goto WAIT_DOCKER
)
echo ✅ Docker pronto


echo.
echo 🔍 Cerco container di altri progetti...

for %%I in (%CD%) do set CURRENT_PROJECT=%%~nxI
set CURRENT_PROJECT_LABEL=%CURRENT_PROJECT: =%
call :TOLOWER CURRENT_PROJECT_LABEL

for /f "tokens=*" %%C in ('docker ps -q') do (
    for /f "tokens=*" %%L in ('docker inspect --format "{{index .Config.Labels \"com.docker.compose.project\"}}" %%C') do (
        if /I NOT "%%L"=="%CURRENT_PROJECT_LABEL%" (
            if NOT "%%L"=="" (
                echo 🛑 Stoppo container %%C ^(progetto: %%L^)
                docker stop %%C >NUL
            )
        )
    )
)
echo ✅ Solo i container di questo progetto saranno attivi


echo.
echo 🚀 Avvio docker compose in background...
docker compose up -d
echo.
echo ✅ Container avviati! Ora esegui:
echo    python seed_db_galleria.py
echo    python app2.py
echo.
pause

goto :EOF


:TOLOWER
for %%L in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do (
    call set %1=%%%1:%%L=%%L%%
)
exit /b
