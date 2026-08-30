@echo off
setlocal
REM ============================================================
REM  GOLEM: остановка сервера по порту
REM ============================================================
set "PORT=5000"
if not "x%GOLEM_PORT%"=="x" set "PORT=%GOLEM_PORT%"
echo Остановка сервера GOLEM на порту %PORT%...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%PORT%" ^| findstr LISTENING') do (
  taskkill /f /pid %%a >nul 2>nul
)
echo Готово.
pause
endlocal