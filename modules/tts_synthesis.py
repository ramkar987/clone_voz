"""Module para síntese TTS com Kokoro."""

import os
import tempfile
from typing import Optional
from datetime import datetime

import streamlit as st
import soundfile as sf

import sys
sys.path.insert(0, str(Path(__file__).parent))
from pathlib import Path
from config import AUDIO_CACHE_DIR, MIN_SPEED, MAX_SPEED


def synthesize_speech_kokoro(pipeline: object, text: str, sample_path: str, language: str = "pt", speed: float = 1.0) -> Optional[bytes]:
    try:
        if not text.strip():
            st.error("❌ Texto vazio.")
            return None
        
        with st.spinner("🎤 Gerando áudio Kokoro... (~5-10s)"):
            generator = pipeline(text, voice=sample_path, speed=speed, split_pattern=r'\n')
            audio_chunks = [segment.audio for segment in generator]
            
            if not audio_chunks:
                st.error("❌ Não gerou áudio.")
                return None
            
            import torch
            audio = torch.cat(audio_chunks, dim=0)
            
            output_path = AUDIO_CACHE_DIR / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            sf.write(output_path, audio.cpu().numpy(), 24000, format='WAV')
            
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            st.success(f"✅ Áudio gerado! ({len(audio_bytes) / 1024:.1f}KB)")
            return audio_bytes
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        return None


def synthesize_speech_kokoro_demo(pipeline: object, text: str, voice_id: str = "pf_snowy", language: str = "pt", speed: float = 1.0) -> Optional[bytes]:
    try:
        if not text.strip():
            st.error("❌ Texto vazio.")
            return None
        
        with st.spinner("🎤 Gerando áudio demo..."):
            generator = pipeline(text, voice=voice_id, speed=speed, split_pattern=r'\n')
            audio_chunks = [segment.audio for segment in generator]
            
            if not audio_chunks: return None
            
            import torch
            audio = torch.cat(audio_chunks, dim=0)
            
            output_path = tempfile.mktemp(suffix=".wav")
            sf.write(output_path, audio.cpu().numpy(), 24000, format='WAV')
            
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            os.remove(output_path)
            st.success(f"✅ Áudio demo gerado! ({len(audio_bytes) / 1024:.1f}KB)")
            return audio_bytes
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        return None


def validate_speed(speed: float) -> bool:
    return MIN_SPEED <= speed <= MAX_SPEED
