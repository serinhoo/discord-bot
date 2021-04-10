import discord
from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["pomoc", "?"])
    async def help_command(self, ctx, *, argument: str = ""):
        """ Shows help command. """
        command = None
        try:
            command = self.bot.get_command(argument)
        except commands.CommandInvokeError:
            pass
        # If no argument was passed
        if command is None:
            embed = discord.Embed(
                title="Spis komend",
                description="Więcej informacji o danej komendzie możesz uzyskać używając `^help [komenda]`.",
                color=0x5175D2,
            )
            number_of_commands = len(self.bot.commands)
            embed.set_footer(
                text=f"Aktualnie jest zarejestrowanych {number_of_commands} komend.",
                icon_url=self.bot.user.avatar_url,
            )

            for key in self.bot.cogs:
                # Resolve cog
                cog = self.bot.cogs.get(key)

                available_commands_names = []
                # Walk through all commands
                for command in cog.walk_commands():
                    try:
                        can_run = await command.can_run(ctx)
                    except commands.CommandError:
                        can_run = False

                    if not can_run:
                        continue

                    available_commands_names.append(f"`^{command.qualified_name}`")
                # Don't add anything to embed if this cog doesn't have any commands
                if len(available_commands_names) == 0:
                    continue

                # Sort by name, from starting from A
                available_commands_names.sort(key=lambda x: x)
                available_commands = " ".join(available_commands_names)

                embed.add_field(name=cog.qualified_name[:-3], value=available_commands)

            await ctx.author.send(embed=embed)

        # If user specified an command we'll look it up and display more information about it (if it exists)
        else:
            aliases_str = " ".join([f"`{command}`" for command in command.aliases])
            embed = discord.Embed(
                title="Informacje o komendzie",
                description=f"Pomoc dotycząca użycia komendy `^{command.qualified_name}`.\n\n**Aliasy:**\n{aliases_str}\n**Dokumentacja:**\n```{command.short_doc}```",
                color=0x5175D2,
            )
            number_of_commands = len(self.bot.commands)
            embed.set_footer(
                text=f"Aktualnie jest zarejestrowanych {number_of_commands} komend.",
                icon_url=self.bot.user.avatar_url,
            )
            await ctx.author.send(embed=embed)


def setup(bot):
    bot.add_cog(BaseCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
