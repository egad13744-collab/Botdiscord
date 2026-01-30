import discord
from discord import app_commands
from discord.ext import commands
from data.items import get_item

class TradeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.pending_trades = {}
    
    @app_commands.command(name="trade", description="Trade items or coins with another player")
    @app_commands.describe(
        user="The user to trade with",
        give_item="Item ID to give (optional)",
        give_quantity="Quantity to give",
        give_coins="Coins to give",
        request_item="Item ID you want (optional)",
        request_quantity="Quantity you want",
        request_coins="Coins you want"
    )
    async def trade(
        self, 
        interaction: discord.Interaction, 
        user: discord.User,
        give_item: str = None,
        give_quantity: int = 1,
        give_coins: int = 0,
        request_item: str = None,
        request_quantity: int = 1,
        request_coins: int = 0
    ):
        sender_id = interaction.user.id
        receiver_id = user.id
        
        if sender_id == receiver_id:
            await interaction.response.send_message(
                "❌ You can't trade with yourself!",
                ephemeral=True
            )
            return
        
        if user.bot:
            await interaction.response.send_message(
                "❌ You can't trade with bots!",
                ephemeral=True
            )
            return
        
        if not give_item and give_coins <= 0 and not request_item and request_coins <= 0:
            await interaction.response.send_message(
                "❌ You must offer or request something to trade!",
                ephemeral=True
            )
            return
        
        sender = await self.db.get_user(sender_id, interaction.user.name)
        await self.db.get_user(receiver_id, user.name)
        
        if give_coins > sender['coins']:
            await interaction.response.send_message(
                f"❌ You don't have enough coins! You have **{sender['coins']:,}** coins.",
                ephemeral=True
            )
            return
        
        if give_item:
            has_item = await self.db.has_item(sender_id, give_item, give_quantity)
            if not has_item:
                await interaction.response.send_message(
                    f"❌ You don't have {give_quantity}x of that item!",
                    ephemeral=True
                )
                return
        
        trade_key = f"{sender_id}_{receiver_id}"
        self.pending_trades[trade_key] = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "give_item": give_item,
            "give_quantity": give_quantity,
            "give_coins": give_coins,
            "request_item": request_item,
            "request_quantity": request_quantity,
            "request_coins": request_coins
        }
        
        embed = discord.Embed(
            title="🔄 Trade Proposal",
            description=f"**{interaction.user.display_name}** wants to trade with **{user.display_name}**",
            color=discord.Color.blue()
        )
        
        offer_text = []
        if give_item:
            item = get_item(give_item)
            if item:
                offer_text.append(f"{item['emoji']} {item['name']} x{give_quantity}")
        if give_coins > 0:
            offer_text.append(f"💰 {give_coins:,} coins")
        
        request_text = []
        if request_item:
            item = get_item(request_item)
            if item:
                request_text.append(f"{item['emoji']} {item['name']} x{request_quantity}")
        if request_coins > 0:
            request_text.append(f"💰 {request_coins:,} coins")
        
        embed.add_field(
            name="📤 Offering",
            value="\n".join(offer_text) if offer_text else "Nothing",
            inline=True
        )
        
        embed.add_field(
            name="📥 Requesting",
            value="\n".join(request_text) if request_text else "Nothing",
            inline=True
        )
        
        embed.set_footer(text=f"{user.display_name}, use /accept_trade to accept or /decline_trade to decline")
        
        await interaction.response.send_message(
            content=f"{user.mention}",
            embed=embed
        )
    
    @app_commands.command(name="accept_trade", description="Accept a pending trade")
    @app_commands.describe(trader="The user who proposed the trade")
    async def accept_trade(self, interaction: discord.Interaction, trader: discord.User):
        receiver_id = interaction.user.id
        sender_id = trader.id
        trade_key = f"{sender_id}_{receiver_id}"
        
        if trade_key not in self.pending_trades:
            await interaction.response.send_message(
                "❌ No pending trade found from this user!",
                ephemeral=True
            )
            return
        
        trade = self.pending_trades[trade_key]
        
        receiver = await self.db.get_user(receiver_id, interaction.user.name)
        sender = await self.db.get_user(sender_id, trader.name)
        
        if trade['request_coins'] > receiver['coins']:
            await interaction.response.send_message(
                f"❌ You don't have enough coins! You need **{trade['request_coins']:,}** coins.",
                ephemeral=True
            )
            return
        
        if trade['request_item']:
            has_item = await self.db.has_item(receiver_id, trade['request_item'], trade['request_quantity'])
            if not has_item:
                await interaction.response.send_message(
                    "❌ You don't have the requested items!",
                    ephemeral=True
                )
                return
        
        if trade['give_coins'] > sender['coins']:
            await interaction.response.send_message(
                "❌ The trader no longer has enough coins!",
                ephemeral=True
            )
            del self.pending_trades[trade_key]
            return
        
        if trade['give_item']:
            has_item = await self.db.has_item(sender_id, trade['give_item'], trade['give_quantity'])
            if not has_item:
                await interaction.response.send_message(
                    "❌ The trader no longer has the offered items!",
                    ephemeral=True
                )
                del self.pending_trades[trade_key]
                return
        
        if trade['give_item']:
            await self.db.remove_item(sender_id, trade['give_item'], trade['give_quantity'])
            await self.db.add_item(receiver_id, trade['give_item'], trade['give_quantity'])
        
        if trade['give_coins'] > 0:
            await self.db.add_coins(sender_id, -trade['give_coins'])
            await self.db.add_coins(receiver_id, trade['give_coins'])
        
        if trade['request_item']:
            await self.db.remove_item(receiver_id, trade['request_item'], trade['request_quantity'])
            await self.db.add_item(sender_id, trade['request_item'], trade['request_quantity'])
        
        if trade['request_coins'] > 0:
            await self.db.add_coins(receiver_id, -trade['request_coins'])
            await self.db.add_coins(sender_id, trade['request_coins'])
        
        del self.pending_trades[trade_key]
        
        embed = discord.Embed(
            title="✅ Trade Complete!",
            description=f"Trade between **{trader.display_name}** and **{interaction.user.display_name}** successful!",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="decline_trade", description="Decline a pending trade")
    @app_commands.describe(trader="The user who proposed the trade")
    async def decline_trade(self, interaction: discord.Interaction, trader: discord.User):
        receiver_id = interaction.user.id
        sender_id = trader.id
        trade_key = f"{sender_id}_{receiver_id}"
        
        if trade_key not in self.pending_trades:
            await interaction.response.send_message(
                "❌ No pending trade found from this user!",
                ephemeral=True
            )
            return
        
        del self.pending_trades[trade_key]
        
        await interaction.response.send_message(
            f"❌ Trade with **{trader.display_name}** has been declined."
        )

async def setup(bot):
    await bot.add_cog(TradeCog(bot))
