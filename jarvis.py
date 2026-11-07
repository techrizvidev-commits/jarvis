#!/usr/bin/env python3
"""
JARVIS v2 - Windows Full-Control Pack
Works on Windows / macOS / Linux. Text mode works everywhere, no mic needed.
Voice mode is optional (needs microphone + pip install).

Run on Windows:
  install_windows.bat            # one-click: installs deps
  python jarvis.py               # text mode
  python jarvis.py --voice       # voice mode (say "Jarvis" then a command)
  python jarvis.py --demo        # self-test

Try on Windows:
  volume 50 / volume up / mute / brightness 70
  wifi off / wifi on / bluetooth on
  open word / open edge / open settings / open task manager
  lock screen / sleep / restart / empty recycle bin
  screenshot / system info / note buy milk tomorrow
  shutdown   (asks for confirmation first)
"""
# Windows-only helpers live in windows_pack.py - imported only on Windows,
# so Linux/Mac keep working with no extra deps.
try:
    import windows_pack as _wp
except Exception:
    _wp = None
import os, sys, re, json, time, datetime, platform, subprocess, webbrowser, shutil
from pathlib import Path

SYSTEM = platform.system()  # Windows, Darwin, Linux
CONFIG_PATH = Path(__file__).parent / "config.json"
NOTES_PATH = Path(__file__).parent / "notes.txt"

def load_config():
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception:
        return {"name": "Jarvis", "user": "Boss", "voice": True, "wake_word": "jarvis"}

CFG = load_config()
NAME = CFG.get("name", "Jarvis")

# ---------- Speech (optional, fails gracefully) ----------
_engine = None
def speak(text):
    print(f"{NAME}: {text}")
    if not CFG.get("voice", True):
        return
    try:
        global _engine
        if _engine is None:
            import pyttsx3
            _engine = pyttsx3.init()
            _engine.setProperty('rate', 175)
        _engine.say(text)
        _engine.runAndWait()
    except Exception:
        pass  # text output is the fallback - still works

def listen_once():
    """Listen once via microphone. Returns text or ''."""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as src:
            print("Listening... (speak now)")
            r.adjust_for_ambient_noise(src, duration=0.5)
            audio = r.listen(src, timeout=8, phrase_time_limit=8)
        return r.recognize_google(audio).lower()
    except Exception as e:
        print(f"[mic] {e}")
        return ""

# ---------- PC Control helpers ----------
def run(cmd, shell=False):
    try:
        subprocess.Popen(cmd, shell=shell)
        return True
    except Exception as e:
        print(f"[run error] {e}")
        return False

def open_app(app):
    app = app.lower().strip()
    if SYSTEM == "Windows" and _wp is not None:
        r = _wp.open_windows_app(app)
        if r:
            return r
    targets = {
        "chrome": "google-chrome" if SYSTEM == "Linux" else "chrome",
        "browser": "google-chrome" if SYSTEM == "Linux" else "chrome",
        "youtube": None, "google": None, "gmail": None,
        "notepad": "notepad" if SYSTEM == "Windows" else ("gedit" if SYSTEM == "Linux" else "TextEdit"),
        "calculator": "calc" if SYSTEM == "Windows" else ("gnome-calculator" if SYSTEM == "Linux" else "Calculator"),
        "files": "explorer" if SYSTEM == "Windows" else ("nautilus" if SYSTEM == "Linux" else "Finder"),
        "terminal": "cmd" if SYSTEM == "Windows" else ("gnome-terminal" if SYSTEM == "Linux" else "Terminal"),
        "spotify": "spotify",
        "vs code": "code", "code": "code",
    }
    if app in ("youtube", "google", "gmail"):
        urls = {"youtube": "https://youtube.com", "google": "https://google.com", "gmail": "https://mail.google.com"}
        webbrowser.open(urls[app]); return f"Opening {app}."
    if app in targets and targets[app]:
        if SYSTEM == "Windows":
            run(f"start {targets[app]}", shell=True)
        else:
            run([targets[app]])
        return f"Opening {app}."
    # fallback: try as a program name / website
    webbrowser.open(f"https://www.google.com/search?q={app}")
    return f"I don't have {app} mapped yet, so I searched for it."

