"""
Windows full-control pack for JARVIS v2.
Only runs on Windows. Imported lazily by jarvis.py, so Linux/Mac still work.
No admin needed for most commands. Wi-Fi toggle needs admin / Run as Administrator.
"""
import subprocess, re

def _ps(cmd):
    """Run a PowerShell command, return (ok, output)."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=20)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)

def _cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)

# --- Volume: uses Windows media keys (no install) for up/down/mute,
#     and pycaw (pip install pycaw) for an exact % ---
def volume_key(action):
    import ctypes
    VK = {"up": 0xAF, "down": 0xAE, "mute": 0xAD}
    code = VK.get(action)
    if not code:
        return "Volume: say up, down, or mute."
    ctypes.windll.user32.keybd_event(code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(code, 0, 2, 0)  # KEYEVENTF_KEYUP
    return f"Volume {action}."

def volume_set(percent):
    try:
        percent = max(0, min(100, int(percent)))
    except Exception:
        return "Volume: give me a number 0 to 100, like 'volume 50'."
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol = cast(interface, POINTER(IAudioEndpointVolume))
        vol.SetMasterVolumeLevelScalar(percent / 100.0, None)
        return f"Volume set to {percent}%."
    except ImportError:
        return (f"Exact volume needs pycaw — run: pip install pycaw — "
                f"then 'volume {percent}' will work. For now use 'volume up / down'.")
    except Exception as e:
        return f"Volume set failed: {e}"

def volume_get():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        vol = cast(interface, POINTER(IAudioEndpointVolume))
        return f"Volume is at {round(vol.GetMasterVolumeLevelScalar()*100)}%."
    except Exception:
        return "Volume level needs pycaw: pip install pycaw"

# --- Brightness: WMI, works on most laptops ---
def brightness_set(percent):
    try:
        percent = max(0, min(100, int(percent)))
    except Exception:
        return "Brightness: give me a number 0 to 100, like 'brightness 70'."
    ok, out = _ps(
        f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
        f".WmiSetBrightness(1, {percent})")
    if ok:
        return f"Brightness set to {percent}%."
    return ("Brightness didn't work on this PC — some desktops / external monitors "
            "don't support it. It works on most laptops.")

def brightness_get():
    ok, out = _ps("(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness")
    return f"Brightness is {out.strip()}%." if ok and out.strip().isdigit() else "Brightness: couldn't read it on this PC."

# --- Wi-Fi / Bluetooth ---
def wifi(on: bool):
    # Needs admin for netsh interface toggle. Try it, explain if blocked.
    state = "enable" if on else "disable"
    ok, out = _cmd(f'netsh interface set interface "Wi-Fi" admin={state}')
    if ok:
        return f"Wi-Fi {'on' if on else 'off'}."
    return ("Wi-Fi toggle needs Administrator — right-click jarvis.py / the shortcut "
            "and choose 'Run as administrator', then try again.")

def bluetooth(on: bool):
    # Windows 10/11: toggle via PowerShell Bluetooth service + radio
    if on:
        ok, out = _ps("Start-Service bthserv; Enable-NetAdapter -Name '*Bluetooth*' -Confirm:$false")
    else:
        ok, out = _ps("Disable-NetAdapter -Name '*Bluetooth*' -Confirm:$false")
    return f"Bluetooth {'on' if on else 'off'} requested." if ok else "Bluetooth toggle needs Administrator."

# --- Power ---
def power(action):
    cmds = {
        "lock": "rundll32.exe user32.dll,LockWorkStation",
        "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
        "hibernate": "shutdown /h",
        "restart": "shutdown /r /t 5",
        "shutdown": "shutdown /s /t 5",
    }
    if action not in cmds:
        return "Power: lock, sleep, hibernate, restart, or shutdown?"
    _cmd(cmds[action])
    return {"lock": "Locking the screen.", "sleep": "Going to sleep.",
            "hibernate": "Hibernating.", "restart": "Restarting in 5 seconds.",
            "shutdown": "Shutting down in 5 seconds."}[action]

# --- Windows apps ---
APPS = {
    "notepad": "notepad", "calculator": "calc", "paint": "mspaint",
    "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
    "edge": "msedge", "chrome": "chrome", "firefox": "firefox",
    "cmd": "cmd", "terminal": "wt", "powershell": "powershell",
    "settings": "ms-settings:", "control panel": "control",
    "task manager": "taskmgr", "file explorer": "explorer",
    "files": "explorer", "explorer": "explorer",
    "spotify": "spotify", "vs code": "code", "code": "code",
    "snipping tool": "snippingtool", "camera": "microsoft.windows.camera:",
    "store": "ms-windows-store:",
}
def open_windows_app(name):
    name = name.lower().strip()
    if name in APPS:
        _cmd(f'start "" "{APPS[name]}"' if APPS[name].endswith(":") else f'start "" {APPS[name]}')
        return f"Opening {name}."
    return None  # let jarvis.py fall back to a web search

def empty_recycle_bin():
    ok, _ = _ps("Clear-RecycleBin -Force -ErrorAction SilentlyContinue")
    return "Recycle bin emptied." if ok else "Couldn't empty the recycle bin."

def set_wallpaper(path):
    ok, _ = _ps(
        f"Add-Type -TypeDefinition 'using System.Runtime.InteropServices; "
        f"public class W {{ [DllImport(\"user32.dll\")] public static extern int SystemParametersInfo(int a,int b,string c,int d); }}'; "
        f"[W]::SystemParametersInfo(20,0,'{path}',3)")
    return "Wallpaper changed." if ok else "Wallpaper: give me the full image path."

def type_text(text):
    try:
        import pyautogui
        pyautogui.typewrite(text, interval=0.02)
        return "Typed."
    except ImportError:
        return "Typing needs pyautogui: pip install pyautogui"
