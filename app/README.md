# 🎤 Clone de Voz Kokoro TTS (82M - Leve & Rápido)

Aplicação Streamlit para clonagem de voz usando **Kokoro-82M** - open-source, gratuito, 3-5x mais rápido.

## ✨ Vantagens do Kokoro

- ✅ **82M params** (20x mais leve que XTTS-v2)
- ✅ **5-10s** por geração (3-5x mais rápido)
- ✅ **86MB** modelo (vs 1.7GB)
- ✅ **3GB VRAM** (vs 4-8GB)
- ✅ **CPU-friendly**

## Instalação

```bash
cd app
pip install -r requirements.txt
```

### Se não tem GPU NVIDIA

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Execução

```bash
streamlit run app.py
```

Abrirá em `http://localhost:8501`

## Como Usar

1. **Clonar Voz**: Upload (3-30s) → nome → clonar
2. **Gerar Áudio**: Selecionar voz → texto → gerar → download

## Recursos

- [Kokoro-82M GitHub](https://github.com/hexgrad/Kokoro-82M)
- [Kokoro PyPI](https://pypi.org/project/kokoro/)
- [Documentação](https://pypi.org/project/kokoro/)
