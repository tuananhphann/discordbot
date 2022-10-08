import asyncio
import os

import constants
import discord
import gtts
from discord.ext import commands
from gtts import gTTS

langs = gtts.tts.tts_langs()

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = constants.TTS_PATH
        self.file_name = r"\voice.mp3"
        self.full_path = self.path + self.file_name
        try: os.mkdir(self.path)
        except: None
    
    async def tts(self, ctx, text: str, lang: str = "vi"):
        loop = asyncio.get_event_loop()
        tts = await loop.run_in_executor(None, lambda: gTTS(text = text, lang = lang))
        tts.save(self.full_path)
        source = discord.FFmpegPCMAudio(self.full_path)
        ctx.voice_client.play(source)

    @commands.command()
    async def s(self, ctx, *args):
        if ctx.voice_client.is_playing():
            await ctx.send("You must wait until the speaker is free.")
        else:
            if args[0] in langs.keys():
                lang = args[0]
                text = ' '.join(args)[3:]
            else:
                lang = 'vi'
                text = ' '.join(args)
                        
            if len(text) > 300:
                await ctx.send("The number of characters exceeds the 300 character limit.")
            else:
                await self.tts(ctx, text, lang)

    @s.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(self_deaf=True)
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")




