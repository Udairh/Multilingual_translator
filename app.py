from flask import Flask, render_template, send_file, session, request # type: ignore
from langdetect import detect # type: ignore
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM # type: ignore
from config import Config
import uuid
from flask_wtf.csrf import CSRFProtect # type: ignore
from flask_session import Session # type: ignore
from forms import TranslateForm
from gtts import gTTS # type: ignore
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup CSRF Protection
csrf = CSRFProtect(app)
csrf.init_app(app)

# Setup Session
app.config["SESSION_FILE_DIR"] = "./session_cache"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Load M2M100 Model
model_name = "facebook/m2m100_418M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Supported Languages
SUPPORTED_LANGS = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'hi': 'Hindi',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ru': 'Russian',
    'ar': 'Arabic'
}

@app.before_request
def setup_user():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    if 'history' not in session:
        session['history'] = []

def save_to_session(data):
    session['history'].append(data)
    session.modified = True

@app.route("/", methods=["GET", "POST"])
def translate_text():
    form = TranslateForm()

    original_text = ""
    translated_text = ""
    detected_lang = ""
    target_lang = "en"

    if form.validate_on_submit():
        text = form.text.data.strip()
        target_lang = form.target_lang.data

        if target_lang not in SUPPORTED_LANGS:
            target_lang = "en"

        if not text and 'file' in request.files:
            file = request.files["file"]
            if file.filename.endswith(".txt"):
                try:
                    text = file.read().decode("utf-8").strip()
                except:
                    text = ""

        if text:
            try:
                detected_lang = detect(text)
                tokenizer.src_lang = detected_lang

                inputs = tokenizer(text, return_tensors="pt", padding=True)
                inputs["forced_bos_token_id"] = tokenizer.get_lang_id(target_lang)

                generated_tokens = model.generate(**inputs)
                translated_text = tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

                original_text = text

                save_to_session({
                    "id": str(uuid.uuid4()),
                    "source": text,
                    "detected_lang": detected_lang,
                    "target_lang": target_lang,
                    "translated": translated_text
                })

            except Exception as e:
                translated_text = f"Translation error: {str(e)}"
                detected_lang = "Unknown"
        else:
            translated_text = ""

    return render_template("index.html",
                           form=form,
                           original=original_text,
                           lang=detected_lang,
                           translation=translated_text,
                           target_lang=target_lang,
                           history=session.get('history', []))

@app.route("/speak")
def speak_translation():
    translated = request.args.get("text", "")
    if not translated:
        return "No text to speak", 400

    tts = gTTS(translated, lang=session.get('detected_lang', 'en'))
    filename = "translation_audio.mp3"
    tts.save(filename)
    return send_file(filename, as_attachment=True, download_name="translation.mp3")

@app.route("/download")
def download_translation():
    translated = request.args.get("text", "")
    filename = "translation_output.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(translated)
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)