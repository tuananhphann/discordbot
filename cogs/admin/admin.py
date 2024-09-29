import discord
from discord.ext import commands
from discord import app_commands
from cogs.music.controller import PlayerManager


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="shutdown", description="Shutdown the bot.")
    @commands.is_owner()
    async def shutdown(self, interaction: discord.Interaction) -> None:
        for player in PlayerManager().players.values():
            player.destroy()
            del player

        ctx = await self.bot.get_context(interaction)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await ctx.send("Bot closed")
        await self.bot.close()

    @app_commands.command(name="sync", description="Sync the guild's slash command.")
    @commands.is_owner()
    async def sync(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send("Sync local guild success")

    @app_commands.command(name="sync_all", description="Sync all slash command.")
    @commands.is_owner()
    async def sync_all(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        await self.bot.tree.sync()
        await ctx.send("Sync all success")

    @app_commands.command(name="remove_command_all", description="Remove all command.")
    @commands.is_owner()
    async def remove_command_all(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        self.bot.tree.clear_commands(guild=ctx.guild)
        await self.bot.tree.sync()
        await ctx.send("Remove all command success")
