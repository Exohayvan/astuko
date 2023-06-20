import discord
from discord.ext import commands
import asyncio
import datetime
import sqlite3
import json
from discord.errors import NotFound

class Voting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('./data/voting.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_votes (
                title TEXT PRIMARY KEY,
                message_id INTEGER,
                channel_id INTEGER,
                option_emojis TEXT,
                votes TEXT,
                start_time TEXT,
                duration INTEGER,
                user_votes TEXT
            )
        """)
        self.conn.commit()
        self.active_votes = {}
        self.running_votes = {}  # Store active voting tasks

        # Schedule the load_votes() coroutine to run as soon as possible
        self.bot.loop.create_task(self.load_votes())

    def cog_unload(self):
        self.conn.close()

    async def resume_vote(self, title):
        vote_data = self.active_votes[title]
        channel = self.bot.get_channel(vote_data['channel_id'])
        start_time = datetime.datetime.strptime(vote_data['start_time'], "%Y-%m-%d %H:%M:%S.%f")
        end_time = start_time + datetime.timedelta(minutes=vote_data['duration'])

        while datetime.datetime.utcnow() < end_time:
            remaining_time = end_time - datetime.datetime.utcnow()
            minutes, seconds = divmod(remaining_time.seconds, 60)
            voting_message = await channel.fetch_message(vote_data['message_id'])
            embed = voting_message.embeds[0]
            embed.set_footer(text=f"Voting Ends in {remaining_time.days}d {minutes}m {seconds}s")
            await voting_message.edit(embed=embed)
            await asyncio.sleep(15)

        embed.set_footer(text="Voting Ended")
        await voting_message.edit(embed=embed)
        del self.active_votes[title]
        del self.running_votes[title]

        winner = max(vote_data['votes'], key=vote_data['votes'].get)

        # create a new embed object for the winner announcement
        winner_embed = discord.Embed(title=f"Vote Results for '{title}'", description=f"The winner is: {winner}", color=0x00ff00)
        await channel.send(embed=winner_embed)

    async def load_votes(self):
        self.cursor.execute("SELECT * FROM active_votes")
        for row in self.cursor.fetchall():
            title, message_id, channel_id, option_emojis, votes, start_time, duration, user_votes = row
            self.active_votes[title] = {
                'message_id': message_id,
                'channel_id': channel_id,
                'option_emojis': json.loads(option_emojis),
                'votes': json.loads(votes),
                'start_time': start_time,
                'duration': duration,
                'user_votes': json.loads(user_votes),
            }
            await self.recount_and_resume_votes(title)  # Add this line to recount and resume votes

    async def recount_votes(self, title):
        vote_data = self.active_votes[title]
        channel = self.bot.get_channel(vote_data['channel_id'])
        message = await channel.fetch_message(vote_data['message_id'])

        for reaction in message.reactions:
            async for user in reaction.users():
                if user == self.bot.user:
                    continue
                emoji = str(reaction.emoji)
                if emoji in vote_data['option_emojis']:
                    user_id = str(user.id)  # user.id should be converted to string because JSON stores keys as string
                    if user_id not in vote_data['user_votes']:
                        vote_data['votes'][vote_data['option_emojis'][emoji]] += 1
                        vote_data['user_votes'][user_id] = vote_data['option_emojis'][emoji]
                        try:
                            await message.remove_reaction(reaction.emoji, user)  # Remove user reaction
                        except NotFound:
                            pass  # Handle case when reaction is not found

    async def recount_and_resume_votes(self, title):
        # Recount votes and then resume the vote
        await self.recount_votes(title)
        self.running_votes[title] = self.bot.loop.create_task(self.resume_vote(title))

    @commands.Cog.listener()
    async def on_ready(self):
        # When the bot starts/restarts, load votes from the database and resume voting countdown
        await self.load_votes()
        
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        message = reaction.message
        for title, vote_data in self.active_votes.items():
            if message.id == vote_data['message_id']:
                emoji = str(reaction.emoji)
                if emoji in vote_data['option_emojis'].keys():
                    option = vote_data['option_emojis'][emoji]
                    if user.id in vote_data['user_votes']:
                        previous_option = vote_data['user_votes'][user.id]
                        vote_data['votes'][previous_option] -= 1
                    vote_data['votes'][option] += 1
                    vote_data['user_votes'][user.id] = option
                    await self.update_vote_count(title)
                    try:
                        await reaction.remove(user)
                    except NotFound:
                        pass
                    break

    async def update_vote_count(self, title):
        vote_data = self.active_votes[title]
        channel = self.bot.get_channel(vote_data['channel_id'])
        voting_message = await channel.fetch_message(vote_data['message_id'])
        embed = discord.Embed(title=title)
        for emoji, option in vote_data['option_emojis'].items():
            vote_count = vote_data['votes'][option]
            embed.add_field(name=option, value=f"{emoji}: {vote_count}", inline=False)
        await voting_message.edit(embed=embed)

        # Update the vote counts in the database
        self.cursor.execute("""
            UPDATE active_votes
            SET votes = ?, user_votes = ?
            WHERE title = ?
        """, (json.dumps(vote_data['votes']), json.dumps(vote_data['user_votes']), title))
        self.conn.commit()

    @commands.command()
    async def vote(self, ctx, time_limit, title, *options):
        if title in self.active_votes:
            await ctx.send("A vote with that title already exists.")
            return
        if len(options) < 2:
            await ctx.send("You need at least two options to start a vote.")
            return

        option_emojis = {f"{i+1}\N{combining enclosing keycap}": option for i, option in enumerate(options)}
        votes = {option: 0 for option in options}
        user_votes = {}

        embed = discord.Embed(title=title)
        for emoji, option in option_emojis.items():
            embed.add_field(name=option, value=f"{emoji}: 0", inline=False)

        message = await ctx.send(embed=embed)
        for emoji in option_emojis:
            await message.add_reaction(emoji)

        start_time = datetime.datetime.utcnow()

        self.active_votes[title] = {
            'message_id': message.id,
            'channel_id': message.channel.id,
            'option_emojis': option_emojis,
            'votes': votes,
            'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'duration': int(time_limit),
            'user_votes': user_votes,
        }

        self.cursor.execute("""
            INSERT INTO active_votes (title, message_id, channel_id, option_emojis, votes, start_time, duration, user_votes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            message.id,
            message.channel.id,
            json.dumps(option_emojis),
            json.dumps(votes),
            start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            int(time_limit),
            json.dumps(user_votes),
        ))
        self.conn.commit()

        self.running_votes[title] = self.bot.loop.create_task(self.resume_vote(title))

    @commands.command()
    async def endvote(self, ctx, title):
        if title not in self.active_votes:
            await ctx.send("There is no active vote with that title.")
            return

        vote_data = self.active_votes[title]
        channel = self.bot.get_channel(vote_data['channel_id'])
        message = await channel.fetch_message(vote_data['message_id'])
        embed = message.embeds[0]
        embed.set_footer(text="Voting Ended")
        await message.edit(embed=embed)

        winner = max(vote_data['votes'], key=vote_data['votes'].get)
        await ctx.send(f"The winner of the vote '{title}' is: {winner}")

        self.cursor.execute("DELETE FROM active_votes WHERE title = ?", (title,))
        self.conn.commit()

        del self.active_votes[title]
        self.running_votes[title].cancel()
        del self.running_votes[title]

async def setup(bot):
    await bot.add_cog(Voting(bot))
