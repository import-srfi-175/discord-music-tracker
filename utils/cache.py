import json
import asyncio
from pathlib import Path

CACHE_FILE = Path("cache.json")

class Cache:
    def __init__(self):
        self._data = {}
        self._loaded = False
        self._lock = asyncio.Lock()

    def _load_sync(self):
        """synchronous load for executor"""
        if not CACHE_FILE.exists():
            return {}
        try:
            return json.loads(CACHE_FILE.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"⚠️ warning: {CACHE_FILE} is corrupted. resetting cache.")
            return {}

    def _save_sync(self, data):
        """synchronous save for executor"""
        CACHE_FILE.write_text(json.dumps(data, indent=2))

    async def load(self):
        """loads cache asynchronously if not loaded"""
        if self._loaded:
            return
        
        loop = asyncio.get_running_loop()
        async with self._lock:
             # double check inside lock
            if self._loaded: 
                return
            self._data = await loop.run_in_executor(None, self._load_sync)
            self._loaded = True

    async def get(self, key: str):
        """get value by key"""
        if not self._loaded:
            await self.load()
        return self._data.get(key)

    async def set(self, key: str, value):
        """set value and save asynchronously"""
        if not self._loaded:
            await self.load()
        
        self._data[key] = value
        
        # save to disk
        loop = asyncio.get_running_loop()
        # we copy data to avoid thread safety issues during write if it changes
        data_to_save = self._data.copy()
        await loop.run_in_executor(None, self._save_sync, data_to_save)

# global instance
cache = Cache()