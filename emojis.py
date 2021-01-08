from discord.emoji import Emoji
from settings import Settings
import discord
import json

class Emojis:
    emojis: dict()

    # ease-of-use pointers to emojis
    check_mark: discord.Emoji
    gravestone: discord.Emoji
    pencil: discord.Emoji

    @staticmethod
    def init(bot: discord.Client, file_path: str):
        with open(file_path) as fin:
            raw_data: dict() = json.loads(fin.read()) # TODO catch and error out file exception

        # load all emojis
        for key, value in raw_data:
            for emoji in bot.emojis:
                if emoji.name == value:
                    Emojis.emojis[key] = str(emoji)
                    break
            # TODO: error out if emoji is not found
        
        # load special emojis
        Emojis.check_mark = Emojis.emojis["check_mark"]
        Emojis.gravestone = Emojis.emojis["gravestone"]
        Emojis.pencil = Emojis.emojis["pencil"]