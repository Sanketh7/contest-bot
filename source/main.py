import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import datetime
from tabulate import tabulate

import new_character
import edit_character
import points_data
import leaderboard
from util import success_embed, error_embed, Logger

from database import *
Database.init_database("sqlite:///database.db")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD')
CMD_PREFIX = os.getenv('CMD_PREFIX')
CONTEST_SUBMISSION_CHANNEL = os.getenv('CONTEST_SUBMISSION_CHANNEL')
SIGN_UP_CHANNEL = os.getenv('SIGN_UP_CHANNEL')
IN_CONTEST_ROLE = os.getenv('IN_CONTEST_ROLE')
LEADERBOARD_CHANNEL = os.getenv('LEADERBOARD_CHANNEL')
ADMIN_ROLE_NAME = os.getenv('ADMIN_ROLE_NAME')
BOT_OWNER = int(os.getenv('BOT_OWNER'))
LOG_CHANNEL = os.getenv('LOG_CHANNEL')

bot = commands.Bot(command_prefix=CMD_PREFIX)

player_emojis = {}
other_emojis = {}
player_classes = ['archer', 'assassin', 'huntress', 'knight', 'mystic', 'necromancer', 'ninja', 'paladin', 'priest',
                  'rogue', 'samurai', 'sorcerer', 'trickster', 'warrior', 'wizard', 'bard']

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

schedule_cache: dict = {}

points_data_manager = points_data.PointsDataManager()

leaderboard = leaderboard.Leaderboard(bot, GUILD_ID, LEADERBOARD_CHANNEL)
Logger.init(bot, GUILD_ID, LOG_CHANNEL)

active_processes = set()  # holds user id for users that have an active process going on

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected!')

    meta_data = Database.get_all_metadata()
    if not meta_data:
        Database.reset_meta_data()
    else:
        for key, value in meta_data.items():
            states[key] = value

    schedule = Database.get_scheduled_contest_list()
    if schedule is not None:
        for key, value in schedule.items():
            schedule_cache[key] = value

    states["states_read"] = True

    leaderboard.set_contest_id(states["current_contest_index"])

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
    try:
        user: discord.User = bot.get_user(user_id)
    except:
        return
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
            allowed = user_id not in active_processes
            if allowed:
                active_processes.add(user_id)
                print("Active processes: " + str(len(active_processes)))

                submission = new_character.NewCharacter(bot, user, player_emojis, guild_id, states["current_contest_index"])
                await submission.start_process()
                active_processes.remove(user_id)
                print("Active processes: " + str(len(active_processes)))

                return
            else:
                return await user.send(embed=error_embed("You can only have one process running at a time. Please cancel or complete the other process."))
        else:
            return await user.send(embed=error_embed("You need to sign up before you can submit or edit a character."))

    # pencil for editing submission
    if reaction == "✏" and is_contest_active and is_on_contest_post:
        role = discord.utils.get(bot.get_guild(guild_id).roles, name=IN_CONTEST_ROLE)
        if role in bot.get_guild(guild_id).get_member(user_id).roles:
            allowed = user_id not in active_processes
            if allowed:
                active_processes.add(user_id)

                submission = edit_character.EditCharacter(bot, user, guild_id, CONTEST_SUBMISSION_CHANNEL,
                                                          points_data_manager.keywords, points_data_manager.points_data,
                                                          states["current_contest_index"], states["current_points_document"])
                await submission.start_process()
                active_processes.remove(user_id)
                return
            else:
                return await user.send(embed=error_embed("You can only have one process running at a time. Please cancel or complete the other process."))
        else:
            return await user.send(embed=error_embed("You need to sign up before you can submit or edit a character."))

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
            submission_user_id = await Database.accept_pending_submission(states["current_contest_index"], msg_id, points_data_manager.points_data, user_id)
            try:
                ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=CONTEST_SUBMISSION_CHANNEL)
                submission_user = bot.get_guild(int(GUILD_ID)).get_member(int(submission_user_id))
                msg = await ch.fetch_message(msg_id)
                await msg.delete()
                await submission_user.send(
                    embed=success_embed("Your submission with ID `" + str(msg_id) + "` was accepted!"))
            except:
                print("Failed to fetch/delete message or user doesn't exist.")
            return

        # Reject points/submission
        if reaction == "❌" and ch_id == sub_channel.id:
            submission_user_id = Database.get_user_from_verification(states["current_contest_index"], msg_id)
            pending_data = Database.get_pending_submission_data(states["current_contest_index"], msg_id)
            try:
                ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=CONTEST_SUBMISSION_CHANNEL)
                submission_user = bot.get_guild(int(GUILD_ID)).get_member(int(submission_user_id))
                msg = await ch.fetch_message(msg_id)
                await msg.delete()
                await submission_user.send(embed=error_embed("Your submission with ID `" + str(msg_id) + "` was denied."))
                await Logger.rejected_submission(user_id, submission_user_id, pending_data)
            except:
                print("Failed to fetch/delete message or user doesn't exist.")
            return

# Checks

