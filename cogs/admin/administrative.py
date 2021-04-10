import discord
from discord.ext import commands


class AdministrativeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.guild_only()
    @commands.command(name="sendas")
    async def send_message_as(self, ctx, member: discord.Member = None, *, content):
        """ Sends message as specified user (using webhook) """
        if member is None:
            member = ctx.message.author

        await ctx.message.delete()
        webhook = await ctx.channel.create_webhook(name="temp")
        await webhook.send(
            content, username=member.display_name, avatar_url=member.avatar_url
        )
        await webhook.delete()

    @commands.is_owner()
    @commands.command(name="senddm")
    async def send_dm_message(self, ctx, member: discord.Member = None, *, content):
        """ Sends direct message to specified user """
        if member is None:
            member = ctx.message.author

        await member.send(content)


def setup(bot):
    bot.add_cog(AdministrativeCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
