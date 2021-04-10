import base64
import datetime
import time

import discord
from discord.ext import commands


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(name="vote", aliases=["poll", "ankieta"])
    async def start_vote(self, ctx):
        """ Starts a vote """
        await ctx.message.add_reaction("👍")
        await ctx.message.add_reaction("👎")

    @commands.command(name="botinfo")
    async def show_bot_info(self, ctx):
        """ Shows detailed bot information """
        owner = self.bot.get_user(259003214790131722)

        current_time = time.time()
        difference = int(round(current_time - self.start_time))
        uptime_as_text = str(datetime.timedelta(seconds=difference))

        embed = discord.Embed(title="**Informacje o bocie**", color=0x5175D2)
        embed.set_author(
            name=f"{owner.name}#{owner.discriminator}", icon_url=owner.avatar_url
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        embed.add_field(name="Czas działania", value=uptime_as_text, inline=True)
        embed.add_field(name="Ilość gildii", value=len(self.bot.guilds), inline=True)
        embed.add_field(
            name="Wersja discord.py", value=discord.__version__, inline=True
        )
        if ctx.guild is not None:
            embed.add_field(name="W tej gildii od", value=ctx.guild.me.joined_at)
        embed.add_field(
            name="Link do zaproszenia",
            value=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot",
        )

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(name="userinfo", aliases=["whois", "user", "info"])
    async def show_user_info(self, ctx, *, member: discord.Member = None):
        """ Shows detailed user information """

        if member is None:
            member = ctx.message.author

        embed = discord.Embed(title="**Informacje o użytkowniku**", color=0x5175D2)
        embed.set_author(
            name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=ctx.message.author.avatar_url,
        )
        embed.set_thumbnail(url=member.avatar_url)

        embed.add_field(
            name="Nazwa: ", value=f"{member.name}#{member.discriminator}", inline=True
        )
        embed.add_field(name="ID konta: ", value=member.id, inline=True)
        embed.add_field(
            name="Dołączył (serwer): ",
            value=member.joined_at.replace(microsecond=0),
            inline=False,
        )
        embed.add_field(
            name="Dołączył (discord): ",
            value=member.created_at.replace(microsecond=0),
            inline=True,
        )
        embed.add_field(
            name="Role użytkownika: ",
            value=", ".join([role.mention for role in member.roles][1:]),
            inline=False,
        )
        if member.bot:
            embed.add_field(name="Bot: ", value="Tak", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["av"])
    async def show_user_avatar(self, ctx, *, member: discord.Member = None):
        """ Shows user avatar """

        if member is None:
            member = ctx.message.author

        embed = discord.Embed(title="**Avatar użytkownika**", color=0x5175D2)
        embed.set_author(
            name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=ctx.message.author.avatar_url,
        )

        embed.set_image(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="encode")
    async def encode_message(self, ctx, *, content):
        """ Encodes message to base85 format """
        encoded_bytelike = base64.b85encode(bytes(content, "utf-8"))
        encoded_string = encoded_bytelike.decode("utf-8")
        await ctx.send(f"{encoded_string}")

    @commands.command(name="decode")
    async def decode_message(self, ctx, *, content):
        """ Decodes message encoded in base85 format """
        decoded_bytelike = base64.b85decode(content)
        decoded_string = decoded_bytelike.decode("utf-8")
        await ctx.send(f"{decoded_string}")

    @commands.command()
    @commands.guild_only()
    async def joindate(self, ctx):
        """ Shows join date of every guild member """
        members = [member for member in ctx.guild.members]
        members.sort(key=lambda m: m.joined_at)
        string = ""
        for member in members:
            string += f"{member.name} dołączył {member.joined_at}\n"
        embed = discord.Embed(title="Daty dołączenia", description=f"```{string}```")
        await ctx.send(embed=embed)

    @commands.command(name="snowflake")
    async def breakdown_snowflake(self, ctx, snowflake: int):
        """ Breaks down snowflake format """
        timestamp = ((snowflake >> 22) + 1420070400000) / 1000
        timestamp_as_date = datetime.datetime.fromtimestamp(timestamp)
        worker_id = (snowflake & 0x3E0000) >> 17
        process_id = (snowflake & 0x1F000) >> 12
        autoincrement_id = snowflake & 0xFFF

        embed = discord.Embed(title="Rozebrane informacje zawierane w snowflake (ID)")
        embed.add_field(name="Timestamp utworzenia:", value=timestamp)
        embed.add_field(
            name="Data utworzenia (human-readable):", value=timestamp_as_date
        )
        embed.add_field(name="Worker ID:", value=worker_id)
        embed.add_field(name="Process ID:", value=process_id)
        embed.add_field(name="Autoincrement ID:", value=autoincrement_id)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UtilityCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
