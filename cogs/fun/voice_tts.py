import asyncio
from collections import defaultdict

import discord
from discord.ext import commands
from gtts import gTTS


class VoiceTTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.races = {}
        self.playing_in = []
        self.queue = defaultdict(list)

    @commands.guild_only()
    @commands.command(name="tts", aliases=["mow", "say"])
    async def speak(self, ctx, *, text: str = None):
        if text is None:
            return
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("Musisz być połączony z jakimś kanałem głosowym.")
            return
        if ctx.guild.id in self.playing_in:
            await ctx.send("Bot jest teraz zajęty. Dodałem tekst do kolejki.")
            self.queue[ctx.channel.id].append(text)
            return

        self.playing_in.append(ctx.guild.id)

        # Set default lang
        lang = "pl"
        pos = text.find(":")
        # Valid language codes are either 2 or 5 characters long.
        if pos == 2 or pos == 5:
            lang = text[:pos]
            text = text[pos + 1 :]

        try:
            tts = gTTS(text, lang=lang)
        # If gTTS raises ValueError, then the language that we passed is incorrect
        except ValueError:
            await ctx.send(f"`{lang}` to nie jest poprawny kod językowy.")
            self.playing_in.remove(ctx.guild.id)
            return

        with open("../tmp/tmp.mp3", "wb") as f:
            tts.write_to_fp(f)

        source = discord.FFmpegOpusAudio("../tmp/tmp.mp3")

        # Get voice state object.
        # If bot is not in out voice chat then make him join it, else get it from bot.voice_clients
        if ctx.author.voice.channel.id not in [
            voice.channel.id for voice in self.bot.voice_clients
        ]:
            voice_state = ctx.voice_client or await ctx.author.voice.channel.connect()
        else:
            voice_state = [
                voice
                for voice in self.bot.voice_clients
                if voice.channel.id == ctx.author.voice.channel.id
            ][0]

        voice_state.play(source)

        while voice_state.is_playing():
            await asyncio.sleep(0.1)

        voice_state.stop()

        self.playing_in.remove(ctx.guild.id)

        # If queue is empty then disconnect.
        if ctx.channel.id not in self.queue:
            await voice_state.disconnect()
            return

        # Get oldest text from queue
        text = self.queue[ctx.channel.id].pop(0)

        await ctx.send("Odpalam kolejny tekst.")

        # Check if queue is empty. If it is, then remove the whole queue
        if not self.queue[ctx.channel.id]:
            self.queue.pop(ctx.channel.id)

        await asyncio.sleep(0.2)

        await self.speak(ctx, text=text)

    @commands.guild_only()
    @commands.command(name="skip", aliases=["pomin"])
    async def skip(self, ctx):
        if ctx.guild.id not in self.playing_in:
            await ctx.send("Nie mam czego pominąć.")
            return

        for voice in self.bot.voice_clients:
            if voice.channel.id == ctx.author.voice.channel.id:
                voice_state = voice
                break

        voice_state.stop()

        await ctx.send("Pominąłem aktualny tekst.")

    @commands.guild_only()
    @commands.command(name="queue", aliases=["kolejka"])
    async def _queue(self, ctx):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("Musisz być połączony z jakimś kanałem głosowym.")
            return
        if ctx.author.voice.channel.id not in [
            voice.channel.id for voice in self.bot.voice_clients
        ]:
            await ctx.send("Na tym kanale aktualnie nie działa bot.")
            return
        if len(self.queue[ctx.channel.id]) < 1:
            await ctx.send("W kolejce nie ma żadnego tekstu.")
            return
        message = "\n".join(self.queue[ctx.channel.id])
        await ctx.send(f"**Teksty w kolejce:**\n{message}")


def setup(bot):
    bot.add_cog(VoiceTTSCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
