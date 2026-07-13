#!/usr/bin/env bash
set -eo pipefail

PROFILE_DIR="$(cd "$(dirname "$0")" && pwd)"
ISO_OUTPUT_DIR="$PROFILE_DIR/out"
WORK_DIR="$PROFILE_DIR/work"
SCRIPT_NAME="$(basename "$0")"

R='\033[0;31m'; G='\033[0;32m'; Y='\033[1;33m'; C='\033[0;36m'; N='\033[0m'
log()  { echo -e "${C}[$(date '+%H:%M:%S')]${N} $*"; }
ok()   { echo -e "  ${G}OK${N}  $*"; }
err()  { echo -e "  ${R}FAIL${N} $*" >&2; }
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [device]

Builds the tails1154OS ISO.

If a device path is given (e.g. /dev/sda), the ISO is written to it with dd after building.

Environment:
  SUDO    sudo command to use (default: sudo)
EOF
    exit 0
}

[[ "${1:-}" =~ ^(-h|--help)$ ]] && usage

SUDO="${SUDO:-sudo}"

cleanup() {
    log "Cleaning up build environment..."
    while read -r mount_point; do
        $SUDO umount -l "$mount_point" 2>/dev/null && log "  Unmounted: $mount_point" || true
    done < <(mount | grep "$WORK_DIR" | awk '{print $3}' | tac)
    $SUDO losetup -D 2>/dev/null || true
    $SUDO rm -rf "$WORK_DIR" && log "  Removed: $WORK_DIR" || true
}

# Prerequisites check
for cmd in mkarchiso "$SUDO"; do
    if ! command -v "$cmd" &>/dev/null; then
        err "$cmd not found. Install archiso and ensure sudo access."
        exit 1
    fi
done

# Clean previous build
cleanup
mkdir -p "$ISO_OUTPUT_DIR"

# Build
log "Starting ISO build..."
$SUDO mkarchiso -v -w "$WORK_DIR" -o "$ISO_OUTPUT_DIR" "$PROFILE_DIR"
log "Build complete."

# Show result
ISO=$(ls -t "$ISO_OUTPUT_DIR"/*.iso 2>/dev/null | head -1)
if [[ -z "$ISO" ]]; then
    err "No ISO found in $ISO_OUTPUT_DIR"
    exit 1
fi
log "ISO: $ISO ($(du -h "$ISO" | cut -f1))"

# Optional dd to device
if [[ -z "${1:-}" ]]; then
    exit 0
fi

if [[ ! -b "$1" ]]; then
    err "$1 is not a block device"
    exit 1
fi

log "Writing ISO to $1..."
$SUDO dd if="$ISO" of="$1" bs=4M status=progress oflag=sync
log "Done! $1 is bootable."
