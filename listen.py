"""
JARVIS Background Listener v8 — runs in the background, silent until called.
  python listen.py            — start background listening
  python jarvis.py --background — same, via jarvis.py
It only wakes when it hears a wake word / greeting, in ANY language:
  English: hey jarvis, hello jarvis, hi jarvis, jarvis, good morning
  Urdu/Roman Urdu: salam, assalam o alaikum, aoa, salam jarvis, jarvis salam
  Hindi: namaste, namaskar
  Arabic: marhaba, assalamu alaikum, salam
  Spanish: hola, hola jarvis
  French: bonjour, salut
  German: hallo, guten tag
  Turkish: merhaba, selam
  Portuguese: ola, bom dia
After waking it listens for ONE command, runs it, replies, and goes back
to silent background listening. It never answers unprompted speech.
Needs: microphone + SpeechRecognition + PyAudio (Windows: pip install).
"""
import re

WAKE_WORDS = [
    "hey jarvis", "hello jarvis", "hi jarvis", "jarvis", "good morning",
    "good evening", "good afternoon", "hey", "hello", "hi",
    "salam", "assalam o alaikum", "assalamu alaikum", "aoa", "salam jarvis",
    "namaste", "namaskar", "namaste jarvis",
    "marhaba", "salam alaikum",
    "hola", "hola jarvis", "buenos dias",
    "bonjour", "salut", "bonjour jarvis",
    "hallo", "guten tag", "guten morgen",
    "merhaba", "selam", "selam jarvis",
    "ola", "bom dia", "oi",
    "ciao", "buongiorno",
    "konnichiwa", "annyeong",
]

def is_wake(text):
    t = (text or "").lower().strip()
    return any(w in t for w in WAKE_WORDS)

def extract_command(text):
    """After 'hey jarvis, open youtube' -> 'open youtube'."""
    t = (text or "").strip()
    t = re.sub(r"(?i)^(hey|hello|hi|ok|okay)\s+jarvis[,. ]*", "", t).strip()
    t = re.sub(r"(?i)^jarvis[,. ]*", "", t).strip()
    return t

def listen_loop(handle):
    try:
        import speech_recognition as sr
    except ImportError:
        print("Voice needs: pip install SpeechRecognition PyAudio")
        return
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as src:
        r.adjust_for_ambient_noise(src, duration=1)
    print("JARVIS background listener running. Say 'Hey Jarvis' (any language) to wake.")
    while True:
        try:
            with mic as src:
                audio = r.listen(src, timeout=None, phrase_time_limit=5)
            try:
                heard = r.recognize_google(audio, language="ur-PK")
            except Exception:
                heard = r.recognize_google(audio)
            if not is_wake(heard):
                continue
            print(f"[wake] {heard}")
            with mic as src:
                audio = r.listen(src, timeout=8, phrase_time_limit=10)
            try:
                cmd = r.recognize_google(audio, language="ur-PK")
            except Exception:
                cmd = r.recognize_google(audio)
            cmd = extract_command(cmd)
            if cmd:
                print(f"[command] {cmd}")
                print("JARVIS:", handle(cmd))
        except KeyboardInterrupt:
            print("Listener stopped.")
            return
        except Exception:
            continue

if __name__ == "__main__":
    from jarvis import handle
    listen_loop(handle)
