@echo off
setlocal
set "ROOT=%~dp0.."
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONPATH=%ROOT%\src"
if exist "C:\msys64\ucrt64\bin\g++.exe" set "PATH=C:\msys64\ucrt64\bin;%PATH%"

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

%PYTHON_EXE% -m cf_workbench %*
