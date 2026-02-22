import json
import streamlit as st
import os
from sarvamai import SarvamAI

# SARVAM AI CENTRALIZED CONFIGURATION
SARVAM_API_KEY = "sk_1x6902nv_YD6iYU66jylp0rxDeynkuu6o"
OPENROUTER_API_KEY = "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"
JSON_FILE = "farmer_data.json"
CACHE_FILE = "translation_cache.json"

import requests
import base64

def detect_crop_from_image(image_base64):
    """Detects crop from image using OpenRouter & Nvidia Nemotron Nano Vision."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "nvidia/nemotron-nano-12b-v2-vl:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Identify the primary crop in this image. Return ONLY the name of the crop (e.g., Rice, Wheat, Sugarcane) in one word."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            })
        )
        result = response.json()
        crop_name = result['choices'][0]['message']['content'].strip().replace(".", "")
        return crop_name
    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return None

# Initialize Global Sarvam Client
sarvam_client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

# Sarvam AI supports 22 languages
SUPPORTED_LANGUAGES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Gujarati": "gu-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Odia": "or-IN",
    "Punjabi": "pa-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Urdu": "ur-IN",
    "Assamese": "as-IN",
    "Kashmiri": "ks-IN",
    "Konkani": "kok-IN",
    "Maithili": "mai-IN",
    "Nepali": "ne-IN",
    "Sanskrit": "sa-IN",
    "Sindhi": "sd-IN",
    "Bodo": "brx-IN",
    "Dogri": "doi-IN",
    "Manipuri": "mni-IN",
    "Santali": "sat-IN"
}

def save_json(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_json():
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE) as f:
                return json.load(f)
    except:
        pass
    return {}

@st.cache_resource
def get_persistent_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except:
        pass

def translate_text(text, target_lang_code):
    if not text or target_lang_code == "en-IN":
        return text
    
    # Persistent Cache check
    if "translation_cache" not in st.session_state:
        st.session_state.translation_cache = get_persistent_cache()
    
    cache_key = f"{text}_{target_lang_code}"
    if cache_key in st.session_state.translation_cache:
        return st.session_state.translation_cache[cache_key]
    
    # Sarvam SDK Call (as per user example)
    try:
        response = sarvam_client.text.translate(
            input=text,
            source_language_code="en-IN",
            target_language_code=target_lang_code,
            speaker_gender="Male",
            mode="formal",
            model="mayura:v1",
            numerals_format="native"
        )
        
        if hasattr(response, 'translated_text'):
            translated_text = response.translated_text
        else:
            translated_text = response.get("translated_text", text) if isinstance(response, dict) else str(response)

        # Save to Cache
        st.session_state.translation_cache[cache_key] = translated_text
        save_cache(st.session_state.translation_cache)
        
        return translated_text
    except Exception as e:
        print(f"Translation Error: {e}")
        return text

def ask_sarvam_ai(prompt, system_prompt="You are a helpful agricultural advisor."):
    """Helper to call Sarvam AI Chat Completion."""
    try:
        response = sarvam_client.chat.completions(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Sarvam LLM Error: {e}")
        return None

def t(text):
    """Utility function to translate dynamic text based on current session language."""
    target_lang = st.session_state.get("lang_code", "en-IN")
    return translate_text(text, target_lang)

# =========================================================
# 🎤 VOICE / AUDIO HELPERS
# =========================================================

import base64

def text_to_speech(text, target_lang_code):
    """Converts text to speech using Sarvam AI Bulbul model."""
    try:
        response = sarvam_client.text_to_speech.convert(
            text=text,
            language_code=target_lang_code,
            model="bulbul:v1",
            voice="amrit"
        )
        if hasattr(response, 'audio_content'):
            return response.audio_content
        return None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def speech_to_text(audio_file, target_lang_code):
    """Transcribes audio using Sarvam AI Saaras model."""
    try:
        response = sarvam_client.speech_to_text.transcribe(
            file=audio_file,
            language_code=target_lang_code,
            model="saaras:v3"
        )
        if hasattr(response, 'transcript'):
            return response.transcript
        elif hasattr(response, 'text'):
            return response.text
        elif isinstance(response, dict) and 'transcript' in response:
            return response['transcript']
        return None
    except Exception as e:
        print(f"STT Error: {e}")
        return None

def get_voice_prompt(field):
    """Returns a natural voice prompt for gathering farmer data."""
    prompts = {
        "introduction": "Welcome to AI Farmer Advisor! Let's set up your farm profile. Please answer correctly to get the best advice.",
        "location": "First, where is your farm located? Please tell me the village and district.",
        "crop": "Great. What crop are you planning to grow or have currently in your field?",
        "field_size": "And what is the size of your field in acres?",
        "burned": "Has your field's crop residue already been burned? Answer yes or no.",
        "equipment": "What equipment do you have access to? For example, tractor, baler, or rotavator.",
        "completion": "Thank you! I have all your details. Now you can check the analysis pages for personalized advice."
    }
    return t(prompts.get(field, "Please answer the question."))

def autoplay_audio(audio_bytes):
    """Encodes audio bytes for Streamlit autoplay."""
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
