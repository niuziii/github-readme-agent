@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv
)

if not exist ".env" copy ".env.example" ".env" >nul

".venv\Scripts\python.exe" -m pip install -r requirements.txt >nul
".venv\Scripts\python.exe" main.py
