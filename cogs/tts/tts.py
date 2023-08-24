import asyncio
import logging

import discord
import gtts
from discord.ext import commands
from gtts import gTTS

import constants
from cogs.components.discord_embed import Embed

langs = gtts.tts.tts_langs()

_log = logging.getLogger(__name__)


class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = constants.TEMP_FOLDER
        self.file_name = r"\voice.mp3"
        self.full_path = self.path + self.file_name

    async def tts(self, ctx, text: str, lang: str = "vi"):
        loop = asyncio.get_event_loop()
        try:
            tts = await loop.run_in_executor(None, lambda: gTTS(text=text, lang=lang))
            tts.save(self.full_path)
        except Exception as e:
            _log.error(e)
            return
        _log.info(f"'voice.mp3' file has been saved at {self.path}.")
        source = discord.FFmpegPCMAudio(self.full_path)
        ctx.voice_client.play(source)

    @commands.command()
    async def s(self, ctx, *text):
        """
        You can change the speaker's language using the language in the list provided by the 'lang' command.
        To ensure performance of this bot. Max characters can be speak at a time are 300.
        """

        if ctx.voice_client.is_playing():
            await ctx.send("You must wait until the speaker is free.")
        else:
            if text[0] in langs.keys():
                lang = text[0]
                text = " ".join(text)[3:]
            else:
                lang = "vi"
                text = " ".join(text)

            if len(text) > 300:
                _log.error(f"Can not ready for '{text[:80]}...' (300 limit)")
                await ctx.send(
                    "The number of characters exceeds the 300 character limit."
                )
            else:
                if len(text) < 100:
                    _log.info(f"Ready for '{text}' at '{lang}'.")
                else:
                    _log.info(f"Ready for '{text[:80]}...' at '{lang}'.")
                await self.tts(ctx, text, lang)

    @commands.command()
    async def lang(self, ctx):
        """Return a list of languages avaiable."""
        embed = Embed(ctx).tts_lang(langs)
        await ctx.send(embed=embed)

    @s.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(self_deaf=True)
            else:
                await ctx.send("You are not connected to a voice channel.")
                # raise commands.CommandError(
                #     "Author not connected to a voice channel.")
