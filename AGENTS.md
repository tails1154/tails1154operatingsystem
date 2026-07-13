# AGENTS.md

## Build

- `./build.sh` delegates to `build.py`. Always edit `build.py`, not `build.sh`.
- Uses `mkarchiso` from the `archiso` package. `profiledef.sh` controls ISO metadata.
- Squashfs uses `zstd` compression (fast, not xz). Set in `profiledef.sh`.

## Packages

- `packages.x86_64` is the package manifest for the live ISO.
- `pacman.conf` has a local repo `[tails1154os]` at an **absolute path** that only works on the host machine. If cloning elsewhere, remove or fix this repo entry.
- `localrepo/` contains Calamares (built from AUR since it's not in official repos).
- Trowser is pre-installed in `airootfs/usr/bin/` via `pip install --root`. Re-run `pip install` if Trowser source changes.
- Flatpak apps (Sober, Vesktop) are NOT pre-installed in the ISO — they're installed on first boot by `tails1154-firstboot`.

## Calamares

- Calamares was built from AUR with `initramfs` and `initramfscfg` modules skipped (`SKIP_MODULES` in PKGBUILD). **Do not add them to the sequence.**
- Module instance keys use `module@id` format (e.g. `shellprocess@ollama-setup`, `notesqml@ai-welcome`).
- Configs are in `airootfs/etc/calamares/`. The branding slideshow is at `airootfs/usr/share/calamares/branding/tails1154os/`.

## First boot

- `tails1154-firstboot` (`airootfs/usr/local/bin/`) runs via XDG autostart on first login. It kills `plasmashell` and `krunner` to lock the user, downloads AI models, installs Flathub apps, then restarts Plasma. This is intentional.

## Boot

- `copytoram=0` is set in GRUB and systemd-boot configs (in `grub/` and `efiboot/`). The live system does not copy the squashfs to RAM.
- Boot beeps are disabled (NOBEEP in syslinux, no `beep on` in systemd-boot, no GRUB init tune).

## Cleaning

- `./build.sh clean` runs `umount -R work/`, `losetup -D`, then `rm -rf work/`. If write errors occur, lazy unmount (`umount -l`) the specific mount first.
