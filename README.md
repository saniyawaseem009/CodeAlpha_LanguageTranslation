# 🌐 Advanced Language Translation Tool

A full-stack translation web app built with Flask. It uses a **Smart Fallback Architecture**: tries DeepL (Premium API) first, and automatically falls back to Google Translate if the API limit is exceeded. 

## ✨ Features
- **Smart Fallback**: Never crashes due to API limits.
- **Engine Badge**: Shows which API translated the text in real-time.
- **14+ Languages** with Auto-Detect.
- **Text-to-Speech (TTS)** & Audio Download.
- **Copy-to-Clipboard** feature.
- **One-Click Language Swap**.
- **Responsive UI** built with Bootstrap 5.

## 🛠️ Tech Stack
- **Backend**: Python, Flask
- **APIs**: DeepL API, Google Translate (deep-translator)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Audio**: gTTS (Google Text-to-Speech)

## 🚀 How to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/CodeAlpha_LanguageTranslation.git

2. Install dependencies:
    ```bash
    pip3 install -r requirements.txt

3. Create a .env file in the root folder and add your DeepL API key:

    ```env
    DEEPL_AUTH_KEY=your_deepl_api_key_here

4. Run the app:
    ```bash
    python3 app.py

5. Open http://127.0.0.1:8000 in your browser.
