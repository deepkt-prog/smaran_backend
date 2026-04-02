@echo off
echo Stopping any running Smaran processes...
taskkill /F /IM python.exe /T 2>nul
echo.
echo Deleting corrupted ephemeris file...
if exist de421.bsp del /F /Q de421.bsp
echo.
echo Redownloading ephemeris file and verifying logic...
call venv\Scripts\python verify_tithi.py
echo.
echo Fix complete. You can now run run.bat again.
pause
