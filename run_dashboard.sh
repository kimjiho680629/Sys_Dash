#!/usr/bin/env bash
# ==============================================================================
# Cyberpunk Sci-Fi Telemetry Dashboard Runner
# Target: HDMI-A-1 (ARZOPA 2K 144Hz Monitor)
# Hardware: AMD Ryzen 7 9800X3D + NVIDIA GeForce RTX 5070 Ti
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 가상환경 검사
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "[-] Virtual environment (.venv) not found. Creating..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    "$SCRIPT_DIR/.venv/bin/pip" install PyQt6 nvidia-ml-py psutil
fi

# Wayland 환경 최적화
export QT_QPA_PLATFORM="wayland;xcb"
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}"

echo "[+] Launching Cyberpunk System HUD on HDMI-A-1..."
exec "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/main.py" "$@"