def is_admin():
    async def predicate(ctx):
        if ctx.guild is None:
            return False
        admin_role = discord.utils.get(ctx.guild.roles, name=ADMIN_ROLE_NAME)
        return ctx.author.id == BOT_OWNER or (admin_role in ctx.author.roles)
    return commands.check(predicate)

def is_bot_owner():
    async def predicate(ctx):
        return ctx.author.id == BOT_OWNER
    return commands.check(predicate)

# Custom Converters

def to_lower(arg):
    return arg.lower()

# Commands

# @bot.command(name='start_contest')
# @is_admin()

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

        result = Database.end_contest()

        states["states_read"] = False
        for key, value in result.items():
            states[key] = value
        states["states_read"] = True

        # await ctx.channel.send("Contest forcefully ended.")
        await ctx.channel.send(embed=success_embed("Contest forcefully ended."))

        await remove_contest_role()
    else:
        # await ctx.channel.send("No contests are active right now.")
        await ctx.channel.send(embed=error_embed("No contests are active right now."))

@bot.command(name='force_refresh_schedule')
@is_admin()
async def force_refresh_schedule(ctx):
    if states["is_contest_active"] or not states["states_read"]:
        return await ctx.channel.send(embed=error_embed("A contest is already active."))

    res = await start_new_contest_from_schedule()
    if res:
        return await ctx.channel.send(embed=success_embed("Contest started."))
    else:
        return await ctx.channel.send(embed=error_embed("No new contest to start."))

@bot.command(name='force_update_leaderboard')
@is_admin()
async def force_update_leaderboard(ctx):
    leaderboard.set_contest_id(states["current_contest_index"])
    await leaderboard.update()
    await leaderboard.display()
    await ctx.channel.send(embed=success_embed("Leaderboard updated."))
    await Logger.force_update_leaderboard(ctx.author)

@bot.command(name='set_points_document')
@is_admin()
async def set_points_document(ctx, contest_type: str, url: str):
    if contest_type not in contest_types:
        return await ctx.channel.send(embed=error_embed("Invalid contest type."))

    Database.set_points_document(contest_type, url)
    await ctx.channel.send(embed=success_embed("Document set for contest type: `" + str(contest_type) + "`"))

@bot.command(name='add_contest')
@is_admin()
async def add_contest(ctx, contest_type: str, start_string: str, end_string: str):
    if contest_type not in contest_types:
        return await ctx.channel.send(embed=error_embed("Invalid contest type."))

    try:
        start_time = datetime.datetime.strptime(start_string, "%m/%d/%y %H:%M")
        end_time = datetime.datetime.strptime(end_string, "%m/%d/%y %H:%M")
    except ValueError:
        return await ctx.channel.send(embed=error_embed("Invalid time input."))

    # start_time = start_time.replace(tzinfo=datetime.timezone.utc).timestamp()
    # end_time = end_time.replace(tzinfo=datetime.timezone.utc).timestamp()
    start_time = start_time.timestamp()
    end_time = end_time.timestamp()
    res = Database.schedule_contest(contest_type, start_time, end_time)
    schedule_cache[res["key"]] = res["data"]

    start_time_str = datetime.datetime.utcfromtimestamp(float(start_time)).strftime("%m/%d/%y %H:%M")
    end_time_str = datetime.datetime.utcfromtimestamp(float(end_time)).strftime("%m/%d/%y %H:%M")

    await ctx.channel.send(embed=success_embed(
        "Contest added. \nStart time (UTC): {}\n End time (UTC): {}".format(start_time_str, end_time_str)
    ))

@bot.command(name='view_schedule')
@is_admin()
async def view_schedule(ctx):
    if not schedule_cache:
        return await ctx.channel.send(embed=error_embed("No upcoming contests."))

    table = []
    for uid, data in schedule_cache.items():
        start_time_str = datetime.datetime.utcfromtimestamp(float(data["start_time"])).strftime("%m/%d/%y %H:%M")
        end_time_str = datetime.datetime.utcfromtimestamp(float(data["end_time"])).strftime("%m/%d/%y %H:%M")
        table.append([str(uid), data["contest_type"], start_time_str, end_time_str])

    embed = discord.Embed(title="Upcoming Contests", color=0x00FF00)
    embed.description = "All times are in UTC."
    table_str = tabulate(table, headers=["ID", "Contest Type", "Start Time", "End Time"])
    embed.add_field(name="Schedule", value="```"+str(table_str)+"```", inline=False)

    await ctx.channel.send(embed=embed)

@bot.command(name='remove_contest')
@is_admin()
async def remove_contest(ctx, contest_id: str):
    Database.remove_contest_with_id(contest_id)
    schedule_cache.pop(contest_id)

    await ctx.channel.send(embed=success_embed("Contest removed (if it existed). \
    Use `+view_schedule` to view scheduled contests."))

