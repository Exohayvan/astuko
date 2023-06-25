from discord.ext import commands
from discord import Permissions
import datetime
import asyncio
import discord
import sqlite3
import os

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime_start = datetime.datetime.utcnow()
        self.init_db()
        self.init_daily_uptime_db()
        self.migrate_from_file_if_exists()
        self.bot_start_time = datetime.datetime.utcnow()
        self.total_uptime = self.load_total_uptime()
        self.bot.loop.create_task(self.uptime_background_task())

    def connect_db(self):
        """Connects to the specific database."""
        rv = sqlite3.connect('./data/uptime.db')
        rv.row_factory = sqlite3.Row
        return rv
        
    def init_daily_uptime_db(self):
        """Initializes the daily uptime database."""
        db = self.connect_db()
        db.execute("CREATE TABLE IF NOT EXISTS daily_uptime (date DATE, uptime INTEGER);")
        db.commit()
    
    def init_db(self):
        """Initializes the database."""
        db = self.connect_db()
        db.execute("CREATE TABLE IF NOT EXISTS uptime (total_uptime INTEGER);")
        db.execute("INSERT INTO uptime (total_uptime) SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM uptime);")
        db.commit()

    def migrate_from_file_if_exists(self):
        """If total_uptime.txt exists, migrate its data to the database and delete the file."""
        if os.path.exists("total_uptime.txt"):
            with open("total_uptime.txt", "r") as f:
                total_uptime_seconds = int(f.read())
                self.save_total_uptime(total_uptime_seconds)
                os.remove("total_uptime.txt")

    def format_timedelta(self, delta):
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds."

    def load_total_uptime(self):
        db = self.connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT total_uptime FROM uptime")
        total_uptime_seconds = cursor.fetchone()[0]
        return datetime.timedelta(seconds=total_uptime_seconds)

    def save_total_uptime(self, total_uptime_seconds=None):
        if total_uptime_seconds is None:
            total_uptime_seconds = int(self.total_uptime.total_seconds())
        db = self.connect_db()
        db.execute("UPDATE uptime SET total_uptime = ?", (total_uptime_seconds,))
        db.commit()

    async def uptime_background_task(self):
        while True:
            await asyncio.sleep(60)
            current_uptime = datetime.datetime.utcnow() - self.uptime_start
            self.total_uptime += current_uptime
            self.save_total_uptime()
            self.uptime_start += datetime.timedelta(minutes=1)  # increment the start time instead of resetting it

    @commands.Cog.listener()
    async def on_ready(self):
        self.uptime_start = datetime.datetime.utcnow()

    @commands.command()
    async def info(self, ctx):
        """Provides detailed information about the bot."""
        creation_time = self.bot.user.created_at
        owner_id = 276782057412362241  # change this to your user ID
        github_link = "https://github.com/Exohayvan/astuko"  # change this to your repository URL
        library_version = discord.__version__  # discord.py library version
        permissions = Permissions.all()
        invite_link = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions={permissions.value}&scope=bot"

        owner = await self.bot.fetch_user(owner_id)

        embed = discord.Embed(
            title="🤖 Bot Information",
            description=f"Here is some info about {self.bot.user.name}!",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(name=":bust_in_silhouette: Owner", value=f"{owner.name}#{owner.discriminator}", inline=True)
        embed.add_field(name=":calendar: Created On", value=creation_time.strftime("%B %d, %Y at %H:%M UTC"), inline=True)
        embed.add_field(name=":books: Library", value=f"discord.py {library_version}", inline=True)
        embed.add_field(name=":link: GitHub", value=f"[Repository]({github_link})", inline=True)
        embed.add_field(name=":mailbox_with_mail: Invite", value=f"[Click here]({invite_link})", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        """Generates an invite link for the bot."""
        permissions = Permissions.all()
        invite_link = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions={permissions.value}&scope=bot"
        await ctx.send(f"Invite me to your server using this link: {invite_link}")

    @commands.command()
    async def stats(self, ctx):
        """Shows the bot's current stats, including the number of guilds, users, and more."""
        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        total_text_channels = sum(len(guild.text_channels) for guild in self.bot.guilds)
        total_voice_channels = total_channels - total_text_channels
        total_roles = sum(len(guild.roles) for guild in self.bot.guilds)
        api_latency = round(self.bot.latency * 1000, 2)  # in milliseconds

        # Presence information
        total_online = total_idle = total_dnd = total_offline = 0
        for guild in self.bot.guilds:
            for member in guild.members:
                if str(member.status) == "online":
                    total_online += 1
                elif str(member.status) == "idle":
                    total_idle += 1
                elif str(member.status) == "dnd":
                    total_dnd += 1
                else:
                    total_offline += 1

        # Emoji count
        total_emojis = sum(len(guild.emojis) for guild in self.bot.guilds)

        embed = discord.Embed(title="Bot Stats", color=discord.Color.blue())

        embed.add_field(name=":satellite: Servers", value=str(total_guilds), inline=True)
        embed.add_field(name=":busts_in_silhouette: Users", value=str(total_users), inline=True)
        embed.add_field(name=":file_folder: Channels", value=str(total_channels), inline=True)
        embed.add_field(name=":speech_balloon: Text Channels", value=str(total_text_channels), inline=True)
        embed.add_field(name=":loud_sound: Voice Channels", value=str(total_voice_channels), inline=True)
        embed.add_field(name=":military_medal: Roles", value=str(total_roles), inline=True)
        embed.add_field(name=":stopwatch: API Latency", value=f"{api_latency} ms", inline=True)
        embed.add_field(name=":green_heart: Online Users", value=str(total_online), inline=True)
        embed.add_field(name=":yellow_heart: Idle Users", value=str(total_idle), inline=True)
        embed.add_field(name=":heart: DND Users", value=str(total_dnd), inline=True)
        embed.add_field(name=":black_heart: Offline Users", value=str(total_offline), inline=True)
        embed.add_field(name=":smiley: Emojis", value=str(total_emojis), inline=True)

        # Most used commands
        number_of_commands = 3
        conn = sqlite3.connect('./data/command_usage.db')
        c = conn.cursor()

        # Get the most used commands
        c.execute('SELECT command_name, SUM(usage_count) as total_usage FROM CommandUsage GROUP BY command_name ORDER BY total_usage DESC LIMIT ?', (number_of_commands,))

        most_used_commands = c.fetchall()
        conn.close()

        # Add most used commands to the embed
        if most_used_commands:
            embed.add_field(name="Most Used Commands", value="\n".join(f"**{command[0]}**: {command[1]} uses" for command in most_used_commands), inline=False)

        await ctx.send(embed=embed)

    async def uptime_background_task(self):
        while True:
            await asyncio.sleep(60)
            current_uptime = datetime.datetime.utcnow() - self.uptime_start
            self.total_uptime += current_uptime
            self.save_total_uptime()
            self.save_daily_uptime(current_uptime)  # save the current uptime to the daily uptime database
            self.uptime_start += datetime.timedelta(minutes=1)
    def get_uptime_for_last_30_days(self):
        date_today = datetime.date.today()
        cutoff_date = date_today - datetime.timedelta(days=30)
    
        db = self.connect_db()
        cursor = db.cursor()
    
        # Get the sum of the uptime for the last 30 days
        cursor.execute("SELECT SUM(uptime) as total_uptime FROM daily_uptime WHERE date >= ?", (cutoff_date,))
        result = cursor.fetchone()
    
        return datetime.timedelta(seconds=result['total_uptime'] if result['total_uptime'] else 0)
    
    def save_daily_uptime(self, current_uptime):
        date_today = datetime.date.today()
        daily_uptime_seconds = int(current_uptime.total_seconds())
    
        db = self.connect_db()
        cursor = db.cursor()
    
        # Check if today's record already exists
        cursor.execute("SELECT * FROM daily_uptime WHERE date = ?", (date_today,))
        record = cursor.fetchone()
    
        if record:
            # If today's record exists, update it
            new_daily_uptime_seconds = record['uptime'] + daily_uptime_seconds
            cursor.execute("UPDATE daily_uptime SET uptime = ? WHERE date = ?", (new_daily_uptime_seconds, date_today))
        else:
            # If today's record does not exist, insert it
            cursor.execute("INSERT INTO daily_uptime (date, uptime) VALUES (?, ?)", (date_today, daily_uptime_seconds))
    
        # Delete records older than 31 days
        cutoff_date = date_today - datetime.timedelta(days=31)
        cursor.execute("DELETE FROM daily_uptime WHERE date < ?", (cutoff_date,))
    
        db.commit()
    
    @commands.command()
    async def uptime(self, ctx):
        """Shows the current uptime of the bot since last restart."""
        current_uptime = datetime.datetime.utcnow() - self.bot_start_time
        total_uptime = self.total_uptime + current_uptime
        uptime_last_30_days = self.get_uptime_for_last_30_days()
        total_seconds_last_30_days = 30 * 24 * 60 * 60
        uptime_percentage_last_30_days = (uptime_last_30_days.total_seconds() / total_seconds_last_30_days) * 100
    
        embed = discord.Embed(title="Current Uptime", color=discord.Color.blue())
        embed.add_field(name="Since Last Restart", value=self.format_timedelta(current_uptime), inline=False)
        embed.add_field(name="Lifetime", value=self.format_timedelta(total_uptime), inline=False)
        embed.add_field(name="Last 30 Days", value=f"{uptime_percentage_last_30_days:.2f}% of total time", inline=False)
    
        await ctx.send(embed=embed)
        
    #@commands.command()
    async def lifetime(self, ctx):
        """Shows the total lifetime uptime of the bot."""
        # Lifetime uptime includes current uptime
        current_uptime = datetime.datetime.utcnow() - self.uptime_start
        total_uptime = self.total_uptime + current_uptime
        await self.send_uptime_message(ctx, "Total Lifetime Uptime", total_uptime)

    async def send_uptime_message(self, ctx, title, delta):
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60
        seconds = delta.seconds % 60

        uptime_string = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds."

        embed = discord.Embed(title=title, color=discord.Color.blue())
        embed.add_field(name="Uptime", value=uptime_string, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
