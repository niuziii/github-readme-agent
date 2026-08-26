@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv
)

if not exist ".env" copy ".env.example" ".env" >nul

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Building executable...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --distpath . --name "GitHubReadmeAgent" main.py
if errorlevel 1 goto :error

echo.
echo Build succeeded: dist\GitHubReadmeAgent.exe
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
