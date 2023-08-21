import asyncio

import discord
from discord.ext import commands

from cogs.greetings import Greeting
from cogs.music.music import Music
from cogs.tts.tts import TTS
from cogs.game_free.game_free import GameFree
from utils import cleanup, get_env, setup_logger


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix = "?", intents=intents)

    # async def setup_hook(self) -> None:
    #     await self.tree.sync()
    #     print(f"Synced slash command for {self.user}")

    async def on_command_error(self, ctx, error) -> None:
        await ctx.reply(error, ephemeral = True)

bot = Bot()

@bot.event
async def on_ready() -> None:
    msg = f"Logged in as {bot.user} (ID: {bot.user.id})"
    print(msg)
    print("-"*len(msg))


async def main() -> None:
    setup_logger(name='discord')
    setup_logger(name='cogs', level = 10)
    async with bot:
        token: str = get_env(key='TOKEN')
        await bot.add_cog(Music(bot))
        await bot.add_cog(Greeting(bot))
        await bot.add_cog(TTS(bot))
        await bot.add_cog(GameFree(bot))
        await bot.start(token=token)

try:
    asyncio.run(main=main())
except KeyboardInterrupt:
    print("Bot ended by host.")
except Exception as e:
    print("Bot ended because under reasons.")
    print(e)
finally:
    cleanup()
