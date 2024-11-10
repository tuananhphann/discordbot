from __future__ import annotations

import asyncio
import logging
import time
from typing import List, Optional, Union, Literal

from cogs.music.manager import PlayerManager, PlaylistManager
from cogs.music.core.song import Song, SongMeta
from cogs.music.view.view import MusicView
import constants
import discord
from cogs.components.discord_embed import Embed
from cogs.music.core.playlist import PlaylistObserver
from cogs.music.search import Search
from discord.ext import commands
from utils import Timer, convert_to_second, get_time

_log = logging.getLogger(__name__)


class Audio:
    def __init__(self, *args, **kwargs) -> None:
        self.bot = None
        self.playlist_manager = PlaylistManager()
        self.is_playing = False

        self.ctx: Optional[commands.Context] = None
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

        self.playlist_manager.playlist.attach(PlaylistObserver(self))

        if not self.playlist_manager.playlist._observers:
            raise Warning("Missing playlist observers.")

    def destroy(self) -> None:
        self.playlist_manager.playlist.clear()
        self.timer.cancel()

    async def play_next(self, ctx: Optional[commands.Context] = None) -> None:
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
                song: Optional[Song] = (
                    await self.playlist_manager.playlist.get_next_prepared()
                )
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
            self.playlist_manager.prev_song = self.playlist_manager.current_song
            self.playlist_manager.current_song = None
            bot.loop.create_task(self.play_next(ctx))

    async def play(self, song: Song) -> None:
        """
        Plays the given song in the voice channel.
        Args:
            song (Song): The song object containing details about the song to be played.
        Returns:
            None
        """
        ctx = song.context
        self.playlist_manager.current_song_start_time = convert_to_second(get_time())
        self.playlist_manager.current_song_duration = convert_to_second(song.duration)

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

        self.playlist_manager.current_song = song
        ctx.voice_client.play(source, after=lambda x: self.after_play(self.bot, ctx))

    async def process_query(
        self, ctx: commands.Context, query: str, priority: bool = False
    ) -> None:
        # assign this context for timeout_handler can work.
        self.ctx = ctx

        start_time = time.time()
        songs = await self._search_songs(query, priority)

        if songs:
            await self.playlist_manager.add_songs(songs, priority)
            self._log_song_addition(len(songs), ctx.guild.id, query, start_time)
            await self._send_song_added_message(songs[0], priority)
        else:
            await self._send_no_songs_found_message()

    async def process_search(
        self,
        ctx: commands.Context,
        query: str,
        provider: Optional[Literal["youtube", "soundcloud"]] = None,
    ) -> None:
        self.ctx = ctx

        songs: Optional[List[SongMeta]] = await self._search_songs(
            query, provider=provider, limit=10
        )
        if songs:
            view = MusicView(songs, self.handle_track_selection_in_search)
            view.message = await ctx.send(embed=view.create_embed(), view=view)
        else:
            await self._send_no_songs_found_message()

    async def handle_track_selection_in_search(
        self, interaction: discord.Interaction, track: SongMeta
    ):
        """
        Handles the selection of a track from a search result.

        This method adds the selected track to the playlist and sends a message
        indicating that the song has been added.

        Args:
            interaction (discord.Interaction): The interaction object that triggered this method.
            track (SongMeta): The metadata of the selected song.

        Returns:
            None
        """
        await self.playlist_manager.add_songs([track], False)
        await self._send_song_added_message(track, False)

    async def handle_track_selection_in_playlist(
        self, interaction: discord.Interaction, track: SongMeta
    ):
        """
        Handles the selection of a track within a playlist and moves it to the next position in the queue.

        Args:
            interaction (discord.Interaction): The interaction object that triggered this action.
            track (SongMeta): The track that has been selected to move within the playlist.

        Returns:
            None
        """
        idx = self.playlist_manager.playlist.index(track)
        if idx is not None:
            await self.playlist_manager.playlist.remove_by_song(track)
            await self.playlist_manager.playlist.add_next(track)
            await interaction.followup.send(
                f"Moved {track.title} to next in the playlist.", ephemeral=True
            )

    async def _search_songs(
        self,
        query: str,
        priority: bool = False,
        provider: Optional[Literal["youtube", "soundcloud"]] = None,
        limit: int = 1,
    ) -> Optional[List[SongMeta]]:
        return await Search().query(query, self.ctx, priority, provider, limit)

    def _log_song_addition(
        self, song_count: int, guild_id: int, query: str, start_time: float
    ) -> None:
        end_time = time.time()
        _log.info(
            f"Added {song_count} song(s) to guild '{guild_id}' playlist in {round(end_time-start_time,2)} seconds from query '{query}'."
        )

    async def _send_song_added_message(
        self, latest_song: SongMeta, priority: bool
    ) -> None:
        embed = self.playlist_manager.get_song_added_embed(
            self.ctx, latest_song, priority
        )
        if embed is not None:
            await self.ctx.send(embed=embed)

    async def _send_no_songs_found_message(self) -> None:
        await self.ctx.send(embed=Embed().error("No songs were found!"))

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
