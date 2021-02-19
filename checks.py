import discord
from discord.ext import commands
from roles import Roles


def is_admin():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return Roles.admin in ctx.author.roles  # TODO: check for bot owner
    return commands.check(predicate)

# TODO: is_bot_owner()


def is_contest_staff():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return Roles.contest_staff in ctx.author.roles  # TODO: check for bot owner
    return commands.check(predicate)
