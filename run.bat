@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    where python >nul 2>nul
    if not errorlevel 1 (
        python -m venv .venv
    ) else (
        py -3 -m venv .venv
    )
    if not exist ".venv\Scripts\python.exe" (
        echo Failed to create virtual environment. Please install Python 3.10+ and add it to PATH.
        pause
        exit /b 1
    )
)

if not exist ".env" copy ".env.example" ".env" >nul

echo [2/3] Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo [3/3] Starting app...
".venv\Scripts\python.exe" main.py
