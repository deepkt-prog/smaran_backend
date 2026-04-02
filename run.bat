@echo off
echo Starting Smaran Application...
call venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0
pause
