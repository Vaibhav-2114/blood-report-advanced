@echo off
setlocal
REM Start the Blood Report Analyzer backend and frontend in separate terminals.

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found.
    echo Create it with: py -m venv .venv
    echo Then install dependencies with: .venv\Scripts\python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting FastAPI backend at http://127.0.0.1:8000 ...
start "Blood Report Analyzer API" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 2 /nobreak >nul

echo Starting Streamlit frontend at http://localhost:8501 ...
start "Blood Report Analyzer UI" cmd /k "call .venv\Scripts\activate.bat && streamlit run frontend/app.py"

echo.
echo Backend: http://127.0.0.1:8000
echo API docs: http://127.0.0.1:8000/docs
echo Frontend: http://localhost:8501
echo Close the two service windows to stop the app.
endlocal
