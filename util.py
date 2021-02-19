import discord
from settings import Settings
import typing


def error_embed(text: str) -> discord.Embed:
    embed = discord.Embed(color=0xFF0000)
    embed.description = str(Settings.reject_emoji) + " " + text
    return embed


def success_embed(text: str) -> discord.Embed:
    embed = discord.Embed(color=0x00FF00)
    embed.description = str(Settings.accept_emoji) + " " + text
    return embed


def character_embed(title: str, rotmg_class: str, keywords: list[str], points: int) -> discord.Embed:
    keywords_str = str(keywords) if len(keywords) > 0 else "**NONE**"

    embed = discord.Embed(title=title)
    embed.add_field(
        name="Class:", value="**{}**".format(rotmg_class), inline=False)
    if len(keywords_str) >= 800:
        curr_arr = []
        curr_len = 3
        counter = 1
        for k in keywords:
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
        name="Points:", value="**{}**".format(points), inline=False)

    return embed
