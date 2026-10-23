@echo off
rem Run the learning engine on Windows (CMD or PowerShell) without activating the virtual environment.
rem First run: finds Python 3.11 or newer and builds .venv. Later runs: rebuilds .venv only if it
rem broke or the folder was moved. Set LEARN_PYTHON to choose the interpreter yourself.
setlocal
set "DIR=%~dp0"
set "VENV=%DIR%.venv"
set "VPY=%VENV%\Scripts\python.exe"
set "STAMP=%VENV%\learn-root.txt"
rem Read and print text as UTF-8 everywhere.
set "PYTHONUTF8=1"
set "CHECK=import sys; sys.exit(sys.version_info < (3, 11))"
set "OURS=import os, sys, learn; sys.exit(os.path.normcase(learn.__file__).find(os.path.normcase(sys.argv[1])) != 0)"

rem Fast path: .venv exists and was built for this folder.
if not exist "%VPY%" goto setup
set "ROOT="
if exist "%STAMP%" set /p ROOT=<"%STAMP%"
if /i "%ROOT%"=="%DIR%" goto run
rem A .venv from before the stamp existed: keep it if it loads the engine from this folder.
"%VPY%" -c "%OURS%" "%DIR%engine" >nul 2>&1
if errorlevel 1 goto setup
<nul set /p "=%DIR%" >"%STAMP%"
goto run

:setup
set "PY="
if not defined LEARN_PYTHON goto find
set PY="%LEARN_PYTHON%"
%PY% -c "%CHECK%" >nul 2>&1
if not errorlevel 1 goto build
echo LEARN_PYTHON is set to "%LEARN_PYTHON%", but that is not Python 3.11 or newer. 1>&2
exit /b 1

:find
rem "py" is the official Python launcher; "-3" picks the newest Python 3 installed.
py -3 -c "%CHECK%" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto build
python -c "%CHECK%" >nul 2>&1
if not errorlevel 1 set "PY=python"
if defined PY goto build
echo This course needs Python 3.11 or newer, and none was found. 1>&2
echo Install it with:  winget install Python.Python.3.13   or from https://www.python.org/downloads/ 1>&2
echo During setup tick "Add python.exe to PATH". Then open a new terminal and run this command again. 1>&2
echo If "python" opens the Microsoft Store, turn off the "App execution aliases" for python in Settings. 1>&2
echo To use a specific one: set LEARN_PYTHON=C:\path\to\python.exe 1>&2
exit /b 1

:build
if exist "%VENV%\" goto rebuild
echo Setting up the engine for the first time (needs internet once)...
goto create
:rebuild
echo The engine's environment (.venv) is broken, incomplete or from another folder. Rebuilding it...
rmdir /s /q "%VENV%"

:create
%PY% -m venv "%VENV%"
if not errorlevel 1 goto install
echo. 1>&2
echo Could not create .venv with %PY%. 1>&2
if exist "%VENV%\" rmdir /s /q "%VENV%"
exit /b 1

:install
rem PyYAML: skip its optional C extension so no compiler is ever needed (the engine uses the
rem pure-Python loader anyway). This matters on brand-new Pythons that have no prebuilt wheel yet.
set "PYYAML_FORCE_LIBYAML=0"
"%VPY%" -m pip install -q --disable-pip-version-check -e "%DIR%."
if not errorlevel 1 goto installed
echo. 1>&2
echo Installing the engine's packages failed (see the message above). 1>&2
echo Check your internet connection, then run this command again. 1>&2
exit /b 1
:installed
set "PYYAML_FORCE_LIBYAML="
<nul set /p "=%DIR%" >"%STAMP%"

:run
"%VPY%" -m learn %*
exit /b %errorlevel%
