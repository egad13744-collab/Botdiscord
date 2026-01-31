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
            'cogs.animal',
            'cogs.leaderboard',
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
        description="Selamat datang di Adventure Quest! Berikut semua command yang tersedia:",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="👤 Profil & Stats",
        value="`/profile` - Lihat profilmu\n`/inventory` - Cek itemmu\n`/daily` - Ambil hadiah harian",
        inline=False
    )
    
    embed.add_field(
        name="🏹 Berburu & Hewan",
        value="`/hunt` - Berburu untuk menangkap hewan\n"
              "`/animal list` - Lihat semua hewanmu\n"
              "`/animal equip <id>` - Tambah hewan ke tim\n"
              "`/animal unequip <id>` - Keluarkan hewan dari tim\n"
              "`/animal info <id>` - Info detail hewan\n"
              "`/animal heal` - Sembuhkan tim\n"
              "`/team` - Lihat tim battle",
        inline=False
    )
    
    embed.add_field(
        name="⚔️ Battle",
        value="`/battle` - Lawan monster dengan tim hewanmu\n"
              "*Battle wajib menggunakan hewan di tim!*",
        inline=False
    )
    
    embed.add_field(
        name="🎣 Memancing",
        value="`/fish` - Memancing untuk mendapat item",
        inline=False
    )
    
    embed.add_field(
        name="💰 Ekonomi",
        value="`/shop` - Lihat toko\n`/buy` - Beli item\n`/sell` - Jual item\n`/trade` - Trade dengan pemain lain",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Mini Games",
        value="`/guess` - Tebak angka\n`/slots` - Mesin slot",
        inline=False
    )
    
    embed.add_field(
        name="🎒 Equipment",
        value="`/equip` - Pasang equipment\n`/unequip` - Lepas equipment",
        inline=False
    )
    
    embed.add_field(
        name="🏆 Leaderboard",
        value="`/leaderboard` - Lihat peringkat\n"
              "`/leaderboard coin` - Top koin\n"
              "`/leaderboard level` - Top level\n"
              "`/leaderboard win` - Top kemenangan",
        inline=False
    )
    
    embed.set_footer(text="Adventure Quest | Selamat bermain!")
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please set your Discord bot token.")
    else:
        bot.run(token)
