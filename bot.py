import discord
from discord import app_commands

import config
from services.lastfm import get_now_playing, get_album_art
from services.youtube import get_youtube_link
from utils.cache import get as cache_get, set as cache_set


# 🔧 DEV GUILD (for instant slash command updates)
GUILD_ID = 1429080736899792948  # replace with your server ID


class MusicBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync commands instantly to dev guild
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("✅ Slash commands synced to dev guild")


bot = MusicBot()


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")


# ─────────────────────────────────────────────
# SLASH COMMAND: /nowplaying
# ─────────────────────────────────────────────
@bot.tree.command(
    name="nowplaying",
    description="Show what I am currently listening to"
)
async def nowplaying(interaction: discord.Interaction):
    data = get_now_playing()

    if not data:
        await interaction.response.send_message(
            "❌ Could not fetch now playing data.",
            ephemeral=True
        )
        return

    track = data["track"]
    artist = data["artist"]
    album = data["album"]

    cache_key = f"{artist} - {track}"
    cached = cache_get(cache_key) or {}

    # 🎨 Album art (cached)
    album_art = cached.get("album_art")
    if not album_art:
        album_art = get_album_art(artist, album, track)
        if album_art:
            cached["album_art"] = album_art

    # ▶️ YouTube link (cached)
    youtube_link = cached.get("youtube")
    if not youtube_link:
        youtube_link = get_youtube_link(track, artist)
        if youtube_link:
            cached["youtube"] = youtube_link

    # Save cache if updated
    if cached:
        cache_set(cache_key, cached)

    # Build embed
    embed = discord.Embed(
        title="Now Playing:",
        description=f"**{track}**\nby *{artist}*",
        color=0xFFFFFF
    )

    if album:
        embed.add_field(name="Album", value=album, inline=False)

    if youtube_link:
        embed.add_field(name="YouTube", value=youtube_link, inline=False)

    if album_art:
        embed.set_thumbnail(url=album_art)

    await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────
# RUN BOT
# ─────────────────────────────────────────────
bot.run(config.DISCORD_TOKEN)
