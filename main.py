import logging
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected!')


@bot.event
async def on_raw_reaction_add(payload):
    try:
        user: discord.User = bot.get_user(payload.user_id)
        guild: discord.Guild = bot.get_guild(payload.guild_id)
        channel: discord.TextChannel = discord.utils.get(
            guild.channels, id=payload.channel_id)
        msg: discord.Message = await channel.fetch_message(payload.message_id)
        emoji: discord.Emoji = payload.emoji
    except Exception as e:
        print(e)
        return
