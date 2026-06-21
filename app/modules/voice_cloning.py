"""
Module para clonagem de voz usando Kokoro TTS + KokoClone.
Kokoro tem voice cloning nativo mais simples que XTTS.
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

import streamlit as st
from config import VOICES_JSON, SUPPORTED_LANGUAGES


def init_kokoro_pipeline() -> Optional[object]:
    """
    Inicializa Kokoro TTS pipeline.
    
    Returns:
        KPipeline instanciado, ou None se erro.
    """
    try:
        from kokoro import KPipeline
        
        st.info("⚙️ Carregando Kokoro TTS (82M params)...")
        
        # Kokoro é muito mais rápido para carregar (~10s vs 2min do XTTS)
        pipeline = KPipeline(lang_code='en')  # Carrega modelo base
        
        st.success("✅ Kokoro TTS carregado! (86MB, 3-5x mais rápido que XTTS)")
        return pipeline
    
    except ImportError as e:
        st.error(f"❌ Biblioteca não instalada: {e}")
        st.info("💡 Execute: pip install -r requirements.txt")
        return None


def init_kokoclone() -> Optional[object]:
    """
    Inicializa KokoClone para voice cloning.
    
    Returns:
        KokoClone instanciado, ou None.
    """
    try:
        from kokoclone import KokoClone
        
        st.info("🔄 Carregando KokoClone para voice cloning...")
        cloner = KokoClone()
        st.success("✅ KokoClone carregado!")
        return cloner
    
    except ImportError:
        st.warning("⚠️ KokoClone não instalado. Voice cloning limitado.")
        st.info("Instale: pip install kokoclone")
        return None


def generate_voice_id(audio_bytes: bytes, name: str) -> str:
    """Gera ID único para voz."""
    hash_input = f"{name}:{len(audio_bytes)}:{audio_bytes[:1000].hex()}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:16]


def save_voice(
    name: str,
    audio_bytes: bytes,
    duration: float,
    language: str = "pt",
    voice_id: str = None
) -> Optional[Dict]:
    """
    Salva voz clonada.
    
    Para Kokoro: salva áudio de referência + metadata.
    KokoClone usa esse áudio para gerar embedding de voz.
    """
    try:
        if voice_id is None:
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
            "is_kokoro": True
        }
        
        voices[voice_id] = voice_metadata
        
        with open(VOICES_JSON, "w", encoding="utf-8") as f:
            json.dump(voices, f, indent=2, ensure_ascii=False)
        
        return voice_metadata
    
    except Exception as e:
        st.error(f"❌ Erro salvando voz: {e}")
        return None


def load_voices() -> Dict:
    """Carrega vozes de voices.json."""
    if not VOICES_JSON.exists():
        return {}
    try:
        with open(VOICES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_voice_list() -> List[Dict]:
    """Retorna lista de vozes."""
    voices = load_voices()
    return [
        {"voice_id": v["voice_id"], "name": v["name"], "created_at": v["created_at"]}
        for v in voices.values()
    ]


def delete_voice(voice_id: str) -> bool:
    """Remove voz salva."""
    try:
        voices = load_voices()
        if voice_id not in voices:
            return False
        
        sample_path = voices[voice_id]["sample_path"]
        if os.path.exists(sample_path):
            os.remove(sample_path)
        
        del voices[voice_id]
        
        with open(VOICES_JSON, "w", encoding="utf-8") as f:
            json.dump(voices, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"❌ Erro removendo voz: {e}")
        return False


# Vozes nativas do Kokoro (para demo sem clonagem)
KOKORO_VOICES = {
    "af_sarah": "Sarah (Female, American)",
    "af_alice": "Alice (Female, American)",
    "af_bella": "Bella (Female, American)",
    "am_james": "James (Male, American)",
    "am_michael": "Michael (Male, American)",
    "bf_emma": "Emma (Female, British)",
    "bm_george": "George (Male, British)",
    "pf_snowy": "Snowy (Female, Portuguese)",
    "pm_alex": "Alex (Male, Portuguese)",
}


def get_kokoro_native_voices() -> List[Dict]:
    """Retorna vozes nativas do Kokoro para dropdown."""
    return [
        {"voice_id": vid, "name": nome, "created_at": "native", "is_native": True}
        for vid, nome in KOKORO_VOICES.items()
    ]
