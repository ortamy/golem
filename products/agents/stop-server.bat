@echo off
setlocal
REM ============================================================
REM  ALEPHY: остановка сервера по порту
REM ============================================================
set "PORT=5000"
if not "x%ALEPHY_PORT%"=="x" set "PORT=%ALEPHY_PORT%"
echo Остановка сервера ALEPHY на порту %PORT%...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%PORT%" ^| findstr LISTENING') do (
  taskkill /f /pid %%a >nul 2>nul
)
echo Готово.
pause
endlocal