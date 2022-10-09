import discord
from discord.ext import commands
from discord import app_commands


class Greeting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hello(self, ctx, member: discord.member = None, *args):
        """Just say hello"""
        member = member or ctx.author

        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f"Hello {member.name}!")
        else:
            await ctx.send(f"Hey, {member.name}. Glad to see you again!")
        self._last_member = member

    @commands.hybrid_command(name = "ping", with_app_command=True, description = "Test bot connection.")
    async def ping(self, ctx):
        """Test connection of this bot."""
        if round(self.bot.latency * 1000) <= 50:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0x44ff44)
        elif round(self.bot.latency * 1000) <= 100:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0xffd000)
        elif round(self.bot.latency * 1000) <= 200:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0xff6600)
        else:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0x990000)
        await ctx.send(embed=embed)



