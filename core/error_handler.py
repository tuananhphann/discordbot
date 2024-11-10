import discord
from discord.ext import commands
import traceback
from typing import Optional
import datetime
import logging
import logging.handlers
from pathlib import Path


class ErrorHandler:
    """A class to handle errors globally across the bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.error_channel_id: Optional[int] = None
        self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration"""
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("bot")
        self.logger.setLevel(logging.INFO)

        # Create formatters
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
        )

        # File handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            filename="logs/bot.log",
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # File handler for errors only
        error_handler = logging.handlers.RotatingFileHandler(
            filename="logs/error.log",
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        self.logger.addHandler(error_handler)

        # Optional console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(
            logging.WARNING
        )  # Only show warnings and errors in console
        self.logger.addHandler(console_handler)

    def log_error(self, error: Exception, error_source: str, **kwargs):
        """Log error with context information"""
        error_info = {
            "Error Type": type(error).__name__,
            "Error Message": str(error),
            "Error Source": error_source,
            **kwargs,
        }

        # Format the error message
        log_message = "\n".join(f"{k}: {v}" for k, v in error_info.items())

        # Add traceback for unexpected errors
        if not isinstance(error, commands.CommandError):
            tb = "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            log_message = f"{log_message}\nTraceback:\n{tb}"

        self.logger.error(log_message)

    async def create_error_embed(
        self,
        error: Exception,
        ctx: Optional[commands.Context] = None,
        interaction: Optional[discord.Interaction] = None,
    ) -> discord.Embed:
        """Creates a detailed error embed with information about the error"""

        embed = discord.Embed(
            title="❌ Error Occurred",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow(),
        )

        # Get command information
        command_name = None
        if ctx:
            command_name = ctx.command.qualified_name if ctx.command else "Unknown"
        elif interaction:
            command_name = (
                interaction.command.name if interaction.command else "Unknown"
            )

        # Add error information
        embed.add_field(
            name="Error Type", value=f"```py\n{type(error).__name__}\n```", inline=False
        )
        embed.add_field(
            name="Error Message", value=f"```py\n{str(error)}\n```", inline=False
        )

        # Add command usage context
        if command_name:
            embed.add_field(name="Command Used", value=f"`{command_name}`", inline=True)

        # Add user information
        user = ctx.author if ctx else interaction.user if interaction else None
        if user:
            embed.add_field(
                name="User", value=f"{user.name} (ID: {user.id})", inline=True
            )

        # Add guild information
        guild = ctx.guild if ctx else interaction.guild if interaction else None
        if guild:
            embed.add_field(
                name="Guild", value=f"{guild.name} (ID: {guild.id})", inline=True
            )

        return embed

    async def handle_command_error(
        self, ctx: commands.Context, error: Exception
    ) -> None:
        """Handles errors from traditional command contexts"""

        # Get original error if exists
        error = getattr(error, "original", error)

        # User-friendly error messages
        user_friendly_errors = {
            commands.MissingPermissions: "You don't have the required permissions to use this command.",
            commands.BotMissingPermissions: "I don't have the required permissions to execute this command.",
            commands.MissingRequiredArgument: f"Missing required argument: {error.param.name}",
            commands.BadArgument: "Invalid argument provided.",
            commands.CommandOnCooldown: f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            commands.NoPrivateMessage: "This command cannot be used in private messages.",
            commands.DisabledCommand: "This command is currently disabled.",
            commands.MemberNotFound: "Could not find the specified member.",
            commands.ChannelNotFound: "Could not find the specified channel.",
            commands.RoleNotFound: "Could not find the specified role.",
            commands.TooManyArguments: "Too many arguments provided.",
            commands.UserInputError: "Invalid input provided.",
            commands.CommandNotFound: None,  # We don't want to respond to unknown commands
        }

        # Log error with context
        self.log_error(
            error,
            "Traditional Command",
            Command=ctx.command.qualified_name if ctx.command else "Unknown",
            User=f"{ctx.author} (ID: {ctx.author.id})",
            Guild=f"{ctx.guild} (ID: {ctx.guild.id})" if ctx.guild else "DM",
            Channel=f"{ctx.channel} (ID: {ctx.channel.id})",
            Message=ctx.message.content,
        )

        # Get user-friendly error message
        error_message = None
        for error_type, message in user_friendly_errors.items():
            if isinstance(error, error_type):
                error_message = message
                break

        if error_message:
            # Send user-friendly error message
            error_embed = discord.Embed(
                title="❌ Error", description=error_message, color=discord.Color.red()
            )
            await ctx.send(embed=error_embed, delete_after=10)

        # Send to error channel if it's an unexpected error
        if not any(isinstance(error, err_type) for err_type in user_friendly_errors):
            error_embed = await self.create_error_embed(error, ctx=ctx)
            if self.error_channel_id:
                error_channel = self.bot.get_channel(self.error_channel_id)
                if error_channel:
                    await error_channel.send(embed=error_embed)

    async def handle_interaction_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        """Handles errors from application commands/interactions"""

        # Get original error if exists
        error = getattr(error, "original", error)

        # Log error with context
        self.log_error(
            error,
            "Interaction Command",
            Command=interaction.command.name if interaction.command else "Unknown",
            User=f"{interaction.user} (ID: {interaction.user.id})",
            Guild=(
                f"{interaction.guild} (ID: {interaction.guild.id})"
                if interaction.guild
                else "DM"
            ),
            Channel=f"{interaction.channel} (ID: {interaction.channel.id})",
        )

        # Create user-friendly error message
        error_message = str(error)
        if isinstance(error, discord.app_commands.CommandInvokeError):
            error_message = str(error.original)

        # Send error message to user
        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ Error",
                        description=error_message,
                        color=discord.Color.red(),
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="❌ Error",
                        description=error_message,
                        color=discord.Color.red(),
                    ),
                    ephemeral=True,
                )
        except discord.errors.InteractionResponded:
            pass

        # Log unexpected errors to error channel
        if not isinstance(error, discord.app_commands.CommandInvokeError):
            error_embed = await self.create_error_embed(error, interaction=interaction)
            if self.error_channel_id:
                error_channel = self.bot.get_channel(self.error_channel_id)
                if error_channel:
                    await error_channel.send(embed=error_embed)
