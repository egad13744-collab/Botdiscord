# Adventure Quest Discord Bot

## Overview
A Discord RPG + Economy bot inspired by OwO Bot but with completely original systems, names, and mechanics. Features hunting to capture animals, animal-based battle system, fishing, mini-games, and a full economy system.

## Project Structure
```
src/
├── main.py           # Bot entry point and help command
├── database/
│   ├── __init__.py
│   └── db.py         # PostgreSQL database handler (users, animals, inventory)
├── data/
│   ├── __init__.py
│   ├── items.py      # Items, weapons, rods, skins with rarity
│   ├── monsters.py   # Legacy monster definitions
│   └── animals.py    # Animal & wild monster definitions for battle
└── cogs/
    ├── __init__.py
    ├── profile.py    # /profile, /equip, /unequip
    ├── hunt.py       # /hunt - capture animals
    ├── fish.py       # /fish command
    ├── inventory.py  # /inventory command
    ├── shop.py       # /shop, /buy, /sell
    ├── daily.py      # /daily reward
    ├── minigames.py  # /guess, /slots
    ├── battle.py     # /battle - PvE with animal team
    ├── animal.py     # /animal list/equip/unequip/info/heal, /team
    └── trade.py      # /trade, /accept_trade, /decline_trade
```

## Core Game Mechanics

### Hunt System
- `/hunt` captures wild **animals** (not loot items)
- Each animal has: Name, Rarity, HP, Attack, Defense, Skill
- Animals automatically added to Animal Inventory
- Cooldown: 15 seconds

### Animal System
- **Animal Inventory**: Store all captured animals
- **Animal Team**: Max 3 animals for battle (unlocks based on player level)
- Commands:
  - `/animal list` - View all animals
  - `/animal equip <id>` - Add to team
  - `/animal unequip <id>` - Remove from team
  - `/animal info <id>` - Detailed animal info
  - `/animal heal` - Heal team (costs coins)
  - `/team` - View battle team

### Battle System
- **Battle ALWAYS uses Animal Team**
- Cannot battle without at least 1 animal in team
- Turn-based combat with animals fighting
- Animals gain EXP from battle and can level up
- Player acts as commander (gives bonuses via equipment)

### Rarity System
- Common (50% drop rate)
- Uncommon (25%)
- Rare (15%)
- Epic (7%)
- Legendary (2.5%)
- Mythic (0.5%)

### Animal Skills
Each animal has a skill (passive or active):
- **Passive**: Always active (e.g., +10% attack)
- **Active**: Triggers during battle (e.g., life drain, stun)

### Progression
- Animals gain EXP from battles
- Animals level up and get stat boosts
- Player level unlocks more team slots

### Balance Rules
- Battle requires animals - no battle without team
- Equipment gives small bonuses only
- Not pay-to-win

## Commands
| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/profile` | View your profile |
| `/inventory` | View your items |
| `/equip` | Equip player equipment |
| `/unequip` | Unequip player equipment |
| `/hunt` | Hunt to capture animals |
| `/fish` | Go fishing for items |
| `/animal list` | View all your animals |
| `/animal equip` | Add animal to team |
| `/animal unequip` | Remove animal from team |
| `/animal info` | View animal details |
| `/animal heal` | Heal all team animals |
| `/team` | View battle team |
| `/battle` | Fight monsters with your team |
| `/daily` | Claim daily reward |
| `/shop` | Browse shop |
| `/buy` | Buy an item |
| `/sell` | Sell items |
| `/trade` | Trade with player |
| `/guess` | Number guessing game |
| `/slots` | Slot machine |
| `/leaderboard` | View leaderboard |
| `/leaderboard coin` | Top coin rankings |
| `/leaderboard level` | Top level rankings |
| `/leaderboard win` | Top win rankings |

## Technical Details
- Language: Python 3.11
- Framework: discord.py
- Database: PostgreSQL (Replit built-in)
- Commands: Slash commands (/)
- Architecture: Modular cogs system

## Database Tables
- `users` - Player profiles
- `inventory` - Item storage
- `animals` - Captured animals with stats
- `battle_stats` - Win/loss tracking
- `trades` - Trade records

## Environment Variables Required
- `DISCORD_BOT_TOKEN` - Your Discord bot token

## Running the Bot
The bot runs via `python src/main.py`

## User Preferences
- Response language: Bahasa Indonesia
