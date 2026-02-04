import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
from io import BytesIO

from services.lastfm import get_top_items, get_weekly_track_chart, get_album_art
from utils.image import create_collage
from utils.graph import create_timeline_url

Period = Literal["7day", "1month", "3month", "6month", "12month", "overall"]

class ChartCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="top", description="View your top artists, albums, or tracks")
    async def top(self, interaction: discord.Interaction, 
                  category: Literal["artists", "albums", "tracks"], 
                  period: Period = "7day"):
        await interaction.response.defer()
        
        method_map = {
            "artists": "user.gettopartists",
            "albums": "user.gettopalbums",
            "tracks": "user.gettoptracks"
        }
        
        items = await get_top_items(self.bot.session, period, method_map[category], limit=10)
        if not items:
            await interaction.followup.send(f"❌ No data found for top {category}.", ephemeral=True)
            return

        description = ""
        for i, item in enumerate(items):
            name = item.get("name")
            playcount = item.get("playcount", "0")
            artist = item.get("artist", {}).get("name", "") if category != "artists" else ""
            
            line = f"**{i+1}.** {name}"
            if artist:
                line += f" - *{artist}*"
            line += f" ({playcount} plays)\n"
            description += line

        embed = discord.Embed(title=f"Top {category.capitalize()} ({period})", description=description, color=0xba0000)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="collage", description="Generate a collage of your top albums")
    async def collage(self, interaction: discord.Interaction, size: Literal["3x3", "5x5"] = "3x3", period: Period = "7day"):
        await interaction.response.defer()
        
        grid_size = int(size[0]) # '3' or '5'
        limit = grid_size * grid_size
        
        albums = await get_top_items(self.bot.session, period, "user.gettopalbums", limit=limit)
        if not albums:
            await interaction.followup.send("❌ Not enough top albums to generate a collage.", ephemeral=True)
            return
            
        # Extract image URLs (largest size usually last)
        img_urls = []
        for album in albums:
            imgs = album.get("image", [])
            url = imgs[-1]["#text"] if imgs else ""
            img_urls.append(url)
            
        # Generate image
        image_bytes = await create_collage(self.bot.session, img_urls, grid_size)
        
        if not image_bytes:
             await interaction.followup.send("❌ Failed to generate collage.", ephemeral=True)
             return
             
        file = discord.File(fp=image_bytes, filename="collage.png")
        embed = discord.Embed(title=f"Top Albums Collage ({period})", color=0xba0000)
        embed.set_image(url="attachment://collage.png")
        
        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="timeline", description="View your listening timeline")
    async def timeline(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Using weekly track chart for now as it gives recent history with timestamps (sometimes)
        # Or just recent tracks. Last.fm API is a bit limited on strict 'history' availability for free/simple calls.
        # user.getrecenttracks gives exact timestamps. Let's fetch last 200 tracks and plot them.
        
        tracks = await self.bot.loop.run_in_executor(None, lambda: []) # placeholder if needed, but we have async service
        
        # We need a new service method or just reuse get_recent_tracks with high limit
        # Let's import get_recent_tracks again locally or assume it's available via service
        from services.lastfm import get_recent_tracks
        tracks = await get_recent_tracks(self.bot.session, limit=200)
        
        if not tracks:
             await interaction.followup.send("❌ Not enough data for timeline.", ephemeral=True)
             return
             
        url = create_timeline_url(tracks)
        if not url:
            await interaction.followup.send("❌ Could not generate timeline.", ephemeral=True)
            return
            
        embed = discord.Embed(title="Listening Timeline (Last 200 tracks)", color=0xba0000)
        embed.set_image(url=url)
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChartCommands(bot))
