@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo DataGuard Agent - Windows Installation
echo ========================================

where py >nul 2>nul
if %errorlevel%==0 (
  py -3.12 -m venv .venv 2>nul
  if not exist ".venv\Scripts\python.exe" py -3.11 -m venv .venv 2>nul
  if not exist ".venv\Scripts\python.exe" py -m venv .venv
) else (
  python -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
  echo Could not create .venv.
  echo Install Python 3.11 or 3.12 and try again.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Installation complete.
echo Next: run run_windows.bat
pause
