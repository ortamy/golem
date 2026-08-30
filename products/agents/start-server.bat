@echo off
setlocal
REM ============================================================
REM  GOLEM: запуск агентного сервера и Лаборатории ResearchLab
REM  Адрес:  http://127.0.0.1:5000/apps/researchlab/
REM  Остановка: закрыть это окно или использовать stop-server.bat
REM  Если python не в PATH — укажите полный путь без кавычек:
REM    set "PYTHON_CMD=C:\Path\To\python.exe"
REM ============================================================
cd /d "%~dp0"

set "PYTHON_CMD=python"
if not "x%GOLEM_PYTHON%"=="x" set "PYTHON_CMD=%GOLEM_PYTHON%"

"%PYTHON_CMD%" server.py --host 127.0.0.1 --port 5000

if errorlevel 1 (
  echo.
  echo Ошибка запуска. Проверьте:
  echo   - установлен ли Python:  python --version
  echo   - установлены ли зависимости:  pip install -r requirements.txt
  echo.
  pause
)
endlocal