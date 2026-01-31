@echo off
set OMP_NUM_THREADS=4
call "%~dp0venv\Scripts\activate.bat"
python "%~dp0main.py" %*
