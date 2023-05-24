from os import stat
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
    top_active_chars: List[Character]

    # refreshes top_chars using the database
    @staticmethod
    async def update():
        contest_id = DB.get_current_contest_id()
        assert(contest_id)
        Leaderboard.top_chars = DB.get_top_characters(
            contest_id, Leaderboard.NUM_TABLE_LIMIT*Leaderboard.NUM_CHARS_PER_TABLE_LIMIT)
        Leaderboard.top_active_chars = DB.get_top_active_characters(
            contest_id, Leaderboard.NUM_TABLE_LIMIT*Leaderboard.NUM_CHARS_PER_TABLE_LIMIT)

    @staticmethod
    async def display(bot: discord.Client):
        await Leaderboard.clean(bot)
        await Leaderboard.display_top_chars()
        await Leaderboard.display_top_active_chars()

    # removes previous bot messages in the leaderboard channel
    @staticmethod
    async def clean(bot: discord.Client):
        ch: discord.TextChannel = Settings.leaderboard_channel
        try:
            async for message in ch.history(limit=100):
                if message.author == bot.user:
                    await message.delete()
        except Exception as e:
            logging.error("Failed to clear old leaderboards.\n" + str(e))

    # displays the leaderboard in the leaderboard channel
    # note that this only shows 5 tables with 10 characters on each table
    # due to discord api rate-limiting 
    @staticmethod
    async def display_top_chars():
        assert(Leaderboard.top_chars)

        place = 0
        table_ind = 0  # limit of 5 tables
        player_count = 0  # limit of 10 chars per table
        prev_points = float("inf")
        table_list = [[] for i in range(0, 5)]

        guild = Settings.guild

        for character in Leaderboard.top_chars:
            if character.points == 0:
                break

            player = guild.get_member(character.user_id)
            if not player:
                continue
            ign = player.display_name
            # truncate to 15 + ellipses if needed
            if len(ign) > 18:
                ign = ign[:15] + "..."

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

        embed = discord.Embed(title="Top Characters", color=0x00FF00)
        embed.description = "Updated every 5 minutes during a contest."

        for table in table_list:
            if not table:
                break
            table_str = tabulate(
                table, headers=["Rank", "Player", "Points", "Class", "Active?"])
            embed.add_field(name='\u200b', value="```{}```".format(
                table_str), inline=False)

        ch: discord.TextChannel = Settings.leaderboard_channel
        return await ch.send(embed=embed)

    # same as above except only displays active characters
    @staticmethod
    async def display_top_active_chars():
        assert(Leaderboard.top_active_chars)

        place = 0
        table_ind = 0  # limit of 5 tables
        player_count = 0  # limit of 10 chars per table
        prev_points = float("inf")
        table_list = [[] for i in range(0, 5)]

        guild = Settings.guild

        for character in Leaderboard.top_active_chars:
            if character.points == 0: # don't display empty characters
                break

            player = guild.get_member(character.user_id)
            if not player:
                continue
            ign = player.display_name
            # truncate to 15 + ellipses if needed
            if len(ign) > 18:
                ign = ign[:15] + "..."

            if player_count >= Leaderboard.NUM_CHARS_PER_TABLE_LIMIT:  # maxed out players for this table
                table_ind += 1
                player_count = 0
            if table_ind >= Leaderboard.NUM_TABLE_LIMIT:  # maxed out tables
                break
            player_count += 1

            if character.points >= prev_points:  # continue with same place
                table_list[table_ind].append(
                    [None, ign, character.points, character.rotmg_class]
                )
            else: # go to the next place
                place += 1
                table_list[table_ind].append(
                    [place, ign, character.points, character.rotmg_class]
                )

        embed = discord.Embed(title="Top Active Characters", color=0x00FF00)
        embed.description = "Updated every 5 minutes during a contest."

        for table in table_list:
            if not table:
                break
            table_str = tabulate(
                table, headers=["Rank", "Player", "Points", "Class"])
            embed.add_field(name='\u200b', value="```{}```".format(
                table_str), inline=False)

        ch: discord.TextChannel = Settings.leaderboard_channel
        return await ch.send(embed=embed)