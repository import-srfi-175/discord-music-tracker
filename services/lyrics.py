import aiohttp

LRCLIB_URL = "https://lrclib.net/api/get"

async def get_lyrics(session: aiohttp.ClientSession, track: str, artist: str) -> str:
    """
    fetches plain lyrics from lrclib.
    returns none if not found.
    """
    params = {
        "track_name": track,
        "artist_name": artist
    }
    
    try:
        async with session.get(LRCLIB_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                # prioritize plainlyrics (no timestamps)
                return data.get("plainLyrics")
    except Exception:
        pass
    
    return None
