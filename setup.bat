@echo off
REM JARVIS — One-click setup (Windows). Run once. No code, no typing.
REM Installs Python packages, opens the firewall for port 5000, starts Jarvis.
cd /d %~dp0
echo Installing JARVIS...
python -m pip install --upgrade pip
python -m pip install -r requirements-windows.txt
echo.
echo Allowing JARVIS through Windows Firewall (port 5000)...
netsh advfirewall firewall add rule name="JARVIS" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
echo.
echo Starting JARVIS — HUD will open in your browser.
echo Phone: scan the QR code on the HUD. That is the whole setup.
start "" http://localhost:5000
python jarvis_server.py
pause
