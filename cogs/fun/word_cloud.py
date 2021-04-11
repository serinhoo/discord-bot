import io
from collections import Counter

import discord
from discord.ext import commands
from wordcloud import WordCloud


class WordplotCog(commands.Cog):
    def __init__(self, bot):
        self.LIMIT = 20000
        self.bot = bot

    def create_word_cloud(self, frequencies: dict):
        wc = WordCloud(
            font_path="lib/bebasneue-wordcloud.ttf",
            background_color="white",
            max_words=250,
            width=2000,
            height=1000,
            min_word_length=4,
            normalize_plurals=True,
        )
        wc.generate_from_frequencies(frequencies)

        image = wc.to_image()

        binary = io.BytesIO()

        image.save(binary, format="PNG")

        binary.seek(0)

        return discord.File(binary, filename="wordcloud.png")

    @commands.guild_only()
    @commands.group(name="wordcloud", aliases=["words", "cloud", "wc"])
    async def wordcloud_base(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Word cloud creator",
                description="This command allows you to create word clouds consisting of most used words.\n Below are available subcommands. You can invoke them by using for example `*wordcloud user @mention`",
            )
            embed.add_field(
                name="guild",
                value="creates wordcloud of words used anywhere on this server",
            )
            embed.add_field(
                name="channel #channel",
                value="creates wordcloud of words used in channel, if you do not specify a channel then it will default to the one you sent the message in",
            )
            embed.add_field(
                name="user @user",
                value="creates wordcloud of words used by user, if you do not specify a user then it will default to you",
            )

            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
    @wordcloud_base.command(name="guild")
    async def wordcloud_guild(self, ctx: commands.Context):

        await ctx.send(
            "This process will take some time. I will ping you when I'm done."
        )

        messages = []

        # Hard limit is 50000 messages, so break it between all channels
        limit = int(self.LIMIT / len(ctx.guild.text_channels))

        for channel in ctx.guild.text_channels:
            # We use .map() to retrieve only the message.content property so
            # we won't have to hold the whole message object in memory.
            # We also .lower() all message contents so "Hi", "hi" and "hI" will be counted together
            messages += (
                await channel.history(limit=limit)
                .map(lambda m: m.content.lower())
                .flatten()
            )

        # We join all strings together and then split them into a list of words.
        list_of_words = " ".join(messages).split(" ")

        c = Counter(list_of_words)

        # We convert tuples in format (word, frequency) to dictionary
        frequencies = {t[0]: t[1] for t in c.most_common(250)}

        image = self.create_word_cloud(frequencies)

        await ctx.send(
            content="{}\nHere's a word cloud that you requested.".format(
                ctx.author.mention
            ),
            file=image,
        )

    @commands.guild_only()
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
    @wordcloud_base.command(name="channel")
    async def wordcloud_channel(
        self, ctx: commands.Context, text_channel: discord.TextChannel = None
    ):

        if text_channel is None:
            text_channel = ctx.message.channel

        await ctx.send(
            "This process will take some time. I will ping you when I'm done."
        )

        messages = []

        messages += (
            await text_channel.history(limit=int(self.LIMIT / 3))
            .map(lambda m: m.content.lower())
            .flatten()
        )

        # We join all strings together and then split them into a list of words.
        list_of_words = " ".join(messages).split(" ")

        c = Counter(list_of_words)

        # We convert tuples in format (word, frequency) to dictionary
        frequencies = {t[0]: t[1] for t in c.most_common(250)}

        image = self.create_word_cloud(frequencies)

        await ctx.send(
            content="{}\nHere's a word cloud of #{} that you requested.".format(
                ctx.author.mention, text_channel.name
            ),
            file=image,
        )

    @commands.guild_only()
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.user)
    @wordcloud_base.command(name="user", aliases=["member"])
    async def wordcloud_user(
        self, ctx: commands.Context, member: discord.Member = None
    ):

        if member is None:
            member = ctx.author

        await ctx.send(
            "This process will take some time. I will ping you when I'm done."
        )

        messages = []

        # Hard limit is 50000 messages, so break it between all channels
        limit = int(self.LIMIT / len(ctx.guild.text_channels))

        for tc in ctx.guild.text_channels:
            # We use .map() to retrieve only the message.content property so
            # we won't have to hold the whole message object in memory.
            # We also .lower() all message contents so "Hi", "hi" and "hI" will be counted together
            messages += (
                await tc.history(limit=limit)
                .filter(lambda m: m.author.id == member.id)
                .map(lambda m: m.content.lower())
                .flatten()
            )

        # We join all strings together and then split them into a list of words.
        list_of_words = " ".join(messages).split(" ")

        c = Counter(list_of_words)

        # We convert tuples in format (word, frequency) to dictionary
        frequencies = {t[0]: t[1] for t in c.most_common(250)}

        image = self.create_word_cloud(frequencies)

        await ctx.send(
            content="{}\nHere's a word cloud of {}'s most used words.".format(
                ctx.author.mention, member
            ),
            file=image,
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(error)


def setup(bot):
    bot.add_cog(WordplotCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
