import discord
from discord import app_commands
from discord.ext import commands
from data.items import WEAPONS, FISHING_RODS, SKINS, get_item, ALL_ITEMS

class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="shop", description="Browse the adventure shop")
    @app_commands.describe(category="Shop category to browse")
    @app_commands.choices(category=[
        app_commands.Choice(name="Weapons", value="weapons"),
        app_commands.Choice(name="Fishing Rods", value="rods"),
        app_commands.Choice(name="Skins", value="skins"),
    ])
    async def shop(self, interaction: discord.Interaction, category: str = "weapons"):
        user = await self.db.get_user(interaction.user.id, interaction.user.name)
        
        if category == "weapons":
            items = WEAPONS
            title = "⚔️ Weapons Shop"
            description = "Stronger weapons deal more damage in battle!"
        elif category == "rods":
            items = FISHING_RODS
            title = "🎣 Fishing Rods Shop"
            description = "Better rods give more luck when fishing!"
        else:
            items = SKINS
            title = "👔 Skins Shop"
            description = "Skins give bonus EXP, coins, and luck!"
        
        embed = discord.Embed(
            title=title,
            description=f"{description}\n\n💰 Your coins: **{user['coins']:,}**",
            color=discord.Color.gold()
        )
        
        for item_id, item in items.items():
            if 'buy_price' not in item:
                continue
                
            stats = []
            if 'attack' in item:
                stats.append(f"Attack: +{item['attack']}")
            if 'luck_bonus' in item:
                stats.append(f"Luck: +{item['luck_bonus']}%")
            if 'exp_bonus' in item:
                stats.append(f"EXP: +{item['exp_bonus']}%")
            if 'coin_bonus' in item:
                stats.append(f"Coins: +{item['coin_bonus']}%")
            
            stats_str = " | ".join(stats) if stats else "No special stats"
            
            embed.add_field(
                name=f"{item['emoji']} {item['name']} ({item['rarity'].display_name})",
                value=f"💰 **{item['buy_price']:,}** coins\n{stats_str}\n`/buy {item_id}`",
                inline=True
            )
        
        embed.set_footer(text="Use /buy <item_id> to purchase | /sell <item_id> to sell")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item_id="The ID of the item to buy")
    async def buy(self, interaction: discord.Interaction, item_id: str):
        user_id = interaction.user.id
        user = await self.db.get_user(user_id, interaction.user.name)
        
        item = get_item(item_id)
        if not item or 'buy_price' not in item:
            await interaction.response.send_message(
                "❌ This item is not available for purchase!",
                ephemeral=True
            )
            return
        
        if user['coins'] < item['buy_price']:
            await interaction.response.send_message(
                f"❌ You need **{item['buy_price']:,}** coins but only have **{user['coins']:,}**!",
                ephemeral=True
            )
            return
        
        await self.db.add_coins(user_id, -item['buy_price'])
        await self.db.add_item(user_id, item_id)
        
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You bought **{item['emoji']} {item['name']}** for **{item['buy_price']:,}** coins!",
            color=discord.Color.green()
        )
        embed.set_footer(text="Use /equip to equip your new item!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="sell", description="Sell an item from your inventory")
    @app_commands.describe(item_id="The ID of the item to sell", quantity="How many to sell")
    async def sell(self, interaction: discord.Interaction, item_id: str, quantity: int = 1):
        user_id = interaction.user.id
        
        if quantity < 1:
            await interaction.response.send_message(
                "❌ Quantity must be at least 1!",
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
        
        if 'sell_price' not in item:
            sell_price = item.get('buy_price', 10) // 2
        else:
            sell_price = item['sell_price']
        
        success = await self.db.remove_item(user_id, item_id, quantity)
        if not success:
            await interaction.response.send_message(
                f"❌ You don't have {quantity}x {item['name']} in your inventory!",
                ephemeral=True
            )
            return
        
        total_coins = sell_price * quantity
        await self.db.add_coins(user_id, total_coins)
        
        embed = discord.Embed(
            title="💰 Item Sold!",
            description=f"You sold **{quantity}x {item['emoji']} {item['name']}** for **{total_coins:,}** coins!",
            color=discord.Color.gold()
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ShopCog(bot))
