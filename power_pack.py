"""
JARVIS Power Pack v6 — lock/unlock + powerful routines.
UI is NOT changed. These are backend commands, used by typing them
in the HUD / mobile app, or via the API.

LOCK / UNLOCK — honest limits, read this first:
- LOCK laptop from phone: instant, always works.
- UNLOCK laptop from phone: Windows will NOT let any app bypass its
  lock screen without your sign-in. Jarvis does the safe version:
  1) wakes the display, 2) if you set Windows to "Require sign-in: Never"
     on wake, it unlocks, 3) otherwise it types YOUR unlock PIN —
     but only if you set it yourself in config.json on your PC
     ("unlock_pin": "1234"). Never send your Windows password in chat.
     No PIN set = Jarvis tells you exactly what to set, it does NOT
     guess or bypass anything.
- LOCK phone from laptop: in the web app this is a full-screen lock
  overlay (PIN to open). Real system lock needs the native APK with
  Device Admin permission — that is the APK step after Git.
- UNLOCK phone from laptop: dismisses that overlay (laptop sends
  "unlock phone"), or the phone PIN opens it.

Other power commands in this pack:
  wake pc / wake on lan   — Wake-on-LAN magic packet (needs MAC in config)
  find phone              — ring + vibrate + flash on the phone
  morning routine         — time + weather + open Chrome + volume 50
  work mode / movie mode  — brightness + volume + apps for that mode
  clipboard <text>        — copy text to the PC clipboard (Windows)
  reminder <text>         — save a reminder with time, shown in /api/status
  kill <app>              — close an app by name (Windows taskkill)
  find file <name>        — search Downloads/Documents for a file
"""
import json, re, socket, subprocess, datetime
from pathlib import Path

BASE = Path(__file__).parent
CFG_PATH = BASE / "config.json"

def _cfg():
    try:
        return json.loads(CFG_PATH.read_text())
    except Exception:
        return {}

def wake_on_lan(mac=None):
    mac = mac or _cfg().get("wake_mac", "")
    if not mac:
        return ("Wake-on-LAN needs your PC MAC address. On your PC run "
                "'getmac' in Command Prompt, then put it in config.json as "
                '"wake_mac": "AA-BB-CC-DD-EE-FF".')
    mac = re.sub(r"[^0-9a-fA-F]", "", mac)
    if len(mac) != 12:
        return "Wake-on-LAN: MAC address looks wrong, check config.json."
    pkt = bytes.fromhex("FF" * 6 + mac * 16)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(pkt, ("255.255.255.255", 9)); s.close()
        return "Wake-on-LAN packet sent. If Wake-on-LAN is on in BIOS + Windows, your PC will wake."
    except Exception as e:
        return f"Wake-on-LAN failed: {e}"

def unlock_laptop():
    """Wake display, then type the user's own unlock PIN if they set it."""
    import platform
    if platform.system() == "Windows":
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                "(Add-Type -MemberDefinition '[DllImport(\"user32.dll\")] public static extern void mouse_event(int a,int b,int c,int d,int e);' -Name W -Namespace X)::mouse_event(0x0001,1,1,0,0)"],
                capture_output=True, timeout=10)
        except Exception:
            pass
    pin = _cfg().get("unlock_pin", "")
    if not pin:
        return ("Unlock: display woken. To unlock from your phone, set it up once on your PC: "
                "1) Settings > Accounts > Sign-in options > Require sign-in: Never, OR "
                "2) put your Windows PIN in config.json as \"unlock_pin\": \"1234\" "
                "(only on your PC, never in chat). Then 'unlock laptop' will type it.")
    try:
        import pyautogui, time
        time.sleep(1.0)
        pyautogui.typewrite(str(pin), interval=0.08)
        pyautogui.press("enter")
        return "Unlock: PIN entered on the lock screen."
    except ImportError:
        return "Unlock: PIN is set, but pyautogui is missing — run: pip install pyautogui"
    except Exception as e:
        return f"Unlock failed: {e}"

def clipboard(text):
    try:
        import subprocess
        subprocess.run(["clip", "/b"], input=text.encode(), capture_output=True, timeout=5)
        return "Copied to clipboard."
    except Exception:
        try:
            import pyperclip; pyperclip.copy(text); return "Copied to clipboard."
        except Exception as e:
            return f"Clipboard failed: {e}"

def kill_app(name):
    import platform
    if platform.system() == "Windows":
        r = subprocess.run(f'taskkill /IM "{name}.exe" /F', shell=True, capture_output=True, text=True, timeout=10)
        return f"Closed {name}." if r.returncode == 0 else f"Could not close {name} — is it running?"
    return "Kill app is Windows-only in this pack."

def find_file(name):
    home = Path.home()
    hits = []
    for folder in (home / "Downloads", home / "Documents", home / "Desktop"):
        if folder.exists():
            hits += [str(p) for p in folder.rglob(f"*{name}*")][:5]
    return "Found: " + "; ".join(hits) if hits else f"No file named '{name}' in Downloads / Documents / Desktop."

def save_reminder(text):
    p = BASE / "reminders.txt"
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} - {text}\n"
    p.write_text(p.read_text() + line if p.exists() else line)
    return f"Reminder saved: {text}"

def routine(name, jarvis_handle):
    if name == "morning":
        return (jarvis_handle("what time is it") + " " + jarvis_handle("weather karachi") + " "
                + jarvis_handle("open chrome") + " " + jarvis_handle("volume 50"))
    if name == "work":
        return jarvis_handle("brightness 70") + " " + jarvis_handle("volume 30") + " " + jarvis_handle("open word")
    if name == "movie":
        return jarvis_handle("brightness 30") + " " + jarvis_handle("volume 80") + " " + jarvis_handle("open youtube")
    return "Routines: morning, work, movie."
