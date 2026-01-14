@echo off
echo ===============================
echo    WORDLE MULTIPLAYER
echo ===============================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installe. Veuillez l'installer depuis python.org
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
echo Installation des dependances...
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt -q

:: Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%a
    goto :found
)
:found
set LOCAL_IP=%LOCAL_IP:~1%

echo.
echo ===============================
echo   Server is running!
echo ===============================
echo.
echo   Local:   http://localhost:8000
echo   Network: http://%LOCAL_IP%:8000
echo.
echo   Share the Network URL with friends!
echo.
echo   Press Ctrl+C to stop
echo.

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
