from __future__ import annotations

import asyncio
import logging
import time
from typing import Union

import constants
import discord
from cogs.components.discord_embed import Embed
from cogs.music.playlist import PlayList
from cogs.music.search import Search, Song
from discord.ext import commands
from patterns.observe import Observer
from patterns.singleton import SingletonMeta
from utils.utils import Timer, convert_to_second, convert_to_time, get_time

_log = logging.getLogger(__name__)


class PlayerManager(metaclass=SingletonMeta):
    """
    A class that manages the players for the music controller.

    Attributes:
        players (dict[int, Audio]): A dictionary that stores the players, where the key is the guild ID and the value is an instance of the Audio class.
    """

    def __init__(self) -> None:
        self.players: dict[int, Audio] = {}


class PlaylistObserver(Observer):
    def __init__(self, player: Audio) -> None:
        super().__init__()
        self.player = player

    async def update(self, observable: PlayList):
        await self.player.play_next()


class Audio:
    def __init__(self, *args, **kwargs) -> None:
        self.bot = None
        self.playlist = PlayList()
        self.is_playing = False
        self.current_song = None
        self.current_song_duration = 0.0
        self.prev_song = None
        self.start_time = 0.0
        self.ctx = None
        self.timer = Timer(callback=self.timeout_handle, ctx=self.ctx)
        self.lock = asyncio.Lock()

        for arg in args:
            if (
                isinstance(arg, (commands.Bot, commands.AutoShardedBot))
                and not self.bot
            ):
                self.bot = arg

        if "bot" in kwargs and not self.bot:
            self.bot = kwargs["bot"]

        if not self.bot:
            raise RuntimeError("Cannot initialize player, missing 'bot' param.")

        self.playlist.attach(PlaylistObserver(self))

        if not self.playlist._observers:
            raise Warning("Missing playlist observers.")

    async def play_next(self, ctx: commands.Context | None = None) -> None:
        async with self.lock:
            if not self.is_playing:
                song: Song | None = await self.playlist.get_next_prepared()
                if song is None:
                    self.current_song = None
                    if ctx is not None:
                        await ctx.send(embed=Embed().end_playlist())
                else:
                    self.is_playing = True
                    await self.play(song=song)

    def after_play(self, bot, ctx) -> None:
        if ctx.voice_client and not ctx.voice_client.is_playing():
            self.is_playing = not self.is_playing
            self.prev_song = self.current_song
            self.current_song = None
            bot.loop.create_task(self.play_next(ctx))

    async def play(self, song: Song) -> None:
        ctx = song.context
        self.start_time = convert_to_second(get_time())
        self.current_song_duration = convert_to_second(song.duration)

        self.timer.cancel()
        self.timer = Timer(self.timeout_handle, ctx=ctx)

        if not isinstance(song.playback_url, str):
            _log.error(
                f"Cannot load playback URL when trying to play this song '{song.title}'. Try to load next song."
            )
            self.after_play(self.bot, ctx)
            return

        source = discord.FFmpegPCMAudio(song.playback_url, **constants.FFMPEG_OPTIONS)
        embed = Embed(ctx).now_playing_song(song)
        await ctx.reply(embed=embed)

        self.current_song = song
        ctx.voice_client.play(source, after=lambda x: self.after_play(self.bot, ctx))

    async def process_query(
        self, ctx: commands.Context, query: str, priority: bool = False
    ) -> None:
        self.ctx = ctx  # assign this context for timeout_handler can work.

        start = time.time()
        songs = await Search().query(query, ctx, priority)

        if songs:
            add_songs = self.playlist.add_next if priority else self.playlist.add
            await asyncio.gather(*(add_songs(song) for song in songs))
            end = time.time()
            _log.info(
                f"Added {len(songs)} song(s) to current playlist in {round(end-start,2)} seconds from query '{query}'."
            )

            latest_song = songs[0]
            if self.playlist.size() > 0 and self.playlist.index(latest_song) is not None:
                current_time = convert_to_second(get_time())
                time_wait = self.current_song_duration - (current_time - self.start_time)
                if not priority:
                    time_wait += convert_to_second(
                        self.playlist.time_wait(self.playlist.index(latest_song))
                    )

                embed = Embed(ctx).add_song(
                    latest_song,
                    position=self.playlist.index(latest_song) + 1,
                    timewait=convert_to_time(time_wait),
                )
                await ctx.send(embed=embed)

        else:
            await ctx.send(embed=Embed().error("No songs were found!"))

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
            playerManager = PlayerManager()
            del playerManager.players[ctx.message.guild.id]
            await ctx.voice_client.disconnect()
            await ctx.send(embed=Embed().leave_channel_message(minutes=constants.VOICE_TIMEOUT//60))
            _log.info("Disconnected from voice channel due to timeout.")
