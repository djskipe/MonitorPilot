@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
set "SCRIPT_DIR=%~dp0"
set "SCRIPT=%SCRIPT_DIR%monitorpilot.py"
set "PYTHON="
set "PYW="

if not exist "%SCRIPT%" goto missing_script

goto find_python

:find_python
rem Prefer the Python 3.12 registered with the Python Launcher.
where py >nul 2>&1
if not errorlevel 1 (
  py -3.12 --version >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('py -3.12 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON=%%P"
    if defined PYTHON (
      "%PYTHON%" --version >nul 2>&1
      if not errorlevel 1 (
        "%PYTHON%" -c "import sys; assert sys.version_info[0] == 3 and sys.version_info[1] == 12" >nul 2>&1
        if not errorlevel 1 goto check_packages
      )
    )
  )
)

rem Try PATH Python entries, but never accept the Microsoft Store stub.
set "PYTHON="
for /f "delims=" %%P in ('where python 2^>nul') do (
  echo %%P | findstr /i /c:"\WindowsApps\" >nul
  if errorlevel 1 (
    "%%P" --version >nul 2>&1
    if not errorlevel 1 (
      "%%P" -c "import sys; assert sys.version_info[0] == 3 and sys.version_info[1] == 12" >nul 2>&1
      if not errorlevel 1 if not defined PYTHON set "PYTHON=%%P"
    )
  )
)
if defined PYTHON goto check_packages
goto install_python

:install_python
echo Python 3.12 non disponibile. Scarico e installo Python 3.12.0 per l'utente corrente...
set "INSTALLER=%TEMP%\python-3.12.0-amd64.exe"
set "MONITORPILOT_INSTALLER=%INSTALLER%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile $env:MONITORPILOT_INSTALLER -ErrorAction Stop } catch { exit 1 }"
if errorlevel 1 goto download_error
if not exist "%INSTALLER%" goto download_error
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_test=0
if errorlevel 1 goto install_error
del "%INSTALLER%" >nul 2>&1

rem Do not rely on the possibly stale PATH after setup; use the known user path.
set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON%" goto installed_python_missing
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 goto installed_python_invalid
"%PYTHON%" -c "import sys; assert sys.version_info[0] == 3 and sys.version_info[1] == 12" >nul 2>&1
if errorlevel 1 goto installed_python_invalid

goto check_packages

:check_packages
echo Controllo le librerie richieste...
set "NEED_PYSIDE6="
set "NEED_PSUTIL="
set "NEED_PYWIN32="
"%PYTHON%" -c "import PySide6" >nul 2>&1
if errorlevel 1 set "NEED_PYSIDE6=1"
"%PYTHON%" -c "import psutil" >nul 2>&1
if errorlevel 1 set "NEED_PSUTIL=1"
"%PYTHON%" -c "import win32api" >nul 2>&1
if errorlevel 1 set "NEED_PYWIN32=1"

if not defined NEED_PYSIDE6 if not defined NEED_PSUTIL if not defined NEED_PYWIN32 goto launch_app
echo Aggiorno pip prima di installare le librerie mancanti...
"%PYTHON%" -m pip install --user --upgrade pip
if errorlevel 1 goto pip_upgrade_error
set "PACKAGES="
if defined NEED_PYSIDE6 set "PACKAGES=!PACKAGES! PySide6"
if defined NEED_PSUTIL set "PACKAGES=!PACKAGES! psutil"
if defined NEED_PYWIN32 set "PACKAGES=!PACKAGES! pywin32"
echo Installo solo le librerie mancanti:!PACKAGES!
"%PYTHON%" -m pip install --user !PACKAGES!
if errorlevel 1 goto package_install_error

:launch_app
for %%D in ("%PYTHON%") do set "PYW=%%~dpDpythonw.exe"
if not exist "%PYW%" goto pythonw_missing
pushd "%SCRIPT_DIR%"
start "" "%PYW%" "%SCRIPT%" %*
popd
exit /b 0

:missing_script
echo ERRORE: monitorpilot.py non si trova nella stessa cartella del launcher.
pause
exit /b 2

:download_error
echo ERRORE: download di Python 3.12.0 non riuscito. Controlla la connessione e riprova.
if exist "%INSTALLER%" del "%INSTALLER%" >nul 2>&1
pause
exit /b 3

:install_error
echo ERRORE: installazione di Python non riuscita. Riprova o controlla i permessi dell'account.
if exist "%INSTALLER%" del "%INSTALLER%" >nul 2>&1
pause
exit /b 4

:installed_python_missing
echo ERRORE: installazione terminata, ma python.exe non si trova nel percorso utente previsto.
pause
exit /b 5

:installed_python_invalid
echo ERRORE: Python installato non si avvia o non e' la versione 3.12.
pause
exit /b 5

:pip_upgrade_error
echo ERRORE: impossibile aggiornare pip. Controlla la connessione e riprova.
pause
exit /b 6

:package_install_error
echo ERRORE: installazione delle librerie mancanti non riuscita. Controlla la connessione e riprova.
pause
exit /b 7

:pythonw_missing
echo ERRORE: pythonw.exe non e' presente nell'installazione Python selezionata.
pause
exit /b 8
