@echo off
rem SCL Plugin Downloader batch script
rem This script runs sdp.py without opening a new CMD window

rem Get the directory of this script
set "SCRIPT_DIR=%~dp0"

rem Run the Python script using cmd /c to ensure output is visible in PowerShell
cmd /c "python "%SCRIPT_DIR%sdp.py" %*"
