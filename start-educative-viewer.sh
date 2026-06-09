#!/usr/bin/env bash

# Educative Viewer Service Installer
# Installs systemd user service for Docker-based auto-start

set -e

echo "=== Educative Viewer Service Installer ==="

# Setup user systemd service


mkdir --parents ~/.config/systemd/user
cp educative-viewer.service ~/.config/systemd/user/
echo "✓ Service file installed"

# Enable and start
systemctl --user daemon-reload
systemctl --user enable educative-viewer.service
loginctl enable-linger "$(whoami)" 2>/dev/null || true
systemctl --user start educative-viewer.service
echo "✓ Service enabled and started"

# Verify
sleep 2
if systemctl --user is-active educative-viewer.service | grep -q "active"; then
    echo "✓ Service is running"
else
    echo "⚠ Service may not be running. Check: systemctl --user status educative-viewer"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Commands:"
echo "  systemctl --user {start|stop|restart|status} educative-viewer"
echo "  journalctl --user -u educative-viewer -f"
echo "  tailscale serve status"
echo ""
echo "Access:"
echo "  Local:     http://localhost:5001/edu-viewer/"
echo "  Tailscale: https://$(tailscale status --json 2>/dev/null | jq -r '.Self.DNSName' 2>/dev/null | sed 's/\.$//' || echo '<your-machine>.ts.net')/edu-viewer/"
