import datetime
import os
import traceback

import discord
from discord.channel import GroupChannel
from discord.ext import commands


class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages_collection = self.bot.mongo.discord.messages

    @commands.Cog.listener()
    async def on_message(self, message):

        query = {}
        query["id"] = message.id
        query["author_id"] = message.author.id
        query["author_name"] = message.author.name + "#" + message.author.discriminator
        if message.guild is not None:
            query["message_guild_id"] = message.guild.id
            query["message_guild_name"] = message.guild.name
        if isinstance(message.channel, discord.TextChannel):
            query["message_channel_id"] = message.channel.id
            query["message_channel_name"] = message.channel.name
        query["message_content"] = message.clean_content

        self.messages_collection.insert_one(query)


def setup(bot):
    bot.add_cog(LoggingCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
