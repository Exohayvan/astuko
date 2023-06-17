from discord.ext import commands
import datetime
import asyncio
import discord

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime_start = datetime.datetime.utcnow()
        self.total_uptime = self.load_total_uptime()
        self.bot.loop.create_task(self.uptime_background_task())

    def load_total_uptime(self):
        try:
            with open("total_uptime.txt", "r") as f:
                total_uptime_seconds = int(f.read())
                return datetime.timedelta(seconds=total_uptime_seconds)
        except FileNotFoundError:
            return datetime.timedelta(seconds=0)

    def save_total_uptime(self):
        total_uptime_seconds = int(self.total_uptime.total_seconds())
        with open("total_uptime.txt", "w") as f:
            f.write(str(total_uptime_seconds))

    async def uptime_background_task(self):
        while True:
            current_uptime = datetime.datetime.utcnow() - self.uptime_start
            self.total_uptime += current_uptime
            self.save_total_uptime()
            self.uptime_start = datetime.datetime.utcnow()
            await asyncio.sleep(60)

    @commands.Cog.listener()
    async def on_ready(self):
        self.uptime_start = datetime.datetime.utcnow()

    @commands.command()
    async def uptime(self, ctx):
        """Shows the current uptime of the bot since last reboot."""
        current_uptime = datetime.datetime.utcnow() - self.uptime_start
        await self.send_uptime_message(ctx, "Current Uptime", current_uptime)

    @commands.command()
    async def lifetime(self, ctx):
        """Shows the total lifetime uptime of the bot."""
        # Lifetime uptime includes current uptime
        current_uptime = datetime.datetime.utcnow() - self.uptime_start
        total_uptime = self.total_uptime + current_uptime
        await self.send_uptime_message(ctx, "Total Lifetime Uptime", total_uptime)

    async def send_uptime_message(self, ctx, title, delta):
        days, seconds = delta.days, delta.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        uptime_string = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds."

        embed = discord.Embed(title=title, color=discord.Color.blue())
        embed.add_field(name="Uptime", value=uptime_string, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
