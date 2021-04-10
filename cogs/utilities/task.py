import discord
from discord.ext import tasks, commands


class TaskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_bot_status.start()

    @tasks.loop(minutes=5.0)
    async def update_bot_status(self):
        guilds = len(self.bot.guilds)
        members = sum([len(guild.members) for guild in self.bot.guilds])

        activity = discord.Streaming(
            name=f"{members} users in {guilds} guilds",
            url="https://www.youtube.com/watch?v=ZKaLvJYSj5U",
        )
        await self.bot.change_presence(activity=activity, status=discord.Status.online)


def setup(bot):
    bot.add_cog(TaskCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
