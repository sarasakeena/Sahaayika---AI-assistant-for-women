# 🌸 Sahaayika — A Caring Health Assistant for Rural Women

> *"Sahaayika"* means **helper** in Sanskrit.

Sahaayika helps rural women understand their medical prescriptions in their own language — spoken aloud, with no technical knowledge required.

---

## 💡 The Problem

A rural woman visits a doctor and receives a handwritten prescription. She faces multiple barriers:

- She **cannot read English**
- She does not know what **OD, BD, TDS, HS, SOS** means
- She has **no internet** at home
- She is **too scared** to ask the doctor again
- She might take the medicine **wrong**

Sahaayika solves all of these problems in one tap.

---

## ✅ What Sahaayika Does

1. **Scan** — Upload a photo of any handwritten or printed prescription
2. **Understand** — Local AI reads and explains it in simple language
3. **Translate** — Converts explanation to Tamil or Hindi (fully offline)
4. **Speak** — Reads the explanation aloud so even non-readers can understand
5. **Answer** — Tap follow-up buttons for pregnancy safety, danger signs, how to take medicines, and more

---

## 🎯 Who Is It For?

Sahaayika is designed to run on a **shared device** at:
- Village health centres (PHC)
- With ASHA workers
- At rural pharmacies

One installation helps hundreds of women in the village.

---

## 🛠️ Tech Stack

| Component | Technology | Offline? |
|-----------|-----------|---------|
| Prescription reading (OCR) | Tesseract OCR | ✅ Yes |
| AI explanation | Ollama + Gemma 3N | ✅ Yes |
| Translation (Tamil/Hindi) | Argostranslate | ✅ Yes |
| Text to speech | gTTS | 🌐 Needs internet |
| Backend | FastAPI + Python | ✅ Yes |
| Frontend | HTML/CSS/JS | ✅ Yes |

> **Note:** gTTS requires internet only for audio generation. All AI processing and translation happen fully offline on the device.

---

## 📁 Project Structure

```
sahaayika/
├── app.py              # FastAPI backend
├── static/
│   └── index.html      # Frontend UI
└── README.md
```

---

## ⚙️ Installation

### Step 1 — Install Python libraries
```bash
pip install fastapi uvicorn python-multipart gradio pillow pytesseract gtts argostranslate requests
```

### Step 2 — Install Tesseract OCR
Download and install from:
```
https://github.com/UB-Mannheim/tesseract/wiki
```
Default Windows path:
```
C:\Users\<YourName>\AppData\Local\Programs\Tesseract-OCR\tesseract.exe
```
Update this path in `app.py` if yours is different.

### Step 3 — Install and start Ollama
Download from: https://ollama.com/download

Then pull the AI model (needs internet once):
```bash
ollama pull gemma3n
```

> If you want Ollama models stored on a specific drive (e.g. D:), set this before pulling:
> ```bash
> setx OLLAMA_MODELS D:\ollama_models
> ```

### Step 4 — Run the app
```bash
python app.py
```

Open your browser at:
```
http://localhost:8000
```

> On first run, Argostranslate will automatically download Tamil and Hindi language packs (needs internet once, ~100MB). After that it works fully offline.

---

## 🖥️ How to Use

1. Open `http://localhost:8000` in your browser
2. Select your language — **Tamil**, **Hindi**, or **English**
3. Upload a photo of the prescription (or tap **Load Sample** for demo)
4. Tap **Understand My Prescription**
5. Read the explanation or tap **play** to listen
6. Tap any follow-up button to ask specific questions:
   - 🤰 Pregnancy safety
   - 🤱 Breastfeeding safety
   - 👶 Child safety
   - ⚠️ Danger signs
   - 💊 How to take medicines
   - 🩺 Questions to ask the doctor

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
- It never recommends specific dosages
- It always advises users to confirm with a doctor or pharmacist
- It is designed to **assist**, not replace, medical professionals

---

## 🚀 Future Scope

- **Android app** using a lightweight on-device model (Gemma 2B / Phi-3 Mini)
- **More languages** — Telugu, Kannada, Bengali, Marathi
- **Voice input** — let women speak their question instead of tapping
- **Medicine photo recognition** — identify medicines from the tablet/packet photo
- **WhatsApp integration** — send prescription photo via WhatsApp, get explanation back

---

## 👩‍💻 Built By

Built for a social impact hackathon focused on rural healthcare accessibility in India.

*Sahaayika — because every woman deserves to understand her own health.* 🌸
