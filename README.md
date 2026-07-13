# tails1154OS


This project is part of the Tails1154 Vibe Coding group


Arch Linux + KDE Plasma + Ollama + Trowser — an AI-powered Linux distro.

## Features

- **KDE Plasma** — modern desktop with SDDM, PipeWire, NetworkManager
- **Ollama** — local LLMs preinstalled, pulls models on first boot
- **Trowser** — WebKit browser with built-in Ollama integration
- **Calamares** — graphical installer with AI-themed slideshow
- **BIOS + UEFI** boot support

## Build

```bash
./build.sh build           # build ISO in ./work, output to ./out
./build.sh flash /dev/sda  # build + write to USB
./build.sh copy /dev/sda   # write existing ISO to USB
./build.sh qemu            # boot ISO in QEMU
./build.sh qemu --iso path # boot specific ISO
./build.sh clean           # remove work directory
./build.sh all /dev/sda    # build + copy + qemu
```

Requires `archiso`, `sudo`, and optionally `pv` for progress bars.

## Contributors

<a href="https://github.com/tails1154">
  <img src="https://github.com/tails1154.png" width="50" height="50" alt="tails1154" style="border-radius:50%">
</a>

## License

MIT
