from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException

try:
    from langdetect import detect as detect_language
except ImportError:
    detect_language = None

app = FastAPI(title="Language Translation Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGUAGES = [
    {"code": "en", "name": "English"}, {"code": "bn", "name": "Bengali"},
    {"code": "es", "name": "Spanish"}, {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"}, {"code": "hi", "name": "Hindi"},
    {"code": "ar", "name": "Arabic"}, {"code": "zh-CN", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"}, {"code": "ko", "name": "Korean"},
    {"code": "ru", "name": "Russian"}, {"code": "ur", "name": "Urdu"},
    {"code": "pt", "name": "Portuguese"}, {"code": "it", "name": "Italian"},
    {"code": "tr", "name": "Turkish"}, {"code": "nl", "name": "Dutch"},
    {"code": "vi", "name": "Vietnamese"}, {"code": "th", "name": "Thai"},
    {"code": "id", "name": "Indonesian"}, {"code": "fa", "name": "Persian"},
]


class TranslateRequest(BaseModel):
    text: str
    source: str = "auto"
    target: str = "en"


@app.get("/")
def root():
    return {"status": "ok", "message": "Translation API is running"}


@app.get("/languages")
async def get_languages():
    return LANGUAGES


def resolve_source_language(text: str, source: str) -> str:
    # GoogleTranslator handles "auto" detection internally, this is
    # just so we can show the user what language it picked
    if source != "auto" or detect_language is None:
        return source
    try:
        detected = detect_language(text)
        return detected.split("-")[0].lower()
    except Exception:
        return "auto"


@app.post("/translate")
async def translate_text(req: TranslateRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text field is empty")

    try:
        translated = GoogleTranslator(source=req.source, target=req.target).translate(req.text)
        detected_display = resolve_source_language(req.text, req.source) if req.source == "auto" else None
        return {
            "translated_text": translated,
            "detected_language": detected_display,
        }
    except LanguageNotSupportedException as e:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Translation failed: {e}")
