"""Decode the base64 asset files back to binary.
The HUD video + robot image are stored in the repo as .b64 text files
(because the GitHub upload route only takes text), and decoded by:
  - the GitHub Actions workflows, before building the .exe / .apk
  - you, locally, if you ever delete ui/assets/:  python decode_assets.py
"""
import base64
from pathlib import Path

BASE = Path(__file__).parent

def decode(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(base64.b64decode(Path(src).read_text()))
    print(f"decoded {src} -> {dst} ({dst.stat().st_size} bytes)")

if __name__ == "__main__":
    decode(BASE / "ui" / "assets" / "jarvis.mp4.b64", BASE / "ui" / "assets" / "jarvis.mp4")
    decode(BASE / "ui" / "assets" / "robot.jpg.b64", BASE / "ui" / "assets" / "robot.jpg")
    decode(BASE / "ui" / "assets" / "jarvis.mp4.b64", BASE / "mobile-app" / "www" / "assets" / "jarvis.mp4")
    decode(BASE / "ui" / "assets" / "robot.jpg.b64", BASE / "mobile-app" / "www" / "assets" / "robot.jpg")
