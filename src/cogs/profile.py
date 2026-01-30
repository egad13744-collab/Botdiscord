import discord
from discord import app_commands
from discord.ext import commands
from data.items import get_item, SKINS, WEAPONS, FISHING_RODS

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="profile", description="View your adventure profile")
    async def profile(self, interaction: discord.Interaction, user: discord.User = None):
        target = user or interaction.user
        profile = await self.db.get_user(target.id, target.name)
        battle_stats = await self.db.get_battle_stats(target.id)
        
        exp_needed = self.db.exp_for_level(profile['level'])
        progress = int((profile['exp'] / exp_needed) * 10)
        progress_bar = "█" * progress + "░" * (10 - progress)
        
        embed = discord.Embed(
            title=f"⚔️ {target.display_name}'s Profile",
            color=discord.Color.blue()
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(
            name="📊 Stats",
            value=f"**Level:** {profile['level']}\n"
                  f"**EXP:** {profile['exp']}/{exp_needed}\n"
                  f"[{progress_bar}]",
            inline=True
        )
        
        embed.add_field(
            name="💰 Economy",
            value=f"**Coins:** {profile['coins']:,}\n"
                  f"**Daily Streak:** {profile['daily_streak']} 🔥",
            inline=True
        )
        
        equipped_weapon = "None"
        equipped_rod = "None"
        equipped_skin = "None"
        
        if profile['equipped_weapon']:
            item = get_item(profile['equipped_weapon'])
            if item:
                equipped_weapon = f"{item['emoji']} {item['name']}"
        
        if profile['equipped_rod']:
            item = get_item(profile['equipped_rod'])
            if item:
                equipped_rod = f"{item['emoji']} {item['name']}"
        
        if profile['equipped_skin']:
            item = get_item(profile['equipped_skin'])
            if item:
                equipped_skin = f"{item['emoji']} {item['name']}"
        
        embed.add_field(
            name="🎒 Equipment",
            value=f"**Weapon:** {equipped_weapon}\n"
                  f"**Rod:** {equipped_rod}\n"
                  f"**Skin:** {equipped_skin}",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ Battle Stats",
            value=f"**Wins:** {battle_stats['wins']}\n"
                  f"**Losses:** {battle_stats['losses']}\n"
                  f"**Monsters Killed:** {battle_stats['monsters_killed']}",
            inline=True
        )
        
        embed.set_footer(text="Use /help to see all commands!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="equip", description="Equip an item from your inventory")
    @app_commands.describe(item_id="The ID of the item to equip")
    async def equip(self, interaction: discord.Interaction, item_id: str):
        user_id = interaction.user.id
        
        has_item = await self.db.has_item(user_id, item_id)
        if not has_item:
            await interaction.response.send_message(
                "❌ You don't have this item in your inventory!",
                ephemeral=True
            )
            return
        
        item = get_item(item_id)
        if not item:
            await interaction.response.send_message(
                "❌ Invalid item ID!",
                ephemeral=True
            )
            return
        
        if item_id in WEAPONS:
            await self.db.update_user(user_id, equipped_weapon=item_id)
            slot = "weapon"
        elif item_id in FISHING_RODS:
            await self.db.update_user(user_id, equipped_rod=item_id)
            slot = "fishing rod"
        elif item_id in SKINS:
            await self.db.update_user(user_id, equipped_skin=item_id)
            slot = "skin"
        else:
            await interaction.response.send_message(
                "❌ This item cannot be equipped!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="✅ Item Equipped!",
            description=f"You equipped **{item['emoji']} {item['name']}** as your {slot}!",
            color=item['rarity'].color
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unequip", description="Unequip an item")
    @app_commands.describe(slot="The slot to unequip (weapon, rod, skin)")
    @app_commands.choices(slot=[
        app_commands.Choice(name="Weapon", value="weapon"),
        app_commands.Choice(name="Fishing Rod", value="rod"),
        app_commands.Choice(name="Skin", value="skin"),
    ])
    async def unequip(self, interaction: discord.Interaction, slot: str):
        user_id = interaction.user.id
        
        if slot == "weapon":
            await self.db.update_user(user_id, equipped_weapon=None)
        elif slot == "rod":
            await self.db.update_user(user_id, equipped_rod=None)
        elif slot == "skin":
            await self.db.update_user(user_id, equipped_skin=None)
        
        await interaction.response.send_message(
            f"✅ Unequipped your {slot}!",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
