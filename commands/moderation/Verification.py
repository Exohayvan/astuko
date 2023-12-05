import discord
from discord.ext import commands
import sqlite3
import random
from discord.ext.commands import MissingRequiredArgument

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_dict = {}
        self.conn = sqlite3.connect('./data/roles.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS roles
                     (guild_id INTEGER, join_role INTEGER, verify_role INTEGER)''')
        self.conn.commit()
        # Initialize a new connection for verification_channel.db
        self.conn_verification_channel = sqlite3.connect('./data/verification_channel.db')
        self.c_verification_channel = self.conn_verification_channel.cursor()
        self.c_verification_channel.execute('''CREATE TABLE IF NOT EXISTS verification_channels
                     (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)''')
        self.conn_verification_channel.commit()

    @commands.command(usage="!set_verify_channel <#channel>")
    @commands.has_permissions(administrator=True)
    async def set_verify_channel(self, ctx, channel: discord.TextChannel):
        """Sets a specific channel for verification purposes."""
        self.c_verification_channel.execute("INSERT OR REPLACE INTO verification_channels VALUES (?, ?)", (ctx.guild.id, channel.id))
        self.conn_verification_channel.commit()
        await ctx.send(f"Verification channel has been set to {channel.mention}.")

    @commands.command(usage="!show_roles")
    @commands.has_permissions(administrator=True)
    async def show_roles(self, ctx):
        """Shows the set join and verify roles for the guild."""
        
        # Query the database for the roles
        self.c.execute("SELECT join_role, verify_role FROM roles WHERE guild_id=?", (ctx.guild.id,))
        roles = self.c.fetchone()
        
        # If we couldn't fetch the roles from the database
        if roles is None:
            await ctx.send("No entry found for this guild in the database.")
            return
    
        join_role, verify_role = roles
    
        # If either role ID is None, inform the user
        if join_role is None or verify_role is None:
            await ctx.send(f"Fetched roles from database:\nJoin Role ID: {join_role}\nVerify Role ID: {verify_role}")
            return
    
        join_role_obj = ctx.guild.get_role(join_role)
        verify_role_obj = ctx.guild.get_role(verify_role)
        
        # If we can't fetch the Role objects from the guild
        if join_role_obj is None or verify_role_obj is None:
            await ctx.send(f"One or both of the roles don't exist anymore in this server.\nJoin Role ID: {join_role}\nVerify Role ID: {verify_role}")
            return
    
        await ctx.send(f"Join Role: {join_role_obj.name}\nVerify Role: {verify_role_obj.name}")
        
    @commands.command(usage="!set_join_role <@role>")
    @commands.has_permissions(administrator=True)
    async def set_join_role(self, ctx, role: commands.RoleConverter):
        """Sets the role to give to users when they first join."""
        self.c.execute("INSERT OR REPLACE INTO roles VALUES (?, ?, (SELECT verify_role FROM roles WHERE guild_id=?))", (ctx.guild.id, role.id, ctx.guild.id))
        self.conn.commit()
        await ctx.send(f"Join role has been set to {role.name}.")
                
    @commands.command(usage="!set_verify_role <@role>")
    @commands.has_permissions(administrator=True)
    async def set_verify_role(self, ctx, role: commands.RoleConverter):
        """Sets the role to give to users when they are verified."""
        
        # Fetch the current join_role from the database
        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (ctx.guild.id,))
        join_role_id = self.c.fetchone()
        if join_role_id is None:  # If no record exists for the guild
            self.c.execute("INSERT INTO roles (guild_id, verify_role) VALUES (?, ?)", (ctx.guild.id, role.id))
        else:
            self.c.execute("UPDATE roles SET verify_role=? WHERE guild_id=?", (role.id, ctx.guild.id))
        
        self.conn.commit()
        await ctx.send(f"Verify role has been set to {role.name}.")
                
    @commands.command(usage="!verify")
    async def verify(self, ctx):
        """Sends a verification CAPTCHA to the user's DMs and alerts the user to check their DMs."""
        try:
            verification_number = random.randint(100, 999)
            self.verification_dict[ctx.author.id] = (verification_number, ctx.guild.id)
            await ctx.author.send(f"Please respond with this number to verify that you are a human: {verification_number}")
            await ctx.send(f"{ctx.author.mention}, I've sent you a DM with your verification number!", delete_after=60)
        except discord.Forbidden:
            # This exception is raised when the bot cannot send a DM to the user
            await ctx.send(f"{ctx.author.mention}, I couldn't send you a DM! Please open your DMs and try again.", delete_after=60)
        finally:
            # Delete the original command invocation message after 60 seconds
            await ctx.message.delete(delay=60)
            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return  # Skip the process for bots
        # Ignore messages from users with administrator privileges
        if message.guild and message.author.guild_permissions.administrator:
            return
        
        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (member.guild.id,))
        join_role_id = self.c.fetchone()
        if join_role_id is not None:
            join_role = member.guild.get_role(join_role_id[0])
            if join_role is not None:
                await member.add_roles(join_role)
            
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Handle messages in the verification channel
        if message.guild:  # Only proceed if the message is in a guild
            self.c_verification_channel.execute("SELECT channel_id FROM verification_channels WHERE guild_id=?", (message.guild.id,))
            result = self.c_verification_channel.fetchone()
            if result and message.channel.id == result[0]:  # Check if the message is in the verification channel
                if message.content.lower() not in ['!verify', '!accept_tos']:
                    reminder_msg = await message.channel.send(
                        f"{message.author.mention}, it looks like you are messaging in a verification channel. "
                        f"Please try the verify command.",
                        delete_after=60
                    )
                    await message.delete(delay=60)
                    return  # Return to prevent processing the message further
    
        # Handle verification CAPTCHA responses in direct messages
        if not message.guild:  # Check if the message is a DM
            verification_data = self.verification_dict.get(message.author.id)
    
            if verification_data and message.content.isdigit() and int(message.content) == verification_data[0]:
                await message.author.send("Verification successful!")
                
                guild = self.bot.get_guild(verification_data[1])
                if guild:
                    member = guild.get_member(message.author.id)
                    if member:
                        # Add the verify role
                        self.c.execute("SELECT verify_role FROM roles WHERE guild_id=?", (guild.id,))
                        verify_role_id = self.c.fetchone()
                        if verify_role_id:
                            verify_role = guild.get_role(verify_role_id[0])
                            if verify_role:
                                await member.add_roles(verify_role)
    
                        # Remove the join role
                        self.c.execute("SELECT join_role FROM roles WHERE guild_id=?", (guild.id,))
                        join_role_id = self.c.fetchone()
                        if join_role_id:
                            join_role = guild.get_role(join_role_id[0])
                            if join_role:
                                await member.remove_roles(join_role)
    
                        self.verification_dict.pop(message.author.id, None)  # Remove used captcha
    
            elif verification_data:
                await message.author.send("Verification failed.")
                            
async def setup(bot):
    await bot.add_cog(Verification(bot))
