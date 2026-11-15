SUMMARY = "Lazy OS Full Assistant Image"
DESCRIPTION = "Full distribution profile with resident LLM engine, Vosk STT, TTS, HUD, and isolated browser runtime."
LICENSE = "MIT"

require lazy-image-base.bb

IMAGE_INSTALL:append = " \
    llama-cpp \
    lazy-model-smollm \
    vosk-api \
    lazy-voice-model \
    espeak-ng \
    alsa-utils \
    lazy-browser \
"
