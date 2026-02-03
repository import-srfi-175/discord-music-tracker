import json
from pathlib import Path

CACHE_FILE = Path("cache.json")

def _load():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}

def _save(data):
    CACHE_FILE.write_text(json.dumps(data, indent=2))

def get(key: str):
    return _load().get(key)

def set(key: str, value):
    data = _load()
    data[key] = value
    _save(data)
