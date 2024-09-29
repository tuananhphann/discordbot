from __future__ import annotations

import asyncio
import logging
import time
from typing import Union

from cogs.music.song import Song
import constants
import discord
from cogs.components.discord_embed import Embed
from cogs.music.playlist import PlayList
from cogs.music.search import Search
from discord.ext import commands
from patterns.observe import Observer
from patterns.singleton import SingletonMeta
from utils.utils import Timer, convert_to_second, convert_to_time, get_time

_log = logging.getLogger(__name__)


class PlayerManager(metaclass=SingletonMeta):
    """
    A class that manages the players for the music controller.

    Attributes:
        players (dict[int, Audio]): A dictionary that stores the players, where the key is the guild ID 
        and the value is an instance of the Audio class.
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

    def destroy(self):
        self.playlist.clear()
        self.timer.cancel()

    async def play_next(self, ctx: commands.Context | None = None) -> None:
        """
        Plays the next song in the playlist.

        This method acquires a lock to ensure that only one song is played at a time.
        If there are no more songs in the playlist, it sets the current song to None
        and sends an end of playlist message to the context if provided. Otherwise,
        it sets the is_playing flag to True and plays the next song.

        Args:
            ctx (commands.Context, optional): The context in which the command was invoked.
                Defaults to None.

        Returns:
            None
        """
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
        """
        Callback function to be called after a song finishes playing.

        This function checks if the voice client is still connected and not playing any song.
        If so, it toggles the `is_playing` flag, updates the `prev_song` to the current song,
        sets the `current_song` to None, and schedules the next song to be played.

        Args:
            bot (discord.ext.commands.Bot): The bot instance.
            ctx (discord.ext.commands.Context): The context in which the command was invoked.

        Returns:
            None
        """
        if ctx.voice_client and not ctx.voice_client.is_playing():
            self.is_playing = not self.is_playing
            self.prev_song = self.current_song
            self.current_song = None
            bot.loop.create_task(self.play_next(ctx))

    async def play(self, song: Song) -> None:
        """
        Plays the given song in the voice channel.
        Args:
            song (Song): The song object containing details about the song to be played.
        Returns:
            None

        This method performs the following steps:
        1. Sets the start time and duration of the current song.
        2. Cancels the existing timer and creates a new one.
        3. Checks if the playback URL is a valid string.
            - If not, logs an error and attempts to play the next song.
        4. Creates an FFmpeg audio source from the playback URL.
        5. Sends an embed message to the context indicating the currently playing song.
        6. Sets the current song and starts playing the audio in the voice client.
        """
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

        source = discord.FFmpegPCMAudio(song.playback_url, **constants.FFMPEG_OPTIONS)  # type: ignore
        embed = Embed(ctx).now_playing_song(song)
        await ctx.reply(embed=embed)

        self.current_song = song
        ctx.voice_client.play(source, after=lambda x: self.after_play(self.bot, ctx))

    async def process_query(
        self, ctx: commands.Context, query: str, priority: bool = False
    ) -> None:
        """
        Processes a search query to add songs to the playlist.
        Args:
            ctx (commands.Context): The context in which the command was invoked.
            query (str): The search query for finding songs.
            priority (bool, optional): If True, the songs will be added with priority. Defaults to False.
        Returns:
            None
        This method performs the following steps:
        1. Assigns the context to `self.ctx` for use in the timeout handler.
        2. Initiates a search for songs based on the provided query.
        3. Adds the found songs to the playlist, either at the next position or at the end, based on the priority flag.
        4. Logs the number of songs added and the time taken to process the query.
        5. Triggers an update for all song metadata in the playlist.
        6. If songs are found, calculates the wait time for the latest song and sends an embedded message with song details.
        7. If no songs are found, sends an embedded error message indicating that no songs were found.
        """
        self.ctx = ctx  # assign this context for timeout_handler can work.

        start = time.time()
        songs = await Search().query(query, ctx, priority)

        if songs:
            add_songs = self.playlist.add_next if priority else self.playlist.add
            await asyncio.gather(*(add_songs(song) for song in songs))
            end = time.time()
            _log.info(
                f"Added {len(songs)} song(s) to guild '{ctx.guild.id}' playlist in {round(end-start,2)} seconds from query '{query}'."
            )
            self.playlist.trigger_update_all_song_meta()

            latest_song = songs[0]
            if (
                self.playlist.size() > 0
                and self.playlist.index(latest_song) is not None
            ):
                current_time = convert_to_second(get_time())
                time_wait = self.current_song_duration - (
                    current_time - self.start_time
                )
                if not priority:
                    time_wait += convert_to_second(
                        await self.playlist.time_wait(self.playlist.index(latest_song))
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
        """
        Handles the timeout for the voice client in a Discord server.

        This method checks if the voice client is still playing audio. If it is,
        the timer is reset. If it is not, the voice client disconnects from the
        voice channel and the player is removed from the PlayerManager.

        Args:
            ctx (Union[commands.Context, None]): The context of the command or None.

        Returns:
            None
        """
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
            await ctx.send(
                embed=Embed().leave_channel_message(
                    minutes=constants.VOICE_TIMEOUT // 60
                )
            )
            _log.info("Disconnected from voice channel due to timeout.")
