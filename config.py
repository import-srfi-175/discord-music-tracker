import os
from dotenv import load_dotenv

load_dotenv()

# discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# last.fm
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")

# gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# other stuff
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")

if not LASTFM_API_KEY:
    raise RuntimeError("LASTFM_API_KEY is missing")

if not LASTFM_USERNAME:
    raise RuntimeError("LASTFM_USERNAME is missing")


