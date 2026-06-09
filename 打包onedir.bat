@echo off
chcp 65001 >nul
echo ========================================
echo   Port Killer - Build EXE (Onedir)
echo ========================================
echo.

echo [1/3] Checking Python...
"C:\msys64\mingw64\bin\python.exe" --version
if errorlevel 1 (
    echo ERROR: Python not found at C:\msys64\mingw64\bin\python.exe
    echo Please update this .bat file with your correct Python path.
    pause
    exit /b 1
)
echo OK.
echo.

echo [2/3] Installing PyInstaller...
"C:\msys64\mingw64\bin\python.exe" -m pip install pyinstaller -q
if errorlevel 1 (
    echo WARNING: pip install may have failed, trying to continue...
)
echo OK.
echo.

echo [3/3] Building EXE (onedir mode)...
"C:\msys64\mingw64\bin\python.exe" -m PyInstaller --clean --noconfirm --onedir --windowed --icon=app.ico --add-data "app.ico;." --name "PortKiller" portkiller.py
echo.

if exist "dist\PortKiller\PortKiller.exe" (
    echo ========================================
    echo   Build SUCCESS!
    echo   EXE location: dist\PortKiller\PortKiller.exe
    echo   Run directly from that folder.
    echo ========================================
) else (
    echo ========================================
    echo   Build may have failed, check output above.
    echo ========================================
)

echo.
pause
