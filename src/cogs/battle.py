import discord
from discord import app_commands
from discord.ext import commands
import random
from data.animals import get_random_monster, get_animal_by_id
from data.items import get_item

class BattleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    def apply_skill_bonus(self, animal_data: dict, animal_stats: dict) -> dict:
        stats = animal_stats.copy()
        skill = animal_data.get('skill', {})
        
        if skill.get('type') == 'passive':
            effect = skill.get('effect', '')
            
            if '+10% attack' in effect.lower():
                stats['attack'] = int(stats['attack'] * 1.1)
            if '+15% defense' in effect.lower():
                stats['defense'] = int(stats['defense'] * 1.15)
            if '+25% damage and defense' in effect.lower():
                stats['attack'] = int(stats['attack'] * 1.25)
                stats['defense'] = int(stats['defense'] * 1.25)
        
        return stats
    
    @app_commands.command(name="battle", description="Fight monsters using your animal team!")
    async def battle(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        await self.db.get_user(user_id, interaction.user.name)
        
        team = await self.db.get_animal_team(user_id)
        
        if not team:
            embed = discord.Embed(
                title="❌ Tidak Bisa Battle!",
                description="**Kamu tidak punya hewan di tim!**\n\n"
                            "Untuk battle, kamu harus:\n"
                            "1. Gunakan `/hunt` untuk menangkap hewan\n"
                            "2. Gunakan `/animal equip <id>` untuk menambahkan ke tim\n"
                            "3. Gunakan `/team` untuk melihat tim\n\n"
                            "*Battle membutuhkan minimal 1 hewan di tim!*",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        alive_animals = [a for a in team if a['current_hp'] > 0]
        
        if not alive_animals:
            embed = discord.Embed(
                title="❌ Tim Terluka!",
                description="**Semua hewanmu sedang terluka!**\n\n"
                            "Gunakan `/animal heal` untuk menyembuhkan timmu.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        profile = await self.db.get_user(user_id, interaction.user.name)
        luck_bonus = 0
        if profile['equipped_skin']:
            skin = get_item(profile['equipped_skin'])
            if skin:
                luck_bonus = skin.get('luck_bonus', 0)
        
        monster = get_random_monster(luck_bonus)
        monster_hp = monster['hp']
        monster_max_hp = monster['hp']
        
        battle_log = []
        round_num = 0
        
        current_animal_idx = 0
        
        while current_animal_idx < len(alive_animals) and monster_hp > 0:
            current_animal = alive_animals[current_animal_idx]
            animal_data = get_animal_by_id(current_animal['animal_id'])
            
            stats = self.apply_skill_bonus(animal_data, {
                'attack': current_animal['attack'],
                'defense': current_animal['defense'],
                'hp': current_animal['current_hp']
            })
            
            animal_hp = current_animal['current_hp']
            animal_emoji = animal_data['emoji'] if animal_data else "🐾"
            animal_name = current_animal['nickname']
            
            while animal_hp > 0 and monster_hp > 0 and round_num < 30:
                round_num += 1
                
                damage_to_monster = max(1, stats['attack'] - monster['defense'] // 3 + random.randint(-2, 4))
                
                if animal_data and 'ignores' in animal_data['skill'].get('effect', '').lower():
                    damage_to_monster = int(damage_to_monster * 1.25)
                
                monster_hp -= damage_to_monster
                battle_log.append(f"⚔️ {animal_emoji} {animal_name} menyerang → **{damage_to_monster}** damage")
                
                if monster_hp <= 0:
                    break
                
                damage_to_animal = max(1, monster['attack'] - stats['defense'] // 3 + random.randint(-2, 3))
                animal_hp -= damage_to_animal
                battle_log.append(f"💥 {monster['emoji']} {monster['name']} menyerang → **{damage_to_animal}** damage ke {animal_name}")
                
                if animal_hp <= 0:
                    battle_log.append(f"💀 {animal_emoji} {animal_name} kalah!")
            
            await self.db.update_animal_hp(current_animal['id'], animal_hp)
            
            if animal_hp <= 0:
                current_animal_idx += 1
                if current_animal_idx < len(alive_animals):
                    next_animal = alive_animals[current_animal_idx]
                    next_data = get_animal_by_id(next_animal['animal_id'])
                    next_emoji = next_data['emoji'] if next_data else "🐾"
                    battle_log.append(f"🔄 {next_emoji} {next_animal['nickname']} maju ke arena!")
        
        won = monster_hp <= 0
        
        embed = discord.Embed(
            title=f"⚔️ Battle vs {monster['emoji']} {monster['name']}",
            color=discord.Color.green() if won else discord.Color.red()
        )
        
        last_logs = battle_log[-8:]
        embed.add_field(
            name="📜 Log Pertarungan",
            value="\n".join(last_logs) if last_logs else "Tidak ada aksi",
            inline=False
        )
        
        if won:
            coins = random.randint(*monster['coin_reward'])
            base_exp = monster['exp_reward']
            
            await self.db.add_coins(user_id, coins)
            level_result = await self.db.add_exp(user_id, base_exp // 2)
            await self.db.update_battle_stats(user_id, wins=1, monsters_killed=1)
            
            exp_per_animal = base_exp // len(alive_animals)
            leveled_animals = []
            
            for a in alive_animals:
                animal_level_result = await self.db.add_animal_exp(a['id'], exp_per_animal)
                if animal_level_result['leveled_up']:
                    animal_data = get_animal_by_id(a['animal_id'])
                    emoji = animal_data['emoji'] if animal_data else "🐾"
                    leveled_animals.append(f"{emoji} {a['nickname']} → Lv.{animal_level_result['new_level']}")
            
            embed.add_field(
                name="🎉 MENANG!",
                value=f"Kamu mengalahkan {monster['emoji']} {monster['name']}!\n\n"
                      f"💰 **+{coins}** koin\n"
                      f"✨ **+{base_exp // 2}** EXP (player)\n"
                      f"🐾 **+{exp_per_animal}** EXP (per hewan)",
                inline=False
            )
            
            if leveled_animals:
                embed.add_field(
                    name="🎊 Level Up Hewan!",
                    value="\n".join(leveled_animals),
                    inline=False
                )
            
            if level_result['leveled_up']:
                embed.add_field(
                    name="🎊 LEVEL UP Player!",
                    value=f"Kamu mencapai **Level {level_result['new_level']}**!",
                    inline=False
                )
        else:
            await self.db.update_battle_stats(user_id, losses=1)
            
            embed.add_field(
                name="💀 KALAH",
                value=f"{monster['emoji']} {monster['name']} terlalu kuat!\n"
                      f"Semua hewanmu telah jatuh.\n\n"
                      f"Gunakan `/animal heal` untuk menyembuhkan tim.",
                inline=False
            )
        
        team_status = []
        for a in team:
            a_updated = await self.db.get_animal(a['id'])
            animal_data = get_animal_by_id(a['animal_id'])
            emoji = animal_data['emoji'] if animal_data else "🐾"
            hp = a_updated['current_hp'] if a_updated else 0
            max_hp = a_updated['max_hp'] if a_updated else a['max_hp']
            status = f"{emoji} {a['nickname']}: {hp}/{max_hp} HP"
            team_status.append(status)
        
        embed.add_field(
            name="📊 Status Tim",
            value="\n".join(team_status),
            inline=False
        )
        
        embed.set_footer(text=f"Monster Rarity: {monster['rarity'].display_name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BattleCog(bot))
