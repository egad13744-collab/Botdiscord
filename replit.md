# Adventure Quest Discord Bot

## Overview
A Discord RPG + Economy bot inspired by OwO Bot but with completely original systems, names, and mechanics. Features hunting, fishing, battles, mini-games, and a full economy system.

## Project Structure
```
src/
├── main.py           # Bot entry point and help command
├── database/
│   ├── __init__.py
│   └── db.py         # PostgreSQL database handler
├── data/
│   ├── __init__.py
│   ├── items.py      # Items, weapons, rods, skins with rarity
│   └── monsters.py   # Monster definitions for battles
└── cogs/
    ├── __init__.py
    ├── profile.py    # /profile, /equip, /unequip
    ├── hunt.py       # /hunt command
    ├── fish.py       # /fish command
    ├── inventory.py  # /inventory command
    ├── shop.py       # /shop, /buy, /sell
    ├── daily.py      # /daily reward
    ├── minigames.py  # /guess, /slots
    ├── battle.py     # /battle PvE combat
    └── trade.py      # /trade, /accept_trade, /decline_trade
```

## Features

### User Profile
- Level & EXP system with progressive requirements
- Coins currency
- Inventory system
- Daily streak bonuses
- Equipment slots (weapon, rod, skin)

### Hunt & Fish
- `/hunt` - Hunt monsters for loot (30s cooldown)
- `/fish` - Fish for treasures (25s cooldown)
- Random drops with rarity tiers
- Equipment bonuses affect luck

### Rarity System
- Common (50% drop rate)
- Uncommon (25%)
- Rare (15%)
- Epic (7%)
- Legendary (2.5%)
- Mythic (0.5%)

### Equipment & Skins
- Weapons: Increase battle damage
- Fishing Rods: Increase fishing luck
- Skins: Bonus EXP, coins, and luck (not pay-to-win)

### Mini Games
- `/guess` - Number guessing (1-10, 3 attempts)
- `/slots` - Slot machine gambling

### Economy
- `/daily` - Daily reward with streak bonus
- `/shop` - Browse weapons, rods, skins
- `/buy` - Purchase items
- `/sell` - Sell items for coins
- `/trade` - Safe player-to-player trading

### Battle System
- `/battle` - Fight random monsters
- Turn-based combat
- Rewards: coins, EXP
- Stronger weapons = more damage

## Commands
| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/profile` | View your profile |
| `/inventory` | View your items |
| `/equip` | Equip an item |
| `/unequip` | Unequip an item |
| `/hunt` | Go hunting |
| `/fish` | Go fishing |
| `/battle` | Fight a monster |
| `/daily` | Claim daily reward |
| `/shop` | Browse shop |
| `/buy` | Buy an item |
| `/sell` | Sell items |
| `/trade` | Trade with player |
| `/guess` | Number guessing game |
| `/slots` | Slot machine |

## Technical Details
- Language: Python 3.11
- Framework: discord.py
- Database: PostgreSQL (Replit built-in)
- Commands: Slash commands (/)
- Architecture: Modular cogs system

## Environment Variables Required
- `DISCORD_BOT_TOKEN` - Your Discord bot token

## Running the Bot
The bot runs via `python src/main.py`

## User Preferences
- Response language: Bahasa Indonesia
