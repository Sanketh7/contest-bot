import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import datetime

import submission
import points_data
import leaderboard
from util import success_embed, error_embed

import database as db
db.init_database()


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD')
CMD_PREFIX = os.getenv('CMD_PREFIX')
CONTEST_SUBMISSION_CHANNEL = os.getenv('CONTEST_SUBMISSION_CHANNEL')
SIGN_UP_CHANNEL = os.getenv('SIGN_UP_CHANNEL')
IN_CONTEST_ROLE = os.getenv('IN_CONTEST_ROLE')
LEADERBOARD_CHANNEL = os.getenv('LEADERBOARD_CHANNEL')

bot = commands.Bot(command_prefix=CMD_PREFIX)

player_emojis = {}
other_emojis = {}
player_classes = ['archer', 'assassin', 'huntress', 'knight', 'mystic', 'necromancer', 'ninja', 'paladin', 'priest',
                  'rogue', 'samurai', 'sorcerer', 'trickster', 'warrior', 'wizard']

contest_types = ['ppe']

# States
states = {
    "current_contest_post_id": -1,
    "current_contest_end_time": -1,
    "current_contest_index": 0,
    "current_contest_type": "",
    "is_contest_active": False,
    "current_points_document": "",
    "states_read": False
}

points_data_manager = points_data.PointsDataManager()

leaderboard = leaderboard.Leaderboard(bot, GUILD_ID, LEADERBOARD_CHANNEL)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected!')

    meta_data = await db.get_all_metadata()
    for key, value in meta_data.items():
        states[key] = value
    states["states_read"] = True

    if states["current_contest_type"] != "":
        points_data_manager.parse_data(states["current_contest_type"])

    for emoji in bot.emojis:
        for player_class in player_classes:
            if emoji.name == os.getenv("EMOJI_" + player_class.upper()):
                player_emojis[player_class] = str(emoji)
        if emoji.name == os.getenv("EMOJI_GRAVESTONE"):
            other_emojis["gravestone"] = str(emoji)

@bot.event
async def on_raw_reaction_add(payload):
    reaction = str(payload.emoji)
    msg_id = payload.message_id
    ch_id = payload.channel_id
    user_id = payload.user_id
    user: discord.User = bot.get_user(user_id)
    if user == bot.user or user is None:
        return
    guild_id = payload.guild_id

    is_contest_active = states["is_contest_active"]
    contest_post_id = states["current_contest_post_id"]
    contest_index = states["current_contest_index"]
    is_on_contest_post = contest_post_id == msg_id

    # gravestone for creating a submission
    if reaction == other_emojis["gravestone"] and is_contest_active and is_on_contest_post:
        role = discord.utils.get(bot.get_guild(guild_id).roles, name=IN_CONTEST_ROLE)
        if role in bot.get_guild(guild_id).get_member(user_id).roles:
            new_submission = submission.Submission(bot, user, player_emojis, guild_id, CONTEST_SUBMISSION_CHANNEL,
                                                   points_data_manager.keywords, points_data_manager.points_data,
                                                   states["current_contest_index"], states["current_points_document"])
            return await new_submission.start_process()
        else:
            return await user.send(embed=error_embed("You need to sign up before you can submit a character."))

    # Give user "contest" role
    if reaction == "✅" and is_contest_active and is_on_contest_post:
        guild = bot.get_guild(guild_id)
        role = discord.utils.get(guild.roles, name=IN_CONTEST_ROLE)
        if role not in guild.get_member(user_id).roles:
            await user.send(embed=success_embed("You are now part of the contest and can now submit and view channels."))
            return await guild.get_member(user_id).add_roles(role)

    if guild_id is not None:
        sub_channel = discord.utils.get(bot.get_guild(int(guild_id)).text_channels, name=CONTEST_SUBMISSION_CHANNEL)

        # Accept points/submission
        if reaction == "✅" and ch_id == sub_channel.id:
            await db.accept_submission(states["current_contest_index"], msg_id)
            try:
                ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=CONTEST_SUBMISSION_CHANNEL)
                msg = await ch.fetch_message(msg_id)
                await msg.delete()
                await user.send(embed=success_embed("Your submission with ID `" + str(msg_id) + "` was accepted!"))
            except:
                print("Failed to fetch/delete message.")
            return

        # Reject points/submission
        if reaction == "❌" and ch_id == sub_channel.id:
            try:
                ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=CONTEST_SUBMISSION_CHANNEL)
                msg = await ch.fetch_message(msg_id)
                await msg.delete()
                await user.send(embed=error_embed("Your submission with ID `" + str(msg_id) + "` was denied."))
            except:
                print("Failed to fetch/delete message.")
            return

