@echo off
REM Startup script for Document QA Agent (Windows)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found. Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Install dependencies if needed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
echo Starting Document QA Agent...
streamlit run app.py

pause