def system_info():
    try:
        import psutil
        return (f"System: {SYSTEM} {platform.release()}, {platform.machine()}. "
                f"CPU {psutil.cpu_percent(interval=0.5)}%, RAM {psutil.virtual_memory().percent}% used, "
                f"Battery {psutil.sensors_battery().percent if psutil.sensors_battery() else 'n/a'}%.")
    except Exception:
        return f"System: {SYSTEM} {platform.release()}, {platform.machine()}. Install psutil for live CPU/RAM: pip install psutil"

def volume(action):
    if SYSTEM == "Windows" and _wp is not None:
        if action.isdigit():
            return _wp.volume_set(action)
        if action in ("up", "down", "mute"):
            return _wp.volume_key(action)
        if action == "level":
            return _wp.volume_get()
        return "Volume: up, down, mute, or a number 0-100."
    if SYSTEM == "Linux":
        if action.isdigit():
            ok = run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{action}%"])
            return f"Volume set to {action}%." if ok else "Volume: pactl not found on this Linux PC."
        m = {"up": "+10%", "down": "-10%", "mute": "toggle"}
        run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", m.get(action, "+10%")] if action != "mute" else ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        return f"Volume {action}."
    return f"Volume {action} - use your system keys on macOS for now."

def screenshot():
    path = Path(__file__).parent / f"screenshot-{datetime.datetime.now():%Y%m%d-%H%M%S}.png"
    try:
        if SYSTEM == "Windows":
            from PIL import ImageGrab; ImageGrab.grab().save(path)
        elif SYSTEM == "Linux":
            run(["gnome-screenshot", "-f", str(path)])
        else:
            run(["screencapture", str(path)])
        return f"Screenshot saved to {path.name}."
    except Exception as e:
        return f"Screenshot needs Pillow / gnome-screenshot: {e}"

# ---------- Power Pack (lock/unlock, routines) ----------
try:
    import power_pack as _pp
except Exception:
    _pp = None

