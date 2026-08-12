"""
Language Translation Tool - Backend
------------------------------------
FastAPI server that receives text from the frontend and forwards it to
MyMemory Translation API (genuinely free, no API key or signup required).

Free tier limit: 5,000 characters/day per IP (anonymous), or 50,000/day
if you set MYMEMORY_EMAIL below (MyMemory raises the limit for a
provided contact email - no account needed, just used for the quota).

To move to Google Cloud Translation or Microsoft Azure Translator later,
replace the call inside translate_text() and add your API key as an
environment variable (never hardcode it).
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

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

MYMEMORY_URL = "https://api.mymemory.translated.net/get"
# Optional: put your email here (raises the free daily limit from 5,000 to 50,000 chars)
MYMEMORY_EMAIL = os.environ.get("MYMEMORY_EMAIL", "")

# Static language list for the dropdowns (MyMemory doesn't expose a /languages endpoint)
LANGUAGES = [
    {"code": "en", "name": "English"}, {"code": "bn", "name": "Bengali"},
    {"code": "es", "name": "Spanish"}, {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"}, {"code": "hi", "name": "Hindi"},
    {"code": "ar", "name": "Arabic"}, {"code": "zh", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"}, {"code": "ko", "name": "Korean"},
    {"code": "ru", "name": "Russian"}, {"code": "ur", "name": "Urdu"},
    {"code": "pt", "name": "Portuguese"}, {"code": "it", "name": "Italian"},
    {"code": "tr", "name": "Turkish"}, {"code": "nl", "name": "Dutch"},
    {"code": "vi", "name": "Vietnamese"}, {"code": "th", "name": "Thai"},
    {"code": "id", "name": "Indonesian"}, {"code": "fa", "name": "Persian"},
]


class TranslateRequest(BaseModel):
    text: str
    source: str = "auto"   # "auto" = auto-detect source language
    target: str = "en"


@app.get("/")
def root():
    return {"status": "ok", "message": "Translation API is running"}


@app.get("/languages")
async def get_languages():
    """Static language list used to populate the frontend dropdowns."""
    return LANGUAGES


def resolve_source_language(text: str, source: str) -> str:
    """MyMemory has no reliable server-side auto-detect, so detect locally
    with langdetect when source == 'auto'. Falls back to English if the
    library isn't installed or detection fails."""
    if source != "auto":
        return source
    if detect_language is None:
        return "en"
    try:
        return detect_language(text)
    except Exception:
        return "en"


@app.post("/translate")
async def translate_text(req: TranslateRequest):
    """Translate text using the MyMemory API and return the translated string."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text field is empty")

    detected_source = resolve_source_language(req.text, req.source)

    params = {
        "q": req.text,
        "langpair": f"{detected_source}|{req.target}",
    }
    if MYMEMORY_EMAIL:
        params["de"] = MYMEMORY_EMAIL

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(MYMEMORY_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            if data.get("responseStatus") not in (200, "200"):
                raise HTTPException(
                    status_code=502,
                    detail=data.get("responseDetails", "Translation service error"),
                )

            return {
                "translated_text": data["responseData"]["translatedText"],
                "detected_language": detected_source if req.source == "auto" else None,
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Translation service error: {e.response.text}",
            )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Could not reach translation service: {e}")
