import discord
import requests
import speedtest
from bs4 import BeautifulSoup
from discord.ext import commands


class Greeting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hello(self, ctx, member: discord.member = None, *args):
        """Just say hello"""
        member = member or ctx.author

        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f"Hello {member.name}!")
        else:
            await ctx.send(f"Hey, {member.name}. Glad to see you again!")
        self._last_member = member

    @commands.hybrid_command(name = "ping", with_app_command=True, description = "Test bot connection.")
    async def ping(self, ctx):
        """Test connection of this bot."""
        if round(self.bot.latency * 1000) <= 50:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0x44ff44)
        elif round(self.bot.latency * 1000) <= 100:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0xffd000)
        elif round(self.bot.latency * 1000) <= 200:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0xff6600)
        else:
            embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(self.bot.latency *1000)}** milliseconds!", color=0x990000)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="sleep", with_app_command=True, description="Help your sleep better.")
    async def sleep(self, ctx):
        import datetime
        current_date_and_time = datetime.datetime.now()
        # add_hours = datetime.timedelta(hours = 7)
        # current_date_and_time = current_time + add_hours
        format_time_now = str(current_date_and_time)
        time_now = format_time_now[format_time_now.find(' ')+1:format_time_now.find('.')-3]
        hours = [4,6,7,9]
        minutes = [44,14,44,14]
        wakeup = []
        session_w = []
        i=0

        def session():
            if format_time>=0 and format_time<12:
                session="sáng"
            elif format_time>=12 and format_time<18:
                session="chiều"
            elif format_time>=18:
                session="tối"
            session_time=session
            return session_time

        for i in range(4):
            hours_added = datetime.timedelta(hours = hours[i])
            minute_added = datetime.timedelta(minutes = minutes[i])
            future_date_and_time = current_date_and_time + hours_added + minute_added
            format_future_time = str(future_date_and_time)
            future_time = format_future_time[format_future_time.find(' ')+1:format_future_time.find('.')-3]
            time = format_future_time[format_future_time.find(' ')+1:format_future_time.find('.')-6]
            format_time = int(time)
            time_ses=session()
            wakeup.append(future_time)
            session_w.append(time_ses)
        await ctx.send(f'Bây giờ là {time_now}. Nếu bạn đi ngủ ngay bây giờ, bạn nên cố gắng thức dậy vào một trong những thời điểm sau: {wakeup[0]} {session_w[0]} hoặc {wakeup[1]} {session_w[1]} hoặc {wakeup[2]} {session_w[2]} hoặc {wakeup[3]} {session_w[3]}. \n\n(Thức dậy giữa một chu kỳ giấc ngủ khiến bạn cảm thấy mệt mỏi, nhưng khi thức dậy vào giữa chu kỳ tỉnh giấc sẽ làm bạn cảm thấy tỉnh táo và minh mẫn.)\n\nChúc ngủ ngon!😴')

    @commands.command()
    async def currency(self, ctx, *args):
        msg = " ".join(args)
        currency_from = msg.split(' ')[0]
        currency_to = msg.split(' ')[1]
        amount = msg.split(' ')[2]
        AmountFromAndTo=[]
        NameCurrency=[]
        InverseConversion=[]

        def get_data():
            url=f'https://vn.exchange-rates.org/converter/{currency_from.upper()}/{currency_to.upper()}/{amount}/Y'
            response=requests.get(url)
            soup=BeautifulSoup(response.content,'html.parser')
            for i in range(1,3):
                data=soup.findAll('div', class_=f'col-xs-6 result-cur{i}')
                for information in data:
                    AmountFromAndTo.append(information.find('span').text)
                    NameCurrency.append(information.find('dd').text)
                    InverseConversion.append(information.find('small').text)

        get_data()
        nl = '\n'
        await ctx.send(f"{AmountFromAndTo[0]} {NameCurrency[0].replace(nl,'')} = {AmountFromAndTo[1]} {NameCurrency[1].replace(nl,'')}")
        await ctx.send(f"{InverseConversion[0][3:-3]} | {InverseConversion[1][3:-2]}")

    @commands.command()
    async def speedtest(self, ctx):
        s = speedtest.Speedtest(secure=True)
        server = s.get_best_server()
        await ctx.send(f"Host: {server['host']} in {server['name']}, {server['country']}")
        await ctx.send('Download testing...')
        download = round(s.download()/1024/1024, 2)
        await ctx.send(f"Download speed: {download} Mbps")
        await ctx.send('Upload testing...')
        upload = round(s.upload()/1024/1024, 2)
        ping = "{:.0f}".format(float(s.results.ping))
        await ctx.send(f"Upload speed: {upload} Mbps")
        await ctx.send(f"Result:\nDownload speed: {download} Mbps = {round(float(download)*0.125, 2)} MB/s\nUpload speed: {upload} Mbps = {round(float(upload)*0.125, 2)} MB/s\nPing: {ping} ms")

    @commands.hybrid_command(name="dogimg", with_app_command=True, description="Get a random dog image.")
    async def dogimg(self, ctx):
        img = requests.get('https://dog.ceo/api/breeds/image/random').json()
        fact = requests.get('https://some-random-api.ml/facts/dog').json()
        embed = discord.Embed(title='Dog', color=discord.Color.purple()) # Create embed
        embed.set_image(url = img['message'])
        embed.set_footer(text = 'Fact: '+fact['fact'])
        await ctx.send(embed = embed)
    


    @commands.hybrid_command(name="catimg", with_app_command=True, description="Get a random cat image.")
    async def catimg(self, ctx):
        img = requests.get('https://some-random-api.ml/img/cat').json()
        fact = requests.get('https://some-random-api.ml/facts/cat').json()
        embed = discord.Embed(title='Cat', color=discord.Color.purple()) # Create embed
        embed.set_image(url = img['link'])
        embed.set_footer(text = 'Fact: '+fact['fact'])
        await ctx.send(embed = embed)
    


    @commands.hybrid_command(name="meme", with_app_command=True, description="Get a random meme.")
    async def meme(self, ctx):
        getMeme = requests.get(f'https://some-random-api.ml/meme').json()
        image = getMeme['image']
        caption = getMeme['caption']
        embed = discord.Embed(title=caption, color=discord.Color.purple()) # Create embed
        embed.set_image(url = image)
        await ctx.send(embed=embed)
