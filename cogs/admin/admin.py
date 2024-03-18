import discord
from discord.ext import commands
from discord import app_commands


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command()
    @commands.is_owner()
    async def shutdown(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await ctx.send("Bot closed")
        await self.bot.close()

    @app_commands.command()
    @commands.is_owner()
    async def sync(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send("Sync local guild success")

    @app_commands.command()
    @commands.is_owner()
    async def sync_global(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send("Sync global success")
