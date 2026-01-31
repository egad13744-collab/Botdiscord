from typing import Dict, Any, List
from data.items import Rarity
import random

ANIMALS: Dict[str, Dict[str, Any]] = {
    "forest_fox": {
        "name": "Forest Fox",
        "emoji": "🦊",
        "hp": 30,
        "attack": 8,
        "defense": 4,
        "skill": {"name": "Swift Strike", "type": "active", "effect": "First attack deals 1.5x damage"},
        "rarity": Rarity.COMMON
    },
    "wild_wolf": {
        "name": "Wild Wolf",
        "emoji": "🐺",
        "hp": 40,
        "attack": 10,
        "defense": 5,
        "skill": {"name": "Pack Howl", "type": "passive", "effect": "+10% attack when in team"},
        "rarity": Rarity.COMMON
    },
    "cave_bat": {
        "name": "Cave Bat",
        "emoji": "🦇",
        "hp": 25,
        "attack": 7,
        "defense": 3,
        "skill": {"name": "Life Drain", "type": "active", "effect": "Heals 20% of damage dealt"},
        "rarity": Rarity.COMMON
    },
    "mountain_bear": {
        "name": "Mountain Bear",
        "emoji": "🐻",
        "hp": 60,
        "attack": 12,
        "defense": 8,
        "skill": {"name": "Thick Hide", "type": "passive", "effect": "+15% defense"},
        "rarity": Rarity.UNCOMMON
    },
    "thunder_eagle": {
        "name": "Thunder Eagle",
        "emoji": "🦅",
        "hp": 35,
        "attack": 15,
        "defense": 4,
        "skill": {"name": "Lightning Dive", "type": "active", "effect": "30% chance to stun enemy"},
        "rarity": Rarity.UNCOMMON
    },
    "shadow_panther": {
        "name": "Shadow Panther",
        "emoji": "🐆",
        "hp": 45,
        "attack": 18,
        "defense": 6,
        "skill": {"name": "Shadow Claw", "type": "active", "effect": "Ignores 25% enemy defense"},
        "rarity": Rarity.UNCOMMON
    },
    "ice_tiger": {
        "name": "Ice Tiger",
        "emoji": "🐅",
        "hp": 55,
        "attack": 20,
        "defense": 10,
        "skill": {"name": "Frost Bite", "type": "active", "effect": "20% chance to freeze enemy for 1 turn"},
        "rarity": Rarity.RARE
    },
    "flame_lion": {
        "name": "Flame Lion",
        "emoji": "🦁",
        "hp": 65,
        "attack": 22,
        "defense": 12,
        "skill": {"name": "Fire Roar", "type": "active", "effect": "Burns enemy for 3 damage per turn"},
        "rarity": Rarity.RARE
    },
    "crystal_unicorn": {
        "name": "Crystal Unicorn",
        "emoji": "🦄",
        "hp": 50,
        "attack": 16,
        "defense": 14,
        "skill": {"name": "Healing Light", "type": "active", "effect": "Heals self for 15 HP once per battle"},
        "rarity": Rarity.RARE
    },
    "storm_dragon": {
        "name": "Storm Dragon",
        "emoji": "🐲",
        "hp": 80,
        "attack": 28,
        "defense": 15,
        "skill": {"name": "Thunder Breath", "type": "active", "effect": "Deals AoE damage to all enemies"},
        "rarity": Rarity.EPIC
    },
    "phoenix_chick": {
        "name": "Phoenix Chick",
        "emoji": "🔥",
        "hp": 45,
        "attack": 25,
        "defense": 8,
        "skill": {"name": "Rebirth", "type": "passive", "effect": "Revives once with 30% HP"},
        "rarity": Rarity.EPIC
    },
    "dark_hydra": {
        "name": "Dark Hydra",
        "emoji": "🐍",
        "hp": 90,
        "attack": 24,
        "defense": 18,
        "skill": {"name": "Multi-Head Strike", "type": "active", "effect": "Attacks 2-3 times per turn"},
        "rarity": Rarity.EPIC
    },
    "celestial_griffin": {
        "name": "Celestial Griffin",
        "emoji": "🦅",
        "hp": 100,
        "attack": 35,
        "defense": 20,
        "skill": {"name": "Divine Wings", "type": "passive", "effect": "+25% damage and defense"},
        "rarity": Rarity.LEGENDARY
    },
    "ancient_dragon": {
        "name": "Ancient Dragon",
        "emoji": "🐉",
        "hp": 120,
        "attack": 40,
        "defense": 25,
        "skill": {"name": "Dragon Rage", "type": "active", "effect": "Deals massive damage, increases each turn"},
        "rarity": Rarity.LEGENDARY
    },
    "void_serpent": {
        "name": "Void Serpent",
        "emoji": "🌀",
        "hp": 150,
        "attack": 50,
        "defense": 30,
        "skill": {"name": "Void Consume", "type": "active", "effect": "Absorbs 30% of damage dealt as HP"},
        "rarity": Rarity.MYTHIC
    },
    "cosmic_phoenix": {
        "name": "Cosmic Phoenix",
        "emoji": "✨",
        "hp": 130,
        "attack": 55,
        "defense": 25,
        "skill": {"name": "Eternal Flame", "type": "passive", "effect": "Cannot be one-shot, revives twice"},
        "rarity": Rarity.MYTHIC
    },
}

