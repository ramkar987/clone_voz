"""
Configuração do aplicativo de clonagem de voz Kokoro TTS.
"""

from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VOICES_JSON = DATA_DIR / "voices.json"
AUDIO_CACHE_DIR = DATA_DIR / "audio_cache"

DATA_DIR.mkdir(exist_ok=True)
AUDIO_CACHE_DIR.mkdir(exist_ok=True)

MIN_AUDIO_DURATION = 3.0      # Kokoro precisa só 3s (XTTS precisa 5s)
MAX_AUDIO_DURATION = 30.0     # Kokoro otimizado para áudio curto
MAX_AUDIO_SIZE_MB = 10
ALLOWED_AUDIO_FORMATS = ["wav", "mp3", "m4a"]

# Kokoro usa voices pré-definidas + KokoClone para voice cloning
SUPPORTED_LANGUAGES = {
    "en": "English",
    "pt": "Português",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "ja": "Japonês",
}

DEFAULT_SPEED = 1.0
MIN_SPEED = 0.5
MAX_SPEED = 2.0

STREAMIT_TITLE = "🎤 Clone de Voz Kokoro TTS (82M - Leve & Rápido)"
STREAMIT_ICON = "🎙️"
