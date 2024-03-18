import asyncio
import logging
import traceback

import discord
from cogs.admin.admin import Admin
from cogs.greetings import Greeting
from cogs.music.music import Music
from cogs.tts.tts import TTS
from discord.ext import commands
from utils.utils import cleanup, get_env, setup_logger

logging.getLogger(name=__name__)


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="?", intents=intents)

    # async def setup_hook(self) -> None:
    #     await self.tree.sync()
    #     print(f"Synced slash command for {self.user}")

    async def on_command_error(self, ctx: commands.Context, error) -> None:
        await ctx.reply("There was an error 🥲", ephemeral=True)
        # _log.error(error)
        pass


bot = Bot()


@bot.event
async def on_ready() -> None:
    msg: str = f"Logged in as {bot.user} (ID: {bot.user.id})"
    print(msg)
    print("-" * len(msg))


async def main() -> None:
    setup_logger(name="discord", level=logging.INFO)
    setup_logger(name="cogs")
    setup_logger(name="discordbot")
    setup_logger(name="pytube", level=logging.INFO)

    async with bot:
        token = get_env(key="TOKEN")
        if token is None:
            raise ValueError("Cannot find token in env.")
        await bot.add_cog(Music(bot))
        await bot.add_cog(Greeting(bot))
        await bot.add_cog(TTS(bot))
        await bot.add_cog(Admin(bot))
        await bot.start(token=token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        for vc in bot.voice_clients:
            vc.disconnect()
        print("Bot terminated by host.")
    except Exception:
        print(
            f"Bot terminated because of the following error:\n{traceback.format_exc()}"
        )
    finally:
        cleanup()
