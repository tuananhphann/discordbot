from discord.ext import commands

from cogs.music.controller import Audio
from cogs.components.discord_embed import Embed


class Music(commands.Cog):
    """Music cog for my OneNine4 Bot"""
    def __init__(self, bot):
        self.bot = bot
        self.player = Audio(bot)

    @commands.command()
    async def p(self, ctx, *args):
        track = ' '.join(args)
        print("Search for:",track)
        await self.player.process_track(ctx, track)
    
    @commands.command()
    async def pn(self, ctx, *args):
        track = ' '.join(args)
        await self.player.process_track(ctx, track, True)
    
    @commands.hybrid_command(name = "playlist", with_app_command=True, description = "Show the current playlist.")
    async def queue(self, ctx):
        if self.player.playlist.size() == 0:
            await ctx.send(embed = Embed(ctx).error(description="There are no songs in the playlist."))
        else:
            embed = Embed(ctx).in_playlist(self.player.playlist.get_list())
            await ctx.send(embed = embed)
    
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await ctx.send(embed = Embed(ctx).error(description="No songs are playing."))

    @commands.command()
    async def stop(self, ctx: commands.Context):
        "Clear the queue, stop playing music and leave the channel."
        self.player.playlist.clear()
        await ctx.voice_client.disconnect()

    @commands.command()
    async def come(self, ctx: commands.Context):
        if ctx.author.voice.channel != ctx.voice_client.channel:
            ctx.voice_client.pause()
            await ctx.voice_client.disconnect()
            await ctx.author.voice.channel.connect(self_deaf=True)
            ctx.voice_client.resume()


    @p.before_invoke
    @come.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(self_deaf=True)
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")