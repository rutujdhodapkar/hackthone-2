import json
import streamlit as st
import os
from sarvamai import SarvamAI

# SARVAM AI CENTRALIZED CONFIGURATION
SARVAM_API_KEY = "sk_zmlsl303_SMPuT8dJPTlYCakAj45krULM"
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

def ask_oss_ai(prompt, system_prompt="You are a helpful agricultural advisor."):
    """Helper to call OSS AI via OpenRouter (single turn)."""
    return ask_oss_chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ])

def ask_oss_chat(messages):
    """Helper to call OSS AI via OpenRouter with full message history."""
    try:
        # Switching to Google's Gemma 2 9B as per user request to resolve provider errors.
        models = [
            "meta-llama/llama-3.1-8b-instruct:free",
            "meta-llama/llama-3.3-70b-instruct:free",
        ]
        
        last_error = ""
        for model in models:
            try:
                # IMPORTANT: Ensuring the API key and headers are perfect to avoid 401
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://localhost:8501", 
                        "X-Title": "Agri AI Advisor",
                    },
                    data=json.dumps({
                        "model": model,
                        "messages": messages
                    }),
                    timeout=15
                )
                
                if response.status_code == 401:
                    last_error = f"401 Unauthorized: {response.text}"
                    print(f"OpenRouter 401 for {model}: {response.text}")
                    continue # Try next model or fail loop

                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    last_error = result.get('error', {}).get('message', 'Unknown Error')
                    print(f"Model {model} failed: {last_error}")
            except Exception as e:
                last_error = str(e)
                print(f"Model {model} exception: {e}")
        
        return f"ERROR: {last_error}"
    except Exception as e:
        print(f"OSS LLM Exception: {e}")
        return f"EXCEPTION: {str(e)}"

def t(text):
    """Utility function to translate dynamic text based on current session language."""
    target_lang = st.session_state.get("lang_code", "en-IN")
    return translate_text(text, target_lang)

# =========================================================
# 🎤 VOICE / AUDIO HELPERS
# =========================================================

import base64
import uuid
import tempfile

def text_to_speech(text, target_lang_code):
    """Converts text to speech using Sarvam AI Bulbul:v3 via streaming Requests."""
    try:
        headers = {
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "target_language_code": target_lang_code,
            "speaker": "shubh",
            "model": "bulbul:v3",
            "pace": 1.0,
            "speech_sample_rate": 22050,
            "output_audio_codec": "mp3",
            "enable_preprocessing": True
        }
        tts_url = "https://api.sarvam.ai/text-to-speech/stream"
        
        response = requests.post(tts_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            print(f"TTS API Error: {response.text}")
            return None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def speech_to_text(audio_data, target_lang_code):
    """Transcribes audio using Sarvam AI Saaras model via Job API."""
    try:
        # 1. Save buffer to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(audio_data.getvalue() if hasattr(audio_data, 'getvalue') else audio_data)
            audio_path = tmp.name

        # 2. Create Job
        job = sarvam_client.speech_to_text_job.create_job(
            model="saaras:v3",
            mode="transcribe",
            language_code="unknown", 
            with_diarization=False   
        )
        
        # 3. Process
        job.upload_files(file_paths=[audio_path])
        job.start()
        job.wait_until_complete()
        
        # 4. Results check
        file_results = job.get_file_results()
        if file_results['successful']:
            out_dir = f"./output_{uuid.uuid4().hex}"
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
                
            try:
                job.download_outputs(output_dir=out_dir)
                files = os.listdir(out_dir)
                if files:
                    with open(os.path.join(out_dir, files[0]), "r", encoding="utf-8") as f:
                        raw_result = f.read()
                    
                    # PROPER PARSING: Sarvam results are JSON
                    try:
                        res_json = json.loads(raw_result)
                        transcript = res_json.get("transcript", raw_result)
                    except:
                        transcript = raw_result
                    
                    import shutil
                    shutil.rmtree(out_dir, ignore_errors=True)
                    try: os.unlink(audio_path)
                    except: pass
                    return transcript
            except Exception as e:
                print(f"STT Error during download/parse: {e}")
                import shutil
                shutil.rmtree(out_dir, ignore_errors=True)
        
        try: os.unlink(audio_path)
        except: pass
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
