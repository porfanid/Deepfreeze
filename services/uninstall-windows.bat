@echo off
REM Uninstallation script for Deep Freeze Auto-Restore Service (Windows)

echo Uninstalling Deep Freeze Auto-Restore Service...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: This script must be run as Administrator
    exit /b 1
)

REM Check if task exists
schtasks /Query /TN "DeepFreezeAutoRestore" >nul 2>&1
if %errorLevel% neq 0 (
    echo Service is not installed
    exit /b 0
)

REM Delete the scheduled task
schtasks /Delete /TN "DeepFreezeAutoRestore" /F

if %errorLevel% equ 0 (
    echo Success: Service uninstalled successfully
) else (
    echo Error: Failed to uninstall service
    exit /b 1
)
