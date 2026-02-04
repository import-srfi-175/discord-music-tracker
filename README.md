# discord music tracker

a minimal discord bot that tracks your music habits using last.fm, with some ai features baked in.

## features

- **now playing**: see what you're currently listening to, complete with youtube links and a lyrics fetcher (powered by lrclib).
- **profile stats**: check your total scrobbles, top artists, and recent history.
- **visuals**: generate 3x3 or 5x5 collages of your top albums.
- **ai companion**: chat with kairos, a music-focused persona, or ask for fun facts about your current track (powered by google gemini).

## setup

1. **clone the repo**
   
2. **environment**:
   create a python virtual environment to keep things clean.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **dependencies**:
   install only what you need.
   ```bash
   pip install -r requirements.txt
   ```

4. **configuration**:
   create a `.env` file in the root directory with the following keys:
   ```text
   DISCORD_TOKEN=your_token_here
   LASTFM_API_KEY=your_key_here
   LASTFM_USERNAME=your_username
   GEMINI_API_KEY=your_key_here
   ```

5. **run**:
   ```bash
   python3 bot.py
   ```

## commands

- `/nowplaying` - shows your current song, track scrobbles, and controls for lyrics/youtube.
- `/profile` - overview of your last.fm stats.
- `/recent` - list of your last 10 tracks.
- `/top [artists|albums|tracks]` - view your charts for different time periods.
- `/collage [size]` - generate an image collage of your top albums.
- `/funfact` - get a short fact about the song you're playing.
- `/chat [message]` - talk to kairos about music.

## structure

- `bot.py` - entry point.
- `commands/` - slash command modules.
- `services/` - api integrations (last.fm, youtube, gemini, lrclib).
- `utils/` - helpers for caching, image processing, etc.

keep it simple.
