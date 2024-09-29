import asyncio
import functools

import discord
from cogs.components.discord_embed import Embed
from cogs.music.controller import Audio, PlayerManager
from discord import app_commands
from discord.ext import commands


# https://github.com/Rapptz/discord.py/discussions/8372#discussioncomment-3459014
def ensure_voice(f):
    @functools.wraps(f)
    async def callback(self, interaction: discord.Interaction, *args, **kwargs):
        ctx = await self.bot.get_context(interaction)
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(self_deaf=True)
            else:
                await ctx.send("You are not connected to a voice channel.")
                return
        await f(self, interaction, *args, **kwargs)

    return callback


class Music(commands.Cog):
    """Music cog for my OneNine4 Bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.playerManager = PlayerManager()

    @app_commands.command(
        name="play",
        description="Adds a song or playlist to the queue and plays it."
    )
    @ensure_voice
    async def p(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)
        ctx = await self.bot.get_context(interaction)

        if ctx.voice_client.channel != ctx.author.voice.channel:
            embed = discord.Embed(
                color=discord.Color.red(),
                description=f"This bot already in {ctx.voice_client.channel.name}. Use **/come** command if you want it here instead!"
            )
            await ctx.send(embed=embed)
            return

        if interaction.guild_id not in self.playerManager.players and interaction.guild_id:
            self.playerManager.players[interaction.guild_id] = Audio(self.bot)

        if interaction.guild_id is not None:
            await self.playerManager.players[interaction.guild_id].process_query(ctx, query)

    @app_commands.command(
        name="playnext",
        description="You just found a great song and want to listen it right now.",
    )
    @ensure_voice
    async def pn(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)

        if ctx.voice_client.channel != ctx.author.voice.channel:
            embed = discord.Embed(
                color=discord.Color.red(),
                description=f"This bot already in {ctx.voice_client.channel.name}. Use **/come** command if you want it here instead!"
            )
            await ctx.send(embed=embed)
            return

        if interaction.guild_id not in self.playerManager.players and interaction.guild_id:
            self.playerManager.players[interaction.guild_id] = Audio(self.bot)

        if interaction.guild_id is not None:
            await self.playerManager.players[interaction.guild_id].process_query(ctx, query, True)

    @app_commands.command(
        name="queue",
        description="Show the current playlist."
    )
    async def queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        if interaction.guild_id and ctx.voice_client:
            if self.playerManager.players[interaction.guild_id].playlist.size() == 0:
                await ctx.send(
                    embed=Embed().error(
                        description="There are no songs in the playlist."
                    )
                )
            else:
                playlist = await self.playerManager.players[interaction.guild_id].playlist.get_list(10)
                embed = Embed(ctx).in_playlist(playlist)
                await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(color=discord.Color.red(), description="No bot in voice channel!"))

    @app_commands.command(
        name="skip",
        description="This song is so terrible? Just use this command to skip.",
    )
    async def skip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(embed=Embed().ok(description="Song skipped."))
        else:
            await ctx.send(embed=Embed().error(description="No songs are playing."))

    @app_commands.command(
        name="stop",
        description="Clear the playlist, stop playing music, and leave the channel.",
    )
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        if ctx.voice_client and interaction.guild_id:
            self.playerManager.players[interaction.guild_id].destroy()
            del self.playerManager.players[interaction.guild_id]
            await ctx.send(embed=Embed().ok("Thanks for using the bot ^^"))
            await ctx.voice_client.disconnect()
        else:
            await ctx.send(embed=Embed().error(description="No songs are playing."))

    @app_commands.command(
        name="come",
        description="Tell the bot to come to your voice channel"
    )
    @ensure_voice
    async def come(self, interaction: discord.Interaction):
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        if ctx.author.voice.channel != ctx.voice_client.channel:
            ctx.voice_client.pause()
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
            await asyncio.sleep(1)
            ctx.voice_client.resume()
            await ctx.send(embed=Embed().ok("Switched to the new voice channel!"))
        else:
            await ctx.send(embed=Embed().error("No need to change the voice channel!"))
