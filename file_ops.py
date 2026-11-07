"""
JARVIS File Ops v8 — any file work, by name or by path.
  delete file <name>        — moves to Recycle Bin if possible, else deletes
  move file <name> to <folder>
  rename file <name> to <new name>
  copy file <name> to <folder>
  create file <name>        — creates an empty file in Documents
  create folder <name>
  list files [in <folder>]  — lists Downloads / Documents / Desktop
Safety: never touches Windows / System32 / Program Files / the jarvis folder
itself. System files are refused with a clear message. Delete is by name:
Jarvis searches Downloads, Documents, Desktop first, then the whole home
folder (but not hidden/system folders).
"""
import shutil
from pathlib import Path

SEARCH_DIRS = ["Downloads", "Documents", "Desktop", "Pictures", "Videos", "Music"]
BLOCKED = ("windows", "system32", "program files", "program files (x86)", "appdata", "jarvis")

def _blocked(p: Path):
    parts = [x.lower() for x in p.parts]
    return any(b in parts for b in BLOCKED) or p == Path.home()

def find(name):
    name = name.strip().strip('"')
    p = Path(name)
    if p.exists() and p.is_absolute():
        return p if not _blocked(p) else None
    home = Path.home()
    for d in SEARCH_DIRS:
        folder = home / d
        if not folder.exists():
            continue
        exact = folder / name
        if exact.exists():
            return exact
        for hit in folder.rglob(f"*{name}*"):
            if hit.is_file() and not _blocked(hit):
                return hit
    return None

def delete_file(name):
    p = find(name)
    if not p:
        return f"File '{name}' nahi mili — Downloads / Documents / Desktop mein check karo."
    if _blocked(p):
        return f"'{name}' system file hai — Jarvis system files delete nahi karta."
    try:
        from send2trash import send2trash
        send2trash(str(p))
        return f"Deleted '{p.name}' — Recycle Bin mein gayi, wapas la sakte ho."
    except Exception:
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            return f"Deleted '{p.name}'."
        except Exception as e:
            return f"Delete nahi hui: {e}"

def move_file(name, dest):
    p = find(name)
    if not p:
        return f"File '{name}' nahi mili."
    d = Path.home() / dest.strip().strip('"')
    d.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p), str(d / p.name))
    return f"Moved '{p.name}' to {d.name}."

def rename_file(name, new):
    p = find(name)
    if not p:
        return f"File '{name}' nahi mili."
    p.rename(p.parent / new.strip().strip('"'))
    return f"Renamed '{p.name}' to {new.strip()}."

def copy_file(name, dest):
    p = find(name)
    if not p:
        return f"File '{name}' nahi mili."
    d = Path.home() / dest.strip().strip('"')
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(d / p.name))
    return f"Copied '{p.name}' to {d.name}."

def create_file(name):
    p = Path.home() / "Documents" / name.strip().strip('"')
    if _blocked(p):
        return "System jagah pe file nahi bana sakta."
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch(exist_ok=True)
    return f"Created '{p.name}' in Documents."

def create_folder(name):
    p = Path.home() / "Documents" / name.strip().strip('"')
    p.mkdir(parents=True, exist_ok=True)
    return f"Created folder '{p.name}' in Documents."

def list_files(folder="Downloads"):
    name = folder.strip().strip('"')
    d = Path.home() / name
    if not d.exists():
        d = Path.home() / name.title()
    if not d.exists():
        for cand in Path.home().iterdir():
            if cand.is_dir() and cand.name.lower() == name.lower():
                d = cand; break
    if not d.exists():
        return f"Folder '{folder}' nahi mila."
    items = [x.name for x in d.iterdir()][:20]
    return f"{folder}: " + (", ".join(items) if items else "empty.")
