#!/usr/bin/env python3
"""tails1154OS builder - build ISOs, copy to USB, run in QEMU."""

import argparse
import subprocess
import shutil
import os
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
OUT = ROOT / "out"
ISO_PATTERN = "tails1154os-*.iso"

def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}")

def run(cmd, **kw):
    log(f"Running: {' '.join(str(c) for c in cmd)}")
    kw.setdefault('check', True)
    return subprocess.run(cmd, **kw)

def find_iso():
    isos = sorted(OUT.glob(ISO_PATTERN))
    return str(isos[-1]) if isos else None

def cmd_build(args):
    log("Cleaning up...")
    run(["sudo", "umount", "-R", str(WORK)], check=False)
    run(["sudo", "losetup", "-D"], check=False)
    if WORK.exists():
        shutil.rmtree(WORK, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)

    log("Building ISO...")
    run(["sudo", "mkarchiso", "-v", "-w", str(WORK), "-o", str(OUT), str(ROOT)])

    iso = find_iso()
    if iso:
        size = os.path.getsize(iso)
        log(f"ISO: {iso} ({size / 1024 / 1024:.0f} MiB)")
    return iso

def cmd_copy(args):
    iso = args.iso or find_iso()
    if not iso or not os.path.exists(iso):
        log("ERROR: no ISO found. Build one first or pass --iso.")
        sys.exit(1)

    log(f"Writing {iso} to {args.device}...")
    size = os.path.getsize(iso)
    if shutil.which("pv"):
        subprocess.run(f"pv -s {size} '{iso}' | sudo dd of='{args.device}' bs=100M oflag=sync", shell=True, check=True)
    else:
        run(["sudo", "dd", f"if={iso}", f"of={args.device}", "bs=100M", "status=progress", "oflag=sync"])
    log(f"Done! {args.device} is bootable.")

def cmd_qemu(args):
    iso = args.iso or find_iso()
    if not iso or not os.path.exists(iso):
        log("ERROR: no ISO found. Build one first or pass --iso.")
        sys.exit(1)

    mem = getattr(args, 'memory', "4G")
    log(f"Launching QEMU with {mem} RAM...")
    run([
        "qemu-system-x86_64", "-m", mem, "-cdrom", iso,
        "-boot", "d", "-vga", "virtio", "-display", "gtk",
        "-cpu", "host", "-enable-kvm", "-smp", "4",
        "-netdev", "user,id=net0", "-device", "e1000,netdev=net0",
    ])

def cmd_clean(args):
    log("Cleaning up...")
    run(["sudo", "umount", "-R", str(WORK)], check=False)
    run(["sudo", "losetup", "-D"], check=False)
    if WORK.exists():
        shutil.rmtree(WORK, ignore_errors=True)
    log("Clean.")

def main():
    p = argparse.ArgumentParser(description="tails1154OS builder")
    p.add_argument("--iso", help="Path to existing ISO (skip build)")

    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("build", help="Build ISO from source")
    sub.add_parser("clean", help="Remove work directory")

    copy = sub.add_parser("copy", help="Write ISO to USB")
    copy.add_argument("device", help="e.g. /dev/sda")
    copy.add_argument("--iso", help="ISO path (default: latest in out/)")

    qemu = sub.add_parser("qemu", help="Boot ISO in QEMU")
    qemu.add_argument("--iso", help="ISO path (default: latest in out/)")
    qemu.add_argument("-m", "--memory", default="4G", help="RAM (default: 4G)")

    flash = sub.add_parser("flash", help="Build + copy to USB (no QEMU)")
    flash.add_argument("device", help="e.g. /dev/sda")

    all_p = sub.add_parser("all", help="Build + copy + qemu in sequence")
    all_p.add_argument("device", nargs="?", help="USB device (optional)")
    all_p.add_argument("--memory", default="4G")
    all_p.add_argument("--skip-copy", action="store_true")
    all_p.add_argument("--skip-qemu", action="store_true")

    args = p.parse_args()

    if args.command == "build":
        cmd_build(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "copy":
        cmd_copy(args)
    elif args.command == "qemu":
        cmd_qemu(args)
    elif args.command == "flash":
        iso = cmd_build(args)
        args.iso = iso
        cmd_copy(args)
    elif args.command == "all":
        iso = cmd_build(args)
        args.iso = iso
        if not getattr(args, 'skip_copy', False) and args.device:
            cmd_copy(args)
        if not getattr(args, 'skip_qemu', False):
            cmd_qemu(args)

if __name__ == "__main__":
    main()
