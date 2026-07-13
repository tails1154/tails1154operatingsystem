#!/usr/bin/env bash
set -euo pipefail

ISO_OUTPUT_DIR="$(dirname "$0")/out"
PROFILE_DIR="$(dirname "$0")"
WORK_DIR="$(dirname "$0")/work"

echo "==> Cleaning up old build artifacts..."
sudo umount -R "$WORK_DIR" 2>/dev/null || true
sudo losetup -D 2>/dev/null || true
sudo rm -rf "$WORK_DIR"
mkdir -p "$ISO_OUTPUT_DIR"

echo "==> Building tails1154OS ISO..."
sudo mkarchiso -v -w "$WORK_DIR" -o "$ISO_OUTPUT_DIR" "$PROFILE_DIR"

ISO=$(ls -t "$ISO_OUTPUT_DIR"/*.iso 2>/dev/null | head -1)
echo "==> Done! ISO: $ISO"

if [[ -z "${1:-}" ]]; then
    exit 0
fi

DEVICE="$1"
echo "==> Writing ISO to $DEVICE with dd..."
sudo dd if="$ISO" of="$DEVICE" bs=4M status=progress oflag=sync
echo "==> Done! $DEVICE is bootable with tails1154OS"
