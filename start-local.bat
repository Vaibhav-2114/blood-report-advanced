@echo off
REM Start Blood Report Analyzer locally
REM This script opens two terminals: one for backend, one for frontend

echo.
echo ===================================
echo Blood Report Analyzer - Local Start
echo ===================================
echo.
echo Starting Backend (FastAPI) on port 8000...
start cmd /k "cd /d %CD% && .\venv\Scripts\activate.bat && python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 2

echo Starting Frontend (Streamlit) on port 8501...
start cmd /k "cd /d %CD% && .\venv\Scripts\activate.bat && streamlit run frontend/app.py"

echo.
echo ===================================
echo Services starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo ===================================
echo.
echo Close the terminal windows to stop the services.
