from discord import app_commands
import discord
import env
import datetime

# TODO: add permission checks
class Schedule(app_commands.Group):
    """Manage the contest schedule."""

    @app_commands.guild_only()
    async def add_contest(self, interaction: discord.Interaction, start_time: str, end_time: str) -> None:
        """Add a contest. Time values use the format \"DD/MM/YY HH:MM\""""
        try:
            start_time = datetime.strptime(start_time, "%d/%m/%y %H:%M")
            end_time = datetime.strptime(end_time, "%d/%m/%y %H:%M")
        except ValueError:
            return await 

    @app_commands.guild_only()
    async def remove_contest(self):
        pass

    @app_commands.guild_only()
    async def view(self):
        pass

    @app_commands.guild_only()
    async def refresh(self):
        pass

    @app_commands.guild_only()
    async def end_contest(self):
        pass


def setup(tree: app_commands.CommandTree):
    tree.add_command(Schedule(), guild=env.DISCORD_TOKEN)
