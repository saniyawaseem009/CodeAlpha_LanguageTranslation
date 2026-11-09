"""Core translation logic using DeepL API with Google Fallback."""
import os
import requests
from deep_translator import GoogleTranslator
from gtts import gTTS
import io

DEEPL_KEY = "07047506-1551-4195-8acf-65ce0f859da0:fx"
DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"

# DeepL specific language codes
LANGUAGES = {
    "English": "EN",
    "Hindi": "HI",
    "Spanish": "ES",
    "French": "FR",
    "German": "DE",
    "Italian": "IT",
    "Portuguese": "PT",
    "Russian": "RU",
    "Japanese": "JA",
    "Korean": "KO",
    "Chinese (Simplified)": "ZH",
    "Arabic": "AR",
    "Bengali": "BN",
    "Tamil": "TA",
    "Telugu": "TE",
    "Urdu": "UR",
    "Dutch": "NL",
    "Turkish": "TR",
}

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    if not text or not text.strip():
        return ""
    if source_lang == target_lang:
        return text

    # DeepL API Request
    if DEEPL_KEY:
        headers = {
            "Authorization": f"DeepL-Auth-Key {DEEPL_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "text": [text],
            "target_lang": target_lang,
            "source_lang": source_lang,
        }
        
        try:
            response = requests.post(DEEPL_ENDPOINT, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()["translations"][0]["text"]
        except Exception:
            pass # Agar DeepL fail hua (jaise Hindi pe), toh niche fallback chalega

    # SMART FALLBACK (Google Translate) - DeepL agar fail ho jaye toh
    try:
        google_src = source_lang.lower()
        google_tgt = target_lang.lower()
        return GoogleTranslator(source=google_src, target=google_tgt).translate(text)
    except Exception as e:
        raise Exception(f"Both APIs failed. Error: {e}")

def text_to_speech(text: str, lang_code: str) -> bytes:
    if not text or not text.strip():
        return b""

    tts_map = {"ZH": "zh-CN", "EN": "en", "HI": "hi"}
    tts_lang = tts_map.get(lang_code, lang_code.lower())

    try:
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return b""