import discord
from discord import app_commands
import aiohttp
import config

# switch to commands.bot for better extension support
from discord.ext import commands

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.session: aiohttp.ClientSession = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        
        # load extensions
        await self.load_extension("commands.nowplaying")
        await self.load_extension("commands.user")
        await self.load_extension("commands.charts")
        await self.load_extension("commands.ai")
        
        await self.tree.sync()
        print("[INFO] Slash commands synced globally")

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

bot = MusicBot()

@bot.event
async def on_ready():
    print(f"[INFO] Logged in as {bot.user} ({bot.user.id})")

# run bot
bot.run(config.DISCORD_TOKEN)
