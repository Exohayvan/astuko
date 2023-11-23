import sqlite3
import discord
import concurrent.futures
from discord.ext import commands, tasks
from diffusers import StableDiffusionPipeline
import torch
import random
import os
import asyncio

class CharacterClaim(commands.Cog):
    def __init__(self, bot):
        self.negative_prompt = 'simple background, duplicate, retro style, low quality, lowest quality, 1980s, 1990s, 2000s, 2005 2006 2007 2008 2009 2010 2011 2012 2013, bad anatomy, bad proportions, extra digits, lowres, username, artist name, error, duplicate, watermark, signature, text, extra digit, fewer digits, worst quality, jpeg artifacts, blurry'
        self.bot = bot
        self.db_path = "./data/db/characterspawns/channels.db"
        self.characters_path = "./data/db/characterspawns/characters"
        self.active_character_id = None
        self.create_db()
        self.spawn_character_loop.start()

    def create_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS spawn_channels (
                            server_id TEXT PRIMARY KEY,
                            channel_id TEXT NOT NULL
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS claimed_characters (
                            character_id INTEGER PRIMARY KEY,
                            claimed_by TEXT
                          )''')
        conn.commit()
        conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setspawn(self, ctx):
        """Sets the spawn channel for character images to the channel where the command is invoked."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('REPLACE INTO spawn_channels (server_id, channel_id) VALUES (?, ?)', 
                       (str(ctx.guild.id), str(ctx.channel.id)))
        conn.commit()
        conn.close()
        await ctx.send(f"Spawn channel set to {ctx.channel.mention}")

    @tasks.loop(minutes=random.randint(20, 60))
    async def spawn_character_loop(self):
        await self.bot.wait_until_ready()
        character_data = await self.generate_character()  # Generate character before the server loop
    
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM spawn_channels')
        rows = cursor.fetchall()
        conn.close()
    
        for row in rows:
            server_id, channel_id = row
            channel = self.bot.get_channel(int(channel_id))
    
            if channel:
                await self.send_character(channel, character_data)  # Send the same character to each channel
                await asyncio.sleep(0.5)  # Delay between each message
            
    async def spawn_character(self, channel):
        """Spawns a character in a channel."""
        character_data = await self.generate_character()
        await self.send_character(channel, character_data)
        return True

    async def generate_character(self):
        """Generates a character with image and stats."""
        prompt = self.generate_random_prompt()
        image = await self.create_image(prompt)
        stats, score = self.roll_stats()
        next_file_id = self.get_next_file_id()
        filename = f"{self.characters_path}/{next_file_id}.png"
        image.save(filename)

        return {
            "file_id": next_file_id,
            "filename": filename,
            "stats": stats,
            "score": score
        }
        
    async def send_character(self, channel, character_data):
        """Sends the generated character to the specified Discord channel as an embed."""
        embed = discord.Embed(
            title=f"Character ID: {character_data['file_id']}",
            description=f"Score: {character_data['score']}\n\n**Stats:**",
            color=discord.Color.blue()  # You can choose any color
        )
        
        # Add stats to the embed
        for stat, value in character_data["stats"].items():
            embed.add_field(name=stat, value=value, inline=True)
    
        # Attach the image to the embed
        file = discord.File(character_data["filename"], filename="character.png")
        embed.set_image(url="attachment://character.png")
    
        # Send the embed with the image
        message = await channel.send(file=file, embed=embed)
        self.active_character_id = character_data["file_id"]
        await message.add_reaction('✅')

    def get_next_file_id(self):
        """Determines the next file ID based on existing files."""
        if not os.path.exists(self.characters_path):
            os.makedirs(self.characters_path)
        files = os.listdir(self.characters_path)
        file_ids = [int(f.split('.')[0]) for f in files if f.endswith('.png')]
        next_id = max(file_ids, default=0) + 1
        return next_id
        
    def generate_random_prompt(self):
        """Generates a random prompt with physical characteristics for the character."""
        hair_colors = ["black", "brown", "blonde", "blue", "green", "red", "pink", "purple", "white", "grey", "orange"]
        race = ["Human", "Vampire", "Neko", "Elf", "Dwarf", "Orc", "Centaur", "Fairy", "Werewolf", "Troll", "Angel", "Demon", "Gnome", "Leprechaun", "Minotaur", "Harpy"]
        genders = ["male", "female"]
        eye_colors = ["brown", "blue", "green", "hazel", "grey", "amber"]
        notable_features = ["with glasses", "with a tattoo", "with a scar", "with freckles", "with a piercing", "wearing a hat"]
    
        return f"masterpiece, high quality, high resolution, {random.choice(hair_colors)} hair, {random.choice(genders)} {random.choice(race)}, {random.choice(eye_colors)} eyes, {random.choice(notable_features)}"
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Listener for reactions to claim a character."""
        if user != self.bot.user and self.active_character_id is not None:
            message = reaction.message
            if message.attachments and self.active_character_id == int(os.path.splitext(message.attachments[0].filename)[0]):
                if self.claim_character(self.active_character_id, user.id):
                    await message.reply(f"{user.mention} has claimed character ID: {self.active_character_id}")
                    self.active_character_id = None
                else:
                    await message.reply("This character has already been claimed.")

    def claim_character(self, character_id, user_id):
        """Claims a character for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if the character is already claimed
        cursor.execute('SELECT * FROM claimed_characters WHERE character_id = ?', (character_id,))
        if cursor.fetchone() is not None:
            conn.close()
            return False

        # Claim the character
        cursor.execute('INSERT INTO claimed_characters (character_id, claimed_by) VALUES (?, ?)', 
                       (character_id, str(user_id)))
        conn.commit()
        conn.close()
        return True

    def roll_stats(self):
        max_values = {
            "💖 HP": 1000,
            "⚔️ ATK": 400,
            "🔮 MAG": 400,
            "🛡️ PHR": 100,
            "🌟 MGR": 100,
            "🍀 Luck": 10,
            "🎭 Charisma": 10,
            "💨 SPD": 10,
            "🏋️‍♂️ STA": 10,
            "🤹 DEX": 10,
            "🧠 INT": 10,
            "💪 STR": 10
        }
    
        stats = {
            "💖 HP": random.randint(1, max_values["💖 HP"]),
            "⚔️ ATK": random.randint(1, max_values["⚔️ ATK"]),
            "🔮 MAG": random.randint(1, max_values["🔮 MAG"]),
            "🛡️ PHR": f"{random.randint(0, max_values['🛡️ PHR'])}%",
            "🌟 MGR": f"{random.randint(0, max_values['🌟 MGR'])}%",
            "🍀 Luck": f"+{random.randint(0, max_values['🍀 Luck'])}",
            "🎭 Charisma": f"+{random.randint(0, max_values['🎭 Charisma'])}",
            "💨 SPD": f"+{random.randint(0, max_values['💨 SPD'])}",
            "🏋️‍♂️ STA": f"+{random.randint(0, max_values['🏋️‍♂️ STA'])}",
            "🤹 DEX": f"+{random.randint(0, max_values['🤹 DEX'])}",
            "🧠 INT": f"+{random.randint(0, max_values['🧠 INT'])}",
            "💪 STR": f"+{random.randint(0, max_values['💪 STR'])}"
        }
    
        # Calculate the score
        numeric_stats = {
            "💖 HP": stats["💖 HP"],
            "⚔️ ATK": stats["⚔️ ATK"],
            "🔮 MAG": stats["🔮 MAG"],
            "🛡️ PHR": int(stats["🛡️ PHR"].strip('%')),
            "🌟 MGR": int(stats["🌟 MGR"].strip('%')),
            "🍀 Luck": int(stats["🍀 Luck"].strip('+')),
            "🎭 Charisma": int(stats["🎭 Charisma"].strip('+')),
            "💨 SPD": int(stats["💨 SPD"].strip('+')),
            "🏋️‍♂️ STA": int(stats["🏋️‍♂️ STA"].strip('+')),
            "🤹 DEX": int(stats["🤹 DEX"].strip('+')),
            "🧠 INT": int(stats["🧠 INT"].strip('+')),
            "💪 STR": int(stats["💪 STR"].strip('+'))
        }
    
        score = sum((numeric_stats[stat] / max_values[stat] for stat in numeric_stats)) / len(numeric_stats) * 100
        return stats, f"Score: {score:.2f}/100.00"

    async def create_image(self, prompt):
        """Creates an image based on the given prompt."""
        # Initialize the executor for running heavy computations
        executor = concurrent.futures.ThreadPoolExecutor()
        loop = asyncio.get_event_loop()
    
        # Define a function for initializing the pipeline
        def init_pipe():
            return StableDiffusionPipeline.from_pretrained("dreamlike-art/dreamlike-anime-1.0", torch_dtype=torch.float32)
    
        # Initialize the pipeline in the executor
        pipe = await loop.run_in_executor(executor, init_pipe)
    
        # Generate the image in the executor
        image = await loop.run_in_executor(executor, lambda: pipe(prompt, negative_prompt=self.negative_prompt).images[0])
        return image

    def cog_unload(self):
        self.spawn_character_loop.cancel()

async def setup(bot):
    await bot.add_cog(CharacterClaim(bot))