import constants
import discord
from cogs.components.discord_embed import Embed
from cogs.music.playlist import PlayList
from cogs.music.search import Search, Song
from discord.ext import commands
from utils import *


class Audio:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.playlist = PlayList()
        self.current_song = None
        self.current_song_duration = None
        self.start_time = None

    def play_next(self, ctx):
        song = self.playlist.get_next()
        if song == None:
            self.current_song = None
            return
        coro = self.play(ctx, song)
        self.bot.loop.create_task(coro)

    async def play(self, ctx: commands.Context, song: Song):
        self.start_time = convert_to_second(get_time())
        self.current_song_duration = convert_to_second(song.DURATION)
        
        source = discord.FFmpegPCMAudio(song.URL, **constants.FFMPEG_OPTIONS)
        embed = Embed(ctx).now_playing_song(song)
        await ctx.defer(ephemeral=True)
        await ctx.reply(embed = embed)
        # await ctx.reply(embed=embed)
        ctx.voice_client.play(source, after=lambda e: self.play_next(ctx))
        self.current_song = song.TITLE

    async def process_track(self, ctx: commands.Context, track: str, priority: bool = False):
        song = await Search().query(track)
        if type(song) == str:
            embed = Embed(ctx).error(song)
            await ctx.send(embed = embed)
            return
        
        if self.current_song == None:
            await self.play(ctx, song)
        else:
            if priority == True:
                current_time = convert_to_second(get_time())
                time_wait = self.current_song_duration - (current_time - self.start_time)

                self.playlist.add_next(song)
                embed = Embed(ctx).add_song(song, self.playlist.index(song)+1, f"Next, about {convert_to_time(time_wait)}")
                await ctx.send(embed=embed)
            else:
                current_time = convert_to_second(get_time())
                time_wait = self.current_song_duration - (current_time - self.start_time) + convert_to_second(self.playlist.time_wait())
                
                self.playlist.add(song)
                embed = Embed(ctx).add_song(song, position = self.playlist.index(song)+1, timewait = convert_to_time(time_wait))
                await ctx.send(embed=embed)
