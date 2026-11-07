# JARVIS API — English

Base URL (local server): `http://localhost:5000`
Phone on the same Wi-Fi: `http://<laptop-IP>:5000`

Start the server: `python jarvis_server.py` or double-click `start_jarvis.bat`.
The HTML UI uses this API automatically. To point the UI at your own API, set
in the browser console or before the script loads:
```js
window.JARVIS_API = "http://192.168.1.5:5000";
```
Live docs in the browser: `GET /api/docs` (JSON) — same data as `api/openapi.json`.

## Endpoints

### GET /api/status — live system status
```bash
curl http://localhost:5000/api/status
```
Response:
```json
{"cpu": 24, "ram": 42, "storage": 61, "network": 86,
 "system": "Windows 11", "time": "03:54 PM", "date": "Sat, 07 Nov 2026",
 "weather": "+88°F Sunny", "phone": {"battery": 78, "charging": false, "time": "03:54 PM"}}
```
`phone` appears only after the phone reports its battery.

### POST /api/command — run a Jarvis command (phone → laptop, or UI → laptop)
```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "open youtube", "from": "phone"}'
```
Response: `{"reply": "Opening youtube."}`

Command examples: `what time is it`, `system info`, `open youtube`, `open word`,
`search cats on google`, `play lofi music`, `volume 50`, `volume up`, `mute`,
`brightness 70`, `wifi off`, `screenshot`, `lock screen`, `sleep`, `restart`,
`empty recycle bin`, `note buy milk`, `weather karachi`, `joke`.

### Lock / unlock + power commands (v6, UI unchanged)
- `lock laptop` — phone locks the laptop, instantly.
- `unlock laptop` — wakes the display. Full unlock needs one-time setup on your PC:
  either Settings > Accounts > Sign-in options > Require sign-in: Never,
  or put your Windows PIN in `config.json` as `"unlock_pin": "1234"`
  (only on your PC, never in chat). Windows does not allow any app to
  bypass its lock screen without your sign-in.
- `wake on lan` — wakes a sleeping PC. Needs `"wake_mac"` in `config.json`
  (run `getmac` on your PC) and Wake-on-LAN on in BIOS + Windows.
- `lock phone` / `unlock phone` — laptop locks/unlocks the phone.
  Web app: full-screen lock overlay with a PIN you set on first lock.
  Real system lock needs the native APK with Device Admin permission.
- `find phone` / `ring phone` — ring + vibrate + flash on the phone.
- `morning routine` — time + weather + Chrome + volume 50.
- `work mode` — brightness 70, volume 30, Word. `movie mode` — brightness 30, volume 80, YouTube.
- `clipboard <text>`, `reminder <text>`, `kill <app>`, `find file <name>`.

### File ops (v8 — any file work)
- `delete file <name>` — Recycle Bin mein jati hai (wapas la sakte ho). System files refuse karta hai.
- `move file <name> to <folder>`, `rename file <name> to <new name>`, `copy file <name> to <folder>`
- `create file <name>`, `create folder <name>`, `list files in <folder>`

### Background + wake word (v8)
- `start_background.bat` (or `python jarvis.py --background`) — background mein chalta hai,
  khamosh rehta hai jab tak aap na kaho: "Hey Jarvis", "Salam", "Namaste", "Hola",
  "Bonjour", "Merhaba" — kisi bhi language mein greeting. Phir ek command sunta hai,
  kaam karta hai, wapas khamosh ho jata hai.

### Any language (v8)
- Brain jis language mein sawal ho, usi mein jawab deta hai — Urdu, Roman Urdu,
  Hindi, Arabic, Spanish, French, German, Turkish, English. LLM key ho to full,
  bina key ke Wikipedia usi language mein.

### Settings + sync (v8)
- HUD aur mobile dono mein **SETTINGS — API & SYNC** card: API key, base URL, model.
  Key sirf laptop ke `config.json` mein save hoti hai, wapas kabhi full nahi aati
  (sirf `••••1234` dikhta hai). Mobile se badlo to PC pe update, PC se badlo to
  mobile pe — dono har 5 second mein `/api/settings` se sync karte hain.
  Connect karna optional hai: bina API key ke bhi Jarvis free research se jawab deta hai.
- `GET /api/settings` — masked key status, base URL, model, `phone_link_enabled`, `ui_language`.
- `POST /api/settings` `{llm_api_key, llm_base_url, llm_model, phone_link_enabled, ui_language, from}` — saves to config.json.
- UI language: `ui_language` is one of `en` (default), `ur-roman`, `ur`, `hi`, `ar`, `es`, `fr`, `de`, `tr`, `pt`, `ru`. It lives in Settings → Language, translates the whole HUD + mobile UI (Urdu/Arabic switch to right-to-left), and syncs both ways like the other settings. Strings live in `ui/i18n.js` (copied to `mobile-app/www/i18n.js` for the phone app).

### Phone link is OPTIONAL (v8.1)
- Jarvis works **fully on the PC alone** — no phone needed at all. Phone link is
  an optional extra, controlled by the **"Connect phone to PC (optional)"**
  checkbox in Settings (PC or mobile, syncs both ways).
- Off: QR card hides, `/api/pair` and `/api/qr.png` refuse, phone commands stop.
  PC commands, Brain, files, lock/unlock on the PC — sab chalta rehta hai.
- On: scan the QR code once, phone connects. Turn it off any time.

### POST /api/phone-command — laptop → phone (queued)
```bash
curl -X POST http://localhost:5000/api/phone-command \
  -H "Content-Type: application/json" -d '{"action": "ring"}'
```
Response: `{"ok": true, "queued": 1}`
Actions: `ring`, `vibrate`, `torch`, `beep`, `flash`, `open_youtube`.

### GET /api/phone-commands — phone polls and runs queued actions
```bash
curl http://localhost:5000/api/phone-commands
```
Response: `{"commands": [{"action": "ring", "time": "03:54 PM"}]}` — the queue is cleared on read.

### POST /api/phone-status — phone reports itself to the laptop
```bash
curl -X POST http://localhost:5000/api/phone-status \
  -H "Content-Type: application/json" -d '{"battery": 78, "charging": false}'
```
Response: `{"ok": true}` — shown in the laptop HUD as phone battery.

### POST /api/send-to-phone — laptop sends a message to the phone inbox
```bash
curl -X POST http://localhost:5000/api/send-to-phone \
  -H "Content-Type: application/json" -d '{"message": "Hello from laptop"}'
```
Response: `{"ok": true, "count": 1}`

### GET /api/inbox — phone reads messages from the laptop
```bash
curl http://localhost:5000/api/inbox
```
Response: `{"messages": [{"text": "Hello from laptop", "time": "03:54 PM, 07 Nov"}]}`

### GET /api/docs — this API as JSON
```bash
curl http://localhost:5000/api/docs
```

## Your own API
If you give me your API (base URL + key, if any), I will wire it in:
1. Set `window.JARVIS_API` to your base URL in `ui/index.html` / `ui/mobile.html`, or
2. Tell me the endpoint names and I will map them to the same UI buttons.

Note: the UI calls the API from the browser, so your API must allow CORS
(`Access-Control-Allow-Origin: *`) or be served from the same origin as the UI.
