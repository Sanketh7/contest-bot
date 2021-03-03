import discord
import asyncio
from settings import Settings
from enum import Enum
import mimetypes


class Response(Enum):
    ACCEPT = 1
    REJECT = 2
    TIMEDOUT = 3
    EDIT = 4


async def yes_no_react_task(bot: discord.Client, msg: discord.Message, user: discord.User, timeout: float) -> Response:
    valid_reacts = [Settings.accept_emoji, Settings.reject_emoji]

    async def do_reacts(msg: discord.Message):
        for e in valid_reacts:
            await msg.add_reaction(e)

    def check(react: discord.Reaction, user_got: discord.User):
        return user_got.id == user.id and (str(react) in valid_reacts)

    task = asyncio.create_task(do_reacts(msg))
    await asyncio.sleep(0)

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        await task
        return Response.TIMEDOUT
    else:
        await task
        if str(reaction) == Settings.reject_emoji:
            return Response.REJECT
        return Response.ACCEPT


async def yes_no_edit_react_task(bot: discord.Client, msg: discord.Message, user: discord.User, timeout: float):
    valid_reacts = [Settings.accept_emoji,
                    Settings.edit_emoji, Settings.reject_emoji]

    async def do_reacts(msg: discord.Message):
        for e in valid_reacts:
            await msg.add_reaction(e)

    def check(react: discord.Reaction, user_got: discord.User):
        return user_got.id == user.id and str(react) in valid_reacts

    task = asyncio.create_task(do_reacts(msg))
    await asyncio.sleep(0)

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        await task
        return Response.TIMEDOUT
    else:
        await task
        if str(reaction) == Settings.reject_emoji:
            return Response.REJECT
        elif str(reaction) == Settings.edit_emoji:
            return Response.EDIT
        return Response.ACCEPT


async def rotmg_class_select_task(bot: discord.Client, msg: discord.Message, user: discord.User, timeout: float):
    # note: map reacts to strings since reject emoji is a string
    valid_reacts = list(map(str, Settings.rotmg_class_emojis.values())) + \
        [Settings.reject_emoji]

    async def do_reacts(msg: discord.Message):
        for e in valid_reacts:
            await msg.add_reaction(e)

    def check(react: discord.Reaction, user_got: discord.User):
        return user_got.id == user.id and str(react) in valid_reacts

    task = asyncio.create_task(do_reacts(msg))
    await asyncio.sleep(0)

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        await task
        return Response.TIMEDOUT
    else:
        await task
        if str(reaction) == Settings.reject_emoji:
            return Response.REJECT
        for name, emoji in Settings.rotmg_class_emojis.items():
            if str(emoji) == str(reaction):
                return name


async def proof_upload_task(bot: discord.Client, msg: discord.Message, user: discord.User, timeout: float):
    await msg.add_reaction(Settings.reject_emoji)

    def is_url_image(url: str):
        mimetype, _ = mimetypes.guess_type(url)
        return (mimetype and mimetype.startswith('image'))

    def check_msg(m: discord.Message):
        valid_attachment = len(
            m.attachments) > 0 and m.attachments[0].url and is_url_image(m.attachments[0].url)
        return m.author.id == user.id and valid_attachment

    def check_react(react: discord.Reaction, user_got: discord.User):
        return user_got.id == user.id and str(react) == Settings.reject_emoji

    try:
        tasks = [asyncio.create_task(bot.wait_for('message', timeout=timeout, check=check_msg)),
                 asyncio.create_task(bot.wait_for('reaction_add', timeout=timeout, check=check_react))]

        for future in asyncio.as_completed(tasks):
            res = await future

            if type(res) is tuple and type(res[0]) is discord.Reaction:
                return Response.REJECT
            elif type(res) is discord.Message:
                return res.attachments[0].url

            for task in tasks:
                task.cancel()

            return
    except asyncio.TimeoutError:
        return Response.TIMEDOUT


async def keyword_input_task(bot: discord.Client, msg: discord.Message, user: discord.User, timeout: float):
    await msg.add_reaction(Settings.reject_emoji)

    def check_msg(m: discord.Message):
        return len(m.content) > 0 and not m.guild and m.author.id == user.id

    def check_react(react: discord.Reaction, user_got: discord.User):
        return user_got.id == user.id and str(react) == Settings.reject_emoji

    try:
        tasks = [
            asyncio.create_task(bot.wait_for(
                'message', timeout=timeout, check=check_msg)),
            asyncio.create_task(bot.wait_for(
                'reaction_add', timeout=timeout, check=check_react))
        ]

        for future in asyncio.as_completed(tasks):
            res = await future

            if type(res) is tuple and type(res[0]) is discord.Reaction:
                return Response.REJECT
            elif type(res) is discord.Message:
                return res.content

            for task in tasks:
                task.cancel()

            return
    except asyncio.TimeoutError:
        return Response.TIMEDOUT
