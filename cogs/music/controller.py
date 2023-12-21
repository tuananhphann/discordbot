import logging
from typing import Union, Optional

import discord
from discord.ext import commands

import constants
from cogs.components.discord_embed import Embed
from cogs.music.playlist import PlayList
from cogs.music.search import Search, Song
from utils import Timer, convert_to_second, convert_to_time, get_time

_log = logging.getLogger(__name__)


class Audio:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.playlist = PlayList()
        self.current_song = None
        self.current_song_duration = 0.0
        self.start_time = 0.0
        self.ctx = None
        self.timer = Timer(callback=self.timeout_handle, ctx=self.ctx)

    def play_next(self) -> None:
        song: Song = self.playlist.get_next()
        if song is None:
            self.current_song = None
            return
        coro = self.play(song=song)
        self.bot.loop.create_task(coro)

    async def play(self, song: Song) -> None:
        ctx = song.context
        self.start_time = convert_to_second(get_time())
        self.current_song_duration = convert_to_second(song.duration)

        self.timer.cancel()
        self.timer = Timer(self.timeout_handle, ctx=ctx)

        source = discord.FFmpegPCMAudio(song.playback_url, **constants.FFMPEG_OPTIONS)
        embed = Embed(ctx).now_playing_song(song)
        await ctx.reply(embed=embed)
        # await ctx.reply(embed=embed)
        ctx.voice_client.play(source, after=lambda x: self.play_next())
        self.current_song = song.title

    async def process_track(
        self, ctx: commands.Context, track: str, priority: bool = False
    ) -> None:
        self.ctx = ctx  # assign this context for timeout_handler can work.
        query_result = await Search().query(track, ctx)

        if query_result is None:
            _log.error(f"Can not process this query '{track}'")
            return

        if isinstance(query_result, Song):
            song = query_result
            _log.info("Added 1 song to the playlist.")
        elif isinstance(query_result, list):
            song = query_result[0]
            for i in range(1, len(query_result)):
                self.playlist.add(query_result[i])
            _log.info(f"Added {len(query_result)} songs to the playlist.")
        else:
            return

        if self.current_song is None:
            _log.info(
                f"Starting to play this song '{song.title}' from query '{track}'."
            )
            await self.play(song)
        else:
            if priority:
                current_time = convert_to_second(get_time())
                time_wait = self.current_song_duration - (
                    current_time - self.start_time
                )

                self.playlist.add_next(song)
                _log.info(
                    f"Added to playlist '{song.title}' from query '{track}' at 'Next' position."
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
                    f"Added to playlist '{song.title}' from query '{track}' at position '{self.playlist.index(song)+1}'."
                )
                embed = Embed(ctx).add_song(
                    song,
                    position=self.playlist.index(song) + 1,
                    timewait=convert_to_time(time_wait),
                )
                await ctx.send(embed=embed)

    async def timeout_handle(self, ctx: Union[commands.Context, None]) -> None:
        if ctx is None:
            return
        if ctx.voice_client.is_playing():
            self.timer.cancel()
            self.timer = Timer(callback=self.timeout_handle, ctx=ctx)
            _log.info(
                "Timer has been reset because discord.voice_client is still playing."
            )
        else:
            await ctx.voice_client.disconnect()
            _log.info(
                f"Disconnected from voice channel due to timeout. ID: {ctx.author.voice.channel.id}"
            )
