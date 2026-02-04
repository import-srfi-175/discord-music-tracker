import discord
from discord import app_commands
from discord.ext import commands
import config

from services.lastfm import get_now_playing, get_album_art, get_track_playcount
from services.lyrics import get_lyrics
from services.youtube import get_youtube_link
from utils.cache import cache
from utils.image import get_dominant_color

class NowPlayingView(discord.ui.View):
    def __init__(self, bot, youtube_link, track, artist):
        super().__init__(timeout=None)
        self.bot = bot
        self.track = track
        self.artist = artist
        
        # youtube button (link)
        if youtube_link:
            self.add_item(discord.ui.Button(label="YouTube", url=youtube_link))
    
    @discord.ui.button(label="Show Lyrics", style=discord.ButtonStyle.secondary, custom_id="show_lyrics")
    async def show_lyrics(self, interaction: discord.Interaction, button: discord.ui.Button):
        # explicit loading state
        await interaction.response.send_message("🔍 **Searching for lyrics...**", ephemeral=True)
        
        # check cache first
        cache_key = f"{self.artist} - {self.track}"
        cached_data = await cache.get(cache_key) or {}
        lyrics = cached_data.get("lyrics")

        if not lyrics:
            lyrics = await get_lyrics(self.bot.session, self.track, self.artist)
            # cache if found
            if lyrics:
                cached_data["lyrics"] = lyrics
                await cache.set(cache_key, cached_data)
        
        if lyrics:
            # discord limit is 4096 chars for description
            if len(lyrics) > 4000:
                lyrics = lyrics[:4000] + "..."
                
            embed = discord.Embed(title=f"Lyrics: {self.track}", description=lyrics, color=0xFFFFFF)
            await interaction.edit_original_response(content=None, embed=embed)
        else:
            await interaction.edit_original_response(content="❌ **Lyrics not found.**")

class NowPlaying(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="nowplaying",
        description="Show what I am currently listening to"
    )
    async def nowplaying(self, interaction: discord.Interaction):
        # 1. immediately defer the response
        await interaction.response.defer()

        # 2. get the shared session from the bot
        session = self.bot.session

        data = await get_now_playing(session)

        if not data:
            await interaction.followup.send("❌ Could not fetch now playing data.", ephemeral=True)
            return

        track = data["track"]
        artist = data["artist"]
        album = data["album"]
        is_playing = data["now_playing"]

        # cache logic
        cache_key = f"{artist} - {track}"
        cached = await cache.get(cache_key) or {}

        # fetch album art
        album_art = cached.get("album_art")
        if not album_art:
            album_art = await get_album_art(session, artist, album, track)
            if album_art:
                cached["album_art"] = album_art
        
        # fetch youtube link
        youtube_link = cached.get("youtube")
        if not youtube_link:
            youtube_link = await get_youtube_link(track, artist)
            if youtube_link:
                cached["youtube"] = youtube_link

        # update cache
        if cached:
            await cache.set(cache_key, cached)

        # ui/ux logic
        color = await get_dominant_color(session, album_art) if album_art else 0x2F3136
        status_text = "Now Playing 🎧" if is_playing else "Last Played 🕒"
        
        # url encoding for last.fm links
        from urllib.parse import quote
        artist_url = f"https://www.last.fm/music/{quote(artist)}"
        album_url = f"{artist_url}/{quote(album)}" if album else ""
        
        # construct description with font hierarchy
        # h1 for track (big), bold for artist/album
        description = f"# {track}\n"
        description += f"by [**{artist}**]({artist_url})"
        if album:
             description += f"\non [**{album}**]({album_url})"
        
        embed = discord.Embed(
            description=description, # title moved here for size
            color=color
        )
        embed.set_author(name=status_text)
        
        if album_art:
            # embed.set_thumbnail(url=album_art) # removed as requested
            embed.set_image(url=album_art)     # keep large bottom

        # footer with track scrobbles
        track_scrobbles = await get_track_playcount(session, artist, track)
        embed.set_footer(text=f"Track Scrobbles: {track_scrobbles}")

        # controls view with lyrics
        view = NowPlayingView(self.bot, youtube_link, track, artist)

        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(NowPlaying(bot))