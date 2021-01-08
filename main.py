import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from meta import Meta

# get bot token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# init meta
Meta.load_from_file("./data/meta.json")

# initialize bot
intents = discord.Intents.default()
intents.members = True # allow member caching
bot = commands.Bot(command_prefix=Meta.prefix)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected!")

