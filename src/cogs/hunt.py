import discord
from discord import app_commands
from discord.ext import commands
import random
from data.items import HUNT_LOOT, Rarity, get_item, SKINS

HUNT_COOLDOWN = 30

class HuntCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    def get_bonuses(self, profile):
        exp_bonus = 0
        coin_bonus = 0
        luck_bonus = 0
        
        if profile['equipped_skin']:
            skin = get_item(profile['equipped_skin'])
            if skin:
                exp_bonus += skin.get('exp_bonus', 0)
                coin_bonus += skin.get('coin_bonus', 0)
                luck_bonus += skin.get('luck_bonus', 0)
        
        return exp_bonus, coin_bonus, luck_bonus
    
    def roll_loot(self, luck_bonus: int = 0):
        roll = random.random() * 100
        adjusted_roll = max(0, roll - luck_bonus)
        
        cumulative = 0
        for item_id, item in HUNT_LOOT.items():
            cumulative += item['rarity'].drop_chance
            if adjusted_roll <= cumulative:
                return item_id, item
        
        first_item_id = list(HUNT_LOOT.keys())[0]
        return first_item_id, HUNT_LOOT[first_item_id]
    
    @app_commands.command(name="hunt", description="Go hunting for monsters and loot!")
    async def hunt(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        profile = await self.db.get_user(user_id, interaction.user.name)
        
        cooldown = await self.db.check_cooldown(user_id, 'last_hunt', HUNT_COOLDOWN)
        if cooldown:
            await interaction.response.send_message(
                f"⏳ You're tired from the last hunt! Wait **{cooldown}** seconds.",
                ephemeral=True
            )
            return
        
        exp_bonus, coin_bonus, luck_bonus = self.get_bonuses(profile)
        
        item_id, item = self.roll_loot(luck_bonus)
        
        base_exp = random.randint(5, 15)
        base_coins = random.randint(3, 10)
        
        exp_gained = int(base_exp * (1 + exp_bonus / 100))
        coins_gained = int(base_coins * (1 + coin_bonus / 100))
        
        await self.db.add_item(user_id, item_id)
        await self.db.add_coins(user_id, coins_gained)
        level_result = await self.db.add_exp(user_id, exp_gained)
        await self.db.set_cooldown(user_id, 'last_hunt')
        
        hunt_messages = [
            "You ventured into the dark forest...",
            "You explored the ancient ruins...",
            "You climbed the treacherous mountain...",
            "You searched through the haunted cave...",
            "You trekked through the mystical swamp...",
        ]
        
        embed = discord.Embed(
            title="🏹 Hunt Results",
            description=random.choice(hunt_messages),
            color=item['rarity'].color
        )
        
        embed.add_field(
            name="📦 Loot Found",
            value=f"{item['emoji']} **{item['name']}** ({item['rarity'].display_name})",
            inline=False
        )
        
        embed.add_field(
            name="💰 Rewards",
            value=f"**+{coins_gained}** coins\n**+{exp_gained}** EXP",
            inline=True
        )
        
        if level_result['leveled_up']:
            embed.add_field(
                name="🎉 LEVEL UP!",
                value=f"You reached **Level {level_result['new_level']}**!",
                inline=True
            )
        
        rarity_tips = {
            Rarity.RARE: "Nice find! That's a rare drop!",
            Rarity.EPIC: "Incredible! An epic item!",
            Rarity.LEGENDARY: "LEGENDARY! You're so lucky!",
            Rarity.MYTHIC: "MYTHIC DROP! This is extremely rare!"
        }
        
        if item['rarity'] in rarity_tips:
            embed.set_footer(text=rarity_tips[item['rarity']])
        else:
            embed.set_footer(text=f"Cooldown: {HUNT_COOLDOWN}s | Use /inventory to see your items")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HuntCog(bot))
