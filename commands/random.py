import re
from discord.ext import commands
import string
import random
import aiohttp
import discord
import requests
import emoji

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.total_anime = 0
        self.bot.loop.create_task(self.set_total_anime())

    async def set_total_anime(self):
        query = """
        query {
            Page(page: 1, perPage: 1) {
                pageInfo {
                    total
                    perPage
                    currentPage
                    lastPage
                    hasNextPage
                }
                media(type: ANIME, sort: ID) {
                    id
                }
            }
        }
        """
        url = 'https://graphql.anilist.co'
        response = await self.session.post(url, json={'query': query})
        data = await response.json()

        if response.status == 200 and "data" in data and "Page" in data["data"]:
            self.total_anime = data["data"]["Page"]["pageInfo"]["total"]

    async def fetch(self, url):
        try:
            async with self.session.get(url) as response:
                return await response.text()
        except Exception:
            return None

    @commands.group(invoke_without_command=True)
    async def random(self, ctx):
        """Shows a help message for the random group command."""
        await ctx.send("Use !random with one of the following: website, reddit, saying, emoji")

    @random.command()
    async def website(self, ctx):
        """Returns a random website."""

        loading_message = await ctx.send(embed=discord.Embed(
            title="Generating a random website…",
        ))

        html = await self.fetch("http://random.whatsmyip.org/")
        if html is not None:
            random_url = re.search(r'<a\s+id="random_link"\s+target="_top"\s+href="(.*?)"\s+style="display:\s+inline;">', html)
            if random_url:
                random_url = random_url.group(1)
                await loading_message.edit(embed=discord.Embed(
                    title="Random Website", 
                    description=random_url,
                    footer="This is a randomly generated website. Please browse at your own risk."
                ))
            else:
                await ctx.send("Failed to find random URL in HTML")
        else:
            await ctx.send("Failed to fetch random URL")

    @random.command()
    async def reddit(self, ctx):
        """Returns a link to a random subreddit."""
        result = "https://www.reddit.com/r/random"

        embed = discord.Embed(title="Random Subreddit", description=f"{result}")
        embed.set_footer(text="This link directs to a random subreddit. The content is randomly generated. Please browse at your own risk. Refresh the page to generate a new subreddit.")

        await ctx.send(embed=embed)

    @random.command()
    async def saying(self, ctx):
        """Returns a random saying."""
        response = requests.get("https://api.quotable.io/random")
    
        if response.status_code == 200:
            try:
                data = response.json()
                quote = data['content']
                author = data['author']

                embed = discord.Embed(title="Random Saying", description=f'"{quote}" - {author}')
                embed.set_footer(text="This is a randomly generated saying. Interpret at your own risk.")
                await ctx.send(embed=embed)
            except json.JSONDecodeError:
                await ctx.send("Sorry, the quote API did not return valid JSON.")
        else:
            await ctx.send("Sorry, I couldn't fetch a saying right now.")

    @random.command()
    async def emoji(self, ctx):
        """Returns a random emoji."""
        emoji_start = 0x1F300
        emoji_end = 0x1F9FF
        random_code_point = random.randint(emoji_start, emoji_end)
        random_emoji = chr(random_code_point)
        
        embed = discord.Embed(title="Random Emoji", description=random_emoji)
        embed.set_footer(text="This is a randomly generated emoji.")
        
        emoji_url = f"https://twemoji.maxcdn.com/v/latest/72x72/{random_code_point:x}.png"
        embed.set_thumbnail(url=emoji_url)

        await ctx.send(embed=embed)
        
    @random.command()
    async def anime(self, ctx):
        """Returns a random anime."""
        # Use the self.total_anime value to get a random anime id
        if self.total_anime == 0:
            await ctx.send("Sorry, I couldn't fetch the total number of anime.")
            return

        id = random.randint(1, self.total_anime)

        query = '''
        query ($id: Int) {
            Media (id: $id, type: ANIME) {
                id
                title {
                    romaji
                    english
                }
                description (asHtml: false)
                coverImage {
                    extraLarge
                }
            }
        }
        '''

        variables = {
            'id': id
        }
        url = 'https://graphql.anilist.co'

        response = await self.session.post(url, json={'query': query, 'variables': variables})
        data = await response.json()

        if response.status == 200:
            if "data" in data and "Media" in data["data"]:
                anime = data["data"]["Media"]
                embed = discord.Embed(title="Random Anime", description=anime["description"])
                embed.set_footer(text="This is a randomly generated anime. Please watch at your own risk.")
                embed.set_thumbnail(url=anime["coverImage"]["extraLarge"])
                await ctx.send(embed=embed)
            else:
                await ctx.send("Sorry, the Anilist API did not return a valid anime.")
        else:
            await ctx.send("Sorry, I couldn't fetch an anime right now.")
            
async def setup(bot):
    await bot.add_cog(Random(bot))
