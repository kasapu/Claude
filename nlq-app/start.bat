@echo off
echo.
echo 🚀 Starting Natural Language Query System...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found! Copying from .env.example...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your ANTHROPIC_API_KEY
    echo ⚠️  Then run this script again.
    pause
    exit /b 1
)

echo.
echo ✅ Setup complete!
echo.
echo Starting servers...
echo.

REM Start backend
echo 🔵 Starting backend server (http://localhost:8000)...
start "NLQ Backend" cmd /k "cd backend\api && python main.py"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
echo 🟢 Starting frontend server (http://localhost:3000)...
start "NLQ Frontend" cmd /k "cd frontend\public && python -m http.server 3000"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✨ NLQ System is running!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📊 Frontend:  http://localhost:3000
echo 🔌 Backend:   http://localhost:8000
echo 📚 API Docs:  http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the servers
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
