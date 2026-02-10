@echo off
rem SunsetCodeLang batch script
rem This script allows running scl command directly on Windows

rem Get the directory of this script
set "SCRIPT_DIR=%~dp0"

rem Check if the first argument is 'sdp'
if "%1"=="sdp" (
    shift
    pythonw "%SCRIPT_DIR%sdp.py" %*
    goto :end
)

rem Run the Python interpreter with scl.py script
pythonw "%SCRIPT_DIR%scl.py" %*

:end
