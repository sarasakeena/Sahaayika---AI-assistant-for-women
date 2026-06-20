# 🌸 Sahaayika — A Caring Health Assistant for Rural Women

> *"Sahaayika"* means **helper** in Sanskrit.

Sahaayika helps rural women understand their medical prescriptions and health documents in their own language — explained simply, spoken aloud, with no technical knowledge required.

---

## 💡 The Problem

A rural woman visits a doctor and receives a handwritten prescription. She faces multiple barriers:

- She **cannot read English**
- She does not know what abbreviations like **OD, BD, TDS, HS, SOS** mean
- She is **too scared** to ask the doctor again
- She might take the medicine **wrong**

Sahaayika solves this in one upload.

---

## ✅ What Sahaayika Does

1. **Scan** — Upload a photo of any handwritten or printed medical document (prescription, lab report, discharge summary, medical certificate)
2. **Understand** — Gemini Vision reads the image directly and explains it in simple, warm language
3. **Translate** — Converts the explanation into Tamil or Hindi
4. **Speak** — Reads the explanation aloud so even non-readers can understand
5. **Remind** — Automatically extracts medicine names and dosage timing into structured reminders
6. **Answer** — Ask follow-up questions about the document, or general health questions, and get simple, reassuring answers

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Image understanding + reasoning | Google Gemini 1.5 Flash (Vision) |
| Translation (Tamil/Hindi) | deep_translator (Google Translate) |
| Text to speech | gTTS |
| Backend | FastAPI + Python |
| Frontend | HTML/CSS/JS (PWA — installable, offline-capable shell) |

> Gemini Vision handles OCR and medical explanation in a single model call — no separate Tesseract OCR step. The model reads the image directly and returns both a plain-language explanation and a structured reminders block.

---

## 📁 Project Structure
sahaayika/

├── app.py              # FastAPI backend + Gemini Vision logic

├── static/

│   ├── index.html      # Frontend UI

│   ├── manifest.json    # PWA manifest

│   ├── sw.js            # Service worker (offline shell)

│   └── icon.svg / bg.png

├── audio_files/         # Temporary TTS audio (auto-deleted after sending)

└── README.md
---

## ⚙️ Installation

### Step 1 — Install dependencies
```bash
pip install fastapi uvicorn python-multipart pillow gtts deep-translator google-generativeai python-dotenv
```

### Step 2 — Set up your Gemini API key
Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey).

Create a `.env` file in the project root:
GEMINI_API_KEY=your_key_here

This is loaded automatically and is excluded from git via `.gitignore`.

### Step 3 — Run the app
```bash
python app.py
```

Open your browser at:
http://localhost:8000

---

## 🖥️ How to Use

1. Open the app in your browser
2. Select your language — **Tamil**, **Hindi**, or **English**
3. Upload a photo of the medical document
4. Tap **Understand My Prescription**
5. Read the explanation or tap **play** to listen
6. View auto-extracted medicine reminders (if a prescription was detected)
7. Ask a follow-up question about the document, or a general health question

---

## 🌍 Languages Supported

| Language | Text | Audio |
|----------|------|-------|
| Tamil (தமிழ்) | ✅ | ✅ |
| Hindi (हिन्दी) | ✅ | ✅ |
| English | ✅ | ✅ |

---

## ⚠️ Important Disclaimers

- Sahaayika is **not a medical diagnosis tool**
- It never recommends specific dosage amounts beyond what's written in the document
- It always advises users to confirm with a doctor or pharmacist
- It is designed to **assist**, not replace, medical professionals

---

## 🚀 Future Scope

- Improve OCR/explanation accuracy on low-quality or heavily handwritten images
- Add more languages — Telugu, Kannada, Bengali, Marathi
- Voice input — let users speak their question instead of typing
- Fully offline mode using an on-device model
- WhatsApp integration — send a prescription photo, get an explanation back

---

## 👩‍💻 Built By

Built for a social impact hackathon (Kaggle / Gemma 3n Challenge track) focused on rural healthcare accessibility in India.

*Sahaayika — because every woman deserves to understand her own health.* 🌸
