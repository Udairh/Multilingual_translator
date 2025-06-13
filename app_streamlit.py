import streamlit as st
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from gtts import gTTS
import base64

@st.cache_resource
def load_model():
    model_name = "facebook/m2m100_418M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

# UI
st.set_page_config(page_title="Multilingual Translator", layout="centered")
st.title("Open Source Multilingual Translator")

text = st.text_area("Enter text or upload a .txt file below:", height=200)

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
if uploaded_file:
    try:
        text = uploaded_file.read().decode("utf-8")
    except:
        st.error("Error reading file.")

target_lang = st.selectbox("Select Target Language", [
    "en", "es", "fr", "de", "hi", "ja", "ko", "zh", "ru", "ar"
])

if st.button("Translate"):
    if text.strip():
        try:
            detected_lang = detect(text.strip())
            st.info(f"Detected Language: `{detected_lang}`")

            tokenizer, model = load_model()
            tokenizer.src_lang = detected_lang

            encoded = tokenizer(text.strip(), return_tensors="pt", padding=True)
            generated_tokens = model.generate(
                **encoded,
                forced_bos_token_id=tokenizer.get_lang_id(target_lang)
            )
            translated_text = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

            st.subheader("Translation:")
            st.markdown(f"`{translated_text}`")

            st.download_button("Download Translation", data=translated_text, file_name="translation.txt")

            # Optional: Add TTS
            tts = gTTS(translated_text, lang=detected_lang)
            tts.save("translation_audio.mp3")
            audio_file = open("translation_audio.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')

        except Exception as e:
            st.error(f"Translation error: {str(e)}")
    else:
        st.warning("Please enter or upload some text.")