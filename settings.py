import discord
import json
import typing


class Settings:
    guild: discord.Guild

    admin_role: discord.Role
    moderator_role: discord.Role
    contest_staff_role: discord.Role

    submission_channel: discord.TextChannel

    accept_emoji: discord.Emoji
    reject_emoji: discord.Emoji
    edit_emoji: discord.Emoji
    grave_emoji: discord.Emoji

    rotmg_classes: list[str] = []
    rotmg_class_emojis: dict[str, discord.Emoji] = dict()

    points_data_file: str
    points_data_url: str

    @staticmethod
    def reload_all(bot: discord.Client) -> None:
        Settings.reload_roles()

    @staticmethod
    def reload_roles() -> None:
        data = json.loads("settings/roles.json")
        Settings.admin = discord.utils.get(
            Settings.guild.roles, name=data["admin"])
        Settings.moderator = discord.utils.get(
            Settings.guild.roles, name=data["admin"])
        Settings.contest_staff = discord.utils.get(
            Settings.guild.roles, name=data["admin"])

    @staticmethod
    def reload_emojis() -> None:
        data = json.loads("settings/emojis.json")
        for emoji in Settings.guild.emojis:
            if emoji == data["accept_emoji"]:
                Settings.accept_emoji = emoji
            elif emoji == data["reject_emoji"]:
                Settings.reject_emoji = emoji
            elif emoji == data["edit_emoji"]:
                Settings.edit_emoji = emoji
            elif emoji == data["grave_emoji"]:
                Settings.grave_emoji = emoji
            else:
                # TODO: handle player classes
                pass
