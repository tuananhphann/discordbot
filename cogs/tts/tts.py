import asyncio
import logging
import os
import gtts
from gtts import gTTS
import discord
from discord.ext import commands
from .tts_constants import *

langs = gtts.tts.tts_langs()
_log = logging.getLogger(__name__)

class TTS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), TEMP_FOLDER)
        self.full_path = os.path.join(self.temp_path, TEMP_FILENAME)
        
        # Ensure temp folder exists
        os.makedirs(self.temp_path, exist_ok=True)

    async def tts(self, ctx: commands.Context, text: str, lang: str = DEFAULT_LANG) -> None:
        loop = asyncio.get_event_loop()
        try:
            tts = await loop.run_in_executor(None, lambda: gTTS(text=text, lang=lang))
            await loop.run_in_executor(None, tts.save, self.full_path)
            _log.info(f"'voice.mp3' file has been saved at {self.temp_path}.")
            
            source = discord.FFmpegPCMAudio(self.full_path)
            ctx.voice_client.play(source)
        except Exception as e:
            _log.error(f"Error in TTS: {e}")
            await ctx.send("There was an error processing your TTS request.")

    @commands.command()
    async def s(self, ctx: commands.Context, *text: str):
        """
        Converts text to speech and plays it in the voice channel.
        
        Usage: ?s [lang] your text here
        You can change the speaker's language using the language codes provided by the 'lang' command.
        """
        if ctx.voice_client.is_playing():
            await ctx.send("You must wait until the speaker is free.")
            return

        lang, text = self._parse_lang_and_text(text)
        
        if len(text) > MAX_TTS_CHARS:
            truncated = text[:TRUNCATED_CHARS]
            _log.error(f"TTS text too long: '{truncated}...' ({MAX_TTS_CHARS} limit)")
            await ctx.send(f"The text exceeds the {MAX_TTS_CHARS} character limit.")
            return

        _log.info(f"TTS request: '{text[:TRUNCATED_CHARS]}...' in '{lang}'.")
        await self.tts(ctx, text, lang)

    def _parse_lang_and_text(self, text_args: tuple) -> tuple:
        if text_args[0] in langs.keys():
            return text_args[0], " ".join(text_args[1:])
        return DEFAULT_LANG, " ".join(text_args)

    @commands.command()
    async def lang(self, ctx: commands.Context):
        """Return a list of available languages."""
        embed = Embed(ctx).tts_lang(langs)
        await ctx.send(embed=embed)

    @s.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(self_deaf=True)
            else:
                await ctx.send("You are not connected to a voice channel.")
