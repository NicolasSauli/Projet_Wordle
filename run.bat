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

:: Start backend server
echo Demarrage du serveur backend sur http://localhost:8000...
start "Wordle Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend server
echo Demarrage du serveur frontend sur http://localhost:3000...
start "Wordle Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ===============================
echo   Serveurs demarres!
echo ===============================
echo.
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Fermez les fenetres de commande pour arreter les serveurs
echo.

:: Open browser
start http://localhost:3000

pause
