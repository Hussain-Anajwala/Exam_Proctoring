@echo off
echo Starting Unified Exam Proctoring System...
echo ================================================
echo.

REM Try to start the server
python start_server.py

REM If that fails, try alternative port
if %errorlevel% neq 0 (
    echo.
    echo Port 8000 failed, trying port 8080...
    python start_server_alt.py
)

pause
