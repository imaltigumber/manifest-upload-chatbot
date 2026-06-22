@echo off
setlocal
cd /d "%~dp0"

echo =====================================================
echo   Client Onboarding Chatbot
echo =====================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [INFO]  Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting Client Onboarding Chatbot...
echo   URL : http://localhost:8502
echo.
echo Press Ctrl+C to stop.
echo.

start "" /b cmd /c "timeout /t 2 >nul && start http://localhost:8502"

streamlit run app.py ^
    --server.port 8502 ^
    --server.address localhost ^
    --browser.gatherUsageStats false ^
    --server.headless true

pause
