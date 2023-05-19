import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from cogs import Scheduling, ContestManagement, UserManagement
from settings import Settings
from points import PointsManager

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

bot = commands.Bot(command_prefix="+", intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected!')

    Settings.reload_all(bot)

    PointsManager.parse_data()

    await bot.add_cog(Scheduling(bot))
    await bot.add_cog(ContestManagement(bot))
    await bot.add_cog(UserManagement(bot))

@bot.command()
async def sync(ctx: commands.Context):
    await ctx.send("Syncing commands...")
    await ctx.bot.tree.sync(guild=Settings.guild)
    await ctx.send("Finished syncing commands.")

bot.run(DISCORD_TOKEN)
