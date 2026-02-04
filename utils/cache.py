import json
from pathlib import Path

CACHE_FILE = Path("cache.json")
_cache = None

def _load():
    """Loads cache into memory if not already loaded."""
    global _cache
    if _cache is not None:
        return

    if not CACHE_FILE.exists() or CACHE_FILE.stat().st_size == 0:
        _cache = {}
        return
    
    try:
        _cache = json.loads(CACHE_FILE.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(f"⚠️ Warning: {CACHE_FILE} is corrupted. Resetting cache.")
        _cache = {}

def _save():
    """Saves memory cache to disk."""
    if _cache is not None:
        CACHE_FILE.write_text(json.dumps(_cache, indent=2))

def get(key: str):
    _load()
    return _cache.get(key)

def set(key: str, value):
    _load()
    _cache[key] = value
    _save()