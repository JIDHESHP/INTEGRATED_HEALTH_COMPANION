@echo off
echo Starting Smart Wellness System...

:: 1. Check/Create Data Directory
if not exist "mongo_data" (
    echo Creating mongo_data directory...
    mkdir "mongo_data"
)

:: 2. Start MongoDB (using the path we found)
echo Starting MongoDB...
start "MongoDB Server" "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "%~dp0mongo_data" --bind_ip 127.0.0.1

:: Wait for DB to initialize
echo Waiting for Database to start...
timeout /t 5 >nul

:: 3. Start Application
echo Starting Flask Application...
:: Check if python is in path
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please ensure Python is installed and in your PATH.
    pause
    exit /b
)

:: Run app
python app.py
pause
