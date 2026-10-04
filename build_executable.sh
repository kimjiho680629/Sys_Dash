#!/usr/bin/env bash
# ==============================================================================
# Sys_Dash Standalone One-File Executable Builder
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[+] Checking build environment..."
if [ ! -d ".venv" ]; then
    echo "[-] Virtual environment not found. Please setup .venv first."
    exit 1
fi

echo "[+] Ensuring PyInstaller is installed..."
.venv/bin/pip install --quiet pyinstaller

echo "[+] Building standalone executable binary (One-File)..."
.venv/bin/pyinstaller sys_dash.spec --clean --noconfirm

echo "[+] Updating root symlink..."
ln -sf dist/sys-dash sys-dash

echo "[✓] Build complete: dist/sys-dash"
ls -lh dist/sys-dash
