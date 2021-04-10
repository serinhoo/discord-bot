import traceback

import discord
from discord.ext import commands


class ManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.group(name="cog", aliases=["cogs"])
    async def extensions(self, ctx):
        """ Shows all loaded cogs"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="**Załadowane moduły**",
                description="Pokazuje wszystkie aktualnie załadowane moduły bota. Możesz też użyć subkomend `load`, `unload` i `reload`.",
            )
            for key in self.bot.cogs:
                cog = self.bot.cogs.get(key)
                embed.add_field(name=f"**{cog.qualified_name}**", value="\uFEFF")
            embed.set_footer(text=f"discord.py {discord.__version__}")
            await ctx.send(embed=embed)

    @commands.is_owner()
    @extensions.command(name="load", aliases=["enable"])
    async def load_dynamic_extension(self, ctx, *, extension_name: str):
        """ Enables specified module """
        try:
            self.bot.load_extension(extension_name)
            await ctx.send(f"Moduł *{extension_name}* został pomyślnie uruchomiony.")
        except:
            await ctx.send(
                f"Coś poszło nie tak podczas ładowania modułu *{extension_name}*. Informacje na temat wyjątku: ```{traceback.format_exc()}```"
            )

    @commands.is_owner()
    @extensions.command(name="unload", aliases=["disable"])
    async def unload_dynamic_extension(self, ctx, *, extension_name: str):
        """ Disables specified module """
        try:
            self.bot.unload_extension(extension_name)
            await ctx.send(
                f"Moduł *{extension_name}* został wyłączony. Jego funcjonalności od teraz nie będą dostępne"
            )
        except:
            await ctx.send(
                f"Coś poszło nie tak podczas odładowywania modułu *{extension_name}*. Informacje na temat wyjątku: ```{traceback.format_exc()}```"
            )

    @commands.is_owner()
    @extensions.command(name="reload", aliases=["restart"])
    async def reload_dynamic_extension(self, ctx, *, extension_name: str):
        """ Reloads specified cog """
        await self.unload_dynamic_extension(ctx, extension_name=extension_name)
        await self.load_dynamic_extension(ctx, extension_name=extension_name)


def setup(bot):
    bot.add_cog(ManagementCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
