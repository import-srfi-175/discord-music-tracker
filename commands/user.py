import discord
from discord import app_commands
from discord.ext import commands
from services.lastfm import get_user_info, get_recent_tracks
from utils.formatting import format_number

class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Show your Last.fm profile stats")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user = await get_user_info(self.bot.session)
        if not user:
            await interaction.followup.send("❌ Could not fetch user data.", ephemeral=True)
            return

        embed = discord.Embed(title=f"👤 {user['name']}", url=user['url'], color=0xba0000)
        embed.set_thumbnail(url=user['image'][2]['#text']) # Large image
        
        embed.add_field(name="Scrobbles", value=format_number(user['playcount']), inline=True)
        embed.add_field(name="Artists", value=format_number(user.get('artist_count', 0)), inline=True)
        # embed.add_field(name="Albums", value=format_number(user.get('album_count', 0)), inline=True)
        embed.add_field(name="Country", value=user.get('country', 'Unknown'), inline=True)
        
        registered = user.get('registered', {}).get('#text', 'Unknown')
        # Convert unix timestamp if needed, but last.fm often gives int
        if isinstance(registered, int):
             registered = f"<t:{registered}:D>"
        
        embed.add_field(name="Registered", value=registered, inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="recent", description="Show your last 10 tracks")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def recent(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        tracks = await get_recent_tracks(self.bot.session, limit=10)
        if not tracks:
            await interaction.followup.send("❌ Could not fetch recent tracks.", ephemeral=True)
            return

        description = ""
        for i, track in enumerate(tracks):
            name = track['name']
            artist = track['artist']['#text']
            # now_playing = "@attr" in track and track["@attr"].get("nowplaying") == "true"
            # prefix = "🎶" if now_playing else f"{i+1}."
            
            # Simple list format
            description += f"**{i+1}.** [{name}]({track['url']}) - *{artist}*\n"

        embed = discord.Embed(title="Recent Tracks", description=description, color=0xba0000)
        user = await get_user_info(self.bot.session)
        if user:
            embed.set_author(name=f"{user['name']}'s History", icon_url=user['image'][0]['#text'])
            
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(UserCommands(bot))
