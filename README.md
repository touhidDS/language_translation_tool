# Language Translation Tool

A full-stack text translation web app. Type or paste text, pick a source and target language (or let it auto-detect), and get an instant translation.

**Live demo:** https://touhidDS.github.io/language_translation_tool/

## Stack

- **Frontend** — vanilla HTML/CSS/JS, no framework or build step, hosted on GitHub Pages
- **Backend** — FastAPI, hosted on Render
- **Translation** — [deep-translator](https://github.com/nidhaloff/deep-translator)'s `GoogleTranslator` wrapper (free, no API key required)
- **Language detection** — `langdetect`, used to report which language was picked when "Auto-detect" is selected

## Project structure

```
language_translation_tool/
├── backend/
│   ├── main.py            # FastAPI app: /translate and /languages endpoints
│   ├── requirements.txt
│   └── runtime.txt        # pins Python version for Render
├── docs/                  # frontend, served directly by GitHub Pages
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── config.js          # points the frontend at the backend URL
└── README.md
```

## How it works

1. The frontend sends `{ text, source, target }` to `POST /translate`.
2. The backend calls `GoogleTranslator(source, target).translate(text)` and returns the result.
3. If `source` is `"auto"`, `langdetect` runs separately just to label which language was detected in the UI — the actual translation still lets `GoogleTranslator` handle auto-detection internally.

## Running locally

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Check it's up at `http://localhost:8000` — you should see `{"status": "ok", ...}`.

**Frontend**

```bash
cd docs
python -m http.server 5500
```

Open `http://localhost:5500`. If you're testing against a local backend, change `API_BASE` in `docs/config.js` to `http://localhost:8000` first.

## Deployment notes

- Backend is deployed on Render's free tier, which spins down after inactivity — the first request after idle can take 30–50 seconds while it wakes up. Not a bug, just how free hosting works.
- Frontend is served straight from the `docs/` folder via GitHub Pages, which is why the folder is named `docs` instead of `frontend`.
- CORS is currently open (`allow_origins=["*"]`) since this is a small demo project. For a production app, this should be locked to the actual frontend origin.

## Known limitations

- Free translation API, so no SLA — occasional slowness or downtime is possible.
- No request rate limiting on the backend yet.
- Language list is a static, hand-picked subset (20 languages) rather than the full set Google Translate supports.

## Possible improvements

- Add basic rate limiting / caching for repeated translations
- Swap in the official Google Cloud Translation API for production reliability
- Add translation history (localStorage) on the frontend
