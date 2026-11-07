# JARVIS — Seller Pack

## What you are selling
JARVIS v7 — a Windows PC + phone personal assistant: video HUD, voice + text,
full PC control, phone ↔ laptop control both ways, lock/unlock, QR pairing,
and a Brain that answers questions and writes code.

## What is in the folder (sell this whole folder, or the .exe + APK when built)
- `setup.bat` — one-click install + start (the buyer never touches code)
- `jarvis_server.py` + `jarvis.py` + `power_pack.py` + `brain.py` + `windows_pack.py`
- `ui/` — approved video HUD (desktop + mobile, same design)
- `config.json` — buyer puts their own LLM key / unlock PIN here, never yours
- `SETUP.md` — 60-second buyer setup guide
- `API.md` — full command + API list
- `LICENSE` — commercial licence (below)
- Build files: `jarvis.spec`, `build_exe.bat`, `mobile-app/`, `.github/workflows/`

## How to sell it
1. Give the buyer the folder (USB / download link) + `SETUP.md`.
2. They run `setup.bat`, scan the QR code with their phone. Done.
3. You do NOT give them your API keys, your Windows PIN, or your config.json
   with secrets in it. Ship `config.json` with empty keys (as it is now).
4. Price: set your own. This is a one-time licence, not a subscription,
   unless you decide to offer support as a separate paid service.

## What to tell the buyer (do not over-promise)
- Works on Windows 10/11, same Wi-Fi as the phone.
- Full brain needs the buyer's own LLM key (OpenAI/Groq/Ollama). Without it,
  Jarvis answers from free web research and writes basic code.
- Lock/unlock: laptop lock is instant; laptop unlock needs the buyer's own
  sign-in setup (see SETUP.md). No bypass, ever.
- Support: offer setup help for 7 days, then paid support if you want.

## Licence (summary — see LICENSE)
One licence = one laptop + one phone, for the buyer. They may not resell,
re-upload, or give away the folder. You keep the source and the right to
sell more copies.