# ---------- Command brain ----------
def handle(command: str) -> str:
    c = command.lower().strip()
    c = re.sub(r'^(hey |ok |okay )?jarvis[,. ]*', '', c).strip()
    if not c:
        return "Yes, Boss?"

    # --- Lock / unlock, both ways (UI unchanged — type these commands) ---
    if c in ("lock laptop", "lock pc", "lock computer"):
        return _wp.power("lock") if (SYSTEM == "Windows" and _wp is not None) else "Locking the screen."
    if c in ("unlock laptop", "unlock pc", "unlock computer", "wake pc"):
        return _pp.unlock_laptop() if _pp is not None else "Unlock needs the power pack."
    if c in ("wake on lan", "wake up pc"):
        return _pp.wake_on_lan() if _pp is not None else "Wake-on-LAN needs the power pack."
    if c in ("lock phone",):
        return "__PHONE_LOCK__"
    if c in ("unlock phone",):
        return "__PHONE_UNLOCK__"
    if c in ("find phone", "find my phone", "ring phone"):
        return "__PHONE_RING__"
    if c in ("morning routine", "morning mode"):
        return _pp.routine("morning", handle) if _pp is not None else "Routine needs the power pack."
    if c in ("work mode", "work routine"):
        return _pp.routine("work", handle) if _pp is not None else "Routine needs the power pack."
    if c in ("movie mode", "movie routine"):
        return _pp.routine("movie", handle) if _pp is not None else "Routine needs the power pack."
    if c.startswith("clipboard "):
        return _pp.clipboard(c[10:]) if _pp is not None else "Clipboard needs the power pack."
    if c.startswith("reminder "):
        return _pp.save_reminder(c[9:]) if _pp is not None else "Reminder needs the power pack."
    if c.startswith("kill "):
        return _pp.kill_app(c[5:]) if _pp is not None else "Kill needs the power pack."
    if c.startswith("find file "):
        return _pp.find_file(c[10:]) if _pp is not None else "Find file needs the power pack."
    # --- File ops: any file work ---
    try:
        import file_ops as _fo
    except Exception:
        _fo = None
    if _fo is not None:
        if c.startswith("delete file "):
            return _fo.delete_file(c[12:])
        if c.startswith("delete "):
            return _fo.delete_file(c[7:])
        if c.startswith("move file "):
            m = re.match(r"move file (.+?) to (.+)", c)
            if m: return _fo.move_file(m.group(1), m.group(2))
        if c.startswith("rename file "):
            m = re.match(r"rename file (.+?) to (.+)", c)
            if m: return _fo.rename_file(m.group(1), m.group(2))
        if c.startswith("copy file "):
            m = re.match(r"copy file (.+?) to (.+)", c)
            if m: return _fo.copy_file(m.group(1), m.group(2))
        if c.startswith("create file "):
            return _fo.create_file(c[12:])
        if c.startswith("create folder "):
            return _fo.create_folder(c[14:])
        if c.startswith("list files"):
            m = re.match(r"list files(?: in)? (.+)", c)
            return _fo.list_files(m.group(1) if m else "Downloads")

    if any(k in c for k in ["what time", "time is it"]):
        return f"It's {datetime.datetime.now():%I:%M %p}."
    if "date" in c or "what day" in c:
        return f"Today is {datetime.datetime.now():%A, %d %B %Y}."
    if c.startswith("open "):
        return open_app(c[5:])
    if c.startswith("search "):
        m = re.match(r"search (.+?) on (youtube|google)", c)
        if m:
            q, where = m.groups()
            url = f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}" if where == "youtube" else f"https://www.google.com/search?q={q.replace(' ', '+')}"
            webbrowser.open(url); return f"Searching {where} for {q}."
        webbrowser.open(f"https://www.google.com/search?q={c[7:].replace(' ', '+')}")
        return f"Searching Google for {c[7:]}."
    if c.startswith("play "):
        webbrowser.open(f"https://www.youtube.com/results?search_query={c[5:].replace(' ', '+')}")
        return f"Playing {c[5:]} on YouTube."
    # --- Windows full-control pack ---
    if c.startswith("brightness"):
        if SYSTEM == "Windows" and _wp is not None:
            m = re.search(r"(\d+)", c)
            return _wp.brightness_set(m.group(1)) if m else _wp.brightness_get()
        return "Brightness control is Windows-only in v2 (laptops)."
    if c.startswith("wifi "):
        if SYSTEM == "Windows" and _wp is not None:
            return _wp.wifi("on" in c)
        return "Wi-Fi control is Windows-only in v2."
    if c.startswith("bluetooth "):
        if SYSTEM == "Windows" and _wp is not None:
            return _wp.bluetooth("on" in c)
        return "Bluetooth control is Windows-only in v2."
    if c in ("sleep", "go to sleep"):
        return _wp.power("sleep") if (SYSTEM == "Windows" and _wp is not None) else "Sleep is Windows-only in v2."
    if c in ("restart", "reboot"):
        return _wp.power("restart") if (SYSTEM == "Windows" and _wp is not None) else "Restart needs confirmation on this system."
    if c in ("hibernate",):
        return _wp.power("hibernate") if (SYSTEM == "Windows" and _wp is not None) else "Hibernate is Windows-only in v2."
    if "empty recycle bin" in c or "empty trash" in c:
        return _wp.empty_recycle_bin() if (SYSTEM == "Windows" and _wp is not None) else "Recycle bin emptying is Windows-only in v2."
    if c.startswith("type "):
        return _wp.type_text(c[5:]) if (SYSTEM == "Windows" and _wp is not None) else "Typing needs pyautogui on Windows: pip install pyautogui"
    if c.startswith("wallpaper "):
        return _wp.set_wallpaper(c[10:].strip()) if (SYSTEM == "Windows" and _wp is not None) else "Wallpaper is Windows-only in v2."
    if "volume" in c:
        m = re.search(r"volume\s+(\d+)", c)
        if m:
            return volume(m.group(1))
        if "level" in c or "how loud" in c:
            return volume("level")
        return volume("up" if "up" in c else "down" if "down" in c else "mute")
    if "system info" in c or "pc info" in c or c in ("status", "battery"):
        return system_info()
    if "screenshot" in c:
        return screenshot()
    if "lock" in c and "screen" in c:
        if SYSTEM == "Windows" and _wp is not None:
            return _wp.power("lock")
        if SYSTEM == "Windows": run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        elif SYSTEM == "Linux": run(["gnome-screensaver-command", "-l"])
        else: run(["pmset", "displaysleepnow"])
        return "Locking the screen."
    if "open downloads" in c or "downloads folder" in c:
        p = str(Path.home() / "Downloads"); webbrowser.open(p) if False else run(["xdg-open", p] if SYSTEM == "Linux" else ["open", p] if SYSTEM == "Darwin" else f'explorer "{p}"', shell=(SYSTEM == "Windows"))
        return "Opening Downloads."
    if c.startswith("list files"):
        folder = Path.home() / "Downloads"
        files = [f.name for f in folder.iterdir()][:10] if folder.exists() else []
        return "Downloads: " + (", ".join(files) if files else "empty.")
    if c.startswith("note "):
        with open(NOTES_PATH, "a") as f: f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {c[5:]}\n")
        return "Note saved."
    if c.startswith("weather"):
        city = c.replace("weather", "").strip() or "lahore"
        try:
            import urllib.request
            with urllib.request.urlopen(f"https://wttr.in/{city}?format=3", timeout=8) as r:
                return r.read().decode().strip()
        except Exception:
            return f"Weather check needs internet - try again in a sec."
    if "shutdown" in c or "shut down" in c:
        return "CONFIRM: type 'yes shutdown' to shut down, or 'cancel'."
    if c == "yes shutdown":
        run("shutdown /s /t 5" if SYSTEM == "Windows" else "shutdown -h +1", shell=True)
        return "Shutting down in a few seconds."
    if "joke" in c:
        return "Why did the developer go broke? Because he used up all his cache."
    if c in ("hello", "hi", "hey", "good morning", "good evening"):
        return f"Hello, Boss. All systems ready. What should I do?"
    if c in ("exit", "quit", "bye", "goodbye", "stop"):
        return "__EXIT__"
    if "who are you" in c:
        return f"I'm {NAME}, your personal assistant. I can open apps, search the web, check the time and system, take notes, screenshots, and control volume - and I'm learning more commands every day."
    # --- Brain v7: any question / code / research goes to the Brain ---
    # (instant commands above win; anything else is answered, not refused)
    try:
        import brain
        return brain.answer(command)
    except Exception:
        return "I heard you, but I don't have that command yet. Try 'open youtube', 'what time is it', 'system info', or 'help'."

