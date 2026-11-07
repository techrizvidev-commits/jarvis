"""
JARVIS Brain v7 — answer anything, write code, research the web.
How it works, in order:
  1) If the user puts an LLM key in config.json ("llm_api_key"), Brain calls
     that OpenAI-compatible API (OpenAI, Groq, OpenRouter, Ollama, LM Studio)
     — that is the full Iron-Man brain: any question, any code, any task.
  2) Without a key, Brain researches the web for free:
     Wikipedia summary + DuckDuckGo instant answer, no key needed.
  3) Code requests without a key use built-in templates (Python, HTML, JS).

Put your key ONLY in config.json on your own PC, never in chat.
config.json:
  "llm_api_key": "sk-...",
  "llm_base_url": "https://api.openai.com/v1",
  "llm_model": "gpt-4o-mini"
For Groq (free tier): base https://api.groq.com/openai/v1, model llama-3.3-70b-versatile
For local Ollama: base http://localhost:11434/v1, model llama3.1, key "ollama"
"""
import json, urllib.request, urllib.parse, re
from pathlib import Path

CFG_PATH = Path(__file__).parent / "config.json"

def _cfg():
    try:
        return json.loads(CFG_PATH.read_text())
    except Exception:
        return {}

# --- Multilingual: reply in the SAME language as the question ---
# Urdu script, Roman Urdu, Hindi, Arabic, Spanish, French, German, Turkish...
ROMAN_URDU = ("kya", "hai", "mujhe", "batao", "karo", "chahiye", "kaise", "kyun",
              "mera", "tum", "yeh", "woh", "kahan", "kab", "bhi", "nahi", "acha")
def detect_language(q):
    if re.search(r"[\u0600-\u06FF]", q):
        return "ur", "Urdu"
    if re.search(r"[\u0900-\u097F]", q):
        return "hi", "Hindi"
    if re.search(r"[\u0400-\u04FF]", q):
        return "ru", "Russian"
    if re.search(r"[\u3040-\u30FF\u4E00-\u9FFF]", q):
        return "ja", "Japanese"
    low = q.lower()
    if any(w in low.split() for w in ROMAN_URDU):
        return "ur-roman", "Roman Urdu"
    if any(w in low for w in ("hola", "gracias", "buenos", "qué", "que es")):
        return "es", "Spanish"
    if any(w in low for w in ("bonjour", "merci", "salut", "c'est", "quoi")):
        return "fr", "French"
    if any(w in low for w in ("hallo", "guten", "danke")):
        return "de", "German"
    if any(w in low for w in ("merhaba", "selam", "nasilsin")):
        return "tr", "Turkish"
    if any(w in low for w in ("marhaba", "assalamu", "salam")):
        return "ar", "Arabic"
    return "en", "English"

def _llm(question):
    cfg = _cfg()
    key = cfg.get("llm_api_key", "").strip()
    if not key:
        return None
    base = cfg.get("llm_base_url", "https://api.openai.com/v1").rstrip("/")
    model = cfg.get("llm_model", "gpt-4o-mini")
    _, lang_name = detect_language(question)
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": f"You are JARVIS, a helpful personal assistant. Answer clearly and completely. When asked for code, give working code with a short explanation. IMPORTANT: the user asked in {lang_name} — reply in {lang_name}, in the same script and style they used (if Roman Urdu, reply in Roman Urdu)."},
        {"role": "user", "content": question}]}).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Brain (LLM) error: {e}. Check llm_api_key / llm_base_url in config.json."

def _wikipedia(topic, lang="en"):
    topic = topic.strip().title()
    sub = lang if lang in ("ur", "hi", "ar", "es", "fr", "de", "tr", "ru", "ja") else "en"
    url = f"https://{sub}.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(topic)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/7.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            return d.get("extract") or None
    except Exception:
        return None

def _duckduckgo(q):
    url = "https://api.duckduckgo.com/?q=" + urllib.parse.quote(q) + "&format=json&no_html=1"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.loads(r.read())
            return d.get("AbstractText") or None
    except Exception:
        return None

def _code_template(q):
    ql = q.lower()
    if "python" in ql and ("function" in ql or "fibonacci" in ql or "prime" in ql):
        return ("Here is Python code:\n\ndef fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a)\n        a, b = b, a + b\n\nfibonacci(10)\n\nFor any other code, add an LLM key in config.json and I will write it exactly as you ask.")
    if "html" in ql or "website" in ql or "web page" in ql:
        return ("Here is a starter HTML page:\n\n<!DOCTYPE html>\n<html><head><title>My Page</title></head>\n<body><h1>Hello, World</h1></body></html>\n\nFor a full website, add an LLM key in config.json and tell me exactly what the page should do.")
    if "javascript" in ql or " js " in ql:
        return ("Here is JavaScript:\n\nfunction greet(name) {\n  return `Hello, ${name}!`;\n}\nconsole.log(greet('Boss'));\n\nFor more complex code, add an LLM key in config.json.")
    return None

def answer(question):
    # 1) Full LLM brain, if configured
    r = _llm(question)
    if r:
        return r
    # 2) Code templates
    if any(k in question.lower() for k in ("write code", "code for", "write a program", "write python", "write html", "write javascript")):
        t = _code_template(question)
        if t:
            return t
    # 3) Free web research, in the user's language where possible
    lang, lang_name = detect_language(question)
    topic = question.strip(" ?.")
    topic = re.sub(r"(?i)^(what is|who is|tell me about|explain|define|what are|yeh kya|ye kya|kya hai|qu'est-ce que|c'est quoi|qué es|que es)\s+", "", topic).strip()
    topic = re.sub(r"(?i)\s+(kya hai|kya he|kya hota hai|kya hoti hai|hai kya|kya hai\?)$", "", topic).strip()
    topic = re.sub(r"\s+(کیا ہے|کیا|ہے)\s*$", "", topic).strip(" ؟?")
    topic = re.sub(r"(?i)^(la|le|el)\s+", "", topic).strip()
    r = _wikipedia(topic or question, lang)
    if not r and lang != "en":
        r = _wikipedia(topic or question, "en")  # fallback: English article
    if r:
        return r + f"\n\n(Source: web research, {lang_name}. For deeper answers, add an LLM key in Settings — see brain.py.)"
    r = _duckduckgo(topic or question)
    if r:
        return r + "\n\n(Source: web research. For deeper answers, add an LLM key in Settings.)"
    return ("I don't have an answer for that yet offline. Add an LLM key in config.json "
            "(OpenAI / Groq / Ollama — see brain.py) and I will answer any question and write any code. "
            "Or try: 'what is photosynthesis', 'who is Albert Einstein', 'write python code for fibonacci'.")
