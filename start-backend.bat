@echo off
REM Start script for Backend Services (Windows)
REM Run this on your laptop to start the classifier service and API server

echo =========================================
echo Fruit Classification System - Backend
echo =========================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Start RabbitMQ
echo.
echo Starting RabbitMQ...
docker-compose up -d

REM Wait for RabbitMQ to be ready
echo Waiting for RabbitMQ to be ready...
timeout /t 5 /nobreak >nul

REM Check if RabbitMQ is running
docker ps | findstr fruit_rabbitmq >nul
if errorlevel 1 (
    echo ❌ RabbitMQ failed to start
    pause
    exit /b 1
)

echo ✅ RabbitMQ is running
echo    Management UI: http://localhost:15672 (guest/guest)

REM Change to backend directory
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit backend\.env with your configuration
)

REM Create directories
if not exist "models" mkdir models
if not exist "data" mkdir data

echo.
echo =========================================
echo Starting Backend Services...
echo =========================================

REM Start classifier service in new window
echo.
echo Starting Classifier Service...
start "Classifier Service" cmd /k "venv\Scripts\activate.bat && python classifier_service.py"

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Start API server in new window
echo.
echo Starting API Server...
start "API Server" cmd /k "venv\Scripts\activate.bat && python api.py"

echo.
echo =========================================
echo Backend Services Started!
echo =========================================
echo API Server: http://localhost:8000
echo Dashboard: http://localhost:8000/dashboard/
echo RabbitMQ Management: http://localhost:15672
echo.
echo Services are running in separate windows.
echo Close those windows or press Ctrl+C to stop.
echo =========================================
echo.

REM Open dashboard in browser
timeout /t 3 /nobreak >nul
start http://localhost:8000/dashboard/

pause
