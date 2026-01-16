@echo off
REM ==========================================
REM Python Virtual Environment Setup (Windows)
REM ==========================================

REM Check if python is available
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies if requirements.txt exists
IF EXIST requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Virtual environment ready.
echo To activate later, run:
echo     venv\Scripts\activate
pause
