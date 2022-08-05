from discord import app_commands
import discord

"""
def is_admin():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return (ctx.author == Settings.bot_owner) or (Settings.admin_role in ctx.author.roles)
    return commands.check(predicate)
"""

def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.guild # TODO
    return app_commands.check(predicate)