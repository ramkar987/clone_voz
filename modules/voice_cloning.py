"""Module para clonagem de voz com Kokoro TTS."""

import json
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import VOICES_JSON


def init_kokoro_pipeline() -> Optional[object]:
    try:
        from kokoro import KPipeline
        st.info("⚙️ Carregando Kokoro TTS (82M params)...")
# Se quiser o modelo em Inglês Americano:
        pipeline = KPipeline(lang_code='a')

# OU, se o seu projeto for focado em Português:
# pipeline = KPipeline(lang_code='p')
        st.success("✅ Kokoro carregado! (86MB, 3-5x mais rápido)")
        return pipeline
    except ImportError as e:
        st.error(f"❌ Biblioteca não instalada: {e}")
        return None


def generate_voice_id(audio_bytes: bytes, name: str) -> str:
    hash_input = f"{name}:{len(audio_bytes)}:{audio_bytes[:1000].hex()}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:16]


def save_voice(name: str, audio_bytes: bytes, duration: float, language: str = "pt") -> Optional[Dict]:
    try:
        voice_id = generate_voice_id(audio_bytes, name)
        cache_path = VOICES_JSON.parent / f"{voice_id}.wav"
        
        with open(cache_path, "wb") as f:
            f.write(audio_bytes)
        
        voices = load_voices()
        voice_metadata = {
            "voice_id": voice_id,
            "name": name,
            "duration": duration,
            "language": language,
            "created_at": datetime.now().isoformat(),
            "sample_path": str(cache_path),
        }
        
        voices[voice_id] = voice_metadata
        
        with open(VOICES_JSON, "w", encoding="utf-8") as f:
            json.dump(voices, f, indent=2, ensure_ascii=False)
        
        return voice_metadata
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        return None


def load_voices() -> Dict:
    if not VOICES_JSON.exists(): return {}
    try:
        with open(VOICES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}


def get_voice_list() -> List[Dict]:
    voices = load_voices()
    return [{"voice_id": v["voice_id"], "name": v["name"], "created_at": v["created_at"]} for v in voices.values()]


def delete_voice(voice_id: str) -> bool:
    try:
        voices = load_voices()
        if voice_id not in voices: return False
        
        sample_path = voices[voice_id]["sample_path"]
        if os.path.exists(sample_path): os.remove(sample_path)
        del voices[voice_id]
        
        with open(VOICES_JSON, "w", encoding="utf-8") as f:
            json.dump(voices, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        return False


KOKORO_VOICES = {
    "af_sarah": "Sarah (Female, American)",
    "af_alice": "Alice (Female, American)",
    "af_bella": "Bella (Female, American)",
    "am_james": "James (Male, American)",
    "am_michael": "Michael (Male, American)",
    "pf_snowy": "Snowy (Female, Portuguese)",
    "pm_alex": "Alex (Male, Portuguese)",
}


def get_kokoro_native_voices() -> List[Dict]:
    return [{"voice_id": vid, "name": nome, "created_at": "native", "is_native": True} for vid, nome in KOKORO_VOICES.items()]
