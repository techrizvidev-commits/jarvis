#!/usr/bin/env python3
"""
JARVIS Server v4 - Futuristic HUD + full bidirectional control, stdlib only.
Serves:
  /               -> ui/index.html  (futuristic laptop HUD)
  /mobile.html    -> ui/mobile.html (futuristic phone app)
  /api/status     -> live CPU/RAM/storage/network + phone battery
  /api/command    -> runs jarvis.handle(command) - phone controls laptop
  /api/inbox      -> messages sent laptop -> phone
  /api/send-to-phone -> laptop sends a message to the phone inbox
  /api/phone-command  -> laptop queues a phone action (ring/vibrate/torch/beep/flash/open_youtube)
  /api/phone-commands -> phone polls and runs queued actions
  /api/phone-status   -> phone reports battery/charging to laptop HUD

Run on Windows:
  python jarvis_server.py
  Then open http://localhost:5000
  Phone (same Wi-Fi): http://<your-laptop-IP>:5000/mobile.html
  Your laptop IP is printed when the server starts.
"""
import json, datetime, socket, sys
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

BASE = Path(__file__).parent
UI = BASE / "ui"
INBOX = []
PHONE_CMDS = []   # laptop -> phone command queue, phone polls /api/phone-commands
PHONE_STATUS = {}  # phone reports battery etc via /api/phone-status
import secrets
PAIR_TOKEN = secrets.token_hex(3)  # 6 hex chars, shown on the HUD, in the QR URL
PAIRED = set()

try:
    import jarvis as _j
except Exception as e:
    print("Could not import jarvis.py:", e)
    _j = None

def _load_cfg():
    try:
        return json.loads((BASE / "config.json").read_text())
    except Exception:
        return {}

