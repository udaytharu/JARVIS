# JARVIS-AI Voice Assistant (Windows, PyQt5)

## Overview
JARVIS-AI 2.0 is an advanced modular voice & desktop assistant featuring voice I/O, real-time web search, desktop automation, AI chat, image generation, and a rich PyQt5 GUI. It leverages Groq for LLM-powered chat, Cohere (configurable, defaulting to 'command-light' for students/free use) for smart routing, and HuggingFace for fast image generation.

---

## Features
- **Voice Interaction**: Microphone/Edge TTS, background wake phrase listener
- **Face Authentication**: Webcam login (OpenCV LBPH)
- **Modern PyQt5 GUI**: with status, animation, and command input
- **AI Chat**: Groq models via Chatbot, fully contextual
- **Real-Time Info**: Google CSE via RealtimeSearchEngine
- **Desktop Automation**: Apps, YouTube, system, content, presentations, email+ more
- **Universal Navigation**: *Now powered by `nav` (Navigator)* for human-language control—scroll, swipe, zoom, keys, PDF nav, all with phrases
- **Real-Time Screen Analysis**: Screen observation, OCR text reading, element detection, and intelligent clicking (NEW!)
- **AI Image Generation**: HuggingFace SDXL
- **.env-Driven Config**: All API keys/names/voices/model choices modular via .env
- **Robust Error Handling**: Every action returns result+error; all surfacing to UI

---

## How Navigation & Commands Work (NEW)

Navigation uses the `Navigator` class — see `Backend/Navigation.py` — with a global `nav` instance. All navigation phrases ("scroll up 10", "fullscreen", etc.) route through `nav.run(phrase1, phrase2, ...)` directly from main.py. To expand phrase support, simply update the mapping in Navigator.run().

> **TIP:** If the intent router (decision model) gives e.g. "scrollup", normalize to "scroll up" before calling nav.run() for perfect mapping (see JARVIS_Commands.md for all supported commands/phrases).

---

## Command List & Natural Language

For all navigation/automation/AI commands, see [`JARVIS_Commands.md`](./JARVIS_Commands.md). If a spoken/typed phrase doesn't work, check/extend the table directly, or normalize it in main.py before execution.

### Screen Observation Commands (NEW!)

JARVIS can now observe and analyze your screen in real-time to help with automation:

- **"analyze screen"** - Analyze screen content and detect UI elements (buttons, text, etc.)
- **"read screen"** or **"read screen text"** - Read all text from screen using OCR
- **"find text [text]"** or **"click on [text]"** - Find and click on specific text on screen
- **"observe screen [query]"** - Observe screen and answer questions about what's displayed
- **"what's on screen"** - Get a summary of what's currently displayed

**Note:** Screen observation features require `pytesseract` and Tesseract OCR engine. Install Tesseract:
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

Screen analysis helps JARVIS make smarter automation decisions by understanding what's actually on your screen!

---

## Model & API Configuration (.env)

- **Cohere Model for DMM/intent routing:** Controlled via `.env`:
  ```
  CohereModel=command-light
  ```
  > If you get a model-deprecated error, update this to a new model name from Cohere’s docs, then restart. **No code change required!**

- **All keys/IDs (.env):**
  - CohereAPIKey, GroqAPIKey, Google_API_KEY, etc.
  - AssistantName, Username, AssistantVoice, InputLanguage, etc.

---

## Error Handling & Troubleshooting

- **NO silent failures**: All backend calls return `(result, error)` and any error is shown in the UI instantly (TTS and/or chat window).
- **Model deprecated?**: Watch for 404 error from Cohere; just update `.env`.
- **Navigation not working?**: Check for command mismatch. If you see `[Navigator] Unknown command: ...`, normalize/extend the mapping in `Backend/Navigation.py`.
- **Microphone/Speech errors?**: Errors shown in chat window. Check permissions.


---

## File Structure (Key)
```sh
Backend/
  assistant_core.py        # Text-to-routing backend
  Automation.py           # Desktop automation (apps/system/media/email/web) + screen analysis
  Chatbot.py              # Groq chatbot/LLM
  ImageGeneration.py      # HuggingFace SDXL
  Model.py                # Cohere intent classification (DMM) - set model in .env
  Navigation.py           # Navigator (nav) universal control (scroll, swipe, zoom...)
  RealTimeScreenShare.py  # Real-time screen analysis, OCR, element detection (NEW!)
  RealtimeSearchEngine.py # Google CSE + Groq
  auth/                   # Face recognition
  SpeechToText.py         # Voice input
  TextToSpeech.py         # Edge TTS
Frontend/GUI.py           # PyQt5 GUI
... (see full tree above)
```

---

## Setup/Install (Summary)
1. `pip install -r Requirements.txt`
2. **Install Tesseract OCR** (for screen observation features):
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`
3. Configure `.env` (see above)
4. Run `JARVIS_START.bat` for background listener+GUI

**Note:** Screen observation features are optional. If Tesseract is not installed, screen analysis will work but OCR text reading will be disabled.

---

## For Contributors
- Extend navigation via `Navigator.run()` mapping.
- Update/normalize model names in .env, not code!
- Errors always surface to UI; check logs for `[Navigator]` or backend errors if something fails.
---
