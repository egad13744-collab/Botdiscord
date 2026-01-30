import discord
from discord import app_commands
from discord.ext import commands
import random
from data.items import FISH_LOOT, Rarity, get_item

FISH_COOLDOWN = 25

class FishCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    def get_bonuses(self, profile):
        exp_bonus = 0
        coin_bonus = 0
        luck_bonus = 0
        
        if profile['equipped_rod']:
            rod = get_item(profile['equipped_rod'])
            if rod:
                luck_bonus += rod.get('luck_bonus', 0)
        
        if profile['equipped_skin']:
            skin = get_item(profile['equipped_skin'])
            if skin:
                exp_bonus += skin.get('exp_bonus', 0)
                coin_bonus += skin.get('coin_bonus', 0)
                luck_bonus += skin.get('luck_bonus', 0)
        
        return exp_bonus, coin_bonus, luck_bonus
    
    def roll_catch(self, luck_bonus: int = 0):
        roll = random.random() * 100
        adjusted_roll = max(0, roll - luck_bonus)
        
        cumulative = 0
        for item_id, item in FISH_LOOT.items():
            cumulative += item['rarity'].drop_chance
            if adjusted_roll <= cumulative:
                return item_id, item
        
        first_item_id = list(FISH_LOOT.keys())[0]
        return first_item_id, FISH_LOOT[first_item_id]
    
    @app_commands.command(name="fish", description="Go fishing for treasures!")
    async def fish(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        profile = await self.db.get_user(user_id, interaction.user.name)
        
        cooldown = await self.db.check_cooldown(user_id, 'last_fish', FISH_COOLDOWN)
        if cooldown:
            await interaction.response.send_message(
                f"⏳ The fish need time to return! Wait **{cooldown}** seconds.",
                ephemeral=True
            )
            return
        
        exp_bonus, coin_bonus, luck_bonus = self.get_bonuses(profile)
        
        item_id, item = self.roll_catch(luck_bonus)
        
        base_exp = random.randint(4, 12)
        base_coins = random.randint(2, 8)
        
        exp_gained = int(base_exp * (1 + exp_bonus / 100))
        coins_gained = int(base_coins * (1 + coin_bonus / 100))
        
        await self.db.add_item(user_id, item_id)
        await self.db.add_coins(user_id, coins_gained)
        level_result = await self.db.add_exp(user_id, exp_gained)
        await self.db.set_cooldown(user_id, 'last_fish')
        
        fish_messages = [
            "You cast your line into the calm lake...",
            "You fished at the rushing river...",
            "You ventured to the mysterious ocean depths...",
            "You found a secret fishing spot...",
            "You waited patiently by the crystal pond...",
        ]
        
        embed = discord.Embed(
            title="🎣 Fishing Results",
            description=random.choice(fish_messages),
            color=item['rarity'].color
        )
        
        embed.add_field(
            name="🐟 Catch",
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
            Rarity.RARE: "What a catch! That's rare!",
            Rarity.EPIC: "Epic catch! Amazing luck!",
            Rarity.LEGENDARY: "LEGENDARY CATCH! Unbelievable!",
            Rarity.MYTHIC: "MYTHIC CATCH! Once in a lifetime!"
        }
        
        if item['rarity'] in rarity_tips:
            embed.set_footer(text=rarity_tips[item['rarity']])
        else:
            embed.set_footer(text=f"Cooldown: {FISH_COOLDOWN}s | Better rods increase luck!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(FishCog(bot))
