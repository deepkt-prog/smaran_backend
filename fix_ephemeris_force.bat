@echo off
echo ===================================================
echo      Smaran Fix - Force Clean Ephemeris Download
echo ===================================================

echo 1. Stopping any running Python/Smaran processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM uvicorn.exe /T 2>nul

echo.
echo 2. Deleting potentially corrupted 'de421.bsp'...
if exist de421.bsp (
    del /F /Q de421.bsp
    echo    Deleted.
) else (
    echo    File was not found (clean slate).
)

echo.
echo 3. downloading de421.bsp (approx 16MB) using PowerShell...
powershell -Command "Invoke-WebRequest -Uri 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de421.bsp' -OutFile 'de421.bsp'"

if exist de421.bsp (
    echo.
    echo 4. Download successful!
    echo.
    echo 5. Verifying logic now...
    call venv\Scripts\python verify_tithi.py
) else (
    echo.
    echo [ERROR] Download failed. Please check your internet connection.
)

pause
