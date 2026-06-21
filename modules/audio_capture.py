"""Module para captura de áudio: upload e gravação."""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st

# Import config relative to this file
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent))
from config import MIN_AUDIO_DURATION, MAX_AUDIO_DURATION, MAX_AUDIO_SIZE_MB, ALLOWED_AUDIO_FORMATS


def validate_audio_file(file_bytes: bytes, filename: str) -> Tuple[bool, str, Optional[float]]:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_AUDIO_FORMATS:
        return False, f"Formato '{ext}' não suportado.", None
    
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_AUDIO_SIZE_MB:
        return False, f"Arquivo muito grande: {size_mb:.1f}MB", None
    
    try:
        from pydub import AudioSegment
        temp_path = tempfile.mktemp(suffix=ext)
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        
        format = ext.replace("m4a", "mp4")
        audio = AudioSegment.from_file(temp_path, format=format)
        duration = audio.duration_seconds
        os.remove(temp_path)
        
        if duration < MIN_AUDIO_DURATION:
            return False, f"Áudio curto: {duration:.1f}s (min: {MIN_AUDIO_DURATION}s)", duration
        if duration > MAX_AUDIO_DURATION:
            return False, f"Áudio longo: {duration:.1f}s (max: {MAX_AUDIO_DURATION}s)", duration
        
        return True, f"Áudio válido: {duration:.1f}s, {size_mb:.1f}MB", duration
    except Exception as e:
        return False, f"Erro: {e}", None


def upload_audio_file() -> Optional[Tuple[bytes, str, float]]:
    uploaded_file = st.file_uploader(
        "Upload de áudio",
        type=ALLOWED_AUDIO_FORMATS,
        help=f"Formatos: {ALLOWED_AUDIO_FORMATS}. Duração: {MIN_AUDIO_DURATION}-{MAX_AUDIO_DURATION}s",
        key="audio_upload"
    )
    
    if uploaded_file:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name
        is_valid, message, duration = validate_audio_file(file_bytes, filename)
        
        if is_valid:
            st.success(message)
            return file_bytes, filename, duration
        else:
            st.error(message)
            return None
    return None


def record_audio(duration: int = 10) -> Optional[Tuple[bytes, str, float]]:
    st.info(f"🎙️ Gravação: fale por ~{duration}s")
    audio_input = st.audio_input("Gravar", key="audio_recording")
    
    if audio_input:
        file_bytes = audio_input.getvalue()
        filename = "recording.wav"
        is_valid, message, duration_sec = validate_audio_file(file_bytes, filename)
        
        if is_valid:
            st.success(message)
            return file_bytes, filename, duration_sec
        else:
            st.error(message)
            return None
    return None


def convert_to_wav(file_bytes: bytes, input_ext: str) -> bytes:
    from pydub import AudioSegment
    temp_input = tempfile.mktemp(suffix=f".{input_ext}")
    temp_output = tempfile.mktemp(suffix=".wav")
    
    try:
        with open(temp_input, "wb") as f:
            f.write(file_bytes)
        
        format = input_ext.replace("m4a", "mp4")
        audio = AudioSegment.from_file(temp_input, format=format)
        audio.export(temp_output, format="wav")
        
        with open(temp_output, "rb") as f:
            wav_bytes = f.read()
        
        return wav_bytes
    finally:
        if os.path.exists(temp_input): os.remove(temp_input)
        if os.path.exists(temp_output): os.remove(temp_output)
