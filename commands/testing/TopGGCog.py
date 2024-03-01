import discord
from discord.ext import commands, tasks
import requests
import json
import asyncio

class TopGGCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjQwNzkyOTQ4NjIwNjU2NjQwMCIsImJvdCI6dHJ1ZSwiaWF0IjoxNzA5MjY1NzUwfQ.Lr3WQMviNrJVEYBF3PpZDmVSJ11gOx6f-HVGI6Ghuzw'
        self.server_count_post.start()

    def cog_unload(self):
        self.server_count_post.cancel()

    async def post_server_count(self):
        server_count = len(self.bot.guilds)  # Get the current server count
        headers = {
            'Authorization': self.token
        }
        payload = {
            'server_count': server_count
        }
        url = f"https://top.gg/api/bots/{self.bot.user.id}/stats"
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            print('Server count posted successfully:', response.text)
        except requests.RequestException as e:
            print('Error posting server count:', e)

    @tasks.loop(hours=6)  # Run every 6 hours
    async def server_count_post(self):
        await self.bot.wait_until_ready()
        await self.post_server_count()

def setup(bot):
    bot.add_cog(TopGGCog(bot))
