// Reads from config.js - change ONE line there when you deploy the backend,
// instead of editing this file.
const API_BASE = window.APP_CONFIG.API_BASE;

const sourceLangEl = document.getElementById("sourceLang");
const targetLangEl = document.getElementById("targetLang");
const sourceTextEl = document.getElementById("sourceText");
const targetTextEl = document.getElementById("targetText");
const sourceCountEl = document.getElementById("sourceCount");
const statusMsgEl = document.getElementById("statusMsg");
const translateBtn = document.getElementById("translateBtn");
const swapBtn = document.getElementById("swapBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const copyLabel = document.getElementById("copyLabel");
const speakBtn = document.getElementById("speakBtn");

let currentTranslation = "";
let currentTargetLangCode = "en";

// Fallback language list, used if the backend/languages call fails
const FALLBACK_LANGS = [
  { code: "en", name: "English" }, { code: "bn", name: "Bengali" },
  { code: "es", name: "Spanish" }, { code: "fr", name: "French" },
  { code: "de", name: "German" }, { code: "hi", name: "Hindi" },
  { code: "ar", name: "Arabic" }, { code: "zh", name: "Chinese" },
  { code: "ja", name: "Japanese" }, { code: "ru", name: "Russian" },
  { code: "ur", name: "Urdu" }, { code: "pt", name: "Portuguese" },
];

async function loadLanguages() {
  let langs = FALLBACK_LANGS;
  try {
    const res = await fetch(`${API_BASE}/languages`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length) langs = data;
    }
  } catch (e) {
    // backend not reachable yet — fallback list is used
  }

  sourceLangEl.innerHTML = `<option value="auto">Auto-detect</option>` +
    langs.map(l => `<option value="${l.code}">${l.name}</option>`).join("");

  targetLangEl.innerHTML = langs.map(l => `<option value="${l.code}">${l.name}</option>`).join("");
  targetLangEl.value = langs.find(l => l.code === "bn") ? "bn" : (langs[1]?.code || "en");
  currentTargetLangCode = targetLangEl.value;
}

function setStatus(msg, type) {
  statusMsgEl.textContent = msg || "";
  statusMsgEl.className = "status-msg" + (type ? ` ${type}` : "");
}

sourceTextEl.addEventListener("input", () => {
  sourceCountEl.textContent = `${sourceTextEl.value.length} / 4000`;
});

clearBtn.addEventListener("click", () => {
  sourceTextEl.value = "";
  sourceCountEl.textContent = "0 / 4000";
  sourceTextEl.focus();
});

swapBtn.addEventListener("click", () => {
  if (sourceLangEl.value === "auto") return; // can't swap when auto-detect is active
  swapBtn.classList.add("spin");
  setTimeout(() => swapBtn.classList.remove("spin"), 250);

  const srcVal = sourceLangEl.value;
  const tgtVal = targetLangEl.value;
  sourceLangEl.value = tgtVal;
  targetLangEl.value = srcVal;

  if (currentTranslation) {
    sourceTextEl.value = currentTranslation;
    sourceCountEl.textContent = `${sourceTextEl.value.length} / 4000`;
  }
});

async function translate() {
  const text = sourceTextEl.value.trim();
  if (!text) {
    setStatus("Enter some text first", "error");
    return;
  }

  translateBtn.disabled = true;
  translateBtn.textContent = "Translating…";
  setStatus("");

  try {
    const res = await fetch(`${API_BASE}/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source: sourceLangEl.value,
        target: targetLangEl.value,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Translation failed");
    }

    const data = await res.json();
    currentTranslation = data.translated_text;
    currentTargetLangCode = targetLangEl.value;
    targetTextEl.textContent = currentTranslation;

    if (sourceLangEl.value === "auto" && data.detected_language) {
      setStatus(`Detected: ${data.detected_language}`, "detected");
    } else {
      setStatus("");
    }
  } catch (e) {
    setStatus(e.message || "Something went wrong", "error");
  } finally {
    translateBtn.disabled = false;
    translateBtn.textContent = "Translate";
  }
}

translateBtn.addEventListener("click", translate);
sourceTextEl.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") translate();
});

// Copy button
copyBtn.addEventListener("click", async () => {
  if (!currentTranslation) return;
  try {
    await navigator.clipboard.writeText(currentTranslation);
    copyLabel.textContent = "Copied";
    copyBtn.classList.add("copied");
    setTimeout(() => {
      copyLabel.textContent = "Copy";
      copyBtn.classList.remove("copied");
    }, 1500);
  } catch (e) {
    setStatus("Could not copy — copy manually", "error");
  }
});

// Text-to-speech (Web Speech API — built into the browser, no API key needed)
speakBtn.addEventListener("click", () => {
  if (!currentTranslation) return;
  if (!("speechSynthesis" in window)) {
    setStatus("Text-to-speech not supported in this browser", "error");
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(currentTranslation);
  utterance.lang = currentTargetLangCode;
  window.speechSynthesis.speak(utterance);
});

loadLanguages();
