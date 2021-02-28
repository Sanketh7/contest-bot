import discord
from util import error_embed, success_embed


class Process:
    def __init__(self, bot: discord.Client, user: discord.User, contest_id: int):
        self.bot = bot
        self.user = user
        self.contest_id = contest_id
        self.dead = False

    async def timed_out(self):
        return await self.user.send(embed=error_embed("Uh oh! You did not respond in time so the process timed out."))

    async def cancelled(self):
        self.dead = True
        return await self.user.send(embed=success_embed("Cancelled."))

    async def finished(self):
        self.dead = True
        raise NotImplementedError()

    async def start(self):
        raise NotImplementedError()
