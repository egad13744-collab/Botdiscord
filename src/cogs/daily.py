import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta

class DailyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="daily", description="Claim your daily reward!")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user = await self.db.get_user(user_id, interaction.user.name)
        
        now = datetime.utcnow()
        last_daily = user['last_daily']
        
        if last_daily:
            time_since = now - last_daily
            if time_since.total_seconds() < 86400:
                remaining = 86400 - int(time_since.total_seconds())
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                await interaction.response.send_message(
                    f"⏳ You already claimed your daily reward!\nCome back in **{hours}h {minutes}m**",
                    ephemeral=True
                )
                return
            
            if time_since.total_seconds() < 172800:
                new_streak = user['daily_streak'] + 1
            else:
                new_streak = 1
        else:
            new_streak = 1
        
        base_coins = 100
        streak_bonus = min(new_streak * 10, 200)
        total_coins = base_coins + streak_bonus
        
        base_exp = 25
        exp_bonus = min(new_streak * 5, 100)
        total_exp = base_exp + exp_bonus
        
        await self.db.add_coins(user_id, total_coins)
        level_result = await self.db.add_exp(user_id, total_exp)
        await self.db.update_user(user_id, daily_streak=new_streak, last_daily=now)
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💰 Coins",
            value=f"**+{total_coins}** coins\n(Base: {base_coins} + Streak: {streak_bonus})",
            inline=True
        )
        
        embed.add_field(
            name="✨ EXP",
            value=f"**+{total_exp}** EXP\n(Base: {base_exp} + Streak: {exp_bonus})",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Daily Streak",
            value=f"**{new_streak} days**",
            inline=True
        )
        
        if level_result['leveled_up']:
            embed.add_field(
                name="🎉 LEVEL UP!",
                value=f"You reached **Level {level_result['new_level']}**!",
                inline=False
            )
        
        streak_milestones = {
            7: "🥉 One Week Warrior!",
            14: "🥈 Two Week Champion!",
            30: "🥇 Monthly Legend!",
            100: "💎 Century Master!",
            365: "👑 YEARLY KING!"
        }
        
        if new_streak in streak_milestones:
            embed.add_field(
                name="🏆 Milestone Reached!",
                value=streak_milestones[new_streak],
                inline=False
            )
        
        embed.set_footer(text="Come back tomorrow to continue your streak!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(DailyCog(bot))
