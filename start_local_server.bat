@echo off
echo ========================================
echo   MOMENTUM CLIPS - Local Server
echo ========================================
echo.
echo Starting Flask development server...
echo.
echo Server will be available at:
echo   http://127.0.0.1:5000
echo   http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

pause

