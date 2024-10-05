import logging
from discord.ext import commands
from core.exceptions import MusicError

_log = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    async def handle_error(ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply("Sorry, I couldn't find that command. Use `/help` to see available commands.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"Oops! You're missing a required argument: {error.param}", ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            await ctx.reply("I couldn't understand one of your arguments. Please check the command usage and try again.", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply("You don't have the necessary permissions to use this command.", ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply("I don't have the necessary permissions to execute this command.", ephemeral=True)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.", ephemeral=True)
        else:
            await ctx.reply("An unexpected error occurred. Our team has been notified.", ephemeral=True)
            _log.error(f"Unhandled error in command {ctx.command}: {error}", exc_info=error)

    @staticmethod
    async def handle_music_error(ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, MusicError):
            await ctx.reply(f"Music playback error: {error}", ephemeral=True)
        else:
            await ErrorHandler.handle_error(ctx, error)
