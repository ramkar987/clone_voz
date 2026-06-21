"""
Module para síntese TTS usando Kokoro.
Kokoro é 3-5x mais rápido que XTTS-v2.
"""

import os
import tempfile
import io
from pathlib import Path
from typing import Optional
from datetime import datetime

import streamlit as st
import soundfile as sf
from config import AUDIO_CACHE_DIR, MIN_SPEED, MAX_SPEED


def synthesize_speech_kokoro(
    pipeline: object,
    text: str,
    sample_path: str,
    language: str = "pt",
    speed: float = 1.0
) -> Optional[bytes]:
    """
    Gerera áudio TTS usando Kokoro com voice cloning.
    
    Kokoro usa KPipeline + voice embedding do áudio de referência.
    """
    try:
        if not text.strip():
            st.error("❌ Texto em vazio.")
            return None
        
        with st.spinner("🎤 Gerando áudio Kokoro... (~5-10s, 3-5x mais rápido que XTTS)"):
            # Kokoro: usa pipeline com voice cloning
            # Precisando extrair embedding da voz de referência
            from kokoro import KPipeline
            
            # Generate audio segments
            generator = pipeline(
                text,
                voice=sample_path,  # Kokoro aceita path de áudio diretamente
                speed=speed,
                split_pattern=r'\n'
            )
            
            # Concatenate audio
            audio_chunks = []
            for segment in generator:
                audio_chunks.append(segment.audio)
            
            if not audio_chunks:
                st.error("❌ Não gerou áudio.")
                return None
            
            import torch
            audio = torch.cat(audio_chunks, dim=0)
            
            # Save to WAV
            output_path = AUDIO_CACHE_DIR / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            sf.write(output_path, audio.cpu().numpy(), 24000, format='WAV')
            
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            st.success(f"✅ Áudio Kokoro gerado! ({len(audio_bytes) / 1024:.1f}KB, ~5-10s)")
            return audio_bytes
    
    except Exception as e:
        st.error(f"❌ Erro gerando áudio: {e}")
        import traceback
        traceback.print_exc()
        return None


def synthesize_speech_kokoro_demo(
    pipeline: object,
    text: str,
    voice_id: str = "pf_snowy",
    language: str = "pt",
    speed: float = 1.0
) -> Optional[bytes]:
    """
    Gerera áudio usando voz nativa do Kokoro (demo).
    
    Voice IDs nativos: af_sarah, am_james, pf_snowy (português), etc.
    """
    try:
        if not text.strip():
            st.error("❌ Texto em vazio.")
            return None
        
        with st.spinner("🎤 Gerando áudio demo Kokoro..."):
            generator = pipeline(
                text,
                voice=voice_id,  # Voice nativa do Kokoro
                speed=speed,
                split_pattern=r'\n'
            )
            
            audio_chunks = []
            for segment in generator:
                audio_chunks.append(segment.audio)
            
            if not audio_chunks:
                return None
            
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
