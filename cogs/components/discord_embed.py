from typing import List, Union

import discord
from discord.ext import commands

from cogs.music.core.song import Song, SongMeta


class Embed:
    """Discord embed templates"""

    def __init__(self, ctx: commands.Context | None = None) -> None:
        self.ctx = ctx
        self.embed = discord.Embed()

    def help(self) -> None:
        pass

    def normal(self, title=None, color=None, description=None) -> discord.Embed:
        self.embed.title = title
        self.embed.color = color
        self.embed.description = description
        return self.embed

    def leave_channel_message(self, minutes: int = 10) -> discord.Embed:
        return self.normal(
            color=discord.Colour.red(),
            description=f"Leave the voice channel after {minutes} minutes of inactivity.",
        )

    def now_playing_song(self, song: Song) -> discord.Embed:
        """Now playing template"""
        self.embed.title = "Now playing"
        self.embed.color = discord.Color.blue()
        self.embed.description = f"""
        [{song.title}]({song.webpage_url})
        Uploader: {song.uploader}
        Playback counts: {song.playback_count}
        Duration: {song.duration}
        Upload date: {song.upload_date}
        """
        if song.album is not None:
            self.embed.description += f"Album: {song.album.title}"

        self.embed.set_thumbnail(url=song.thumbnail)
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}",
            icon_url=self.ctx.author.avatar.url if self.ctx.author.avatar else None,
        )
        return self.embed

    def in_playlist(self, playlist: List[SongMeta]) -> discord.Embed:
        """playlist template"""
        self.embed.title = "In the playlist (10 songs next)"
        self.embed.color = discord.Color.green()
        self.embed.description = ""
        for song in playlist:
            self.embed.description += (
                f"{playlist.index(song)+1}. [{song.title}]({song.webpage_url})\n"
            )
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}",
            icon_url=self.ctx.author.avatar.url if self.ctx.author.avatar else None,
        )
        return self.embed

    def add_song(self, song, position: int, timewait: str) -> discord.Embed:
        self.embed.title = "Song added"
        self.embed.color = discord.Color.orange()
        self.embed.description = f"""
        Song: [{song.title}]({song.webpage_url})
        Position in playlist: {position}
        Estimate time to this song: {timewait}
        """
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}",
            icon_url=self.ctx.author.avatar.url if self.ctx.author.avatar else None,
        )
        return self.embed

    def error(self, description: str, title: str | None = None) -> discord.Embed:
        self.embed.title = title
        self.embed.color = discord.Color.red()
        self.embed.description = description
        return self.embed

    def ok(self, description: str, title: str | None = None) -> discord.Embed:
        self.embed.title = title
        self.embed.color = discord.Color.green()
        self.embed.description = description
        return self.embed

    def tts_lang(self, lang_dict: dict) -> discord.Embed:
        self.embed.title = "Language List"
        self.embed.color = discord.Color.green()
        self.embed.description = ""
        for lang in lang_dict:
            self.embed.description += f"{lang}: {lang_dict[lang]}\n"
        return self.embed

    def game_free(self, game) -> discord.Embed:
        if len(game["title"]) > 256:
            self.embed.title = game["title"][:253] + "..."
        else:
            self.embed.title = game["title"]
        self.embed.description = f"""
        Link: {game['link']}
        Posted by {game['author']}
        Posting date: {game['date']}
        Link post: {game['id']}
        """
        self.embed.color = 0xFFA500
        self.embed.set_footer(text="Reddit", icon_url="https://i.imgur.com/sdO8tAw.png")
        return self.embed

    def end_playlist(self) -> discord.Embed:
        self.embed.title = "End playlist"
        self.embed.description = "There is no song in the playlist!"
        self.embed.color = discord.Color.green()
        return self.embed

    def summary(
        self, total_income, total_expense, balance, most_expense, most_income, month
    ) -> discord.Embed:
        self.embed.title = f"Summary of your account in {month}"
        self.embed.color = discord.Color.green()
        self.embed.description = f"""
        Total income: {total_income}
        Total expense: {total_expense}
        Balance: {balance}
        Most expense: {most_expense}
        Most income: {most_income}
        """
        return self.embed
