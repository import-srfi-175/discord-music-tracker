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
        await self.load_extension("commands.currency")
        await self.add_cog(Sync(self))
        
        await self.tree.sync()
        print("[INFO] Slash commands synced globally")

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx, spec: str = None):
        if spec == "guild":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"Synced {len(synced)} commands to this guild.")
        else:
            synced = await ctx.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands globally.")

    @commands.command()
    @commands.is_owner()
    async def clear(self, ctx):
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send("Cleared guild commands.")



bot = MusicBot()

@bot.event
async def on_ready():
    print(f"[INFO] Logged in as {bot.user} ({bot.user.id})")

# run bot
bot.run(config.DISCORD_TOKEN)
