import discord
import json

class Emojis:
    roles: dict()

    # ease-of-use pointers to roles
    admin: discord.Role
    moderator: discord.Role
    contest_staff: discord.Role

    @staticmethod
    def init(bot: discord.Client, file_path: str):
        with open(file_path) as fin:
            raw_data: dict() = json.loads(fin.read()) # TODO catch and error out file exception

        # load all roles
        for key, value in raw_data:
            role = discord.utils.get(bot.get_guild(guild_id))
            for role in :
                if emoji.name == value:
                    Emojis.emojis[key] = str(emoji)
                    break
            # TODO: error out if emoji is not found
        
        # load special emojis
        Emojis.check_mark = Emojis.emojis["check_mark"]
        Emojis.gravestone = Emojis.emojis["gravestone"]
        Emojis.pencil = Emojis.emojis["pencil"]