from enum import Enum
from typing import Dict, Any

class Rarity(Enum):
    COMMON = ("Common", 0x808080, 50)
    UNCOMMON = ("Uncommon", 0x32CD32, 25)
    RARE = ("Rare", 0x0066FF, 15)
    EPIC = ("Epic", 0x9932CC, 7)
    LEGENDARY = ("Legendary", 0xFFD700, 2.5)
    MYTHIC = ("Mythic", 0xFF1493, 0.5)
    
    def __init__(self, display_name: str, color: int, drop_chance: float):
        self.display_name = display_name
        self.color = color
        self.drop_chance = drop_chance

HUNT_LOOT: Dict[str, Dict[str, Any]] = {
    "wolf_fang": {"name": "Wolf Fang", "rarity": Rarity.COMMON, "sell_price": 5, "emoji": "🦷"},
    "bear_claw": {"name": "Bear Claw", "rarity": Rarity.COMMON, "sell_price": 8, "emoji": "🐻"},
    "goblin_ear": {"name": "Goblin Ear", "rarity": Rarity.UNCOMMON, "sell_price": 15, "emoji": "👂"},
    "orc_tusk": {"name": "Orc Tusk", "rarity": Rarity.UNCOMMON, "sell_price": 20, "emoji": "🦴"},
    "dragon_scale": {"name": "Dragon Scale", "rarity": Rarity.RARE, "sell_price": 50, "emoji": "🐉"},
    "phoenix_feather": {"name": "Phoenix Feather", "rarity": Rarity.RARE, "sell_price": 75, "emoji": "🪶"},
    "demon_horn": {"name": "Demon Horn", "rarity": Rarity.EPIC, "sell_price": 150, "emoji": "😈"},
    "titan_heart": {"name": "Titan Heart", "rarity": Rarity.EPIC, "sell_price": 200, "emoji": "💜"},
    "celestial_shard": {"name": "Celestial Shard", "rarity": Rarity.LEGENDARY, "sell_price": 500, "emoji": "✨"},
    "void_essence": {"name": "Void Essence", "rarity": Rarity.MYTHIC, "sell_price": 1500, "emoji": "🌀"},
}

FISH_LOOT: Dict[str, Dict[str, Any]] = {
    "small_fish": {"name": "Small Fish", "rarity": Rarity.COMMON, "sell_price": 3, "emoji": "🐟"},
    "cod": {"name": "Cod", "rarity": Rarity.COMMON, "sell_price": 5, "emoji": "🐟"},
    "salmon": {"name": "Salmon", "rarity": Rarity.COMMON, "sell_price": 7, "emoji": "🐠"},
    "tuna": {"name": "Tuna", "rarity": Rarity.UNCOMMON, "sell_price": 15, "emoji": "🐟"},
    "pufferfish": {"name": "Pufferfish", "rarity": Rarity.UNCOMMON, "sell_price": 20, "emoji": "🐡"},
    "octopus": {"name": "Octopus", "rarity": Rarity.RARE, "sell_price": 45, "emoji": "🐙"},
    "electric_eel": {"name": "Electric Eel", "rarity": Rarity.RARE, "sell_price": 60, "emoji": "⚡"},
    "ancient_carp": {"name": "Ancient Carp", "rarity": Rarity.EPIC, "sell_price": 120, "emoji": "🏆"},
    "golden_koi": {"name": "Golden Koi", "rarity": Rarity.LEGENDARY, "sell_price": 400, "emoji": "🌟"},
    "leviathan_scale": {"name": "Leviathan Scale", "rarity": Rarity.MYTHIC, "sell_price": 1200, "emoji": "🌊"},
}

WEAPONS: Dict[str, Dict[str, Any]] = {
    "wooden_sword": {"name": "Wooden Sword", "rarity": Rarity.COMMON, "attack": 5, "buy_price": 50, "emoji": "🗡️"},
    "iron_sword": {"name": "Iron Sword", "rarity": Rarity.UNCOMMON, "attack": 12, "buy_price": 200, "emoji": "⚔️"},
    "steel_blade": {"name": "Steel Blade", "rarity": Rarity.RARE, "attack": 25, "buy_price": 500, "emoji": "🔪"},
    "shadow_dagger": {"name": "Shadow Dagger", "rarity": Rarity.EPIC, "attack": 45, "buy_price": 1500, "emoji": "🗡️"},
    "dragon_slayer": {"name": "Dragon Slayer", "rarity": Rarity.LEGENDARY, "attack": 80, "buy_price": 5000, "emoji": "⚔️"},
    "void_blade": {"name": "Void Blade", "rarity": Rarity.MYTHIC, "attack": 150, "buy_price": 15000, "emoji": "🌀"},
}

FISHING_RODS: Dict[str, Dict[str, Any]] = {
    "basic_rod": {"name": "Basic Rod", "rarity": Rarity.COMMON, "luck_bonus": 0, "buy_price": 50, "emoji": "🎣"},
    "bamboo_rod": {"name": "Bamboo Rod", "rarity": Rarity.UNCOMMON, "luck_bonus": 5, "buy_price": 200, "emoji": "🎣"},
    "carbon_rod": {"name": "Carbon Rod", "rarity": Rarity.RARE, "luck_bonus": 12, "buy_price": 600, "emoji": "🎣"},
    "enchanted_rod": {"name": "Enchanted Rod", "rarity": Rarity.EPIC, "luck_bonus": 25, "buy_price": 2000, "emoji": "✨"},
    "golden_rod": {"name": "Golden Rod", "rarity": Rarity.LEGENDARY, "luck_bonus": 40, "buy_price": 6000, "emoji": "🌟"},
}

SKINS: Dict[str, Dict[str, Any]] = {
    "adventurer": {"name": "Adventurer", "rarity": Rarity.COMMON, "exp_bonus": 2, "coin_bonus": 0, "luck_bonus": 0, "buy_price": 100, "emoji": "🧑‍🌾"},
    "hunter": {"name": "Hunter", "rarity": Rarity.UNCOMMON, "exp_bonus": 5, "coin_bonus": 3, "luck_bonus": 0, "buy_price": 500, "emoji": "🏹"},
    "warrior": {"name": "Warrior", "rarity": Rarity.RARE, "exp_bonus": 8, "coin_bonus": 5, "luck_bonus": 2, "buy_price": 1500, "emoji": "⚔️"},
    "shadow_knight": {"name": "Shadow Knight", "rarity": Rarity.EPIC, "exp_bonus": 12, "coin_bonus": 8, "luck_bonus": 5, "buy_price": 4000, "emoji": "🛡️"},
    "dragon_master": {"name": "Dragon Master", "rarity": Rarity.LEGENDARY, "exp_bonus": 18, "coin_bonus": 12, "luck_bonus": 8, "buy_price": 10000, "emoji": "🐲"},
    "void_walker": {"name": "Void Walker", "rarity": Rarity.MYTHIC, "exp_bonus": 25, "coin_bonus": 15, "luck_bonus": 12, "buy_price": 25000, "emoji": "🌀"},
}

ALL_ITEMS = {**HUNT_LOOT, **FISH_LOOT, **WEAPONS, **FISHING_RODS, **SKINS}

def get_item(item_id: str) -> Dict[str, Any]:
    return ALL_ITEMS.get(item_id, None)

def get_rarity_color(rarity: Rarity) -> int:
    return rarity.color