# Checks

def is_admin():
    async def predicate(ctx):
        admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        return ctx.author.id == 343142603996528641 or (admin_role in ctx.author.roles)
    return commands.check(predicate)

# Custom Converters

def to_lower(arg):
    return arg.lower()

# Commands

@bot.command(name='start_contest')
@is_admin()
async def start_contest(ctx, contest_type: str, days: int, hours: int, minutes: int):
    if contest_type not in contest_types:
        # await ctx.channel.send("Not a valid contest type.")
        return await ctx.channel.send(embed=error_embed("Not a valid contest type."))

    curr_time = datetime.datetime.utcnow()
    end_time = curr_time + datetime.timedelta(days=days, hours=hours, minutes=minutes)

    embed = discord.Embed(title="A New `" + contest_type.upper() + "` Contest Has Started!")
    embed.description = "Ends on " + f'{end_time:%B %d, %Y}' + " at " + f'{end_time: %H:%M:%S%z}' + " (UTC)"
    embed.add_field(
        name="Instructions",
        value=
        '''
        ✅ - Sign up for the contest. (Let's you view all the channels and submit a character.)
        {} - Submit a character. The bot will send instructions and a way to submit a character along with proof.
        '''.format(str(other_emojis["gravestone"])),
        inline=False
    )

    is_contest_active = states["is_contest_active"]
    if is_contest_active:
        # await ctx.channel.send("A contest is already active. This bot only supports 1 contest at a time.")
        return await ctx.channel.send(embed=error_embed("A contest is already active. This bot only supports 1 contest at a time."))

    states["states_read"] = False
    ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=SIGN_UP_CHANNEL)
    post = await ch.send(embed=embed)

    result = await db.new_contest(contest_type, end_time.timestamp(), post.id)
    await post.add_reaction("✅")
    await post.add_reaction(other_emojis["gravestone"])

    await db.clear_leaderboard()

    for key, value in result.items():
        states[key] = value
    states["states_read"] = True

    points_data_manager.parse_data(contest_type)

    await ctx.channel.send(embed=success_embed("Contest started."))

@bot.command(name='force_end_contest')
@is_admin()
async def force_end_contest(ctx):
    if states["is_contest_active"]:
        ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=SIGN_UP_CHANNEL)
        try:
            msg = await ch.fetch_message(states["current_contest_post_id"])
            await msg.delete()
        except:
            print("Failed to retrieve/delete message.")

        result = await db.end_contest()

        states["states_read"] = False
        for key, value in result.items():
            states[key] = value
        states["states_read"] = True

        # await ctx.channel.send("Contest forcefully ended.")
        await ctx.channel.send(embed=success_embed("Contest forcefully ended."))
    else:
        # await ctx.channel.send("No contests are active right now.")
        await ctx.channel.send(embed=error_embed("No contests are active right now."))

@bot.command(name='force_update_leaderboard')
@is_admin()
async def force_update_leaderboard(ctx):
    await leaderboard.update()
    await leaderboard.display()
    await ctx.channel.send(embed=success_embed("Leaderboard updated."))

@bot.command(name='set_points_document')
@is_admin()
async def set_points_document(ctx, contest_type: str, url: str):
    if contest_type not in contest_types:
        return await ctx.channel.send(embed=error_embed("Invalid contest type."))

    await db.set_points_document(contest_type, url)
    await ctx.channel.send(embed=success_embed("Document set for contest type: `" + str(contest_type) + "`"))

# Special Event Loops

async def end_current_contest_loop():
    while True:
        if states["current_contest_end_time"] != -1 and states["states_read"] and states["is_contest_active"]:
            curr_time = datetime.datetime.utcnow().timestamp()
            if curr_time >= float(states["current_contest_end_time"]):
                ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=SIGN_UP_CHANNEL)
                try:
                    msg = await ch.fetch_message(states["current_contest_post_id"])
                    await msg.delete()
                except:
                    print("Failed to retrieve/delete message.")

                result = await db.end_contest()

                states["states_read"] = False
                for key, value in result.items():
                    states[key] = value
                states["states_read"] = True
        await asyncio.sleep(60)

async def update_leaderboard_loop():
    while True:
        if states["is_contest_active"]:
            await leaderboard.update()
            await leaderboard.display()
        await asyncio.sleep(60*60)

bot.loop.create_task(end_current_contest_loop())
bot.loop.create_task(update_leaderboard_loop())

bot.run(TOKEN)
