@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"

set "PYTHON_EXE="
py -3.11 -V >nul 2>nul
if not errorlevel 1 set "PYTHON_EXE=py -3.11"
if not defined PYTHON_EXE (
    py -3 -V >nul 2>nul
    if not errorlevel 1 set "PYTHON_EXE=py -3"
)
if not defined PYTHON_EXE (
    python -V >nul 2>nul
    if not errorlevel 1 set "PYTHON_EXE=python"
)
if not defined PYTHON_EXE (
    echo Python 3.11 or newer was not found. Install Python from https://www.python.org/downloads/
    exit /b 1
)

%PYTHON_EXE% "%~dp0cfw_workbench_launcher.py" %*
if errorlevel 1 (
    echo cf-workbench failed to start. Check .cfw\logs\cfw-workbench.err.log
    pause
)
