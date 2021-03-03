import discord
from discord.ext import commands
from settings import Settings


def is_admin():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return (ctx.author == Settings.bot_owner) or (Settings.admin_role in ctx.author.roles)
    return commands.check(predicate)


def is_bot_owner():
    async def predicate(ctx):
        return ctx.author == Settings.bot_owner
    return commands.check(predicate)


def is_contest_staff():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return (ctx.author == Settings.bot_owner) or (Settings.contest_staff_role in ctx.author.roles)
    return commands.check(predicate)
