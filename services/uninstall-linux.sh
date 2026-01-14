#!/bin/bash
# Uninstallation script for Deep Freeze Auto-Restore Service (Linux/systemd)

set -e

SERVICE_NAME="deepfreeze-restore.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo "Error: systemd is not available on this system"
    exit 1
fi

# Check if service exists
if [ ! -f "${SERVICE_FILE}" ]; then
    echo "Service is not installed"
    exit 0
fi

echo "Uninstalling Deep Freeze Auto-Restore Service..."

# Stop the service if running
systemctl stop "${SERVICE_NAME}" 2>/dev/null || true

# Disable the service
systemctl disable "${SERVICE_NAME}" 2>/dev/null || true

# Remove service file
rm -f "${SERVICE_FILE}"

# Reload systemd daemon
systemctl daemon-reload

# Reset failed status if any
systemctl reset-failed "${SERVICE_NAME}" 2>/dev/null || true

echo "✓ Service uninstalled successfully"
