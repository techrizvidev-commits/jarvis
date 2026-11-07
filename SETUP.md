# JARVIS — Setup in 60 seconds (no code, ever)

## 1. On the laptop (once)
1. Copy the `jarvis` folder to the laptop.
2. Double-click **`setup.bat`** — it installs everything, opens the firewall, starts Jarvis.
3. The HUD opens at `http://localhost:5000`.

## 2. Connect the phone — OPTIONAL (skip this if you only want the PC)
Jarvis works fully on the PC alone. Phone is an optional extra.
1. If you want it: on the laptop HUD, find the **CONNECT PHONE — SCAN ONCE (OPTIONAL)** card.
2. Open the phone camera and scan the QR code.
3. The phone opens Jarvis mobile. Done. It stays connected on the same Wi-Fi.
4. No camera? Type the address shown under the QR code once, or use the 6-character pair code.

**It never asks for a new code.** The QR code and pair code are generated once when the server starts. If the laptop IP changes (new Wi-Fi), just scan the QR code again — same 10 seconds.

To turn phone link off any time: Settings > uncheck **"Connect phone to PC (optional)"** > Save. PC keeps working exactly the same.

## 3. Make it the full Iron-Man brain (optional, 2 minutes)
Without a key, Jarvis already answers from Wikipedia / web research and writes basic code.
For the full brain — any question, any code, any complex task:
1. Get a key: OpenAI (platform.openai.com) or Groq (console.groq.com, free tier).
2. Open `config.json` on the laptop, paste it in `"llm_api_key"`.
3. Groq: also set `"llm_base_url": "https://api.groq.com/openai/v1"` and `"llm_model": "llama-3.3-70b-versatile"`.
4. Restart `setup.bat`. Never share the key, never put it in chat.

## 4. Daily use
- Start: double-click `start_jarvis.bat` (or `setup.bat`).
- Phone controls laptop, laptop controls phone, lock/unlock both ways — see `API.md`.
- Same Wi-Fi only. Outside home: use Tailscale (free) on both devices, then the same QR works.

## What is NOT included (honest)
- No Iron-Man suit. No flying, no weapons.
- Windows cannot be unlocked without your own sign-in (see `API.md` — unlock section).
- Phone system lock needs the native APK (Device Admin). Web gives a PIN lock screen.
