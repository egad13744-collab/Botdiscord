import discord
from discord import app_commands
from discord.ext import commands
import random
from data.monsters import get_random_monster
from data.items import get_item, WEAPONS

BATTLE_COOLDOWN = 60

class BattleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    def get_player_stats(self, profile):
        base_hp = 100 + (profile['level'] * 10)
        base_attack = 10 + (profile['level'] * 2)
        base_defense = 5 + profile['level']
        
        if profile['equipped_weapon']:
            weapon = get_item(profile['equipped_weapon'])
            if weapon:
                base_attack += weapon.get('attack', 0)
        
        return {
            "hp": base_hp,
            "max_hp": base_hp,
            "attack": base_attack,
            "defense": base_defense
        }
    
    @app_commands.command(name="battle", description="Fight a random monster in PvE combat!")
    async def battle(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        profile = await self.db.get_user(user_id, interaction.user.name)
        
        luck_bonus = 0
        if profile['equipped_skin']:
            skin = get_item(profile['equipped_skin'])
            if skin:
                luck_bonus = skin.get('luck_bonus', 0)
        
        monster = get_random_monster(luck_bonus)
        player = self.get_player_stats(profile)
        
        battle_log = []
        round_num = 1
        
        while player['hp'] > 0 and monster['hp'] > 0:
            player_damage = max(1, player['attack'] - monster['defense'] // 2 + random.randint(-3, 5))
            monster['hp'] -= player_damage
            battle_log.append(f"⚔️ You dealt **{player_damage}** damage to {monster['emoji']} {monster['name']}")
            
            if monster['hp'] <= 0:
                break
            
            monster_damage = max(1, monster['attack'] - player['defense'] // 2 + random.randint(-2, 4))
            player['hp'] -= monster_damage
            battle_log.append(f"💥 {monster['emoji']} {monster['name']} dealt **{monster_damage}** damage to you")
            
            round_num += 1
            if round_num > 20:
                break
        
        won = monster['hp'] <= 0
        
        embed = discord.Embed(
            title=f"⚔️ Battle vs {monster['emoji']} {monster['name']}",
            color=discord.Color.green() if won else discord.Color.red()
        )
        
        last_5_logs = battle_log[-5:]
        embed.add_field(
            name="📜 Battle Log",
            value="\n".join(last_5_logs) if last_5_logs else "No actions",
            inline=False
        )
        
        if won:
            coins = random.randint(*monster['coin_reward'])
            exp = monster['exp_reward']
            
            await self.db.add_coins(user_id, coins)
            level_result = await self.db.add_exp(user_id, exp)
            await self.db.update_battle_stats(user_id, wins=1, monsters_killed=1)
            
            embed.add_field(
                name="🎉 VICTORY!",
                value=f"You defeated {monster['emoji']} {monster['name']}!\n\n"
                      f"💰 **+{coins}** coins\n"
                      f"✨ **+{exp}** EXP",
                inline=False
            )
            
            if level_result['leveled_up']:
                embed.add_field(
                    name="🎊 LEVEL UP!",
                    value=f"You reached **Level {level_result['new_level']}**!",
                    inline=False
                )
        else:
            await self.db.update_battle_stats(user_id, losses=1)
            
            embed.add_field(
                name="💀 DEFEAT",
                value=f"{monster['emoji']} {monster['name']} was too strong!\n"
                      f"Better luck next time!",
                inline=False
            )
        
        embed.add_field(
            name="📊 Final Status",
            value=f"Your HP: **{max(0, player['hp'])}/{player['max_hp']}**\n"
                  f"Monster HP: **{max(0, monster['hp'])}/{monster['hp'] + sum(int(log.split('**')[1]) for log in battle_log if 'dealt' in log and 'You' in log)}**",
            inline=False
        )
        
        embed.set_footer(text=f"Monster Rarity: {monster['rarity'].display_name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BattleCog(bot))
