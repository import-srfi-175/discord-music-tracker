import requests
import re
import config

BASE_URL = "https://ws.audioscrobbler.com/2.0/"

def force_hd_url(url: str) -> str:
    """
    Transforms a standard Last.fm image URL into the original high-res version.
    Example: .../300x300/abc.jpg -> .../_/abc.jpg
    """
    if not url:
        return url
    # Replaces the size segment (e.g., /300x300/ or /174s/) with /_/ 
    return re.sub(r'\/i\/u\/[^\/]+\/', '/i/u/_/', url)

def get_now_playing():
    """Fetches current track info."""
    params = {
        "method": "user.getrecenttracks",
        "user": config.LASTFM_USERNAME,
        "api_key": config.LASTFM_API_KEY,
        "format": "json",
        "limit": 1
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        track = data["recenttracks"]["track"][0]
        
        return {
            "track": track["name"],
            "artist": track["artist"]["#text"],
            "album": track.get("album", {}).get("#text", ""),
            "now_playing": "@attr" in track,
        }
    except (KeyError, IndexError, requests.RequestException):
        return None

def get_album_art(artist: str, album: str = None, track: str = None):
    """
    Fetches the best available image URL and forces it to original resolution.
    """
    # 1. Try Album lookup (usually most reliable for art)
    if album:
        params = {
            "method": "album.getinfo",
            "artist": artist,
            "album": album,
            "api_key": config.LASTFM_API_KEY,
            "format": "json"
        }
        try:
            res = requests.get(BASE_URL, params=params, timeout=10).json()
            images = res.get("album", {}).get("image", [])
            # Grab the first non-empty URL (checking largest sizes first)
            raw_url = next((img["#text"] for img in reversed(images) if img["#text"]), None)
            if raw_url:
                return force_hd_url(raw_url)
        except Exception:
            pass

    # 2. Fallback to Track lookup
    if track:
        params = {
            "method": "track.getInfo",
            "artist": artist,
            "track": track,
            "api_key": config.LASTFM_API_KEY,
            "format": "json"
        }
        try:
            res = requests.get(BASE_URL, params=params, timeout=10).json()
            images = res.get("track", {}).get("album", {}).get("image", [])
            raw_url = next((img["#text"] for img in reversed(images) if img["#text"]), None)
            if raw_url:
                return force_hd_url(raw_url)
        except Exception:
            pass

    return None

if __name__ == "__main__":
    now = get_now_playing()
    if now:
        art = get_album_art(now['artist'], now['album'], now['track'])
        print(f"Track: {now['track']}\nArtist: {now['artist']}\nArt: {art}")