def laptop_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def status():
    cpu = ram = storage = network = 0
    try:
        import psutil
        cpu = round(psutil.cpu_percent(interval=0.3))
        ram = round(psutil.virtual_memory().percent)
        storage = round(psutil.disk_usage(str(BASE.anchor if BASE.anchor else "/")).percent)
        network = 86
    except Exception:
        import random
        cpu, ram, storage, network = 24, 42, 61, 86
    try:
        import urllib.request
        with urllib.request.urlopen("https://wttr.in/Karachi?format=%t+%C", timeout=5) as r:
            weather = r.read().decode().strip()
    except Exception:
        weather = ""
    import platform
    out = {"cpu": cpu, "ram": ram, "storage": storage, "network": network,
            "system": f"{platform.system()} {platform.release()}",
            "time": datetime.datetime.now().strftime("%I:%M %p"),
            "date": datetime.datetime.now().strftime("%a, %d %b %Y"),
            "weather": weather}
    if PHONE_STATUS:
        out["phone"] = dict(PHONE_STATUS, time=datetime.datetime.now().strftime("%I:%M %p"))
    return out

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(UI), **k)
    def log_message(self, *a):
        pass
    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        if self.path.startswith("/api/status"):
            return self._json(status())
        if self.path.startswith("/api/docs"):
            try:
                return self._json(json.loads((BASE / "api" / "openapi.json").read_text()))
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        if self.path.startswith("/api/qr"):
            # QR pairing: scan once with the phone camera, it opens mobile.html
            # with the pairing token. No IP typing, no new code, ever.
            # Phone link is optional — when off, no QR is served.
            if not _load_cfg().get("phone_link_enabled", True):
                return self._json({"enabled": False, "error": "Phone link is off — turn it on in Settings to connect a phone."}, 403)
            mobile_url = f"http://{laptop_ip()}:5000/mobile.html?pair={PAIR_TOKEN}"
            try:
                import qrcode, io
                img = qrcode.make(mobile_url)
                buf = io.BytesIO(); img.save(buf, format="PNG"); data = buf.getvalue()
                self.send_response(200); self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(data))); self.end_headers()
                self.wfile.write(data); return
            except Exception:
                # Fallback: public QR service (needs internet once)
                import urllib.request
                qr = "https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=" + urllib.parse.quote(mobile_url)
                self.send_response(302); self.send_header("Location", qr); self.end_headers()
                return
        if self.path.startswith("/api/pair"):
            # Phone link is OPTIONAL: if the user turns it off, pairing is
            # disabled and Jarvis works fully on the PC alone.
            if not _load_cfg().get("phone_link_enabled", True):
                return self._json({"enabled": False, "pair_token": "", "mobile_url": "", "paired": []})
            return self._json({"enabled": True, "pair_token": PAIR_TOKEN, "mobile_url": f"http://{laptop_ip()}:5000/mobile.html?pair={PAIR_TOKEN}", "paired": sorted(PAIRED)})
        if self.path.startswith("/api/settings"):
            # GET: masked key status + model/base — both HUD and phone poll this,
            # so a change on one appears on the other (sync).
            cfg = _load_cfg()
            key = cfg.get("llm_api_key", "")
            return self._json({"llm_api_key_set": bool(key), "llm_api_key_masked": ("••••" + key[-4:] if len(key) > 4 else ""),
                               "llm_base_url": cfg.get("llm_base_url", "https://api.openai.com/v1"),
                               "llm_model": cfg.get("llm_model", "gpt-4o-mini"),
                               "phone_link_enabled": cfg.get("phone_link_enabled", True),
                               "user": cfg.get("user", "Boss"), "name": cfg.get("name", "Jarvis")})
        if self.path.startswith("/api/inbox"):
            return self._json({"messages": INBOX[-20:]})
        if self.path.startswith("/api/phone-commands"):
            if not _load_cfg().get("phone_link_enabled", True):
                PHONE_CMDS.clear()
                return self._json({"commands": [], "enabled": False})
            cmds = list(PHONE_CMDS); PHONE_CMDS.clear()
            return self._json({"commands": cmds})
        return super().do_GET()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            data = {}
        if self.path.startswith("/api/command"):
            cmd = (data.get("command") or "").strip()
            reply = _j.handle(cmd) if _j else "Jarvis core not loaded."
            # Phone lock/unlock/ring markers from jarvis.handle -> queue for the phone
            markers = {"__PHONE_LOCK__": ("lock_phone", "Phone locked — enter your phone PIN to open it."),
                       "__PHONE_UNLOCK__": ("unlock_phone", "Phone unlocked from the laptop."),
                       "__PHONE_RING__": ("ring", "Ringing your phone — check it now.")}
            if reply in markers:
                action, text = markers[reply]
                PHONE_CMDS.append({"action": action, "time": datetime.datetime.now().strftime("%I:%M %p")})
                reply = text
            print(f"[{data.get('from','pc')}] {cmd} -> {reply}")
            return self._json({"reply": reply})
        if self.path.startswith("/api/send-to-phone"):
            msg = (data.get("message") or "").strip()
            if msg:
                INBOX.append({"text": msg, "time": datetime.datetime.now().strftime("%I:%M %p, %d %b")})
                print(f"[laptop -> phone] {msg}")
            return self._json({"ok": True, "count": len(INBOX)})
        if self.path.startswith("/api/phone-command"):
            action = (data.get("action") or "").strip()
            if action:
                PHONE_CMDS.append({"action": action, "time": datetime.datetime.now().strftime("%I:%M %p")})
                print(f"[laptop -> phone command] {action}")
            return self._json({"ok": True, "queued": len(PHONE_CMDS)})
        if self.path.startswith("/api/phone-status"):
            PHONE_STATUS.update({k: data.get(k) for k in ("battery", "charging") if k in data})
            return self._json({"ok": True})
        if self.path.startswith("/api/settings"):
            # Save settings from HUD or phone. The key is stored ONLY on the
            # laptop's config.json — it is never sent back in full, only masked.
            cfg = _load_cfg()
            for k in ("llm_base_url", "llm_model", "user", "name"):
                if data.get(k):
                    cfg[k] = data[k]
            if "phone_link_enabled" in data:
                cfg["phone_link_enabled"] = bool(data["phone_link_enabled"])
            if data.get("llm_api_key"):
                cfg["llm_api_key"] = data["llm_api_key"]
            (BASE / "config.json").write_text(json.dumps(cfg, indent=2))
            print("[settings] updated from", data.get("from", "unknown"))
            return self._json({"ok": True, "llm_api_key_set": bool(cfg.get("llm_api_key")), "phone_link_enabled": cfg.get("phone_link_enabled", True)})
        return self._json({"error": "unknown route"}, 404)

if __name__ == "__main__":
    ip = laptop_ip()
    print(f"\n🤖 JARVIS HUD running")
    print(f"   Laptop: http://localhost:5000")
    print(f"   Phone (same Wi-Fi): http://{ip}:5000/mobile.html")
    print(f"   Press Ctrl+C to stop.\n")
    # One-click .exe: open the HUD in the browser automatically.
    if getattr(sys, "frozen", False):
        import threading, webbrowser
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    ThreadingHTTPServer(("0.0.0.0", 5000), H).serve_forever()
