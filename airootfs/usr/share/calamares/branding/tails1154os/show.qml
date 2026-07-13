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
            "Arch Linux + KDE Plasma + AI",
            "Welcome to the future of desktop computing.",
            "",
            "This installer will guide you through setting up",
            "your AI-powered operating system.",
        ]
        textFormat: Text.RichText
    }

    Slide {
        title: "Built-in AI with Ollama"
        content: [
            "Ollama is pre-installed and ready to go.",
            "Run local LLMs without any cloud dependency.",
            "",
            "Pre-configured models:",
            "  - llama3.2:3b (lightweight chat)",
            "  - qwen2.5:1.5b (fast inference)",
            "",
            "Pull more models anytime: ollama pull <model>",
        ]
    }

    Slide {
        title: "Trowser - AI Web Browser"
        content: [
            "Trowser is a WebKit-based browser with",
            "built-in Ollama integration for AI-powered",
            "browsing and local assistance.",
            "",
            "Features:",
            "  - Encrypted password vault",
            "  - TailsAccount cloud sync",
            "  - Local AI chatbot integration",
            "  - Privacy-first design",
        ]
    }

    Slide {
        title: "KDE Plasma Desktop"
        content: [
            "Beautiful, modern desktop environment.",
            "Fully customizable with widgets, themes,",
            "and Plasma Addons.",
            "",
            "Includes:",
            "  - SDDM display manager",
            "  - PipeWire audio",
            "  - NetworkManager",
            "  - Full KDE Applications suite",
        ]
    }

    Slide {
        title: "Get Started"
        content: [
            "You're about to install tails1154OS.",
            "Follow the steps ahead to configure:",
            "",
            "  1. Language & Location",
            "  2. Keyboard Layout",
            "  3. Disk Partitioning",
            "  4. User Account",
            "  5. Installation Summary",
            "",
            "AI models will be pulled on first boot.",
        ]
    }

    function onActivate() {
        presentation.currentSlide = 0;
    }

    function onLeave() {
    }
}
