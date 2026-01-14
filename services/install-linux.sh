#!/bin/bash
# Installation script for Deep Freeze Auto-Restore Service (Linux/systemd)

set -e

SERVICE_NAME="deepfreeze-restore.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SERVICE="${SCRIPT_DIR}/${SERVICE_NAME}"

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

# Check if freeze command is available
if ! command -v freeze &> /dev/null; then
    echo "Error: 'freeze' command not found. Please install Deep Freeze first."
    exit 1
fi

echo "Installing Deep Freeze Auto-Restore Service..."

# Copy service file to systemd directory
cp "${SOURCE_SERVICE}" "${SERVICE_FILE}"

# Reload systemd daemon
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable "${SERVICE_NAME}"

echo "✓ Service installed successfully"
echo ""
echo "The service will now run automatically on every boot to restore"
echo "the default Deep Freeze snapshot."
echo ""
echo "Useful commands:"
echo "  - Check status: sudo systemctl status ${SERVICE_NAME}"
echo "  - View logs: sudo journalctl -u ${SERVICE_NAME}"
echo "  - Test now: sudo systemctl start ${SERVICE_NAME}"
echo "  - Disable: sudo systemctl disable ${SERVICE_NAME}"
echo "  - Uninstall: Run the uninstall script"
