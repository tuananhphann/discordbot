import logging
from datetime import datetime

import asyncpraw
import constants
from cogs.components.discord_embed import Embed
from discord.ext import commands, tasks
from table import Table
from utils import get_env

_log = logging.getLogger(__name__)

class GameFree(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.channel_id = constants.GAMEFREE_CHANNEL_ID
        self.games = []
        self.keywords = ['free','100%','100% off','free/100% off']
        self.table = Table("game_data.db")
        self.update.start()

    @tasks.loop(seconds=constants.RENEW_TIME)
    async def update(self):
        _log.info("Renew update task.")
        game_channel = self.bot.get_channel(self.channel_id)
        
        reddit = asyncpraw.Reddit(
            client_id=get_env("REDDIT_CLIENT_ID"),
            client_secret=get_env("REDDIT_CLIENT_SECRET"),
            user_agent=get_env("REDDIT_USER_AGENT")
        )

        subreddit = await reddit.subreddit('GameDeals')

        for keyword in self.keywords:
            async for post in subreddit.search(keyword):
                if self.table.checkRecord("GameFree", post.title, "Title") == False and post.link_flair_text != "Expired":
                    self.games.append({'title':post.title,'link':post.url,'id':f"https://reddit.com/{post.id}",'author':post.author.name,'date':datetime.fromtimestamp(post.created_utc).strftime('%d-%m-%Y %H:%M:%S'),'flair':post.link_flair_text})
                    self.table.addRecord("GameFree", post.id, post.title, post.url, post.author.name, datetime.fromtimestamp(post.created_utc).strftime('%d-%m-%Y %H:%M:%S'), str(post.link_flair_text))
        
        if len(self.games) > 0:
            self.games.reverse()
            _log.info(f"Found {len(self.games)} new games.")
            for game in self.games:
                game_embed = Embed(None).game_free(game)
                await game_channel.send(embed = game_embed)
                _log.info(f"New game: {game['title']}.")
        self.games.clear()
        await reddit.close()

    
    @update.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()
