@echo off
REM Build script (Windows) — run from project folder
set APP=app.py
set ICON=icon.ico
set ASSETS=assets

REM Check if assets folder exists
if exist %ASSETS% (
    set ADDDATA=--add-data "%ASSETS%;%ASSETS%"
) else (
    set ADDDATA=
)

pyinstaller --onefile --windowed --icon=%ICON% %ADDDATA% %APP%

if %ERRORLEVEL% equ 0 (
    echo Build finished. Output in dist\%~nAPP%.exe
) else (
    echo PyInstaller failed with error %ERRORLEVEL%
)
