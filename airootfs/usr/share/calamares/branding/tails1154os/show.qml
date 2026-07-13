import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation
    Timer {
        interval: 5000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }
    Slide {
        title: "tails1154OS"
        content: [
            "Arch Linux + KDE Plasma + AI + Gaming",
            "The most bloat-maxxed distro on Earth.",
            "",
            "Built-in AI, Steam, Roblox (via Sober Flatpak),",
            "and every useless terminal toy you could want.",
        ]
    }
    Slide {
        title: "Built-in AI with Ollama"
        content: [
            "Ollama is pre-installed.",
            "Run local LLMs: llama3.2, qwen2.5, and more.",
            "Pull models on first boot or anytime:",
            "  ollama pull <model>",
            "",
            "Trowser browser has built-in Ollama chat.",
        ]
    }
    Slide {
        title: "Gaming Ready"
        content: [
            "Steam + Steam Devices pre-installed.",
            "Gamescope for compositor-free gaming.",
            "Flatpak with Sober (Roblox) ready to go.",
            "Discover app center for all your apps.",
        ]
    }
    Slide {
        title: "Essential Bloatware"
        content: [
            "cowsay, figlet, lolcat, cmatrix,",
            "sl, fortune-mod, ponysay...",
            "All the terminal nonsense you'll never use",
            "but definitely need.",
        ]
    }
    Slide {
        title: "KDE Plasma Desktop"
        content: [
            "Beautiful, modern, customizable.",
            "SDDM display manager, PipeWire audio,",
            "NetworkManager, and full KDE suite.",
        ]
    }
    Slide {
        title: "Get Started"
        content: [
            "Follow the steps to install.",
            "AI models pull on first boot.",
            "Install Sober for Roblox:",
            "  flatpak install flathub org.vinegarhq.Sober",
            "",
            "Welcome to the bloat. Welcome home.",
        ]
    }
    function onActivate() { presentation.currentSlide = 0; }
    function onLeave() {}
}