@bot.command(name='profile')
async def profile(ctx):
    if not states["is_contest_active"]:
        return await ctx.author.send(embed=error_embed("There are no active contests at the moment."))

    char_embeds = []
    char_data = Database.get_all_characters_from_user(states["current_contest_index"], ctx.author.id)
    embeds_index = 0
    field_count = 0

    char_embeds.append(discord.Embed(title='''Your Characters (page {})'''.format(embeds_index+1)))
    for c in char_data:
        if field_count >= 25:
            embeds_index += 1
            field_count = 0
            char_embeds.append(discord.Embed(title='''Your Characters (page {})'''.format(embeds_index + 1)))

        char_embeds[embeds_index].add_field(
            name=str(c["class"]).capitalize() + "    " + player_emojis[c["class"]] + (
                "  - ACTIVE :white_check_mark:" if c["is_active"] else ""),
            value=
            '''
            **Items/Achievements**: `{}`
            **Points**: `{}`
            '''.format(c["keywords"], c["points"]),
            inline=False
        )
        field_count += 1

    for e in char_embeds:
        await ctx.author.send(embed=e)

@bot.command(name='notify_active_users')
@is_bot_owner()
async def notify_active_users(ctx):
    for user_id in active_processes:
        user = bot.get_user(int(user_id))
        await user.send(embed=error_embed('''
        **STOP**. The bot is being **restarted**. 
        (If you're not in the middle of a process, ignore this.)
        
        Once the bot is back online, **you will have to start this process from the beginning**.
        If you ignore this and continue, your changes will likely not be saved.
        
        Sorry for the inconvenience.
        '''))
    await ctx.author.send(embed=success_embed("Notified " + str(len(active_processes)) + " users."))

async def start_contest(contest_type: str, end_time_num: float):
    if contest_type not in contest_types:
        return

    end_time = datetime.datetime.utcfromtimestamp(end_time_num)

    embed = discord.Embed(title="A New `" + contest_type.upper() + "` Contest Has Started!")
    embed.description = "Ends on " + f'{end_time:%B %d, %Y}' + " at " + f'{end_time: %H:%M}' + " (UTC)"
    embed.add_field(
        name="Instructions",
        value=
        '''
        ✅ - Sign up for the contest. (Let's you view all the channels and submit.)
        {} - Start a new character. Completing this will STOP your previous character (so you can't edit it anymore).
        ✏ - Edit a character. This will add items/achievements to your current character.
        
        Use the command `+profile` to view all your characters for this contest.
        '''.format(str(other_emojis["gravestone"])),
        inline=False
    )

    is_contest_active = states["is_contest_active"]
    if is_contest_active:
        return

    states["states_read"] = False
    ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=SIGN_UP_CHANNEL)
    post = await ch.send(embed=embed)

    result = Database.new_contest(contest_type, end_time_num, post.id)
    await post.add_reaction("✅")
    await post.add_reaction(other_emojis["gravestone"])
    await post.add_reaction("✏")

    # Database.clear_leaderboard()

    for key, value in result.items():
        states[key] = value
    states["states_read"] = True

    points_data_manager.parse_data(contest_type)

async def remove_contest_role():
    role = discord.utils.get(bot.get_guild(int(GUILD_ID)).roles, name=IN_CONTEST_ROLE)
    members = role.members
    for member in members:
        await member.remove_roles(role)

async def start_new_contest_from_schedule():
    if not states["is_contest_active"] and states["states_read"]:
        curr_time = datetime.datetime.utcnow().timestamp()
        if schedule_cache:
            for uid, contest_data in schedule_cache.items():
                if float(contest_data["start_time"]) <= curr_time <= float(contest_data["end_time"]):
                    await start_contest(contest_data["contest_type"], float(contest_data["end_time"]))
                    Database.remove_contest_with_id(str(uid))
                    schedule_cache.pop(str(uid))
                    return True
    return False

# Special Event Loops

async def contest_schedule_loop():
    while True:
        # end current contest if it's done
        if states["current_contest_end_time"] != -1 and states["states_read"] and states["is_contest_active"]:
            curr_time = datetime.datetime.utcnow().timestamp()
            if curr_time >= float(states["current_contest_end_time"]):
                ch = discord.utils.get(bot.get_guild(int(GUILD_ID)).text_channels, name=SIGN_UP_CHANNEL)
                try:
                    msg = await ch.fetch_message(states["current_contest_post_id"])
                    await msg.delete()
                except:
                    print("Failed to retrieve/delete message.")

                result = Database.end_contest()

                states["states_read"] = False
                for key, value in result.items():
                    states[key] = value
                states["states_read"] = True

                await remove_contest_role()

        # start new contest if it is time to do so
        elif not states["is_contest_active"] and states["states_read"]:
            await start_new_contest_from_schedule()

        await asyncio.sleep(60)

async def update_leaderboard_loop():
    while True:
        if states["is_contest_active"]:
            leaderboard.set_contest_id(states["current_contest_index"])
            await leaderboard.update()
            await leaderboard.display()
        await asyncio.sleep(60*10)

bot.loop.create_task(contest_schedule_loop())
bot.loop.create_task(update_leaderboard_loop())

bot.run(TOKEN)
