from typing import Dict, Any, List
from data.items import Rarity
import random

MONSTERS: Dict[str, Dict[str, Any]] = {
    "slime": {
        "name": "Slime",
        "emoji": "🟢",
        "hp": 20,
        "attack": 3,
        "defense": 1,
        "exp_reward": 10,
        "coin_reward": (5, 15),
        "rarity": Rarity.COMMON
    },
    "goblin": {
        "name": "Goblin",
        "emoji": "👺",
        "hp": 35,
        "attack": 8,
        "defense": 3,
        "exp_reward": 20,
        "coin_reward": (10, 30),
        "rarity": Rarity.COMMON
    },
    "wolf": {
        "name": "Shadow Wolf",
        "emoji": "🐺",
        "hp": 50,
        "attack": 12,
        "defense": 5,
        "exp_reward": 35,
        "coin_reward": (20, 50),
        "rarity": Rarity.UNCOMMON
    },
    "orc": {
        "name": "Orc Warrior",
        "emoji": "👹",
        "hp": 80,
        "attack": 18,
        "defense": 10,
        "exp_reward": 60,
        "coin_reward": (40, 80),
        "rarity": Rarity.UNCOMMON
    },
    "skeleton_knight": {
        "name": "Skeleton Knight",
        "emoji": "💀",
        "hp": 120,
        "attack": 25,
        "defense": 15,
        "exp_reward": 100,
        "coin_reward": (60, 120),
        "rarity": Rarity.RARE
    },
    "dark_mage": {
        "name": "Dark Mage",
        "emoji": "🧙",
        "hp": 90,
        "attack": 35,
        "defense": 8,
        "exp_reward": 120,
        "coin_reward": (80, 150),
        "rarity": Rarity.RARE
    },
    "dragon_whelp": {
        "name": "Dragon Whelp",
        "emoji": "🐲",
        "hp": 200,
        "attack": 45,
        "defense": 25,
        "exp_reward": 200,
        "coin_reward": (150, 300),
        "rarity": Rarity.EPIC
    },
    "demon_lord": {
        "name": "Demon Lord",
        "emoji": "😈",
        "hp": 350,
        "attack": 60,
        "defense": 35,
        "exp_reward": 350,
        "coin_reward": (250, 500),
        "rarity": Rarity.EPIC
    },
    "ancient_dragon": {
        "name": "Ancient Dragon",
        "emoji": "🐉",
        "hp": 600,
        "attack": 85,
        "defense": 50,
        "exp_reward": 600,
        "coin_reward": (500, 1000),
        "rarity": Rarity.LEGENDARY
    },
    "void_titan": {
        "name": "Void Titan",
        "emoji": "🌀",
        "hp": 1000,
        "attack": 120,
        "defense": 70,
        "exp_reward": 1000,
        "coin_reward": (1000, 2000),
        "rarity": Rarity.MYTHIC
    }
}

def get_random_monster(luck_bonus: int = 0) -> Dict[str, Any]:
    weights = []
    monsters = list(MONSTERS.values())
    
    for monster in monsters:
        base_weight = monster["rarity"].drop_chance
        if luck_bonus > 0:
            if monster["rarity"] in [Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY, Rarity.MYTHIC]:
                base_weight += luck_bonus * 0.1
        weights.append(base_weight)
    
    selected = random.choices(monsters, weights=weights, k=1)[0]
    return selected.copy()

def get_monster_by_id(monster_id: str) -> Dict[str, Any]:
    return MONSTERS.get(monster_id, None)
