@echo off
echo ========================================
echo Starting Backend Services
echo ========================================
echo.

REM Check if RabbitMQ is running
echo [1/3] Checking RabbitMQ status...
sc query RabbitMQ | find "RUNNING" >nul
if errorlevel 1 (
    echo RabbitMQ is not running. Starting...
    net start RabbitMQ
    timeout /t 3 >nul
) else (
    echo RabbitMQ is already running.
)

echo.
echo [2/3] Starting Classifier Service...
echo Press Ctrl+C to stop
echo.

REM Start classifier service in new window
start "Classifier Service" cmd /k "cd /d %~dp0 && python classifier_service.py"

REM Wait a bit
timeout /t 2 >nul

echo.
echo [3/3] Starting API Server...
echo.

REM Start API in this window
python api.py

REM If API stops, cleanup
echo.
echo Stopping services...
taskkill /FI "WindowTitle eq Classifier Service*" /T /F >nul 2>&1
pause
