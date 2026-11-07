@echo off
REM JARVIS v2 - Windows one-click installer
REM Double-click this file. It checks Python, installs deps, then starts Jarvis.
echo ========================================
echo  JARVIS v2 - Windows Full-Control Pack
echo ========================================
python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found.
  echo Install Python 3.10+ from https://www.python.org/downloads/
  echo Tick "Add Python to PATH" during install, then run this again.
  pause
  exit /b 1
)
echo [1/3] Python found.
python -m pip install --upgrade pip
echo [2/3] Installing Jarvis deps...
python -m pip install -r requirements-windows.txt
echo [3/3] Done. Starting Jarvis...
echo Type 'help' for commands, 'exit' to quit.
python jarvis.py
pause
