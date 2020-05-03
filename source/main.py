import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import datetime

import source.database as db
db.init_database()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CMD_PREFIX = os.getenv('CMD_PREFIX')
CONTEST_SUBMISSION_CHANNEL = os.getenv('CONTEST_SUBMISSION_CHANNEL')
SIGN_UP_CHANNEL = os.getenv('SIGN_UP_CHANNEL')

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
    "states_read": False
}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected!')

    meta_data = await db.get_all_metadata()
    for key, value in meta_data.items():
        states[key] = value
    states["states_read"] = True

    for emoji in bot.emojis:
        for player_class in player_classes:
            if emoji.name == os.getenv("EMOJI_" + player_class.upper()):
                player_emojis[player_class] = str(emoji)
        if emoji.name == os.getenv("EMOJI_GRAVESTONE"):
            other_emojis["gravestone"] = str(emoji)

@bot.event
async def on_message(message: discord.Message):

    if message.author != bot.user:
        if message.guild is None: # in DM

            if len(message.attachments) > 0:
                img_url = message.attachments[0].url
                if img_url is not None:
                    ch = discord.utils.get(bot.get_guild(int(GUILD)).text_channels, name=CONTEST_SUBMISSION_CHANNEL)
                    await ch.send(img_url)

    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    reaction = str(payload.emoji)
    msg_id = payload.message_id
    ch_id = payload.channel_id
    user_id = payload.user_id
    user: discord.User = bot.get_user(user_id)
    if user == bot.user:
        return
    guid_id = payload.guild_id

    is_contest_active = states["is_contest_active"]
    contest_post_id = states["current_contest_post_id"]
    contest_index = states["current_contest_index"]
    is_on_contest_post = contest_post_id == msg_id

    # gravestone for creating a submission
    if reaction == other_emojis["gravestone"] and is_contest_active and is_on_contest_post:

        # send class select dialog
        embed = discord.Embed(title="Class Selection.")
        embed.add_field(
            name="Note",
            value=
            '''
            **This will ERASE previous submissions for this contest, regardless of class.**
            ''',
            inline=False
        )
        # TODO: add owner ping
        embed.add_field(
            name="Instructions",
            value=
            '''
            React to one of the class reactions below to select a class for this contest.
            After selecting a class you should see a dialog which allows you to submit a screenshot.
            **Contact @vexor if you do not see the dialog after selecting a class.**
            '''
        )

        dm_msg = await user.send(embed=embed)
        for e in player_emojis.values():
            await dm_msg.add_reaction(e)

        await db.set_user_class_select_dialog(contest_index, user_id, dm_msg.id)

        return

    # user selected player class in class select dialog (dm)
    current_class_select_dialog = await db.get_class_select_dialog(contest_index, user_id)
    is_on_class_select_dialog = (current_class_select_dialog is not None) and (current_class_select_dialog == msg_id)

    if reaction in player_emojis.values() and is_contest_active and is_on_class_select_dialog:

        # create submission dialog
        class_name = next((name for name, emoji_str in player_emojis.items() if emoji_str == reaction), None)
        embed = discord.Embed(title="Submission for class `" + class_name + "`.")
        embed.add_field(
            name="Instructions",
            value=
            '''
            Send a message with a screenshot **in this DM** as specified in the contest rules. 
            Click the **plus button** next to where you type a message to attach an image \
            or **copy and paste** and image into the message box.
            If you do not use either of the methods above, the bot **cannot** detect it.
            ''',
            inline=False
        )

        dm_msg = await user.send(embed=embed)
        await db.set_user_submission_dialog(contest_index, user_id, dm_msg.id)
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
        ctx.channel.send("Not a valid contest type.")
        return

    embed = discord.Embed(title="A New `" + contest_type.upper() + "` Contest Has Started!")
    embed.add_field(name="How to Join", value="idk", inline=False)

    is_contest_active = states["is_contest_active"]
    if is_contest_active:
        await ctx.channel.send("A contest is already active. This bot only supports 1 contest at a time.")
        return

    states["states_read"] = False
    ch = discord.utils.get(bot.get_guild(int(GUILD)).text_channels, name=SIGN_UP_CHANNEL)
    post = await ch.send(embed=embed)

    curr_time = datetime.datetime.utcnow()
    end_time = curr_time + datetime.timedelta(days=days, hours=hours, minutes=minutes)
    result = await db.new_contest(contest_type, end_time.timestamp(), post.id)
    await post.add_reaction(other_emojis["gravestone"])

    for key, value in result.items():
        states[key] = value
    states["states_read"] = True

@bot.command(name='force_end_contest')
@is_admin()
async def force_end_contest(ctx):
    if states["is_contest_active"]:
        ch = discord.utils.get(bot.get_guild(int(GUILD)).text_channels, name=SIGN_UP_CHANNEL)
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
    else:
        ctx.channel.send("No contests are active right now.")

# Special Event Loops

async def end_current_contest_loop():
    while True:
        if states["current_contest_end_time"] != -1 and states["states_read"] and states["is_contest_active"]:
            curr_time = datetime.datetime.utcnow().timestamp()
            print(curr_time >= float(states["current_contest_end_time"]))
            if curr_time >= float(states["current_contest_end_time"]):
                ch = discord.utils.get(bot.get_guild(int(GUILD)).text_channels, name=SIGN_UP_CHANNEL)
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

bot.loop.create_task(end_current_contest_loop())

bot.run(TOKEN)
