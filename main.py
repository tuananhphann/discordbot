import asyncio

import discord
from discord.ext import commands

from cogs.greetings import Greeting
from cogs.music.music import Music
from cogs.tts.tts import TTS
from utils import get_env, cleanup

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix = "?", intents=intents)

    async def setup_hook(self) -> None:
        await self.tree.sync()
        print(f"Synced slash command for {self.user}")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral = True)

bot = Bot()

@bot.event
async def on_ready():
    msg = f"Logged in as {bot.user} (ID: {bot.user.id})"
    print(msg)
    print("-"*len(msg))


async def main():
    async with bot:
        TOKEN = get_env('TOKEN')
        await bot.add_cog(Music(bot))
        await bot.add_cog(Greeting(bot))
        await bot.add_cog(TTS(bot))
        await bot.start(TOKEN)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Bot ended by host.")
except:
    print("Bot ended because unknown reason.")
finally:
    cleanup()
