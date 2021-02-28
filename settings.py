import discord
import json
import typing


class Settings:
    bot_owner: discord.User

    guild: discord.Guild

    admin_role: discord.Role
    moderator_role: discord.Role
    contest_staff_role: discord.Role
    contestant_role: discord.Role

    sign_up_channel: discord.TextChannel
    submission_channel: discord.TextChannel
    leaderboard_channel: discord.TextChannel
    log_channel: discord.TextChannel

    accept_emoji: discord.Emoji
    reject_emoji: discord.Emoji
    edit_emoji: discord.Emoji
    grave_emoji: discord.Emoji

    rotmg_classes: list[str] = []
    rotmg_class_emojis: dict[str, discord.Emoji] = dict()

    points_data_file: str
    points_reference_url: str

    @staticmethod
    def reload_all(bot: discord.Client) -> None:
        Settings.reload_bot_owner(bot)
        Settings.reload_guild(bot)
        Settings.reload_roles()
        Settings.reload_rotmg_classes()
        Settings.reload_emojis(bot)
        Settings.reload_channels()
        Settings.reload_points_data()

    @staticmethod
    def reload_guild(bot: discord.Client) -> None:
        data = json.loads("settings.json")
        Settings.guild = bot.get_guild(data.guild)

    @staticmethod
    def reload_bot_owner(bot: discord.Client) -> None:
        data = json.loads("settings.json")
        Settings.bot_owner = bot.get_user(data.bot_owner)

    @staticmethod
    def reload_roles() -> None:
        assert(Settings.guild)
        data = json.loads("settings.json")
        Settings.admin_role = discord.utils.get(
            Settings.guild.roles, name=data.roles.admin)
        Settings.moderator_role = discord.utils.get(
            Settings.guild.roles, name=data.roles.moderator)
        Settings.contest_staff_role = discord.utils.get(
            Settings.guild.roles, name=data.roles.contest_staff)
        Settings.contestant_role = discord.utils.get(
            Settings.guild.roles, name=data.roles.contestant)

    @staticmethod
    def reload_rotmg_classes() -> None:
        data = json.loads("settings.json")
        Settings.rotmg_classes = list(data.rotmg_classes)

    @staticmethod
    def reload_emojis(bot: discord.Client) -> None:
        data = json.loads("settings.json")
        Settings.accept_emoji = discord.utils.get(
            bot.emojis, name=data.emojis.accept)
        Settings.reject_emoji = discord.utils.get(
            bot.emojis, name=data.emojis.reject)
        Settings.edit_emoji = discord.utils.get(
            bot.emojis, name=data.emojis.edit)
        Settings.grave_emoji = discord.utils.get(
            bot.emojis, name=data.emojis.grave)

        assert(Settings.rotmg_classes)
        for rotmg_class in Settings.rotmg_classes:
            Settings.rotmg_class_emojis[rotmg_class] = discord.utils.get(
                bot.emojis, name=data.emojis[rotmg_class])

    @staticmethod
    def reload_channels() -> None:
        data = json.loads("settings.json")
        Settings.sign_up_channel = discord.utils.get(
            Settings.guild.text_channels, name=data.channels.sign_up)
        Settings.submission_channel = discord.utils.get(
            Settings.guild.text_channels, name=data.channels.submission)
        Settings.leaderboard_channel = discord.utils.get(
            Settings.guild.text_channels, name=data.channels.leaderboard)
        Settings.log_channel = discord.utils.get(
            Settings.guild.text_channels, name=data.channels.log)

    @staticmethod
    def reload_points_data() -> None:
        data = json.loads("settings.json")
        Settings.points_data_file = data.points_data_file
        Settings.poins_reference_url = data.points_reference_url