WILD_MONSTERS: Dict[str, Dict[str, Any]] = {
    "slime": {
        "name": "Wild Slime",
        "emoji": "🟢",
        "hp": 30,
        "attack": 5,
        "defense": 2,
        "exp_reward": 15,
        "coin_reward": (5, 15),
        "rarity": Rarity.COMMON
    },
    "goblin": {
        "name": "Goblin Scout",
        "emoji": "👺",
        "hp": 45,
        "attack": 10,
        "defense": 5,
        "exp_reward": 25,
        "coin_reward": (10, 30),
        "rarity": Rarity.COMMON
    },
    "skeleton": {
        "name": "Skeleton Warrior",
        "emoji": "💀",
        "hp": 60,
        "attack": 15,
        "defense": 8,
        "exp_reward": 40,
        "coin_reward": (20, 50),
        "rarity": Rarity.UNCOMMON
    },
    "orc": {
        "name": "Orc Brute",
        "emoji": "👹",
        "hp": 80,
        "attack": 20,
        "defense": 12,
        "exp_reward": 60,
        "coin_reward": (30, 70),
        "rarity": Rarity.UNCOMMON
    },
    "dark_knight": {
        "name": "Dark Knight",
        "emoji": "🗡️",
        "hp": 100,
        "attack": 28,
        "defense": 18,
        "exp_reward": 100,
        "coin_reward": (50, 120),
        "rarity": Rarity.RARE
    },
    "demon": {
        "name": "Lesser Demon",
        "emoji": "😈",
        "hp": 130,
        "attack": 35,
        "defense": 20,
        "exp_reward": 150,
        "coin_reward": (80, 180),
        "rarity": Rarity.RARE
    },
    "dragon_whelp": {
        "name": "Dragon Whelp",
        "emoji": "🐲",
        "hp": 180,
        "attack": 45,
        "defense": 28,
        "exp_reward": 250,
        "coin_reward": (150, 300),
        "rarity": Rarity.EPIC
    },
    "demon_lord": {
        "name": "Demon Lord",
        "emoji": "👿",
        "hp": 250,
        "attack": 55,
        "defense": 35,
        "exp_reward": 400,
        "coin_reward": (250, 500),
        "rarity": Rarity.EPIC
    },
    "elder_dragon": {
        "name": "Elder Dragon",
        "emoji": "🐉",
        "hp": 400,
        "attack": 70,
        "defense": 45,
        "exp_reward": 700,
        "coin_reward": (500, 1000),
        "rarity": Rarity.LEGENDARY
    },
    "void_titan": {
        "name": "Void Titan",
        "emoji": "🌀",
        "hp": 600,
        "attack": 90,
        "defense": 55,
        "exp_reward": 1200,
        "coin_reward": (1000, 2000),
        "rarity": Rarity.MYTHIC
    }
}

def get_random_animal(luck_bonus: int = 0) -> Dict[str, Any]:
    weights = []
    animals = list(ANIMALS.items())
    
    for animal_id, animal in animals:
        base_weight = animal["rarity"].drop_chance
        if luck_bonus > 0 and animal["rarity"] in [Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY, Rarity.MYTHIC]:
            base_weight += luck_bonus * 0.15
        weights.append(base_weight)
    
    selected_id, selected = random.choices(animals, weights=weights, k=1)[0]
    result = selected.copy()
    result['animal_id'] = selected_id
    return result

def get_random_monster(luck_bonus: int = 0) -> Dict[str, Any]:
    weights = []
    monsters = list(WILD_MONSTERS.items())
    
    for monster_id, monster in monsters:
        base_weight = monster["rarity"].drop_chance
        if luck_bonus > 0 and monster["rarity"] in [Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY, Rarity.MYTHIC]:
            base_weight += luck_bonus * 0.1
        weights.append(base_weight)
    
    selected_id, selected = random.choices(monsters, weights=weights, k=1)[0]
    result = selected.copy()
    result['monster_id'] = selected_id
    return result

def get_animal_by_id(animal_id: str) -> Dict[str, Any]:
    if animal_id in ANIMALS:
        result = ANIMALS[animal_id].copy()
        result['animal_id'] = animal_id
        return result
    return None
