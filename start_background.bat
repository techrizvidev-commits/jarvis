@echo off
REM JARVIS — Background mode. Silent until you say "Hey Jarvis" (any language).
REM Run this, then minimise the window. Jarvis keeps listening in the background.
cd /d %~dp0
echo JARVIS background listener — say "Hey Jarvis" to wake.
python jarvis.py --background
pause
