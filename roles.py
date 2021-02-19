import discord
import json


class Roles:
    admin: discord.Role
    moderator: discord.Role
    contest_staff: discord.Role

    @staticmethod
    def reload(bot: discord.Client):
        data = json.loads("settings/roles.json")
        Roles.admin = discord.utils.get(bot.get_guild(
        Roles.moderator=data["moderator"]
        Roles.contest_staff=data["contest_staff"]
