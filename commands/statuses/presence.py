from discord.ext import commands, tasks
from discord import Game, Watching, ActivityType
import itertools

class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.statuses = itertools.cycle([
            ("with the !help command 📚", ActivityType.playing),  
            (f"with {len(self.bot.users)} users 👥", ActivityType.watching),
            (f"on {len(self.bot.guilds)} servers 🌐", ActivityType.playing),
            (f"around {sum(len(guild.channels) for guild in self.bot.guilds)} channels 💬", ActivityType.watching),
            ("with my creator, ExoHayvan 🩵", ActivityType.playing)
        ])
        self.change_presence.start()  # Start the task

    def cog_unload(self):
        self.change_presence.cancel()  # Cancel the task when the cog gets unloaded

    @tasks.loop(seconds=30)
    async def change_presence(self):
        """Automatically changes the bot's presence every 30 seconds."""
        next_status, activity_type = next(self.statuses)
        if activity_type == ActivityType.playing:
            await self.bot.change_presence(activity=Game(name=next_status))
        elif activity_type == ActivityType.watching:
            await self.bot.change_presence(activity=Watching(name=next_status))
        print(f'Presence changed to: {next_status}')

    @change_presence.before_loop
    async def before_change_presence(self):
        await self.bot.wait_until_ready()  # Wait until the bot has connected to discord

async def setup(bot):
    await bot.add_cog(Presence(bot))