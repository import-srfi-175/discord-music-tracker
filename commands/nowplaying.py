import discord
from discord import app_commands
from discord.ext import commands

from services.lastfm import get_now_playing, get_album_art
from services.youtube import get_youtube_link
from utils.cache import get as cache_get, set as cache_set
from utils.image import get_dominant_color

class NowPlaying(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="nowplaying",
        description="Show what I am currently listening to"
    )
    async def nowplaying(self, interaction: discord.Interaction):
        # 1. Immediately defer the response
        await interaction.response.defer()

        # 2. Get the shared session from the bot
        session = self.bot.session

        data = await get_now_playing(session)

        if not data:
            await interaction.followup.send("❌ Could not fetch now playing data.", ephemeral=True)
            return

        track = data["track"]
        artist = data["artist"]
        album = data["album"]
        is_playing = data["now_playing"]

        # Cache Logic
        cache_key = f"{artist} - {track}"
        cached = cache_get(cache_key) or {}

        # Fetch Album Art
        album_art = cached.get("album_art")
        if not album_art:
            album_art = await get_album_art(session, artist, album, track)
            if album_art:
                cached["album_art"] = album_art
        
        # Fetch YouTube Link
        youtube_link = cached.get("youtube")
        if not youtube_link:
            youtube_link = await get_youtube_link(track, artist)
            if youtube_link:
                cached["youtube"] = youtube_link

        # Update Cache
        if cached:
            cache_set(cache_key, cached)

        # UI/UX Logic
        color = await get_dominant_color(session, album_art) if album_art else 0x2F3136
        status_text = "Now Playing 🎧" if is_playing else "Last Played 🕒"
        
        # URL Encoding for Last.fm links
        from urllib.parse import quote
        artist_url = f"https://www.last.fm/music/{quote(artist)}"
        album_url = f"{artist_url}/{quote(album)}" if album else ""
        
        # Construct Description with Font Hierarchy
        # H1 for Track (Big), Bold for Artist/Album
        description = f"# {track}\n"
        description += f"by [**{artist}**]({artist_url})"
        if album:
             description += f"\non [**{album}**]({album_url})"
        
        embed = discord.Embed(
            description=description, # Title moved here for size
            color=color
        )
        embed.set_author(name=status_text)
        
        if album_art:
            # embed.set_thumbnail(url=album_art) # Removed as requested
            embed.set_image(url=album_art)     # Keep Large Bottom

        # YouTube Button
        view = None
        if youtube_link:
            view = discord.ui.View()
            # unique_id is not strictly needed for link buttons but good practice if persistent
            # Using a standard play button emoji which resembles YouTube play
            btn = discord.ui.Button(label="Listen on YouTube", url=youtube_link, emoji="▶️")
            view.add_item(btn)

        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(NowPlaying(bot))