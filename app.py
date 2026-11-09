import os
import io
import base64
import requests
from flask import Flask, render_template_string, request
from deep_translator import GoogleTranslator
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DEEPL_KEY = os.getenv("DEEPL_AUTH_KEY", "")

SOURCE_LANGUAGES = [
    {"code": "AUTO", "name": "Auto Detect 🌐"},
    {"code": "EN", "name": "English"},
    {"code": "HI", "name": "Hindi (हिंदी)"},
    {"code": "ES", "name": "Spanish (Español)"},
    {"code": "FR", "name": "French (Français)"},
    {"code": "DE", "name": "German (Deutsch)"},
    {"code": "JA", "name": "Japanese (日本語)"},
    {"code": "KO", "name": "Korean (한국어)"},
    {"code": "ZH", "name": "Chinese (中文)"},
    {"code": "AR", "name": "Arabic (العربية)"},
    {"code": "RU", "name": "Russian (Русский)"},
    {"code": "PT", "name": "Portuguese (Português)"},
    {"code": "IT", "name": "Italian (Italiano)"},
    {"code": "TR", "name": "Turkish (Türkçe)"}
]

TARGET_LANGUAGES = [lang for lang in SOURCE_LANGUAGES if lang["code"] != "AUTO"]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Language Translation Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .container { margin-top: 40px; max-width: 1100px; }
        .header-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 30px;}
        .header-card h1 { font-weight: 700; font-size: 2.2rem; margin-bottom: 5px; }
        .header-card p { font-size: 1rem; opacity: 0.9; margin: 0;}
        .card { box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: none; border-radius: 12px; }
        .lang-selector { width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; background: #fff; border-bottom: 1px solid #eee; border-top-left-radius: 12px; border-top-right-radius: 12px;}
        textarea { resize: none; border-radius: 8px; border: 1px solid #ddd; padding: 15px; font-size: 1.1rem; background: #fafafa; color: #333;}
        textarea:focus { box-shadow: none; border-color: #667eea; background: #fff; }
        .form-select { border: none; font-weight: 600; color: #555; cursor: pointer; background-color: transparent; padding: 5px 10px; }
        .form-select:focus { box-shadow: none; }
        .btn-primary { background: #667eea; border: none; padding: 12px 30px; font-size: 1.1rem; font-weight: 600; border-radius: 8px; transition: all 0.3s; width: 100%; color: white;}
        .btn-primary:hover { background: #5a6fd6; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
        .btn-swap { background: #fff; border: 1px solid #ddd; font-size: 1.2rem; padding: 8px 15px; border-radius: 50%; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; height: 45px; width: 45px; margin-top: 20px;}
        .btn-swap:hover { background: #f0f0f0; transform: rotate(180deg); }
        
        .btn-action { font-size: 0.9rem; padding: 8px 15px; border-radius: 6px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; transition: 0.2s; border: none; cursor: pointer;}
        .btn-copy { background: #e2e8f0; color: #475569; }
        .btn-copy:hover { background: #cbd5e1; color: #0f172a; }
        .btn-download { background: #dcfce7; color: #166534; }
        .btn-download:hover { background: #bbf7d0; color: #14532d; }
        
        .tone-selector { margin-top: 15px; text-align: center; display: flex; justify-content: center; gap: 10px; align-items: center;}
        .error-msg { color: #dc3545; font-size: 1rem; margin-top: 10px; text-align: center; font-weight: bold; }
        .engine-badge { font-size: 0.8rem; padding: 3px 8px; border-radius: 4px; background: #e2e8f0; color: #475569; margin-left: 10px; font-weight: normal;}
    </style>
    <script>
        function copyText() {
            var copyText = document.getElementById("output-text");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            navigator.clipboard.writeText(copyText.value);
            var btn = document.getElementById("copy-btn");
            var originalText = btn.innerHTML;
            btn.innerHTML = "✅ Copied!";
            setTimeout(function() { btn.innerHTML = originalText; }, 2000);
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header-card">
            <h1>🌐 Language Translation Tool</h1>
            <p>Powered by DeepL & Google Translate</p>
        </div>

        <form method="POST">
            <div class="row">
                <div class="col-md-5 mb-3">
                    <div class="card h-100">
                        <div class="lang-selector">
                            <span class="text-muted fw-bold" style="font-size: 0.9rem;">Translate From</span>
                            <select name="source_lang" class="form-select w-auto">
                                {% for lang in source_languages %}
                                <option value="{{ lang.code }}" {% if source_lang == lang.code %}selected{% endif %}>{{ lang.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="card-body p-3">
                            <textarea name="text" class="form-control" rows="8" placeholder="Type here..." required>{{ source_text }}</textarea>
                        </div>
                    </div>
                </div>

                <div class="col-md-2 mb-3 d-flex align-items-center justify-content-center">
                    <button type="submit" name="swap" value="true" class="btn btn-swap shadow-sm" title="Swap Languages">🔁</button>
                </div>

                <div class="col-md-5 mb-3">
                    <div class="card h-100">
                        <div class="lang-selector">
                            <span class="text-muted fw-bold" style="font-size: 0.9rem;">Translate To</span>
                            <select name="target_lang" class="form-select w-auto">
                                {% for lang in target_languages %}
                                <option value="{{ lang.code }}" {% if target_lang == lang.code %}selected{% endif %}>{{ lang.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="card-body p-3">
                            <!-- Engine Badge to show which API was used -->
                            {% if engine_used %}
                            <div class="text-end mb-1"><span class="engine-badge">Engine: {{ engine_used }}</span></div>
                            {% endif %}
                            
                            <textarea id="output-text" class="form-control" rows="7" readonly>{{ result_text }}</textarea>
                            
                            {% if result_text %}
                            <div class="action-btns mt-2">
                                <button type="button" id="copy-btn" class="btn-action btn-copy" onclick="copyText()">📋 Copy Text</button>
                            </div>
                            {% endif %}

                            {% if audio_data %}
                            <audio controls class="mt-3 w-100" style="border-radius: 8px; outline: none; height: 40px;">
                                <source src="data:audio/mp3;base64,{{ audio_data }}" type="audio/mp3">
                            </audio>
                            <div class="action-btns mt-2">
                                <a href="data:audio/mp3;base64,{{ audio_data }}" download="translation_audio.mp3" class="btn-action btn-download">📥 Download Audio</a>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-2">
                <div class="col-md-6 mx-auto tone-selector">
                    <label style="font-weight: bold; font-size: 0.95rem; color: #555;">Translation Engine: </label>
                    <select name="tone" class="form-select w-auto border" style="border-radius: 8px; background: #fff;">
                        <option value="default" {% if tone == 'default' %}selected{% endif %}>Auto (DeepL → Google Fallback)</option>
                        <option value="google" {% if tone == 'google' %}selected{% endif %}>Force Google Translate</option>
                    </select>
                </div>
            </div>

            <div class="row mt-3">
                <div class="col-md-4 mx-auto">
                    <button type="submit" name="translate" value="true" class="btn btn-primary shadow d-flex align-items-center justify-content-center gap-2">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-translate" viewBox="0 0 16 16">
        <path d="M4.545 6.714 4.11 8H3l1.862-5h1.284L8 8H6.833l-.435-1.286zm1.634-.736L5.5 3.956h-.049l-.679 2.022z"/>
        <path d="M0 2a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v3h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-3H2a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zm7.138 9.995c.193.301.402.583.63.846-.748.575-1.673 1.001-2.768 1.292.178.217.451.635.555.867 1.125-.359 2.08-.844 2.886-1.494.777.665 1.739 1.165 2.93 1.472.133-.254.414-.673.629-.89-1.125-.253-2.057-.694-2.82-1.284.681-.747 1.222-1.651 1.621-2.757H14V8h-3v1.047h.765c-.318.844-.74 1.546-1.272 2.13a6 6 0 0 1-.415-.492 2 2 0 0 1-.294-.55H8v1.19h-.001v-1.19a2.5 2.5 0 0 1-.345.644 6 6 0 0 1-.415.492c-.532-.584-.954-1.286-1.272-2.13H6V8H3v1.047h.882c.399 1.106.94 2.01 1.621 2.757-.763.59-1.695 1.031-2.82 1.284.215.217.496.636.629.89 1.191-.307 2.153-.807 2.93-1.472.806.65 1.761 1.135 2.886 1.494.104-.232.377-.65.555-.867-1.095-.291-2.02-.717-2.768-1.292.228-.263.437-.545.63-.846"/>
    </svg>
    Translate
</button>
                    {% if error %}
                    <div class="error-msg">{{ error }}</div>
                    {% endif %}
                </div>
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    source_text = ""
    result_text = ""
    source_lang = "EN"
    target_lang = "HI"
    tone = "default"
    audio_data = ""
    error = None
    engine_used = None

    if request.method == "POST":
        source_text = request.form.get("text", "")
        source_lang = request.form.get("source_lang", "EN")
        target_lang = request.form.get("target_lang", "HI")
        tone = request.form.get("tone", "default")
        
        if "swap" in request.form:
            if source_lang == "AUTO":
                source_lang = "EN"
            source_lang, target_lang = target_lang, source_lang
            return render_template_string(HTML, source_languages=SOURCE_LANGUAGES, target_languages=TARGET_LANGUAGES, source_text=source_text, result_text="", source_lang=source_lang, target_lang=target_lang, tone=tone, audio_data="", error=None, engine_used=None)

        if source_text and "translate" in request.form:
            result_text = ""
            
            # --- ENGINE 1: DEEPL (Primary) ---
            if tone == "default" and DEEPL_KEY:
                try:
                    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_KEY}"}
                    payload = {"text": [source_text], "target_lang": target_lang}
                    if source_lang != "AUTO":
                        payload["source_lang"] = source_lang
                    
                    res = requests.post("https://api-free.deepl.com/v2/translate", headers=headers, json=payload, timeout=5)
                    
                    if res.status_code == 200:
                        result_text = res.json()["translations"][0]["text"]
                        engine_used = "DeepL (Premium)"
                    else:
                        # 456 = Quota Exceeded, 429 = Too Many Requests
                        raise Exception("Limit Exceeded")
                except Exception:
                    pass # DeepL fail hua, neeche Google chalega

            # --- ENGINE 2: GOOGLE (Fallback) ---
            if not result_text:
                try:
                    gl_source = 'auto' if source_lang == "AUTO" else source_lang.lower()
                    gl = GoogleTranslator(source=gl_source, target=target_lang.lower())
                    result_text = gl.translate(source_text)
                    engine_used = "Google Translate (Fallback)"
                except Exception as e:
                    error = f"Translation failed. Error: {e}"

            # --- ENGINE 3: AUDIO GENERATION ---
            if result_text and not error:
                try:
                    tts_lang = target_lang.lower()
                    if target_lang == "ZH": tts_lang = "zh-CN"
                    
                    tts = gTTS(text=result_text, lang=tts_lang, slow=False)
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    audio_data = base64.b64encode(audio_buffer.read()).decode('utf-8')
                except Exception:
                    error = "Audio generation failed for this language."

    return render_template_string(HTML, source_languages=SOURCE_LANGUAGES, target_languages=TARGET_LANGUAGES, source_text=source_text, result_text=result_text, source_lang=source_lang, target_lang=target_lang, tone=tone, audio_data=audio_data, error=error, engine_used=engine_used)

if __name__ == "__main__":
    app.run(debug=True, port=8000)