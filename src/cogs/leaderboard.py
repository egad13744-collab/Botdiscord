import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def get_coin_leaderboard(self, limit: int = 10):
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT user_id, username, coins 
                FROM users 
                ORDER BY coins DESC 
                LIMIT $1
            ''', limit)
            return [dict(r) for r in rows]
    
    async def get_level_leaderboard(self, limit: int = 10):
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT user_id, username, level, exp 
                FROM users 
                ORDER BY level DESC, exp DESC 
                LIMIT $1
            ''', limit)
            return [dict(r) for r in rows]
    
    async def get_win_leaderboard(self, limit: int = 10):
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT u.user_id, u.username, b.wins, b.losses, b.monsters_killed
                FROM users u
                JOIN battle_stats b ON u.user_id = b.user_id
                ORDER BY b.wins DESC, b.monsters_killed DESC
                LIMIT $1
            ''', limit)
            return [dict(r) for r in rows]
    
    async def get_user_rank(self, user_id: int, category: str) -> Optional[int]:
        async with self.db.pool.acquire() as conn:
            if category == "coin":
                result = await conn.fetchval('''
                    SELECT rank FROM (
                        SELECT user_id, RANK() OVER (ORDER BY coins DESC) as rank
                        FROM users
                    ) ranked WHERE user_id = $1
                ''', user_id)
            elif category == "level":
                result = await conn.fetchval('''
                    SELECT rank FROM (
                        SELECT user_id, RANK() OVER (ORDER BY level DESC, exp DESC) as rank
                        FROM users
                    ) ranked WHERE user_id = $1
                ''', user_id)
            elif category == "win":
                result = await conn.fetchval('''
                    SELECT rank FROM (
                        SELECT user_id, RANK() OVER (ORDER BY wins DESC, monsters_killed DESC) as rank
                        FROM battle_stats
                    ) ranked WHERE user_id = $1
                ''', user_id)
            else:
                return None
            return result
    
    def get_rank_emoji(self, rank: int) -> str:
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return f"**{rank}.**"
    
    @app_commands.command(name="leaderboard", description="View the leaderboard")
    @app_commands.describe(category="Choose leaderboard category")
    async def leaderboard(
        self, 
        interaction: discord.Interaction, 
        category: Literal["coin", "level", "win"] = "coin"
    ):
        user_id = interaction.user.id
        await self.db.get_user(user_id, interaction.user.name)
        
        if category == "coin":
            data = await self.get_coin_leaderboard()
            title = "💰 Leaderboard Koin"
            emoji = "💰"
            
            entries = []
            for i, row in enumerate(data, 1):
                rank_emoji = self.get_rank_emoji(i)
                highlight = "→ " if row['user_id'] == user_id else ""
                entries.append(
                    f"{rank_emoji} {highlight}**{row['username']}**\n"
                    f"   {emoji} {row['coins']:,} koin"
                )
            
            user_rank = await self.get_user_rank(user_id, "coin")
            footer = f"Peringkatmu: #{user_rank}" if user_rank else "Belum ada data"
            
        elif category == "level":
            data = await self.get_level_leaderboard()
            title = "⭐ Leaderboard Level"
            emoji = "⭐"
            
            entries = []
            for i, row in enumerate(data, 1):
                rank_emoji = self.get_rank_emoji(i)
                highlight = "→ " if row['user_id'] == user_id else ""
                entries.append(
                    f"{rank_emoji} {highlight}**{row['username']}**\n"
                    f"   {emoji} Level {row['level']} ({row['exp']} EXP)"
                )
            
            user_rank = await self.get_user_rank(user_id, "level")
            footer = f"Peringkatmu: #{user_rank}" if user_rank else "Belum ada data"
            
        else:
            data = await self.get_win_leaderboard()
            title = "⚔️ Leaderboard Kemenangan"
            emoji = "🏆"
            
            entries = []
            for i, row in enumerate(data, 1):
                rank_emoji = self.get_rank_emoji(i)
                highlight = "→ " if row['user_id'] == user_id else ""
                win_rate = (row['wins'] / (row['wins'] + row['losses']) * 100) if (row['wins'] + row['losses']) > 0 else 0
                entries.append(
                    f"{rank_emoji} {highlight}**{row['username']}**\n"
                    f"   {emoji} {row['wins']} Win | ❌ {row['losses']} Loss ({win_rate:.1f}%)"
                )
            
            user_rank = await self.get_user_rank(user_id, "win")
            footer = f"Peringkatmu: #{user_rank}" if user_rank else "Belum ada data"
        
        if not entries:
            embed = discord.Embed(
                title=title,
                description="Belum ada data di leaderboard ini!",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title=title,
                description="\n\n".join(entries),
                color=discord.Color.gold()
            )
        
        embed.set_footer(text=footer)
        embed.set_author(name="Adventure Quest Leaderboard", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        view = LeaderboardView(self, user_id, category)
        await interaction.response.send_message(embed=embed, view=view)

class LeaderboardView(discord.ui.View):
    def __init__(self, cog: LeaderboardCog, user_id: int, current: str):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.current = current
        
        self.coin_button.style = discord.ButtonStyle.primary if current == "coin" else discord.ButtonStyle.secondary
        self.level_button.style = discord.ButtonStyle.primary if current == "level" else discord.ButtonStyle.secondary
        self.win_button.style = discord.ButtonStyle.primary if current == "win" else discord.ButtonStyle.secondary
    
    async def update_leaderboard(self, interaction: discord.Interaction, category: str):
        if category == "coin":
            data = await self.cog.get_coin_leaderboard()
            title = "💰 Leaderboard Koin"
            emoji = "💰"
            
            entries = []
            for i, row in enumerate(data, 1):
                rank_emoji = self.cog.get_rank_emoji(i)
                highlight = "→ " if row['user_id'] == self.user_id else ""
                entries.append(
                    f"{rank_emoji} {highlight}**{row['username']}**\n"
                    f"   {emoji} {row['coins']:,} koin"
                )
            
            user_rank = await self.cog.get_user_rank(self.user_id, "coin")
            footer = f"Peringkatmu: #{user_rank}" if user_rank else "Belum ada data"
            
        elif category == "level":
            data = await self.cog.get_level_leaderboard()
            title = "⭐ Leaderboard Level"
            emoji = "⭐"
            
            entries = []
            for i, row in enumerate(data, 1):
                rank_emoji = self.cog.get_rank_emoji(i)
                highlight = "→ " if row['user_id'] == self.user_id else ""
                entries.append(
                    f"{rank_emoji} {highlight}**{row['username']}**\n"
                    f"   {emoji} Level {row['level']} ({row['exp']} EXP)"
                )
            
            user_rank = await self.cog.get_user_rank(self.user_id, "level")
            footer = f"Peringkatmu: #{user_rank}" if user_rank else "Belum ada data"
            
        else:
            data = await self.cog.get_win_leaderboard()
            title = "⚔️ Leaderboard Kemenangan"
            emoji = "🏆"
            
            entries = []
            for i, row in enumerate(data, 1):
                rank_emoji = self.cog.get_rank_emoji(i)
                highlight = "→ " if row['user_id'] == self.user_id else ""
                win_rate = (row['wins'] / (row['wins'] + row['losses']) * 100) if (row['wins'] + row['losses']) > 0 else 0
                entries.append(
                    f"{rank_emoji} {highlight}**{row['username']}**\n"
                    f"   {emoji} {row['wins']} Win | ❌ {row['losses']} Loss ({win_rate:.1f}%)"
                )
            
            user_rank = await self.cog.get_user_rank(self.user_id, "win")
            footer = f"Peringkatmu: #{user_rank}" if user_rank else "Belum ada data"
        
        if not entries:
            embed = discord.Embed(
                title=title,
                description="Belum ada data di leaderboard ini!",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title=title,
                description="\n\n".join(entries),
                color=discord.Color.gold()
            )
        
        embed.set_footer(text=footer)
        embed.set_author(name="Adventure Quest Leaderboard", icon_url=self.cog.bot.user.avatar.url if self.cog.bot.user.avatar else None)
        
        self.current = category
        self.coin_button.style = discord.ButtonStyle.primary if category == "coin" else discord.ButtonStyle.secondary
        self.level_button.style = discord.ButtonStyle.primary if category == "level" else discord.ButtonStyle.secondary
        self.win_button.style = discord.ButtonStyle.primary if category == "win" else discord.ButtonStyle.secondary
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="💰 Koin", style=discord.ButtonStyle.secondary)
    async def coin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_leaderboard(interaction, "coin")
    
    @discord.ui.button(label="⭐ Level", style=discord.ButtonStyle.secondary)
    async def level_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_leaderboard(interaction, "level")
    
    @discord.ui.button(label="⚔️ Win", style=discord.ButtonStyle.secondary)
    async def win_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_leaderboard(interaction, "win")

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
