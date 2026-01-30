import discord
from discord import app_commands
from discord.ext import commands
from data.items import get_item, ALL_ITEMS, Rarity

class InventoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="inventory", description="View your inventory")
    async def inventory(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        await self.db.get_user(user_id, interaction.user.name)
        inventory = await self.db.get_inventory(user_id)
        
        if not inventory:
            embed = discord.Embed(
                title="🎒 Your Inventory",
                description="Your inventory is empty!\nUse `/hunt` or `/fish` to get items.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        categorized = {
            "hunt_loot": [],
            "fish_loot": [],
            "weapons": [],
            "rods": [],
            "skins": [],
            "other": []
        }
        
        from data.items import HUNT_LOOT, FISH_LOOT, WEAPONS, FISHING_RODS, SKINS
        
        for inv_item in inventory:
            item_id = inv_item['item_id']
            quantity = inv_item['quantity']
            item = get_item(item_id)
            
            if not item:
                continue
            
            item_str = f"{item['emoji']} {item['name']} x{quantity}"
            
            if item_id in HUNT_LOOT:
                categorized["hunt_loot"].append(item_str)
            elif item_id in FISH_LOOT:
                categorized["fish_loot"].append(item_str)
            elif item_id in WEAPONS:
                categorized["weapons"].append(item_str)
            elif item_id in FISHING_RODS:
                categorized["rods"].append(item_str)
            elif item_id in SKINS:
                categorized["skins"].append(item_str)
            else:
                categorized["other"].append(item_str)
        
        embed = discord.Embed(
            title=f"🎒 {interaction.user.display_name}'s Inventory",
            color=discord.Color.green()
        )
        
        if categorized["weapons"]:
            embed.add_field(
                name="⚔️ Weapons",
                value="\n".join(categorized["weapons"]),
                inline=False
            )
        
        if categorized["rods"]:
            embed.add_field(
                name="🎣 Fishing Rods",
                value="\n".join(categorized["rods"]),
                inline=False
            )
        
        if categorized["skins"]:
            embed.add_field(
                name="👔 Skins",
                value="\n".join(categorized["skins"]),
                inline=False
            )
        
        if categorized["hunt_loot"]:
            embed.add_field(
                name="🏹 Hunt Loot",
                value="\n".join(categorized["hunt_loot"][:10]) + 
                      (f"\n... and {len(categorized['hunt_loot']) - 10} more" if len(categorized['hunt_loot']) > 10 else ""),
                inline=False
            )
        
        if categorized["fish_loot"]:
            embed.add_field(
                name="🐟 Fish",
                value="\n".join(categorized["fish_loot"][:10]) +
                      (f"\n... and {len(categorized['fish_loot']) - 10} more" if len(categorized['fish_loot']) > 10 else ""),
                inline=False
            )
        
        embed.set_footer(text="Use /sell <item_id> to sell items | /equip <item_id> to equip")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InventoryCog(bot))
