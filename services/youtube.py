import yt_dlp
import asyncio

async def get_youtube_link(track: str, artist: str) -> str | None:
    queries = [
        f"{track} {artist} topic",
        f"{track} {artist} official audio",
        f"{track} {artist}",
    ]

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
    }

    loop = asyncio.get_running_loop()

    def _search(q):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch1:{q}", download=False)
                if info and info.get("entries"):
                    return info["entries"][0]["id"]
            except Exception:
                return None
        return None

    for q in queries:
        video_id = await loop.run_in_executor(None, _search, q)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

    return None
