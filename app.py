"""
Aplicativo Streamlit principal para Clone de Voz Kokoro TTS.
Kokoro-82M: 82M params, 3-5x mais rápido, 86MB (vs 1.7GB do XTTS).
"""

from pathlib import Path
import streamlit as st

from config import STREAMIT_TITLE, STREAMIT_ICON, SUPPORTED_LANGUAGES, get_voice_list, get_kokoro_native_voices
from voice_cloning import init_kokoro_pipeline, save_voice, delete_voice
from tts_synthesis import synthesize_speech_kokoro, synthesize_speech_kokoro_demo, validate_speed
from audio_capture import upload_audio_file, record_audio, convert_to_wav

st.set_page_config(page_title=STREAMIT_TITLE, page_icon=STREAMIT_ICON, layout="wide")

st.title(f"{STREAMIT_ICON} {STREAMIT_TITLE}")
st.markdown("---")

st.info("""
**✨ Kokoro TTS - 82M params (LEVE & RÁPIDO):**
- ✅ 20x mais leve que XTTS-v2 (82M vs 1.7B params)
- ✅ 3-5x mais rápido (5-10s vs 30s-2min)
- ✅ Só 86MB de modelo (vs 1.7GB)
- ✅ VRAM: 3GB (vs 4-8GB)
- ✅ Funciona bem em CPU
""")

tab_clonar, tab_gen = st.tabs(["🎤 Clonar Voz", "🎧 Gerar Áudio"])

# ==================== ABA 1: CLONAR VOZ ====================
with tab_clonar:
    st.header("Clonar uma Nova Voz com Kokoro")
    
    if upload_audio_file():
        file_bytes, filename, duration = upload_audio_file()
        
        with st.form("clonagem_form"):
            nome_voz = st.text_input("Nome da voz", placeholder="Ex: Minha Voz...")
            lingua = st.selectbox(
                "Língua do áudio",
                options=list(SUPPORTED_LANGUAGES.keys()),
                format_func=lambda x: SUPPORTED_LANGUAGES[x]
            )
            btn_clonar = st.form_submit_button("🎤 Clonar Voz")
        
        if btn_clonar and nome_voz.strip():
            ext = Path(filename).suffix.lower()
            if ext != "wav":
                file_bytes = convert_to_wav(file_bytes, ext)
            
            with st.spinner("🔄 Processando voz..."):
                voice_meta = save_voice(
                    name=nome_voz.strip(),
                    audio_bytes=file_bytes,
                    duration=duration,
                    language=lingua
                )
            
            if voice_meta:
                st.success(f"✅ Voz '{nome_voz}' clonada!")
                st.json(voice_meta)

# ==================== ABA 2: GERAR ÁUDIO ====================
with tab_gen:
    st.header("Gerar Áudio com Kokoro")
    
    pipeline = init_kokoro_pipeline()
    
    if pipeline is None:
        st.error("❌ Kokoro não carregado. Instale: pip install -r requirements.txt")
        st.stop()
    
    # Vozes: nativas + clonadas
    vozes_nativas = get_kokoro_native_voices()
    vozes_clonadas = get_voice_list()
    
    st.subheader("📚 Selecionar Voz")
    
    voz_options = {}
    for v in vozes_nativas:
        voz_options[f"🔊 {v['name']} (nativa)"] = v['voice_id']
    for v in vozes_clonadas:
        voz_options[f"🎤 {v['name']} (clonada)"] = v['voice_id']
    
    voz_selecionada = st.selectbox("Voz", options=list(voz_options.keys()))
    
    if voz_selecionada:
        voice_id = voz_options[voz_selecionada]
        is_native = " (nativa)" in voz_selecionada
        
        with st.form("geracao_form"):
            texto = st.text_area("Texto", height=150, placeholder="Digite o texto...")
            speed = st.slider("Velocidade", 0.5, 2.0, 1.0, 0.1)
            lingua_tts = st.selectbox("Língua", options=list(SUPPORTED_LANGUAGES.keys()), format_func=lambda x: SUPPORTED_LANGUAGES[x])
            btn_gerar = st.form_submit_button("🎧 Gerar Áudio")
        
        if btn_gerar:
            if not texto.strip():
                st.error("❌ Digite texto.")
            elif not validate_speed(speed):
                st.error("❌ Velocidade inválida.")
            else:
                if is_native:
                    audio_bytes = synthesize_speech_kokoro_demo(pipeline, texto, voice_id, lingua_tts, speed)
                else:
                    voz_meta = next((v for v in vozes_clonadas if v["voice_id"] == voice_id), None)
                    if voz_meta and voz_meta["sample_path"]:
                        audio_bytes = synthesize_speech_kokoro(pipeline, texto, voz_meta["sample_path"], lingua_tts, speed)
                    else:
                        st.error("❌ Áudio de referência não encontrado.")
                        audio_bytes = None
                
                if audio_bytes:
                    st.subheader("🔊 Resultado")
                    st.audio(audio_bytes, format="wav")
                    st.download_button("💾 Salvar .wav", audio_bytes, file_name="voz.wav", mime="audio/wav", type="primary")

st.markdown("---")
st.markdown("**🔗 [Kokoro-82M GitHub](https://github.com/hexgrad/Kokoro-82M)** | **[Kokoro PyPI](https://pypi.org/project/kokoro/)**")