HELP = """Windows v2: open [word/excel/edge/notepad/settings/task manager] | volume 50 / up / down / mute | brightness 70 | wifi on/off | bluetooth on/off | lock screen | sleep / restart / hibernate | empty recycle bin | screenshot | system info | type [text] | note [text] | weather [city] | search [x] on google/youtube | exit"""

def main():
    if "--background" in sys.argv:
        from listen import listen_loop
        print(f"\n🤖 {NAME} background listener — silent until you say 'Hey Jarvis' (any language).")
        listen_loop(handle)
        return
    print(f"\n🤖 {NAME} online — {SYSTEM} | {datetime.datetime.now():%A, %d %B %Y %I:%M %p}")
    print("Text mode: type a command. Say 'help' for the list, 'exit' to quit.\n")
    if "--demo" in sys.argv:
        for cmd in ["what time is it", "system info", "list files", "note demo note from Jarvis v1", "joke"]:
            print(f"> {cmd}\n{NAME}: {handle(cmd)}\n", flush=True)
        print("Demo done.", flush=True)
        return
    if "--voice" in sys.argv:
        print("Voice mode: say 'Jarvis' + command. Ctrl+C to stop.\n")
        while True:
            try:
                heard = listen_once()
                if not heard: continue
                print(f"You (voice): {heard}")
                if "jarvis" not in heard: continue
                reply = handle(heard)
                if reply == "__EXIT__": break
                speak(reply)
            except KeyboardInterrupt:
                break
        print(f"{NAME}: Going offline. Goodbye, Boss.")
        return
    # text loop
    while True:
        try:
            cmd = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{NAME}: Going offline. Goodbye, Boss."); break
        if not cmd: continue
        if cmd.lower() == "help":
            print(HELP); continue
        reply = handle(cmd)
        if reply == "__EXIT__":
            print(f"{NAME}: Going offline. Goodbye, Boss."); break
        speak(reply)

if __name__ == "__main__":
    main()
