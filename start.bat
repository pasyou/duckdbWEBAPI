@echo off
echo Starting DuckDB Concurrent Web API...
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
start http://localhost:8000/docs

:restart_loop
python src\main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Service crashed with exit code: %ERRORLEVEL%
    echo Restarting service in 1 seconds...
    echo.
    timeout /t 1 /nobreak > nul
    goto restart_loop
)

echo.
echo Service stopped normally.
pause
