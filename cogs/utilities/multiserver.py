import asyncio

import discord
from discord.ext import commands


class MultiServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = self.bot.mongo.discord.multiserver
        self.connections = {}
        for result in self.collection.find({}):
            self.connections[result["guild"]] = result["channel"]

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return

        # If this channel is assigned as multiserver connection channel
        if message.channel.id in self.connections.values():

            files = []
            # Convert attachments to file format, we are doing it before calling message.delete because after that we will not have permission to access the attachments as they are deleted
            for attachment in message.attachments:
                file = await attachment.to_file(use_cached=True)
                files.append(file)

            # Delete old message
            await message.delete()

            # Replace annoying mentions
            if "@everyone" in message.content or "@here" in message.content:
                await message.author.send(
                    "kazdy nastepny ping @here albo @everyone zakonczy sie terminacja uzytkownika (ciebie)"
                )
            message.content = message.content.replace(
                "@everyone", "@\\everyone"
            ).replace("@here", "@\\here")

            await self.send_multiserver_message(
                content=message.content,
                username=f"[{message.guild.name}] {message.author.name}#{message.author.discriminator}",
                avatar_url=message.author.avatar_url,
                files=files,
                embeds=message.embeds,
            )

    @commands.guild_only()
    @commands.group(name="multiserver", aliases=["ms"])
    async def multiserver(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Lista serwerów korzystających z czatu międzyserwerowego"
            )
            for guild_id in self.connections:

                guild = None
                channel = None

                try:
                    guild = self.bot.get_guild(guild_id)
                    channel = guild.get_channel(self.connections[guild_id])
                except commands.CommandInvokeError:
                    self.connections.pop(guild_id)
                    self.collection.delete_one({"guild": guild_id})
                    continue

                embed.add_field(name=f"{guild.name}", value=f"#{channel.name}")

            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    @multiserver.command(name="assign", aliases=["set"])
    async def assign_multiserver_channel(self, ctx):
        # Update channel id if this server already has enabled multiserver integration, otherwise add it to database and dict
        self.connections[ctx.guild.id] = ctx.channel.id
        self.collection.update_one(
            filter={"guild": ctx.guild.id},
            update={"$set": {"guild": ctx.guild.id, "channel": ctx.channel.id}},
            upsert=True,
        )

        embed = discord.Embed(
            title="Sukces!",
            description="Pomyślnie ustawiłeś ten kanał jako służący do komunikacji między serwerami. Każda wiadomość którą tu wyślesz zostanie przesłana na pozostałe serwery korzystające z tej funkcji.",
        )
        embed.set_footer(
            text=f"Aktualnie z tej opcji korzysta {len(self.connections)} serwerów."
        )

        await ctx.send(embed=embed)
        # Send a notification that this server has disabled integration
        await self.send_multiserver_message(
            content="Nowy serwer połączył się.",
            username=ctx.guild.name,
            avatar_url=ctx.guild.icon_url,
        )

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True, manage_webhooks=True)
    @multiserver.command(name="disable", aliases=["unset"])
    async def disable_multiserver_communications(self, ctx):
        # If this server doesn't have multiserver comms enabled
        if ctx.guild.id not in self.connections.keys():
            embed = discord.Embed(
                title="Błąd",
                description="Ten serwer nie miał włączonych komunikacji międzyserwerowych, więc nic się nie zmienia. ",
            )
            await ctx.send(embed=embed)
            return

        self.connections.pop(ctx.guild.id)
        self.collection.delete_one({"guild": ctx.guild.id})

        embed = discord.Embed(
            title="Sukces!",
            description="Pomyślnie wyłączyłeś opcję komunikacji międzyserwerowej.",
        )
        embed.set_footer(
            text=f"Aktualnie z tej opcji korzysta {len(self.connections)} serwerów."
        )
        await ctx.send(embed=embed)

        # Send a notification that this server has disabled integration
        await self.send_multiserver_message(
            content="Serwer odłączył się od sieci.",
            username=ctx.guild.name,
            avatar_url=ctx.guild.icon_url,
        )

    async def send_multiserver_message(
        self, content=None, username=None, avatar_url=None, files=None, embeds=None
    ):
        for guild_id in self.connections:
            channel = self.bot.get_channel(self.connections[guild_id])
            if channel is None:
                self.connections.pop(guild_id)
                self.collection.delete_one({"guild": guild_id})
                continue
            # If message has files attached to it then wait one second
            # We are doing it to stop our bot from being rate-limited
            if files:
                await asyncio.sleep(1)

            webhook = None
            # Iterate through all channel webhooks, look for our specific webhook
            webhooks = await channel.webhooks()
            for wh in webhooks:
                if wh.name == "multiserver-integration":
                    webhook = wh
            # Create a new webhook if we didn't find any
            if webhook is None:
                webhook = await channel.create_webhook(name="multiserver-integration")

            await webhook.send(
                content=content,
                username=username,
                avatar_url=avatar_url,
                files=files,
                embeds=embeds,
            )


def setup(bot):
    bot.add_cog(MultiServerCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
