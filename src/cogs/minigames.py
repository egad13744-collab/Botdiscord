import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class MinigamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.guess_games = {}
    
    @app_commands.command(name="guess", description="Play a number guessing game!")
    @app_commands.describe(bet="Amount of coins to bet (10-1000)")
    async def guess(self, interaction: discord.Interaction, bet: int = 50):
        user_id = interaction.user.id
        
        if user_id in self.guess_games:
            await interaction.response.send_message(
                "❌ You already have a guessing game in progress!",
                ephemeral=True
            )
            return
        
        if bet < 10 or bet > 1000:
            await interaction.response.send_message(
                "❌ Bet must be between 10 and 1000 coins!",
                ephemeral=True
            )
            return
        
        user = await self.db.get_user(user_id, interaction.user.name)
        if user['coins'] < bet:
            await interaction.response.send_message(
                f"❌ You don't have enough coins! You have **{user['coins']:,}** coins.",
                ephemeral=True
            )
            return
        
        secret_number = random.randint(1, 10)
        self.guess_games[user_id] = {
            "number": secret_number,
            "bet": bet,
            "attempts": 3
        }
        
        embed = discord.Embed(
            title="🎲 Number Guessing Game",
            description=f"I'm thinking of a number between **1** and **10**!\n\n"
                        f"💰 Your bet: **{bet}** coins\n"
                        f"🎯 Attempts left: **3**\n\n"
                        f"Type a number in chat to guess!",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)
        
        def check(m):
            return m.author.id == user_id and m.channel.id == interaction.channel.id and m.content.isdigit()
        
        try:
            while user_id in self.guess_games and self.guess_games[user_id]["attempts"] > 0:
                msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                guess = int(msg.content)
                
                if guess < 1 or guess > 10:
                    await msg.reply("Please guess a number between 1 and 10!")
                    continue
                
                game = self.guess_games[user_id]
                
                if guess == game["number"]:
                    winnings = game["bet"] * 2
                    await self.db.add_coins(user_id, winnings - game["bet"])
                    
                    win_embed = discord.Embed(
                        title="🎉 Correct!",
                        description=f"The number was **{game['number']}**!\n\n"
                                    f"💰 You won **{winnings}** coins!",
                        color=discord.Color.green()
                    )
                    await msg.reply(embed=win_embed)
                    del self.guess_games[user_id]
                    return
                else:
                    game["attempts"] -= 1
                    hint = "Higher!" if guess < game["number"] else "Lower!"
                    
                    if game["attempts"] > 0:
                        await msg.reply(f"❌ Wrong! {hint} You have **{game['attempts']}** attempts left.")
                    else:
                        await self.db.add_coins(user_id, -game["bet"])
                        
                        lose_embed = discord.Embed(
                            title="😢 Game Over!",
                            description=f"The number was **{game['number']}**!\n\n"
                                        f"💸 You lost **{game['bet']}** coins!",
                            color=discord.Color.red()
                        )
                        await msg.reply(embed=lose_embed)
                        del self.guess_games[user_id]
                        return
                        
        except asyncio.TimeoutError:
            if user_id in self.guess_games:
                game = self.guess_games[user_id]
                await self.db.add_coins(user_id, -game["bet"])
                
                await interaction.followup.send(
                    f"⏰ Time's up! The number was **{game['number']}**. You lost **{game['bet']}** coins!"
                )
                del self.guess_games[user_id]
    
    @app_commands.command(name="slots", description="Try your luck at the slot machine!")
    @app_commands.describe(bet="Amount of coins to bet (10-500)")
    async def slots(self, interaction: discord.Interaction, bet: int = 50):
        user_id = interaction.user.id
        
        if bet < 10 or bet > 500:
            await interaction.response.send_message(
                "❌ Bet must be between 10 and 500 coins!",
                ephemeral=True
            )
            return
        
        user = await self.db.get_user(user_id, interaction.user.name)
        if user['coins'] < bet:
            await interaction.response.send_message(
                f"❌ You don't have enough coins! You have **{user['coins']:,}** coins.",
                ephemeral=True
            )
            return
        
        symbols = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣', '⭐']
        weights = [30, 25, 20, 15, 6, 3, 1]
        
        result = random.choices(symbols, weights=weights, k=3)
        
        multiplier = 0
        if result[0] == result[1] == result[2]:
            if result[0] == '7️⃣':
                multiplier = 10
            elif result[0] == '💎':
                multiplier = 7
            elif result[0] == '⭐':
                multiplier = 15
            else:
                multiplier = 5
        elif result[0] == result[1] or result[1] == result[2]:
            multiplier = 2
        
        winnings = bet * multiplier
        net = winnings - bet
        
        await self.db.add_coins(user_id, net)
        
        slot_display = f"╔═══════════╗\n║ {' '.join(result)} ║\n╚═══════════╝"
        
        if multiplier > 0:
            color = discord.Color.green()
            if multiplier >= 10:
                title = "🎰 JACKPOT!!!"
            elif multiplier >= 5:
                title = "🎰 BIG WIN!"
            else:
                title = "🎰 Winner!"
            result_text = f"💰 You won **{winnings}** coins! (x{multiplier})"
        else:
            color = discord.Color.red()
            title = "🎰 No Luck..."
            result_text = f"💸 You lost **{bet}** coins!"
        
        embed = discord.Embed(
            title=title,
            description=f"```\n{slot_display}\n```\n{result_text}",
            color=color
        )
        
        new_balance = user['coins'] + net
        embed.set_footer(text=f"Your balance: {new_balance:,} coins")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MinigamesCog(bot))
