@echo off
REM JARVIS v3 - HUD + Mobile
REM Double-click: starts the server and opens the HUD in your browser.
echo Starting JARVIS HUD...
start http://localhost:5000
python jarvis_server.py
pause
