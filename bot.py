import discord
import config

# Intents
intents = discord.Intents.default()
intents.message_content = True  # needed for text commands

# Client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    print(f"🆔 Bot ID: {client.user.id}")

@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # Simple test command
    if message.content == "!ping":
        await message.channel.send("pong :3")

# Start the bot
client.run(config.DISCORD_TOKEN)
