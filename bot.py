import discord
from discord import app_commands

import config
from services.lastfm import get_now_playing, get_album_art
from services.youtube import get_youtube_link
from utils.cache import get as cache_get, set as cache_set


class MusicBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # 🌍 GLOBAL sync (works in any server)
        await self.tree.sync()
        print("🌍 Slash commands synced globally")


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
    # 1. Immediately defer the response
    # This shows "Bot is thinking..." in Discord
    await interaction.response.defer()

    # 2. Now do your slow API calls
    data = get_now_playing()

    if not data:
        # Since we deferred, we must use followups.send instead of response.send_message
        await interaction.followup.send("❌ Could not fetch now playing data.", ephemeral=True)
        return

    track = data["track"]
    artist = data["artist"]
    album = data["album"]

    cache_key = f"{artist} - {track}"
    cached = cache_get(cache_key) or {}

    album_art = cached.get("album_art")
    if not album_art:
        album_art = get_album_art(artist, album, track)
        if album_art:
            cached["album_art"] = album_art

    youtube_link = cached.get("youtube")
    if not youtube_link:
        youtube_link = get_youtube_link(track, artist)
        if youtube_link:
            cached["youtube"] = youtube_link

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

    # 3. Use followup.send to finish the response
    await interaction.followup.send(embed=embed)


# ─────────────────────────────────────────────
# RUN BOT
# ─────────────────────────────────────────────
bot.run(config.DISCORD_TOKEN)
