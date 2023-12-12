from discord.ext import commands
import sqlite3
import asyncio
import datetime
from discord.ext import tasks

class KeepClean(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = './data/db/keepclean.db'
        self.check_messages.start()

    def cog_unload(self):
        self.check_messages.cancel()

    @commands.group()
    async def keepclean(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid keepclean command. Use `keepclean on`, `keepclean off`, or `keepclean on <mins>`.")

    @keepclean.command(name='on')
    async def keepclean_on(self, ctx, mins: int = 60):
        self.update_channel(ctx.channel.id, mins)
        await ctx.send(f"KeepClean is now ON for {mins} minutes in this channel.")

    @keepclean.command(name='off')
    async def keepclean_off(self, ctx):
        self.remove_channel(ctx.channel.id)
        await ctx.send("KeepClean is now OFF for this channel.")

    @tasks.loop(minutes=5)
    async def check_messages(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT channel_id, time_limit FROM Channels")
            channels = cursor.fetchall()

        for channel_id, time_limit in channels:
            channel = self.bot.get_channel(channel_id)
            if channel:
                async for message in channel.history(limit=None, after=datetime.datetime.utcnow() - datetime.timedelta(minutes=time_limit)):
                    await message.delete()
            else:
                self.remove_channel(channel_id)

    def update_channel(self, channel_id, time_limit):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO Channels (channel_id, time_limit) VALUES (?, ?)", (channel_id, time_limit))
            conn.commit()

    def remove_channel(self, channel_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Channels WHERE channel_id = ?", (channel_id,))
            conn.commit()

async def setup(bot):
    await bot.add_cog(KeepClean(bot))
