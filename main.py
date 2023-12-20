import asyncio
import logging

import discord
from discord.ext import commands

from cogs.game_free.game_free import GameFree
from cogs.greetings import Greeting
from cogs.music.music import Music
from cogs.tts.tts import TTS
from utils import cleanup, get_env, setup_logger

logging.getLogger(name=__name__)


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="?", intents=intents)

    # async def setup_hook(self) -> None:
    #     await self.tree.sync()
    #     print(f"Synced slash command for {self.user}")

    # async def on_command_error(self, ctx: commands.Context, error) -> None:
    #     # await ctx.reply(error, ephemeral = True)
    #     _log.error(error)
    #     pass


bot = Bot()


@bot.event
async def on_ready() -> None:
    msg: str = f"Logged in as {bot.user} (ID: {bot.user.id})"
    print(msg)
    print("-" * len(msg))


async def main() -> None:
    setup_logger(name="discord")
    setup_logger(name="cogs", level=10)
    setup_logger(name="DiscordBot")
    async with bot:
        token = get_env(key="TOKEN")
        if token is None:
            raise ValueError("Cannot find token in env.")
        await bot.add_cog(Music(bot))
        await bot.add_cog(Greeting(bot))
        await bot.add_cog(TTS(bot))
        await bot.add_cog(GameFree(bot))
        await bot.start(token=token)


try:
    asyncio.run(main=main())
except KeyboardInterrupt:
    print("Bot ended by host.")
except Exception as ex:
    print(
        f"""Bot ended because under reasons:
          {ex}"""
    )
finally:
    cleanup()
