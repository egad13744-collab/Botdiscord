import discord
from discord import app_commands
from discord.ext import commands
from data.animals import get_animal_by_id, ANIMALS

class AnimalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    animal_group = app_commands.Group(name="animal", description="Manage your animals")
    
    @animal_group.command(name="list", description="View all your captured animals")
    async def animal_list(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        await self.db.get_user(user_id, interaction.user.name)
        
        animals = await self.db.get_user_animals(user_id)
        
        if not animals:
            embed = discord.Embed(
                title="🐾 Koleksi Hewanmu",
                description="Kamu belum punya hewan!\nGunakan `/hunt` untuk menangkap hewan pertamamu.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"🐾 Koleksi Hewan {interaction.user.display_name}",
            description=f"Total: **{len(animals)}** hewan",
            color=discord.Color.blue()
        )
        
        team_animals = [a for a in animals if a['is_in_team']]
        reserve_animals = [a for a in animals if not a['is_in_team']]
        
        if team_animals:
            team_text = ""
            for a in sorted(team_animals, key=lambda x: x['team_slot'] or 0):
                animal_data = get_animal_by_id(a['animal_id'])
                emoji = animal_data['emoji'] if animal_data else "❓"
                rarity = animal_data['rarity'].display_name if animal_data else "Unknown"
                team_text += f"**{a['team_slot']}.** {emoji} {a['nickname']} (Lv.{a['level']}) - {rarity}\n"
                team_text += f"   ❤️ {a['current_hp']}/{a['max_hp']} | ⚔️ {a['attack']} | 🛡️ {a['defense']}\n"
                team_text += f"   🆔 `{a['id']}`\n"
            embed.add_field(name="⚔️ Tim Aktif", value=team_text, inline=False)
        
        if reserve_animals:
            reserve_text = ""
            for a in reserve_animals[:10]:
                animal_data = get_animal_by_id(a['animal_id'])
                emoji = animal_data['emoji'] if animal_data else "❓"
                rarity = animal_data['rarity'].display_name if animal_data else "Unknown"
                reserve_text += f"{emoji} {a['nickname']} (Lv.{a['level']}) - {rarity} | ID: `{a['id']}`\n"
            
            if len(reserve_animals) > 10:
                reserve_text += f"\n... dan {len(reserve_animals) - 10} hewan lainnya"
            
            embed.add_field(name="📦 Cadangan", value=reserve_text, inline=False)
        
        max_team = await self.db.get_max_team_size(user_id)
        embed.set_footer(text=f"Slot tim: {len(team_animals)}/{max_team} | Gunakan /animal equip <id> untuk menambah ke tim")
        
        await interaction.response.send_message(embed=embed)
    
    @animal_group.command(name="equip", description="Add an animal to your battle team")
    @app_commands.describe(animal_id="The ID of the animal to add to your team")
    async def animal_equip(self, interaction: discord.Interaction, animal_id: str):
        user_id = interaction.user.id
        await self.db.get_user(user_id, interaction.user.name)
        
        animal = await self.db.get_animal(animal_id)
        
        if not animal or animal['user_id'] != user_id:
            await interaction.response.send_message(
                "❌ Hewan tidak ditemukan atau bukan milikmu!",
                ephemeral=True
            )
            return
        
        if animal['is_in_team']:
            await interaction.response.send_message(
                "❌ Hewan ini sudah ada di timmu!",
                ephemeral=True
            )
            return
        
        success = await self.db.add_animal_to_team(user_id, animal_id)
        
        if not success:
            max_team = await self.db.get_max_team_size(user_id)
            await interaction.response.send_message(
                f"❌ Tim sudah penuh! (Maksimal {max_team} hewan)\n"
                f"Gunakan `/animal unequip <id>` untuk mengeluarkan hewan dari tim.",
                ephemeral=True
            )
            return
        
        animal_data = get_animal_by_id(animal['animal_id'])
        emoji = animal_data['emoji'] if animal_data else "🐾"
        
        embed = discord.Embed(
            title="✅ Hewan Ditambahkan ke Tim!",
            description=f"{emoji} **{animal['nickname']}** (Lv.{animal['level']}) sekarang ada di timmu!",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @animal_group.command(name="unequip", description="Remove an animal from your battle team")
    @app_commands.describe(animal_id="The ID of the animal to remove from your team")
    async def animal_unequip(self, interaction: discord.Interaction, animal_id: str):
        user_id = interaction.user.id
        
        animal = await self.db.get_animal(animal_id)
        
        if not animal or animal['user_id'] != user_id:
            await interaction.response.send_message(
                "❌ Hewan tidak ditemukan atau bukan milikmu!",
                ephemeral=True
            )
            return
        
        if not animal['is_in_team']:
            await interaction.response.send_message(
                "❌ Hewan ini tidak ada di timmu!",
                ephemeral=True
            )
            return
        
        await self.db.remove_animal_from_team(user_id, animal_id)
        
        animal_data = get_animal_by_id(animal['animal_id'])
        emoji = animal_data['emoji'] if animal_data else "🐾"
        
        embed = discord.Embed(
            title="✅ Hewan Dikeluarkan dari Tim",
            description=f"{emoji} **{animal['nickname']}** telah dipindahkan ke cadangan.",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @animal_group.command(name="info", description="View detailed info about an animal")
    @app_commands.describe(animal_id="The ID of the animal")
    async def animal_info(self, interaction: discord.Interaction, animal_id: str):
        user_id = interaction.user.id
        
        animal = await self.db.get_animal(animal_id)
        
        if not animal or animal['user_id'] != user_id:
            await interaction.response.send_message(
                "❌ Hewan tidak ditemukan atau bukan milikmu!",
                ephemeral=True
            )
            return
        
        animal_data = get_animal_by_id(animal['animal_id'])
        if not animal_data:
            await interaction.response.send_message("❌ Data hewan tidak ditemukan!", ephemeral=True)
            return
        
        exp_needed = self.db.animal_exp_for_level(animal['level'])
        progress = int((animal['exp'] / exp_needed) * 10)
        progress_bar = "█" * progress + "░" * (10 - progress)
        
        embed = discord.Embed(
            title=f"{animal_data['emoji']} {animal['nickname']}",
            description=f"**{animal_data['name']}** ({animal_data['rarity'].display_name})",
            color=animal_data['rarity'].color
        )
        
        embed.add_field(
            name="📊 Level",
            value=f"Level **{animal['level']}**\n"
                  f"EXP: {animal['exp']}/{exp_needed}\n"
                  f"[{progress_bar}]",
            inline=True
        )
        
        embed.add_field(
            name="⚔️ Stats",
            value=f"❤️ HP: {animal['current_hp']}/{animal['max_hp']}\n"
                  f"⚔️ Attack: {animal['attack']}\n"
                  f"🛡️ Defense: {animal['defense']}",
            inline=True
        )
        
        embed.add_field(
            name=f"✨ Skill: {animal_data['skill']['name']}",
            value=f"*{animal_data['skill']['effect']}*\n"
                  f"Type: {animal_data['skill']['type'].title()}",
            inline=False
        )
        
        status = "⚔️ Dalam Tim" if animal['is_in_team'] else "📦 Cadangan"
        embed.add_field(name="📍 Status", value=status, inline=True)
        embed.add_field(name="🆔 ID", value=f"`{animal['id']}`", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @animal_group.command(name="heal", description="Heal all animals in your team (costs coins)")
    async def animal_heal(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user = await self.db.get_user(user_id, interaction.user.name)
        
        team = await self.db.get_animal_team(user_id)
        
        if not team:
            await interaction.response.send_message(
                "❌ Kamu tidak punya hewan di tim!",
                ephemeral=True
            )
            return
        
        injured = [a for a in team if a['current_hp'] < a['max_hp']]
        
        if not injured:
            await interaction.response.send_message(
                "✅ Semua hewanmu sudah sehat!",
                ephemeral=True
            )
            return
        
        heal_cost = len(injured) * 20
        
        if user['coins'] < heal_cost:
            await interaction.response.send_message(
                f"❌ Kamu butuh **{heal_cost}** koin untuk menyembuhkan timmu!\n"
                f"Kamu hanya punya **{user['coins']}** koin.",
                ephemeral=True
            )
            return
        
        await self.db.add_coins(user_id, -heal_cost)
        await self.db.heal_team(user_id)
        
        embed = discord.Embed(
            title="💚 Tim Disembuhkan!",
            description=f"Semua hewanmu telah disembuhkan!\n\n"
                        f"💰 Biaya: **{heal_cost}** koin",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="team", description="View your current battle team")
    async def team_view(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        await self.db.get_user(user_id, interaction.user.name)
        
        team = await self.db.get_animal_team(user_id)
        max_team = await self.db.get_max_team_size(user_id)
        
        embed = discord.Embed(
            title=f"⚔️ Tim Battle {interaction.user.display_name}",
            color=discord.Color.gold()
        )
        
        if not team:
            embed.description = (
                "❌ **Tim Kosong!**\n\n"
                "Kamu tidak bisa battle tanpa hewan!\n"
                "1. Gunakan `/hunt` untuk menangkap hewan\n"
                "2. Gunakan `/animal equip <id>` untuk menambahkan ke tim"
            )
        else:
            for a in sorted(team, key=lambda x: x['team_slot'] or 0):
                animal_data = get_animal_by_id(a['animal_id'])
                emoji = animal_data['emoji'] if animal_data else "❓"
                rarity = animal_data['rarity'].display_name if animal_data else "Unknown"
                skill_name = animal_data['skill']['name'] if animal_data else "Unknown"
                
                hp_percent = (a['current_hp'] / a['max_hp']) * 100
                hp_bar_len = int(hp_percent / 10)
                hp_bar = "🟩" * hp_bar_len + "🟥" * (10 - hp_bar_len)
                
                embed.add_field(
                    name=f"Slot {a['team_slot']}: {emoji} {a['nickname']} (Lv.{a['level']})",
                    value=f"**{rarity}**\n"
                          f"❤️ {a['current_hp']}/{a['max_hp']} {hp_bar}\n"
                          f"⚔️ ATK: {a['attack']} | 🛡️ DEF: {a['defense']}\n"
                          f"✨ {skill_name}",
                    inline=False
                )
            
            embed.description = f"Tim siap untuk battle! ({len(team)}/{max_team} slot)"
        
        embed.set_footer(text=f"Max Team Size: {max_team} | Level up untuk unlock lebih banyak slot!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AnimalCog(bot))
