import random
import asyncio

import discord
from discord.ext import commands


class EntertainmentCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.races = {}

    @commands.command(name="race", aliases=["wyscig", "zygzak"])
    async def racing_cars(self, ctx, number_of_cars: int = 2, race_length: int = 30):
        if 2 > number_of_cars > 10:
            await ctx.send("Minimalna ilość aut to 2, a maskymalna to 10.")
            return
        if 10 > race_length > 30:
            await ctx.send(
                "Długość trasy to minimalnie 10 jednostek, a maksymalnie 30."
            )
            return
        if ctx.guild.id in self.races:
            await ctx.send("Ktoś się już tu ściga.")
            return

        self.races[ctx.guild.id] = True
        guild = await self.bot.fetch_guild(632631408442998794)
        car_emoji = await guild.fetch_emoji(793258469385568258)
        car_positions = {}
        for i in range(1, number_of_cars + 1):
            car_positions[i] = 1

        race_string = "\n· ".join(
            [
                "　" * car_positions[car]
                + str(car_emoji)
                + "　" * (race_length - car_positions[car])
                + "|"
                for car in car_positions
            ]
        )
        embed = discord.Embed(
            title="**Wyścig!**",
            description=f"W wyścigu bierze udział {number_of_cars} uczestników.\n· {race_string}",
        )
        message = await ctx.send(embed=embed)

        while not any(car_positions[car] >= race_length for car in car_positions):
            for car in car_positions:
                car_positions[car] += random.randint(1, 3)
                if car_positions[car] > race_length:
                    car_positions[car] = race_length
            race_string = "\n· ".join(
                [
                    "　" * car_positions[car]
                    + str(car_emoji)
                    + "　" * (race_length - car_positions[car])
                    + "|"
                    for car in car_positions
                ]
            )
            embed = discord.Embed(
                title="**Wyścig!**",
                description=f"W wyścigu bierze udział {number_of_cars} uczestników.\n· {race_string}",
            )
            await message.edit(embed=embed)
            await asyncio.sleep(1)

        race_string = "\n· ".join(
            [
                "　" * car_positions[car]
                + str(car_emoji)
                + "　" * (race_length - car_positions[car])
                + "|"
                for car in car_positions
            ]
        )
        embed = discord.Embed(
            title="**Wyścig zakończony!**",
            description=f"W wyścigu brało udział {number_of_cars} uczestników.\n· {race_string}",
        )
        await message.edit(embed=embed)

        del self.races[ctx.guild.id]


def setup(bot):
    bot.add_cog(EntertainmentCog(bot))
    print(f"Uruchomiono moduł {__name__}")


def teardown(bot):
    print(f"Wyłączono moduł {__name__}")
