from gc import get_referents
import discord
import logging
from typing import List

from discord.ext.commands.converter import Greedy
from settings import Settings
from database import Submission

COLOR_RED = 0xFF0000
COLOR_GREEN = 0x00FF00
COLOR_BLUE = 0x0000FF

# logs events to the server's logging channel
class Logger:
    @staticmethod
    async def send_log(text: str, embed_color: int, image_url=None):
        ch: discord.TextChannel = Settings.log_channel
        embed = discord.Embed(color=embed_color)
        embed.description = text
        if image_url:
            embed.set_image(url=image_url)
        return await ch.send(embed=embed)

    @staticmethod
    async def updated_leaderboard(user: discord.User):
        text = "{} updated the leaderboard.".format(user.mention)
        return await Logger.send_log(text, COLOR_BLUE)

    @staticmethod
    async def added_keywords(staff_user: discord.User, player_user: discord.User, character_id: int, keywords_added: List[str]):
        text = '''
        {} added these keywords to {}'s character (ID: `{}`):
        `{}`
        '''.format(staff_user.mention, player_user.mention, character_id, str(keywords_added))
        return await Logger.send_log(text, COLOR_GREEN)

    @staticmethod
    async def removed_keywords(staff_user: discord.User, player_user: discord.User, character_id: int, keywords_removed: List[str]):
        text = '''
        {} removed these keywords to {}'s character (ID: `{}`):
        `{}`
        '''.format(staff_user.mention, player_user.mention, character_id, str(keywords_removed))
        return await Logger.send_log(text, COLOR_GREEN)

    @staticmethod
    async def accepted_submission(staff_user: discord.User, submission: Submission):
        try:
            player_user = Settings.guild.get_member(
                submission.character.user_id)
        except Exception as e:
            logging.error("Failed to get user {}\n".format(
                submission.character.user_id) + str(e))
            return

        text = '''
        {} accepted {}'s submission:
        Class: {}
        Items/Achievements: `{}`
        Points: {}
        Proof: [image]({})
        '''.format(staff_user.mention, player_user.mention, submission.character.rotmg_class,
                   str(submission.keywords), submission.points, submission.img_url)

        return await Logger.send_log(text, COLOR_GREEN, submission.img_url)

    @staticmethod
    async def rejected_submission(staff_user: discord.User, submission: Submission):
        try:
            player_user = Settings.guild.get_user(submission.character.user_id)
        except Exception as e:
            logging.error("Failed to get user {}\n".format(
                submission.character.user_id) + str(e))
            return

        text = '''
        {} rejected {}'s submission:
        Class: {}
        Items/Achievements: `{}`
        Points: {}
        Proof: [image]({})
        '''.format(staff_user.mention, player_user.mention, submission.character.rotmg_class,
                   str(submission.keywords), submission.points, submission.img_url)

        return await Logger.send_log(text, COLOR_RED, submission.img_url)

    @staticmethod
    async def banned_user(staff_user: discord.Member, target_user: discord.Member):
        text = f'{staff_user.mention} banned {target_user.mention} from participating in the contest.'
        return await Logger.send_log(text, COLOR_RED)

    @staticmethod
    async def unbanned_user(staff_user: discord.Member, target_user: discord.Member):
        text = f'{staff_user.mention} unbanned {target_user.mention} from participating in the contest.'
        return await Logger.send_log(text, COLOR_GREEN)
