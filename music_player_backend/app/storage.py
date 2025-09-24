import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MUSIC_DIR = DATA_DIR / "music"
DB_FILE = DATA_DIR / "db.json"

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}


def ensure_dirs() -> None:
    """
    Ensure the required data directories and files exist.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_FILE.exists():
        DB_FILE.write_text(json.dumps({"tracks": [], "preferences": {}}, indent=2))


def _read_db() -> Dict[str, Any]:
    ensure_dirs()
    try:
        return json.loads(DB_FILE.read_text() or "{}")
    except Exception:
        return {"tracks": [], "preferences": {}}


def _write_db(data: Dict[str, Any]) -> None:
    ensure_dirs()
    DB_FILE.write_text(json.dumps(data, indent=2))


def allowed_file(filename: str) -> bool:
    """
    Check if a filename has an allowed music extension.
    """
    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def save_music_file(file_storage) -> Dict[str, Any]:
    """
    Save an uploaded file into MUSIC_DIR and register metadata in db.json.

    Returns track metadata dict.
    """
    ensure_dirs()
    original = secure_filename(file_storage.filename or "")
    if not original:
        raise ValueError("Invalid filename.")
    if not allowed_file(original):
        raise ValueError("Unsupported file type.")

    # Avoid overwrite: if exists, append a numeric suffix
    target = MUSIC_DIR / original
    name, ext = os.path.splitext(original)
    counter = 1
    while target.exists():
        target = MUSIC_DIR / f"{name}_{counter}{ext}"
        counter += 1

    file_storage.save(str(target))

    # Build simple track metadata
    track = {
        "id": target.stem,  # simple id derived from filename stem
        "filename": target.name,
        "path": str(target),
        "size": target.stat().st_size,
        "extension": target.suffix.lower(),
    }
    db = _read_db()
    # remove any existing with same path
    db["tracks"] = [t for t in db.get("tracks", []) if t.get("path") != str(target)]
    db["tracks"].append(track)
    _write_db(db)
    return track


def list_tracks() -> List[Dict[str, Any]]:
    """
    Return all tracks.
    """
    db = _read_db()
    return db.get("tracks", [])


def get_track_by_id(track_id: str) -> Optional[Dict[str, Any]]:
    """
    Find a track by its id (filename stem).
    """
    for t in list_tracks():
        if t.get("id") == track_id:
            return t
    return None


def delete_track(track_id: str) -> bool:
    """
    Delete a track file and remove it from the database.
    """
    db = _read_db()
    tracks = db.get("tracks", [])
    target = None
    for t in tracks:
        if t.get("id") == track_id:
            target = t
            break

    if not target:
        return False

    # Remove file if exists
    p = Path(target.get("path"))
    try:
        if p.exists():
            p.unlink()
    except Exception:
        # ignore filesystem errors
        pass

    db["tracks"] = [t for t in tracks if t.get("id") != track_id]
    _write_db(db)
    return True


def save_preferences(user_id: str, prefs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save preferences for a user_id.
    """
    db = _read_db()
    preferences = db.get("preferences", {})
    preferences[user_id] = prefs
    db["preferences"] = preferences
    _write_db(db)
    return prefs


def get_preferences(user_id: str) -> Dict[str, Any]:
    """
    Get preferences for a user_id.
    """
    db = _read_db()
    return db.get("preferences", {}).get(user_id, {})
