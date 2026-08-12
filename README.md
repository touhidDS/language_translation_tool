# Language Translation Tool

A simple full-stack translation app:
- **Frontend**: plain HTML/CSS/JS (no build tools needed)
- **Backend**: FastAPI, which relays requests to **LibreTranslate** (free, no API key)
- **Extras**: Copy button + Text-to-Speech (built into the browser)

```
translator/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

## How to Run

### 1. Set up and start the backend

Open a terminal in the `translator/backend` folder:

```bash
# create a virtual environment (recommended)
python -m venv venv

# activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the server
uvicorn main:app --reload --port 8000
```

You should see something like:
```
Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal running. Test it works by opening **http://localhost:8000** in your browser — you should see `{"status":"ok", ...}`.

### 2. Open the frontend

No build step needed — just open the HTML file directly:

- Go to the `translator/frontend` folder
- Double-click `index.html` (it will open in your default browser)

**OR**, for a cleaner setup, serve it with a tiny local server (avoids some browser file:// quirks):

```bash
cd translator/frontend
python -m http.server 5500
```
Then visit **http://localhost:5500** in your browser.

### 3. Use it

1. Type or paste text in the left box
2. Pick "From" (or leave it on Auto-detect) and "To" language
3. Click **Translate** (or press Ctrl/Cmd + Enter)
4. Read the result on the right — use **Copy** to copy it, or the speaker icon to hear it read aloud
5. Use the circular swap button in the middle to flip source ↔ target language

## Notes & Customization

- **Free API used**: `https://libretranslate.com/translate` — no key required, but it's rate-limited and can occasionally be slow/unavailable since it's a shared public instance. For production use, swap in your own LibreTranslate instance, or replace `call` logic in `backend/main.py` with **Google Cloud Translation API** or **Microsoft Azure Translator** (both need an API key + billing account).
- **Text-to-Speech** uses the browser's built-in Web Speech API — completely free, no setup, but voice availability/quality depends on the user's OS/browser.
- **CORS** is open (`allow_origins=["*"]`) for easy local testing — tighten this before deploying publicly.
- If you swap to Google/Azure, you'd add your API key as an environment variable in `backend/main.py` (never hardcode it or expose it to the frontend).

## Deploying Live (so people can use it without running any code)

To put this on your CV/GitHub as something recruiters can actually click and try, deploy the backend and frontend as two separate free services.

### Step 1 — Push to GitHub
```bash
cd translator
git init
git add .
git commit -m "Initial commit: language translation tool"
git branch -M main
git remote add origin https://github.com/<your-username>/translation-tool.git
git push -u origin main
```

### Step 2 — Deploy the backend (Render.com, free tier)
1. Go to [render.com](https://render.com) → sign up with GitHub
2. **New → Web Service** → connect your `translation-tool` repo
3. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy. Render gives you a live URL like `https://translation-tool-abcd.onrender.com`
5. Visit that URL — you should see `{"status":"ok",...}`

*(Note: Render's free tier "sleeps" after inactivity — the first request after idle takes ~30-50s to wake up. That's normal for free hosting, not a bug.)*

### Step 3 — Point the frontend at the live backend
Edit `frontend/config.js`:
```js
window.APP_CONFIG = {
  API_BASE: "https://translation-tool-abcd.onrender.com",  // your Render URL
};
```
Commit and push this change.

### Step 4 — Deploy the frontend (GitHub Pages, free)
1. On GitHub → your repo → **Settings → Pages**
2. Source: **Deploy from a branch** → Branch: `main`, folder: `/frontend` (or move `frontend/*` into a `docs/` folder and select that — GitHub Pages needs root or `/docs`)
3. Save. GitHub gives you a live URL like `https://<your-username>.github.io/translation-tool/`

Now that URL is what goes on your CV/LinkedIn/GitHub README — anyone can open it and use the tool with zero setup.

**Alternative to GitHub Pages**: [Vercel](https://vercel.com) or [Netlify](https://netlify.com) — both let you drag-and-drop the `frontend` folder or connect the repo, and deploy in under a minute, with a nicer custom subdomain.

### Step 5 — Lock down CORS (optional but good practice)
Once you know your live frontend URL, tighten `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://<your-username>.github.io"],  # instead of "*"
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Switching to Google Cloud Translation API (optional upgrade)

1. Get an API key from Google Cloud Console (enable "Cloud Translation API")
2. In `backend/main.py`, replace the LibreTranslate call with:
```python
GOOGLE_API_KEY = "YOUR_KEY"  # better: os.environ["GOOGLE_API_KEY"]
url = f"https://translation.googleapis.com/language/translate/v2?key={GOOGLE_API_KEY}"
payload = {"q": text, "source": source, "target": target, "format": "text"}
```
3. Adjust the response parsing to match Google's JSON shape (`data.data.translations[0].translatedText`)
