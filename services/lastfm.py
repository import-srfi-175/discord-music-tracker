import aiohttp
import re
import config

BASE_URL = "https://ws.audioscrobbler.com/2.0/"

def force_hd_url(url: str) -> str:
    """
    transforms a standard last.fm image url into the original high-res version.
    example: .../300x300/abc.jpg -> .../_/abc.jpg
    """
    if not url:
        return url
    # replaces the size segment (e.g., /300x300/ or /174s/) with /_/ 
    return re.sub(r'\/i\/u\/[^\/]+\/', '/i/u/_/', url)

async def get_now_playing(session: aiohttp.ClientSession):
    """fetches current track info"""
    params = {
        "method": "user.getrecenttracks",
        "user": config.LASTFM_USERNAME,
        "api_key": config.LASTFM_API_KEY,
        "format": "json",
        "limit": 1
    }
    try:
        async with session.get(BASE_URL, params=params) as response:
            if response.status != 200:
                return None
            data = await response.json()
            
        track = data["recenttracks"]["track"][0]
        total_scrobbles = data["recenttracks"].get("@attr", {}).get("total", "0")
        
        return {
            "track": track["name"],
            "artist": track["artist"]["#text"],
            "album": track.get("album", {}).get("#text", ""),
            "now_playing": "@attr" in track,
            "total_scrobbles": total_scrobbles
        }
    except (KeyError, IndexError, aiohttp.ClientError):
        return None

async def get_album_art(session: aiohttp.ClientSession, artist: str, album: str = None, track: str = None):
    """
    fetches the best available image url and forces it to original resolution
    """
    # 1. try album lookup (usually most reliable for art)
    if album:
        params = {
            "method": "album.getinfo",
            "artist": artist,
            "album": album,
            "api_key": config.LASTFM_API_KEY,
            "format": "json"
        }
        try:
            async with session.get(BASE_URL, params=params) as response:
                if response.status == 200:
                    res = await response.json()
                    images = res.get("album", {}).get("image", [])
                    # grab the first non-empty url (checking largest sizes first)
                    raw_url = next((img["#text"] for img in reversed(images) if img["#text"]), None)
                    if raw_url:
                        return force_hd_url(raw_url)
        except Exception:
            pass

    # 2. fallback to track lookup
    if track:
        params = {
            "method": "track.getInfo",
            "artist": artist,
            "track": track,
            "api_key": config.LASTFM_API_KEY,
            "format": "json"
        }
        try:
            async with session.get(BASE_URL, params=params) as response:
                if response.status == 200:
                    res = await response.json()
                    images = res.get("track", {}).get("album", {}).get("image", [])
                    raw_url = next((img["#text"] for img in reversed(images) if img["#text"]), None)
                    if raw_url:
                        return force_hd_url(raw_url)
        except Exception:
            pass

    return None

async def get_user_info(session: aiohttp.ClientSession):
    """fetches user profile information"""
    params = {
        "method": "user.getinfo",
        "user": config.LASTFM_USERNAME,
        "api_key": config.LASTFM_API_KEY,
        "format": "json"
    }
    try:
        async with session.get(BASE_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("user")
    except Exception:
        pass
    return None

async def get_recent_tracks(session: aiohttp.ClientSession, limit: int = 10):
    """fetches recent tracks"""
    params = {
        "method": "user.getrecenttracks",
        "user": config.LASTFM_USERNAME,
        "api_key": config.LASTFM_API_KEY,
        "format": "json",
        "limit": limit
    }
    try:
        async with session.get(BASE_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("recenttracks", {}).get("track", [])
    except Exception:
        pass
    return []

async def get_top_items(session: aiohttp.ClientSession, period: str, method: str, limit: int = 10):
    """
    fetches top artists, albums, or tracks
    period: overall | 7day | 1month | 3month | 6month | 12month
    method: user.gettopartists | user.gettopalbums | user.gettoptracks
    """
    params = {
        "method": method,
        "user": config.LASTFM_USERNAME,
        "api_key": config.LASTFM_API_KEY,
        "format": "json",
        "period": period,
        "limit": limit
    }
    try:
        async with session.get(BASE_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                # determine the key based on method name
                key_map = {
                    "user.gettopartists": "topartists",
                    "user.gettopalbums": "topalbums",
                    "user.gettoptracks": "toptracks"
                }
                root_key = key_map.get(method)
                if root_key:
                    # the inner list key is usually artist, album, or track
                    item_key = root_key.replace("top", "").rstrip("s")
                    return data.get(root_key, {}).get(item_key, [])
    except Exception:
        pass
    return []

async def get_weekly_track_chart(session: aiohttp.ClientSession):
    """fetches the user's weekly track chart list (timeline data)"""
    # note: user.getweeklytrackchart usually requires a specific from/to range,
    # but without args it defaults to most recent.
    # basically, for a timeline, we might want 'user.getweeklychartlist' to show available ranges,
    # or just use 'user.getrecenttracks' and aggregate manually if we want a detailed history graph.
    # to keep it simple for now, let's use user.getweeklytrackchart for the last week.
    params = {
        "method": "user.getweeklytrackchart",
        "user": config.LASTFM_USERNAME,
        "api_key": config.LASTFM_API_KEY,
        "format": "json"
    }
    try:
        async with session.get(BASE_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("weeklytrackchart", {}).get("track", [])
    except Exception:
        pass
    except Exception:
        pass
    return []

async def get_track_playcount(session: aiohttp.ClientSession, artist: str, track: str) -> str:
    """fetches the user's playcount for a specific track"""
    params = {
        "method": "track.getInfo",
        "api_key": config.LASTFM_API_KEY,
        "artist": artist,
        "track": track,
        "username": config.LASTFM_USERNAME, # needed to get userplaycount
        "format": "json"
    }
    try:
        async with session.get(BASE_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("track", {}).get("userplaycount", "0")
    except Exception:
        pass
    return "0"