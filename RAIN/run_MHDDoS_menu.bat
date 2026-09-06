@echo off
setlocal
title RAIN Interactive Menu
cd /d "%~dp0"
chcp 65001 >nul

where python >nul 2>nul
if %errorlevel% equ 0 goto run_python

where py >nul 2>nul
if %errorlevel% equ 0 goto run_py

echo [ERROR] Python was not found on PATH.
echo Install Python 3.11+ from https://www.python.org/downloads/
echo and tick "Add python.exe to PATH" during setup.
pause
exit /b 1

:run_python
python start.py
goto done

:run_py
py -3 start.py

:done
pause
endlocal
