import discord
from discord import app_commands
import aiohttp
import config

class MusicBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.session: aiohttp.ClientSession = None

    async def setup_hook(self):
        # Initialize the session
        self.session = aiohttp.ClientSession()

        # Load extension
        await self.load_extension("commands.nowplaying")
        
        # 🌍 GLOBAL sync (works in any server)
        synced = await self.tree.sync()
        print(f"🌍 Slash commands synced globally: {len(synced)} commands")
        for cmd in synced:
            print(f" - /{cmd.name}")

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

    async def load_extension(self, extension: str):
        # Basic implementation since discord.Client doesn't have load_extension by default
        # We need to use discord.ext.commands.Bot for full extension support usually,
        # but here we can just import and setup manually if sticking to Client,
        # OR switch to commands.Bot which is better for extensions.
        # Given we used commands.Cog in the command file, we MUST use commands.Bot.
        pass

# Switch to commands.Bot for better extension support
from discord.ext import commands

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.session: aiohttp.ClientSession = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        
        # Load extensions
        await self.load_extension("commands.nowplaying")
        await self.load_extension("commands.user")
        await self.load_extension("commands.charts")
        
        await self.tree.sync()
        print("🌍 Slash commands synced globally")

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

bot = MusicBot()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

# ─────────────────────────────────────────────
# RUN BOT
# ─────────────────────────────────────────────
bot.run(config.DISCORD_TOKEN)
