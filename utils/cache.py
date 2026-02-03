import json
from pathlib import Path

CACHE_FILE = Path("cache.json")

def _load():
    """Safely loads JSON data, handling empty or corrupted files."""
    if not CACHE_FILE.exists() or CACHE_FILE.stat().st_size == 0:
        return {}
    
    try:
        return json.loads(CACHE_FILE.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError):
        # If the file exists but isn't valid JSON, return empty dict 
        # so the bot doesn't crash.
        print(f"⚠️ Warning: {CACHE_FILE} is corrupted. Resetting cache.")
        return {}

def _save(data):
    """Saves data to the cache file with pretty-printing."""
    CACHE_FILE.write_text(json.dumps(data, indent=2))

def get(key: str):
    return _load().get(key)

def set(key: str, value):
    data = _load()
    data[key] = value
    _save(data)