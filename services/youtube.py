import yt_dlp

def get_youtube_link(track: str, artist: str) -> str | None:
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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for q in queries:
            try:
                info = ydl.extract_info(f"ytsearch1:{q}", download=False)
                if info and info.get("entries"):
                    video_id = info["entries"][0]["id"]
                    return f"https://www.youtube.com/watch?v={video_id}"
            except Exception:
                continue

    return None
