import discord
from cogs.music.song import Song
from cogs.music.playlist import PlayList

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
        [{song.TITLE}]({song.YT_URL})
        Channel: {song.CHANNEL}
        Views: {song.VIEW_COUNT}
        Duration: {song.DURATION}
        Upload date: {song.UPLOAD_DATE}
        """
        self.embed.set_thumbnail(url=song.THUMBNAIL)
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}", icon_url=self.ctx.author.avatar.url)
        return self.embed

    def in_playlist(self, playlist: PlayList):
        """playlist template"""
        self.embed.title = "In playlist"
        self.embed.color = discord.Color.green()
        self.embed.description = ""
        for song in playlist:
            self.embed.description += f"{playlist.index(song)+1}. [{song.TITLE}]({song.YT_URL})\n"
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}", icon_url=self.ctx.author.avatar.url)
        return self.embed
    
    def add_song(self, song, position: int, timewait: str):
        self.embed.title = "Added song"
        self.embed.color = discord.Color.orange()
        self.embed.description = f"""
        Song: [{song.TITLE}]({song.YT_URL})
        Position in playlist: {position}
        Estimate time to this song: {timewait}
        """
        self.embed.set_footer(
            text=f"Requested by {self.ctx.author.name}", icon_url=self.ctx.author.avatar.url)
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