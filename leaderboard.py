import discord
from typing import List
import logging
from database import DB, Contest, Character
from tabulate import tabulate
from settings import Settings


# displays and maintains a leaderboard of top characters of the contest
class Leaderboard:
    NUM_TABLE_LIMIT = 5
    NUM_CHARS_PER_TABLE_LIMIT = 10

    top_chars: List[Character]

    # refreshes top_chars using the database
    @staticmethod
    async def update():
        contest_id = DB.get_current_contest_id()
        assert(contest_id)
        Leaderboard.top_chars = DB.get_top_characters(
            contest_id, Leaderboard.NUM_TABLE_LIMIT*Leaderboard.NUM_CHARS_PER_TABLE_LIMIT)

    # displays the leaderboard in the leaderboard channel
    # note that this only shows 5 tables with 10 characters on each table
    # due to discord api rate-limiting 
    @staticmethod
    async def display(bot: discord.Client):
        assert(Leaderboard.top_chars)

        place = 0
        table_ind = 0  # limit of 5 tables
        player_count = 0  # limit of 10 chars per table
        prev_points = float("inf")
        table_list = [[] for i in range(0, 5)]

        guild = Settings.guild

        for character in Leaderboard.top_chars:
            player = guild.get_member(character.user_id)
            if not player:
                continue
            ign = player.display_name

            if player_count >= Leaderboard.NUM_CHARS_PER_TABLE_LIMIT:  # maxed out players for this table
                table_ind += 1
                player_count = 0
            if table_ind >= Leaderboard.NUM_TABLE_LIMIT:  # maxed out tables
                break
            player_count += 1

            if character.points >= prev_points:  # continue with same place
                table_list[table_ind].append(
                    [None, ign, character.points, character.rotmg_class, str(
                        Settings.accept_emoji) if character.is_active else " "]
                )
            else:
                place += 1
                table_list[table_ind].append(
                    [place, ign, character.points, character.rotmg_class, str(
                        Settings.accept_emoji) if character.is_active else " "]
                )

        embed = discord.Embed(title="Leaderboard", color=0x00FF00)
        embed.description = "Updated every 10 minutes during a contest."

        for table in table_list:
            if not table:
                break
            table_str = tabulate(
                table, headers=["Rank", "Player", "Points", "Class", "Active?"])
            embed.add_field(name='\u200b', value="```{}```".format(
                table_str), inline=False)

        ch: discord.TextChannel = Settings.leaderboard_channel

        try:
            async for message in ch.history(limit=100):
                if message.author == bot.user:
                    await message.delete()
        except Exception as e:
            logging.error("Failed to clear old leaderboards.\n" + str(e))

        return await ch.send(embed=embed)
