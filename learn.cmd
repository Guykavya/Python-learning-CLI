@echo off
rem Run the learning engine on Windows (CMD or PowerShell) without activating the virtual environment.
set "DIR=%~dp0"
if not exist "%DIR%.venv\Scripts\learn.exe" (
  echo Setting up the engine for the first time...
  python -m venv "%DIR%.venv" || exit /b 1
  "%DIR%.venv\Scripts\python" -m pip install -q -e "%DIR%." || exit /b 1
)
"%DIR%.venv\Scripts\learn.exe" %*
