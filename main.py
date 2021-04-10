import datetime
import traceback

import settings
import discord
import pymongo
from discord.ext import commands

# Put your environmental variables into .env


default_extensions = [
    "cogs.base",
    "cogs.management",
    "cogs.admin.administrative",
    "cogs.admin.logging",
    "cogs.admin.notification",
    "cogs.utilities.multiserver",
    "cogs.utilities.utility",
    "cogs.utilities.task",
    "cogs.fun.entertainment",
    "cogs.fun.voice_tts",
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

    async def on_error(self, event, *args, **kwargs):
        # Log to file
        with open("/log/bot/error.log", "a") as f:
            d = datetime.datetime.now()
            date = d.strftime("%Y-%m-%d %H:%M:%S")

            f.write(f"-----\n[{date}]\n{traceback.format_exc()}\n-----\n")


def get_command_prefix(bot, message):
    # Prefixy na które bot odpowiada
    prefixes = ["*"]
    # if bot.guild_prefixes.has_key(message.guild.id):
    #     prefixes = bot.guild_prefixes()
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = MyBot(
    command_prefix=get_command_prefix, intents=discord.Intents.all(), help_command=None
)

bot.run(settings.discord_token)
