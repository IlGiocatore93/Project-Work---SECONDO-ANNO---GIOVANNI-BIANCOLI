@echo off


echo.
echo ╔══════════════════════════════════════════╗
echo ║       AVVIO PROGETTO GIOVANNI BIANCOLI   ║
echo ╚══════════════════════════════════════════╝
echo.

REM ════════════════════════════════════════════════
REM  SETUP VENV E DIPENDENZE PYTHON (automatico)
REM ════════════════════════════════════════════════

REM Trova il comando Python disponibile (py, python, python3)
set PYTHON_CMD=
where py >NUL 2>&1
if %errorlevel%==0 set PYTHON_CMD=py
if "%PYTHON_CMD%"=="" (
    where python >NUL 2>&1
    if %errorlevel%==0 set PYTHON_CMD=python
)
if "%PYTHON_CMD%"=="" (
    where python3 >NUL 2>&1
    if %errorlevel%==0 set PYTHON_CMD=python3
)
if "%PYTHON_CMD%"=="" (
    echo ❌ Python non trovato. Installalo da https://www.python.org/downloads/
    echo    e assicurati di spuntare "Add Python to PATH" durante l'installazione.
    pause
    exit /b 1
)
echo ✅ Python trovato: %PYTHON_CMD%

if not exist "venv\Scripts\python.exe" (
    echo 📦 Creazione virtual environment...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ❌ Errore creazione venv.
        pause
        exit /b 1
    )
    echo ✅ Virtual environment creato
) else (
    echo ✅ Virtual environment già presente
)

call venv\Scripts\activate.bat

echo 📥 Verifica/installazione dipendenze...
python -m pip install --upgrade pip >NUL 2>&1
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    pip install flask pymongo pyjwt ultralytics opencv-python pillow requests tzdata
)
if errorlevel 1 (
    echo ❌ Errore durante l'installazione delle dipendenze.
    pause
    exit /b 1
)
echo ✅ Dipendenze pronte

echo.

REM ════════════════════════════════════════════════
REM  TROVA E AVVIA DOCKER DESKTOP
REM ════════════════════════════════════════════════

REM Verifica che il comando 'docker' sia disponibile (qualsiasi runtime)
where docker >NUL 2>&1
if errorlevel 1 (
    echo ❌ Comando 'docker' non trovato nel PATH.
    echo    Installa Docker Desktop ^(https://www.docker.com/products/docker-desktop^)
    echo    o un'alternativa come Rancher Desktop / Podman.
    pause
    exit /b 1
)
echo ✅ Docker CLI trovato nel PATH

REM Cerca Docker Desktop nei percorsi conosciuti (opzionale, per avvio automatico GUI)
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

REM Verifica se il daemon Docker è attivo
docker info >NUL 2>&1
if errorlevel 1 (
    if "%DOCKER_FOUND%"=="1" (
        echo 🐳 Docker non attivo, avvio Docker Desktop...
        start "" %DOCKER_EXE%
    ) else (
        echo ⚠️  Docker non risulta attivo e Docker Desktop non è stato trovato.
        echo    Se usi un'alternativa ^(Rancher/Podman/WSL^), avviala manualmente e riprova.
        pause
        exit /b 1
    )
) else (
    echo ✅ Docker già attivo e funzionante
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
