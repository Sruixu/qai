@echo off
echo Starting QAI Platform...
cd /d "%~dp0"

:: Check for python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.10+ and add to PATH.
    pause
    exit /b
)

:: Install dependencies
echo Installing dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b
)

:: Start server
echo.
echo ========================================================
echo QAI Server starting...
echo.
echo [Your Access Address]: http://localhost:8000
echo.
echo [Team Access Address]:
ipconfig | findstr "IPv4"
echo (Use the IP address above with port 8000, e.g., http://192.168.1.5:8000)
echo.
echo IMPORTANT: If others cannot connect, please check your Firewall settings
echo and allow port 8000 or the python process.
echo.
echo Press Ctrl+C to stop.
echo ========================================================
echo.

uvicorn main:app --host 0.0.0.0 --port 8000

pause
