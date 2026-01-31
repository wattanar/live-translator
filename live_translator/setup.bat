@echo off
echo Creating virtual environment...
python -m venv "%~dp0venv"
echo Installing dependencies...
"%~dp0venv\Scripts\pip" install -r "%~dp0requirements.txt"
echo Setup complete. Use run.bat to start the application.
pause
