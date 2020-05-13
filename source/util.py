import discord


def error_embed(text: str):
    embed = discord.Embed(color=0xFF0000)
    embed.description = "❌ " + text
    return embed


def success_embed(text: str):
    embed = discord.Embed(color=0x00FF00)
    embed.description = "✅ " + text
    return embed

