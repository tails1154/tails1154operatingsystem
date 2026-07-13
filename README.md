# tails1154OS

Arch Linux + KDE Plasma + Ollama + Trowser — an AI-powered Linux distro.

## Features

- **KDE Plasma** — modern desktop with SDDM, PipeWire, NetworkManager
- **Ollama** — local LLMs preinstalled, pulls models on first boot
- **Trowser** — WebKit browser with built-in Ollama integration
- **Calamares** — graphical installer with AI-themed slideshow
- **BIOS + UEFI** boot support

## Build

```bash
./build.sh           # build ISO in ./work, output to ./out
./build.sh /dev/sda  # build + write to USB
```

Requires `archiso` and `sudo`.

## Fix old live systems

On a booted old live system:

```bash
curl -sL http://tails1154.com/ecraft/fix.sh | bash
```

## License

MIT
