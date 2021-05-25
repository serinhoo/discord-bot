import discord
import pymongo
from discord.ext import commands

import settings

default_extensions = [
    "cogs.base",
    "cogs.management",
    "cogs.admin.administrative",
    "cogs.admin.notification",
    "cogs.utilities.utility",
    "cogs.utilities.task",
    "cogs.fun.word_cloud",
]


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mongo = pymongo.MongoClient(settings.discord_mongo_uri)

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_ready(self):
        print(f"\n---\nNazwa bota: {bot.user.name} (ID: {bot.user.id})")
        print(f"Wersja discord.py: {discord.__version__}")
        print(
            f"Invite link: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot\n---\n"
        )

        activity = discord.Streaming(
            name="prefix: ^", url="https://www.youtube.com/watch?v=ZKaLvJYSj5U"
        )
        await bot.change_presence(activity=activity, status=discord.Status.online)

        print("------------ EXTENSIONS ------------")
        for extension in default_extensions:
            self.load_extension(extension)
        print("-------------- GUILDS --------------")
        for guild in self.guilds:
            print(
                f"[{guild.id}] {guild.name} ({guild.owner.name}#{guild.owner.discriminator})"
            )
        print("------------- FINISHED -------------")


def get_command_prefix(bot, message):
    # Prefixy na które bot odpowiada
    prefixes = ["^", "*"]
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = MyBot(
    command_prefix=get_command_prefix, intents=discord.Intents.all(), help_command=None
)

bot.run(settings.discord_token)
