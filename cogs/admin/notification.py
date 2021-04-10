import discord
from discord.ext import commands


class NotificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title=f"**Nowy użytkownik**", color=0x32CD32)
        embed.set_author(
            name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url
        )
        embed.set_thumbnail(url=member.avatar_url)

        embed.add_field(
            name="Nazwa: ", value=f"{member.name}#{member.discriminator}", inline=True
        )
        embed.add_field(name="ID konta: ", value=member.id, inline=True)
        embed.add_field(
            name="Dołączył (discord): ",
            value=member.created_at.replace(microsecond=0),
            inline=True,
        )

        # Send message to system messages channel if it is set, else send it to the topmost channel
        channel = (
            (member.guild.system_channel)
            if (member.guild.system_channel != None)
            else (member.guild.text_channels[0])
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title=f"**Użytkownik opuścił serwer**", color=0x8B0000)
        embed.set_author(
            name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url
        )
        embed.set_thumbnail(url=member.avatar_url)

        embed.add_field(
            name="Nazwa: ", value=f"{member.name}#{member.discriminator}", inline=True
        )
        embed.add_field(name="ID konta: ", value=member.id, inline=False)
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

        # Send message to system messages channel if it is set, else send it to the topmost channel
        channel = (
            (member.guild.system_channel)
            if (member.guild.system_channel != None)
            else (member.guild.text_channels[0])
        )
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(NotificationCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
