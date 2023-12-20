from typing import Deque

import discord

from cogs.music.playlist import PlayList
from cogs.music.song import Song


class Embed:
    """Discord embed templates"""

    def __init__(self, ctx):
        self.ctx = ctx
        self.embed = discord.Embed()

    def help(self):
        pass

    def now_playing_song(self, song: Song):
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
        self.embed.set_thumbnail(url=song.thumbnail)
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}",
            icon_url=self.ctx.author.avatar.url,
        )
        return self.embed

    def in_playlist(self, playlist: Deque[Song]):
        """playlist template"""
        self.embed.title = "In playlist"
        self.embed.color = discord.Color.green()
        self.embed.description = ""
        for song in playlist:
            self.embed.description += (
                f"{playlist.index(song)+1}. [{song.title}]({song.webpage_url})\n"
            )
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}",
            icon_url=self.ctx.author.avatar.url,
        )
        return self.embed

    def add_song(self, song, position: int, timewait: str):
        self.embed.title = "Added song"
        self.embed.color = discord.Color.orange()
        self.embed.description = f"""
        Song: [{song.title}]({song.webpage_url})
        Position in playlist: {position}
        Estimate time to this song: {timewait}
        """
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}",
            icon_url=self.ctx.author.avatar.url,
        )
        return self.embed

    def error(self, description: str):
        self.embed.title = "Error"
        self.embed.color = discord.Color.red()
        self.embed.description = description
        return self.embed

    def tts_lang(self, lang_dict: dict):
        self.embed.title = "Language List"
        self.embed.color = discord.Color.green()
        self.embed.description = ""
        for lang in lang_dict:
            self.embed.description += f"{lang}: {lang_dict[lang]}\n"
        return self.embed

    def game_free(self, game):
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
