import re
import uuid
import base64
import io
import os

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from gtts import gTTS

import google.generativeai as genai

# =========================
# CONFIG — Gemini Cloud API
# =========================
GEMINI_API_KEY = "AIzaSyC8JdhckA8a8Zq73frxOctkk8dhyCoVji4"
genai.configure(api_key=GEMINI_API_KEY)

# Use gemini-1.5-flash — fast, free-tier, excellent at vision
vision_model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# TRANSLATION (deep-translator via Google Translate)
# =========================
def translate_text(text: str, lang: str) -> str:
    if lang == "English":
        return text
    target_code = {"Tamil": "ta", "Hindi": "hi"}.get(lang, "en")
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="en", target=target_code).translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# =========================
# TTS
# =========================
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

# =========================
# GEMINI VISION — Core AI
# =========================
def call_gemini_vision(image_bytes: bytes, language: str):
    """
    Sends the image directly to Gemini Vision.
    Returns (explanation_english, reminders_list)
    """
    img = Image.open(io.BytesIO(image_bytes))

    prompt = """You are Sahaayika, a warm, caring female health assistant for rural women in India.

A user has uploaded a photo of a medical document. Your job is to:

1. Look at the image carefully and identify what type of document it is (prescription, medical certificate, lab report, discharge summary, etc.)
2. Extract all important information: patient name, age, diagnosis, medicines, dosage, when to take them, doctor's advice, test results — whatever is present.
3. Explain everything in simple, clear English in 6-8 lines as if speaking directly to the patient.

IMPORTANT RULES:
- Be warm, reassuring, and empathetic in your tone.
- Use simple language. Avoid medical jargon.
- If it is a PRESCRIPTION with medicines, you MUST add this at the very end of your response on a new line, formatted EXACTLY like this example:
[REMINDERS] Paracetamol: Morning, Night | Amoxicillin: Morning, Afternoon, Night
(Only include medicines that are actually in the document. Use Morning / Afternoon / Evening / Night based on what the prescription says.)
- If the image is blurry or unreadable, say: "This document is not fully clear. Please show it to a doctor or health worker for help."
- Never diagnose. Never give specific dosage amounts beyond what is written.
"""

    try:
        response = vision_model.generate_content([prompt, img])
        return response.text.strip()
    except Exception as e:
        print(f"Gemini Vision error: {e}")
        return f"GEMINI_ERROR: {e}"

def parse_reminders(raw_text: str):
    """Parse the [REMINDERS] block out of the AI response."""
    reminders = []
    if "[REMINDERS]" in raw_text:
        parts = raw_text.split("[REMINDERS]")
        clean_answer = parts[0].strip()
        reminders_text = parts[1].strip()
        for med_block in reminders_text.split("|"):
            if ":" in med_block:
                med_name, times = med_block.split(":", 1)
                reminders.append({
                    "medicine": med_name.strip(),
                    "times": [t.strip() for t in times.split(",")]
                })
        return clean_answer, reminders
    return raw_text, reminders

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
    print(f"[GEMINI] Processing image ({len(img_bytes)//1024} KB)...")

    raw_response = call_gemini_vision(img_bytes, language)

    if raw_response.startswith("GEMINI_ERROR"):
        return JSONResponse({"error": "Could not process image. Please try again."}, status_code=400)

    explanation_english, reminders = parse_reminders(raw_response)

    if len(explanation_english.strip()) < 10:
        explanation_english = "This document is not fully clear. Please show it to a doctor or health worker for help."

    print(f"[GEMINI] Response: {explanation_english[:100]}...")
    if reminders:
        print(f"[GEMINI] Reminders found: {reminders}")

    translated = translate_text(explanation_english, language)
    audio_file = speak(translated, language)

    audio_b64 = None
    if audio_file and os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        os.remove(audio_file)

    return JSONResponse({
        "explanation": translated,
        "audio": audio_b64,
        "raw_text": explanation_english,
        "reminders": reminders
    })

@app.post("/followup")
async def followup(
    question: str = Form(""),
    language: str = Form("English"),
    context: str = Form("")
):
    prompt = f"""You are Sahaayika, a caring female health assistant for rural women in India.
You previously explained this medical document to the user:
{context}

The user is now asking this follow-up question: "{question}"

Answer in very simple, warm English in 2-3 lines. Never give specific dosage amounts. Be reassuring and kind."""

    try:
        response = vision_model.generate_content(prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = "I'm sorry, I could not connect right now. Please try again in a moment."

    translated = translate_text(answer, language)
    audio_file = speak(translated, language)

    audio_b64 = None
    if audio_file and os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        os.remove(audio_file)

    return JSONResponse({"answer": translated, "audio": audio_b64})

@app.post("/chat")
async def general_chat(
    question: str = Form(""),
    language: str = Form("English")
):
    prompt = f"""You are Sahaayika, a calm, warm, and caring female health assistant for rural women in India.
The user is asking a general health or wellbeing question: "{question}"

Answer in very simple English in 2-3 lines. Be highly reassuring and supportive. 
Never diagnose or give specific medication dosages. Recommend seeing a doctor for serious issues."""

    try:
        response = vision_model.generate_content(prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = "I'm sorry, I could not connect right now. Please try again in a moment."

    translated = translate_text(answer, language)
    audio_file = speak(translated, language)

    audio_b64 = None
    if audio_file and os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        os.remove(audio_file)

    return JSONResponse({"answer": translated, "audio": audio_b64})

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)