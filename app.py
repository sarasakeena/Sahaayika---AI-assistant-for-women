import re
import requests
import pytesseract
import uuid
import json
import base64
import io
import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from gtts import gTTS

# =========================
# CONFIG
# =========================
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\HP\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
OLLAMA_URL = "http://localhost:11434/api/generate"

# =========================
# OFFLINE TRANSLATION SETUP
# =========================
import argostranslate.package
import argostranslate.translate

def install_argos_language(from_code: str, to_code: str):
    print(f"  Checking language package: {from_code} → {to_code} ...")
    installed = argostranslate.translate.get_installed_languages()
    for lang in installed:
        if lang.code == from_code:
            for t in lang.translations_to:
                if t.to_lang.code == to_code:
                    print(f"  ✅ Already installed: {from_code} → {to_code}")
                    return True
    print(f"  ⬇️  Downloading: {from_code} → {to_code} ...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    matching = [p for p in available_packages if p.from_code == from_code and p.to_code == to_code]
    if not matching:
        print(f"  ❌ Package not found: {from_code} → {to_code}")
        return False
    pkg_path = matching[0].download()
    argostranslate.package.install_from_path(pkg_path)
    print(f"  ✅ Installed: {from_code} → {to_code}")
    return True

# Try to install packages, track what's available
print("🌐 Setting up offline translation languages...")
TAMIL_OFFLINE = install_argos_language("en", "ta")
HINDI_OFFLINE = install_argos_language("en", "hi")
print("✅ Translation setup complete.\n")

def translate_offline(text: str, lang: str) -> str:
    if lang == "English":
        return text

    target_code = "ta" if lang == "Tamil" else "hi"
    use_offline = TAMIL_OFFLINE if lang == "Tamil" else HINDI_OFFLINE

    # Try Argos offline first
    if use_offline:
        try:
            translated = argostranslate.translate.translate(text, "en", target_code)
            if translated:
                return translated
        except Exception as e:
            print(f"Argos translation error: {e}")

    # Fallback: deep-translator (Google Translate)
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="en", target=target_code).translate(text)
        if translated:
            print(f"  ℹ️  Used Google fallback for {lang}")
            return translated
    except Exception as e:
        print(f"Google translate fallback error: {e}")

    return text  # Return original if all else fails



# =========================
# HELPERS
# =========================
def clean(text: str) -> str:
    return re.sub(r"\s{2,}", " ", text).strip()

def speak(text: str, lang: str) -> str | None:
    try:
        code = {"English": "en", "Tamil": "ta", "Hindi": "hi"}.get(lang, "en")
        os.makedirs("audio_files", exist_ok=True)
        filename = f"audio_files/audio_{uuid.uuid4().hex[:6]}.mp3"
        gTTS(text=text, lang=code).save(filename)
        return filename
    except Exception as e:
        print(f"TTS error: {e}")
        return None

def call_ollama(prompt: str) -> str:
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3:mini",
                "prompt": prompt,
                "system": (
                    "You are Sahaayika, a calm and caring female health assistant for rural women in India. "
                    "Never diagnose. Never give specific dosage. Be reassuring, gentle, and use very simple language. "
                    "Always respond in English — translation happens separately."
                ),
                "stream": True
            },
            stream=True,
            timeout=180
        )
        out = ""
        for line in r.iter_lines():
            if line:
                try:
                    out += json.loads(line.decode()).get("response", "")
                except Exception:
                    pass
        return clean(out)
    except Exception as e:
        return f"Could not connect to Ollama. Please make sure it is running. Error: {e}"

def explain_prescription(text: str, language: str):
    prompt = f"""
You are Sahaayika, a helpful assistant for rural women in India.

Identify what type of document this is:
- Prescription, Medical Certificate, Lab Report, Discharge Summary,
  Government/Scheme document, Insurance, Bill, or Other

Then explain it in simple English in under 8 lines.

For prescriptions: list medicines, explain OD/BD/TDS (once/twice/thrice a day). Never give dosage amounts.
For medical certificates: mention patient name, illness, rest days.
For lab reports: mention test names and whether values are normal or not.
For other documents: explain what it is and what the person needs to know or do.
If unclear: say "This document is not clear. Please show it to someone who can help."

TEXT:
{text}
"""

    answer = call_ollama(prompt)
# ✅ SMART FALLBACK FIX

    lower_answer = answer.lower()

# ✅ Only fallback if truly unclear
    if len(answer.strip()) < 10:
        answer = "This document is not fully clear. Please show it to a doctor, pharmacist, or trusted person for help."

    translated = translate_offline(answer, language)
    audio_file = speak(translated, language)

    return translated, audio_file, text

# =========================
# FASTAPI APP
# =========================
app = FastAPI()

@app.get("/")
def root():
    return FileResponse("static/index.html")
@app.post("/analyse")
async def analyse(
    image: UploadFile = File(...),
    language: str = Form("English")
):
    img_bytes = await image.read()

    pil_image = Image.open(io.BytesIO(img_bytes)).convert("L")

    # 🔥 resize (boost OCR accuracy A LOT)
    width, height = pil_image.size
    pil_image = pil_image.resize((width * 2, height * 2))

    # 🔥 threshold
    pil_image = pil_image.point(lambda x: 0 if int(x) < 140 else 255)

    text = pytesseract.image_to_string(
        pil_image,
        config='--psm 6 --oem 3'
    ).strip()

    print(f"[OCR TEXT]: {text[:200]}")

    if not text.strip():
        return JSONResponse({
            "error": "Text is unclear. Please upload a clearer image."
        }, status_code=400)

    explanation, audio_file, raw_text = explain_prescription(text, language)

    audio_b64 = None
    if audio_file and os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        os.remove(audio_file)

    return JSONResponse({
        "explanation": explanation,
        "audio": audio_b64,
        "raw_text": raw_text
    })






app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)