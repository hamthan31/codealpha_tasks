"""
Language Translation Tool
--------------------------
A simple Streamlit web app that lets a user enter text, pick a source
and target language, and get a translated result on screen.

Run with:
    streamlit run app.py
"""

import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import io

# ---- Supported languages (display name -> language code) ----
LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
    "Sinhala": "si",
    "Tamil": "ta",
}

# gTTS doesn't support every language deep-translator does (e.g. "auto")
TTS_SUPPORTED = set(LANGUAGES.values()) - {"auto"}


def translate_text(text: str, source: str, target: str) -> str:
    """Translate text using the free Google Translate wrapper."""
    return GoogleTranslator(source=source, target=target).translate(text)


def text_to_speech_bytes(text: str, lang_code: str) -> bytes:
    """Convert text to speech and return raw mp3 bytes (in-memory, no file saved)."""
    tts = gTTS(text=text, lang=lang_code)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def main():
    st.set_page_config(page_title="Language Translation Tool", page_icon="🌐")
    st.title("🌐 Language Translation Tool")
    st.write("Enter text below, choose your source and target languages, and translate.")

    col1, col2 = st.columns(2)
    with col1:
        source_lang_name = st.selectbox("Source language", list(LANGUAGES.keys()), index=0)
    with col2:
        target_lang_name = st.selectbox("Target language", list(LANGUAGES.keys()), index=1)

    source_code = LANGUAGES[source_lang_name]
    target_code = LANGUAGES[target_lang_name]

    input_text = st.text_area("Enter text to translate", height=150, placeholder="Type or paste text here...")

    translate_clicked = st.button("Translate", type="primary")

    # Keep the last result around so the optional TTS section can reuse it
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""

    if translate_clicked:
        if not input_text.strip():
            st.warning("Please enter some text to translate.")
        elif source_code == target_code and source_code != "auto":
            st.warning("Source and target languages are the same.")
        else:
            try:
                with st.spinner("Translating..."):
                    result = translate_text(input_text, source_code, target_code)
                st.session_state.translated_text = result
            except Exception as e:
                st.error(f"Translation failed: {e}")

    if st.session_state.translated_text:
        st.subheader("Translated text")
        st.text_area("Result", value=st.session_state.translated_text, height=150, key="result_box")

        # "Copy" affordance: st.code() renders a built-in copy-to-clipboard icon
        st.caption("Click the copy icon below to copy the result:")
        st.code(st.session_state.translated_text, language=None)

        # Optional: text-to-speech playback
        if target_code in TTS_SUPPORTED:
            if st.button("🔊 Play translated text"):
                try:
                    with st.spinner("Generating audio..."):
                        audio_bytes = text_to_speech_bytes(st.session_state.translated_text, target_code)
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error(f"Text-to-speech failed: {e}")
        else:
            st.caption("Text-to-speech isn't available for this target language.")


if __name__ == "__main__":
    main()
