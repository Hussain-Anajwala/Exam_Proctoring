@echo off
echo Starting Exam Proctoring System Frontend...
echo ================================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    echo.
)

echo Starting development server...
echo Frontend will be available at: http://localhost:5173
echo Make sure the Python server is running on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
