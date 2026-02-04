import discord
from discord import app_commands
from discord.ext import commands

from services.lastfm import get_now_playing, get_album_art
from services.youtube import get_youtube_link
from utils.cache import get as cache_get, set as cache_set

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

        cache_key = f"{artist} - {track}"
        cached = cache_get(cache_key) or {}

        # 3. Fetch Album Art (if not cached)
        album_art = cached.get("album_art")
        if not album_art:
            album_art = await get_album_art(session, artist, album, track)
            if album_art:
                cached["album_art"] = album_art
        
        # 4. Fetch YouTube Link (if not cached)
        youtube_link = cached.get("youtube")
        if not youtube_link:
            youtube_link = await get_youtube_link(track, artist)
            if youtube_link:
                cached["youtube"] = youtube_link

        # 5. Update Cache
        if cached:
            cache_set(cache_key, cached)

        embed = discord.Embed(
            title="Now Playing",
            description=f"**{track}**\nby *{artist}*",
            color=0xFFFFFF
        )

        if album:
            embed.add_field(name="Album", value=album, inline=False)
        if youtube_link:
            embed.add_field(name="YouTube", value=youtube_link, inline=False)
        if album_art:
            embed.set_image(url=album_art)

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(NowPlaying(bot))