import logging

import discord
from discord.ext import commands

import constants
from cogs.components.discord_embed import Embed
from cogs.music.playlist import PlayList
from cogs.music.search import Search, Song
from utils import *

_log = logging.getLogger(__name__)


class Audio:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.playlist = PlayList()
        self.current_song = None
        self.current_song_duration = None
        self.start_time = None
        self.ctx = None
        self.timer = Timer(callback=self.timeout_handle(ctx=self.ctx))

    def play_next(self) -> None:
        song: Song = self.playlist.get_next()
        if song == None:
            self.current_song = None
            return
        coro = self.play(song=song)
        self.bot.loop.create_task(coro)

    async def play(self, song: Song) -> None:
        ctx = song.CTX
        self.start_time: float = convert_to_second(get_time())
        self.current_song_duration = convert_to_second(song.DURATION)

        self.timer.cancel()
        self.timer = Timer(self.timeout_handle(ctx))

        source = discord.FFmpegPCMAudio(song.URL, **constants.FFMPEG_OPTIONS)
        embed = Embed(ctx).now_playing_song(song)
        await ctx.reply(embed=embed)
        # await ctx.reply(embed=embed)
        ctx.voice_client.play(source, after=lambda e: self.play_next())
        self.current_song = song.TITLE

    async def process_track(
        self, ctx: commands.Context, track: str, priority: bool = False
    ) -> None:
        self.ctx = ctx  # assign this context for timeout_handler can work.
        song = await Search().query(track, ctx)
        if song == -1:
            _log.error(f"Can not play this song '{track}'")
            return

        if self.current_song == None:
            _log.info(
                f"Starting to play this song '{song.TITLE}' from query '{track}'."
            )
            await self.play(song)
        else:
            if priority == True:
                current_time = convert_to_second(get_time())
                time_wait = self.current_song_duration - (
                    current_time - self.start_time
                )

                self.playlist.add_next(song)
                _log.info(
                    f"Added to playlist '{song.TITLE}' from query '{track}' at 'Next' position."
                )
                embed = Embed(ctx).add_song(
                    song,
                    self.playlist.index(song) + 1,
                    f"Next, about {convert_to_time(time_wait)}",
                )
                await ctx.send(embed=embed)
            else:
                current_time = convert_to_second(get_time())
                time_wait = (
                    self.current_song_duration
                    - (current_time - self.start_time)
                    + convert_to_second(self.playlist.time_wait())
                )

                self.playlist.add(song)
                _log.info(
                    f"Added to playlist '{song.TITLE}' from query '{track}' at position '{self.playlist.index(song)+1}'."
                )
                embed = Embed(ctx).add_song(
                    song,
                    position=self.playlist.index(song) + 1,
                    timewait=convert_to_time(time_wait),
                )
                await ctx.send(embed=embed)

    async def timeout_handle(self, ctx: commands.Context) -> None:
        if ctx.voice_client.is_playing():
            self.timer.cancel()
            self.timer = Timer(callback=self.timeout_handle(ctx))
            _log.info(
                "Timer has been reset because discord.voice_client is still playing."
            )
        else:
            await ctx.voice_client.disconnect()
            _log.info(
                f"Disconnected from voice channel due to timeout. ID: {ctx.author.voice.channel.id}"
            )
