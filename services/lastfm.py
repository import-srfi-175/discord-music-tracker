import requests
from urllib.parse import quote_plus
import config


BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def get_now_playing():
    """
    Returns:
        dict with keys: track, artist, album, now_playing
        or None if no data
    """
    url = (
        f"{BASE_URL}"
        f"?method=user.getrecenttracks"
        f"&user={quote_plus(config.LASTFM_USERNAME)}"
        f"&api_key={config.LASTFM_API_KEY}"
        f"&format=json"
        f"&limit=1"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    try:
        track = data["recenttracks"]["track"][0]

        return {
            "track": track["name"],
            "artist": track["artist"]["#text"],
            "album": track.get("album", {}).get("#text", ""),
            "now_playing": "@attr" in track,
        }
    except (KeyError, IndexError):
        return None


def get_album_art(artist: str, album: str | None, track: str | None):
    # Try album-based lookup first (best quality)
    if album:
        url = (
            f"{BASE_URL}"
            f"?method=album.getinfo"
            f"&artist={quote_plus(artist)}"
            f"&album={quote_plus(album)}"
            f"&api_key={config.LASTFM_API_KEY}"
            f"&format=json"
        )

        r = requests.get(url, timeout=10)
        data = r.json()

        try:
            return data["album"]["image"][-1]["#text"]
        except (KeyError, IndexError):
            pass

    # Fallback: track-based lookup
    if track:
        url = (
            f"{BASE_URL}"
            f"?method=track.getInfo"
            f"&artist={quote_plus(artist)}"
            f"&track={quote_plus(track)}"
            f"&api_key={config.LASTFM_API_KEY}"
            f"&format=json"
        )

        r = requests.get(url, timeout=10)
        data = r.json()

        try:
            return data["track"]["album"]["image"][-1]["#text"]
        except (KeyError, IndexError):
            pass

    return None