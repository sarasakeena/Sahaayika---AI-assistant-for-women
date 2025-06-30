import gradio as gr
import requests
from PIL import Image
from gtts import gTTS
from deep_translator import GoogleTranslator
import uuid
import time
import speech_recognition as sr


OLLAMA_URL = "http://localhost:11434/api/generate"

# Simulated OCR output (fallback for Hugging Face deployment)
def simulate_ocr(image):
    return "This is a sample text extracted from the uploaded image."

# Profile-based context
def get_profile_context(profile):
    context_map = {
        "Woman": "Explain in very simple language for a rural woman who may not be familiar with complex forms or medical terms.",
        "Farmer": "Explain in simple language for a rural woman who is a farmer, with examples or relevance to farming if possible.",
        "Elderly": "Explain in slow, clear, and simple words for an elderly rural woman with possibly limited literacy.",
        "Other": "Explain simply and clearly for someone who may not be familiar with formal documents."
    }
    return context_map.get(profile, context_map["Woman"])

# Translate using Deep Translator
def translate_text(text, lang):
    lang_code = {'Hindi': 'hi', 'Tamil': 'ta'}.get(lang)
    if not lang_code:
        return text
    try:
        return GoogleTranslator(source='auto', target=lang_code).translate(text)
    except Exception as e:
        return f"🌐 Translation failed: {str(e)}"

# Text to speech
def speak(text, lang):
    lang_code = {'Hindi': 'hi', 'Tamil': 'ta', 'English': 'en'}.get(lang, 'en')
    filename = f"output_{uuid.uuid4().hex[:8]}.mp3"
    try:
        gTTS(text=text.replace("*", ""), lang=lang_code).save(filename)
        return filename
    except:
        return None

# Main processing
def process_image(image, language, profile):
    start = time.time()
    extracted_text = simulate_ocr(image)

    instruction = get_profile_context(profile)
    suffix = "\n\nIf it mentions medicine or pesticides, explain what it does and warn of any risks."
    prompt = f"{instruction}\n\n{extracted_text}\n{suffix}"

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": "gemma3n:latest", "prompt": prompt, "system_prompt": "You are a helpful assistant.", "stream": False},
            timeout=60
        )
        result = response.json().get("response", "❌ No response from model.")
    except:
        result = "❌ Ollama server did not respond."

    translated = translate_text(result, language)
    audio = speak(translated, language)
    return f"⏱️ Took {time.time() - start:.2f} sec\n\n{translated}", audio

# Audio transcription
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        # type: ignore is used to suppress type checker warnings about recognize_google
        return recognizer.recognize_google(audio)  # type: ignore
    except:
        return ""

# Doubt handling
def handle_doubt(doubt_text_input, doubt_audio_input, language, profile, image):
    if doubt_audio_input:
        doubt_text_input = transcribe_audio(doubt_audio_input)

    if not doubt_text_input:
        return "⚠️ Please enter or record a question.", None

    lang_code = {'Hindi': 'hi', 'Tamil': 'ta'}.get(language)
    if lang_code:
        try:
            doubt_english = GoogleTranslator(source='auto', target='en').translate(doubt_text_input)
        except:
            doubt_english = doubt_text_input
    else:
        doubt_english = doubt_text_input

    context_text = simulate_ocr(image)
    prompt = f"You explained the following:\n\n{context_text}\n\nNow the user has a question: {doubt_english}\n\nAnswer clearly in simple English."

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": "gemma3n:latest", "prompt": prompt, "system_prompt": "You are a helpful assistant.", "stream": False},
        )
        answer = response.json().get("response", "❌ No response.")
    except:
        answer = "❌ Ollama did not respond."

    if lang_code:
        try:
            answer_translated = GoogleTranslator(source='auto', target=lang_code).translate(answer)
        except:
            answer_translated = answer
    else:
        answer_translated = answer

    audio = speak(answer_translated, language)
    return answer_translated, audio

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🌸 Sahaayika — AI Visual Assistant for Rural Women")
    gr.Markdown("Reads and explains any form or medicine label in **Hindi**, **Tamil**, or **English**.\nWorks best with clear photos!")

    with gr.Row():
        image_input = gr.Image(type="pil", label="📸 Upload an Image")
        language_input = gr.Radio(["Hindi", "Tamil", "English"], label="🌍 Choose Output Language", value="English")
        profile_input = gr.Dropdown(["Woman", "Farmer", "Elderly", "Other"], label="👤 Profile Type", value="Woman")

    output_text = gr.Textbox(label="📝 Simplified Explanation", lines=10)
    output_audio = gr.Audio(type="filepath", label="🔊 Listen to the Output")

    gr.Button("🧠 Understand Image").click(
        fn=process_image,
        inputs=[image_input, language_input, profile_input],
        outputs=[output_text, output_audio]
    )

    gr.Markdown("## ❓ Ask a Doubt About the Document")
    with gr.Row():
        doubt_text = gr.Textbox(label="✍️ Ask your question", placeholder="Type your doubt in your language...")
        doubt_audio_input = gr.Audio(type="filepath", label="🎙️ Or record your doubt")

    doubt_response_text = gr.Textbox(label="🧾 Answer to your question", lines=6)
    doubt_audio_output = gr.Audio(type="filepath", label="🔊 Spoken Answer")

    gr.Button("📩 Ask My Doubt").click(
        fn=handle_doubt,
        inputs=[doubt_text, doubt_audio_input, language_input, profile_input, image_input],
        outputs=[doubt_response_text, doubt_audio_output]
    )

demo.launch()
