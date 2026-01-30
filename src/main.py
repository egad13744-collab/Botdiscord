import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from database.db import Database

intents = discord.Intents.default()
intents.message_content = True

class AdventureBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.db = Database()
        
    async def setup_hook(self):
        await self.db.init()
        
        cogs = [
            'cogs.profile',
            'cogs.hunt',
            'cogs.fish',
            'cogs.inventory',
            'cogs.shop',
            'cogs.daily',
            'cogs.minigames',
            'cogs.battle',
            'cogs.trade',
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")
        
        await self.tree.sync()
        print("Slash commands synced!")
        
    async def on_ready(self):
        print(f'{self.user} is now online!')
        print(f'Connected to {len(self.guilds)} servers')
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="/help | Adventure Quest"
            )
        )

bot = AdventureBot()

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Adventure Quest - Commands",
        description="Welcome to Adventure Quest! Here are all available commands:",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="Profile & Stats",
        value="`/profile` - View your profile\n`/inventory` - Check your items\n`/daily` - Claim daily reward",
        inline=False
    )
    
    embed.add_field(
        name="Adventure",
        value="`/hunt` - Hunt for monsters and loot\n`/fish` - Go fishing for treasures\n`/battle` - Fight monsters in PvE",
        inline=False
    )
    
    embed.add_field(
        name="Economy",
        value="`/shop` - Browse the shop\n`/buy` - Purchase items\n`/sell` - Sell your items\n`/trade` - Trade with other players",
        inline=False
    )
    
    embed.add_field(
        name="Mini Games",
        value="`/guess` - Number guessing game\n`/slots` - Try your luck at slots",
        inline=False
    )
    
    embed.add_field(
        name="Equipment",
        value="`/equip` - Equip items\n`/unequip` - Unequip items",
        inline=False
    )
    
    embed.set_footer(text="Adventure Quest | Have fun!")
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please set your Discord bot token.")
    else:
        bot.run(token)
