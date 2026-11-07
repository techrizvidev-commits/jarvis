@echo off
REM Build Jarvis.exe locally on Windows
pip install pyinstaller
pyinstaller jarvis.spec
echo.
echo Done. Your exe is at: dist\Jarvis\Jarvis.exe
echo Double-click it to start the HUD server.
pause
