import discord
from settings import Settings
import typing
from datetime import datetime
from database import Character


def error_embed(text: str) -> discord.Embed:
    embed = discord.Embed(color=0xFF0000)
    embed.description = str(Settings.reject_emoji) + " " + text
    return embed


def success_embed(text: str) -> discord.Embed:
    embed = discord.Embed(color=0x00FF00)
    embed.description = str(Settings.accept_emoji) + " " + text
    return embed


def character_embed(character: Character) -> discord.Embed:
    keywords_str = str(list(character.keywords)) if len(
        list(character.keywords)) > 0 else "**NONE**"

    title = "{}\t{}\t{}\t(ID: {})".format(
        character.rotmg_class.capitalize(),
        str(Settings.rotmg_class_emojis[character.rotmg_class]),
        "ACTIVE " + str(Settings.accept_emoji) if character.is_active else "",
        str(character.id)
    )
    embed = discord.Embed(title=title)

    if len(keywords_str) >= 800:
        curr_arr = []
        curr_len = 3
        counter = 1
        for k in character.keywords:
            curr_len += len(str(k)) + 3
            if curr_len >= 800:
                embed.add_field(
                    name="More Items/Achievements:" if counter > 1 else "Items/Achievements:",
                    value="`{}`".format(curr_arr),
                    inline=False
                )
                curr_len = 0
                curr_arr = []
                counter += 1
            curr_arr.append(k)
        if len(curr_arr) > 0:
            embed.add_field(
                name="More Items/Achievements:" if counter > 1 else "Items/Achievements:",
                value="`{}`".format(curr_arr),
                inline=False
            )
    else:
        embed.add_field(name="Items/Achievements:",
                        value="`{}`".format(keywords_str), inline=False)

    embed.add_field(
        name="Points:", value="**{}**".format(character.points), inline=False)

    return embed


def contest_post_embed(end_time: datetime):
    embed = discord.Embed(title="A New PPE Contest Has Started!")
    embed.description = "Ends on {} at {} (UTC)".format(
        f'{end_time:%B %d, %Y}', f'{end_time: %H:%M}')
    embed.add_field(
        name="Instructions",
        value='''
        {} - Sign up for the contest, (Let's you view all the channels and submit.)
        {} - Start a new character. Completing this will STOP your previous character (so you can't edit it anymore).
        {} - Edit a character. This will add items/achievements to your current character.

        Use the command `+profile` to view all your characters for this contest.
        '''.format(Settings.accept_emoji, Settings.grave_emoji, Settings.edit_emoji), inline=False)
    return embed


def user_busy_embed():
    return error_embed("You already have a process running. Please end that process first.")
