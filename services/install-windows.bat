@echo off
REM Installation script for Deep Freeze Auto-Restore Service (Windows)

echo Installing Deep Freeze Auto-Restore Service...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script must be run as Administrator
    exit /b 1
)

REM Check if freeze command is available
where freeze >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: 'freeze' command not found. Please install Deep Freeze first.
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Import the scheduled task
schtasks /Create /XML "%SCRIPT_DIR%deepfreeze-restore.xml" /TN "DeepFreezeAutoRestore" /F

if %errorLevel% equ 0 (
    echo.
    echo Success: Service installed successfully
    echo.
    echo The scheduled task will now run automatically on every boot to restore
    echo the default Deep Freeze snapshot.
    echo.
    echo Useful commands:
    echo   - Check status: schtasks /Query /TN "DeepFreezeAutoRestore"
    echo   - Test now: schtasks /Run /TN "DeepFreezeAutoRestore"
    echo   - Disable: schtasks /Change /TN "DeepFreezeAutoRestore" /DISABLE
    echo   - Uninstall: Run the uninstall script
) else (
    echo Error: Failed to install service
    exit /b 1
)
