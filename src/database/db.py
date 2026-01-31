import os
import asyncpg
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import uuid

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        
    async def init(self):
        self.pool = await asyncpg.create_pool(os.environ.get("DATABASE_URL"))
        await self.create_tables()
        print("Database connected and tables created!")
        
    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    coins INTEGER DEFAULT 100,
                    daily_streak INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    last_hunt TIMESTAMP,
                    last_fish TIMESTAMP,
                    equipped_weapon TEXT,
                    equipped_rod TEXT,
                    equipped_skin TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    item_id TEXT NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    UNIQUE(user_id, item_id)
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id SERIAL PRIMARY KEY,
                    sender_id BIGINT REFERENCES users(user_id),
                    receiver_id BIGINT REFERENCES users(user_id),
                    sender_items JSONB,
                    sender_coins INTEGER DEFAULT 0,
                    receiver_items JSONB,
                    receiver_coins INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS battle_stats (
                    user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    monsters_killed INTEGER DEFAULT 0,
                    total_damage_dealt BIGINT DEFAULT 0
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS animals (
                    id TEXT PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    animal_id TEXT NOT NULL,
                    nickname TEXT,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0,
                    current_hp INTEGER,
                    max_hp INTEGER,
                    attack INTEGER,
                    defense INTEGER,
                    is_in_team BOOLEAN DEFAULT FALSE,
                    team_slot INTEGER,
                    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_animals_user ON animals(user_id)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_animals_team ON animals(user_id, is_in_team)
            ''')
    
    async def get_user(self, user_id: int, username: str = None) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(
                'SELECT * FROM users WHERE user_id = $1', user_id
            )
            
            if not user:
                await conn.execute('''
                    INSERT INTO users (user_id, username) VALUES ($1, $2)
                ''', user_id, username or "Unknown")
                
                await conn.execute('''
                    INSERT INTO battle_stats (user_id) VALUES ($1)
                ''', user_id)
                
                user = await conn.fetchrow(
                    'SELECT * FROM users WHERE user_id = $1', user_id
                )
            
            return dict(user)
    
    async def update_user(self, user_id: int, **kwargs):
        if not kwargs:
            return
            
        set_clause = ', '.join(f'{k} = ${i+2}' for i, k in enumerate(kwargs.keys()))
        values = list(kwargs.values())
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                f'UPDATE users SET {set_clause} WHERE user_id = $1',
                user_id, *values
            )
    
    async def add_exp(self, user_id: int, amount: int) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(
                'SELECT level, exp FROM users WHERE user_id = $1', user_id
            )
            
            new_exp = user['exp'] + amount
            level = user['level']
            leveled_up = False
            
            exp_needed = self.exp_for_level(level)
            while new_exp >= exp_needed:
                new_exp -= exp_needed
                level += 1
                leveled_up = True
                exp_needed = self.exp_for_level(level)
            
            await conn.execute(
                'UPDATE users SET exp = $1, level = $2 WHERE user_id = $3',
                new_exp, level, user_id
            )
            
            return {"leveled_up": leveled_up, "new_level": level, "exp": new_exp}
    
    def exp_for_level(self, level: int) -> int:
        return 100 + (level * 50)
    
    def animal_exp_for_level(self, level: int) -> int:
        return 50 + (level * 30)
    
    async def add_coins(self, user_id: int, amount: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                'UPDATE users SET coins = coins + $1 WHERE user_id = $2',
                amount, user_id
            )
    
    async def get_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            items = await conn.fetch(
                'SELECT item_id, quantity FROM inventory WHERE user_id = $1',
                user_id
            )
            return [dict(item) for item in items]
    
    async def add_item(self, user_id: int, item_id: str, quantity: int = 1):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO inventory (user_id, item_id, quantity)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, item_id)
                DO UPDATE SET quantity = inventory.quantity + $3
            ''', user_id, item_id, quantity)
    
    async def remove_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        async with self.pool.acquire() as conn:
            item = await conn.fetchrow(
                'SELECT quantity FROM inventory WHERE user_id = $1 AND item_id = $2',
                user_id, item_id
            )
            
            if not item or item['quantity'] < quantity:
                return False
            
            new_quantity = item['quantity'] - quantity
            if new_quantity <= 0:
                await conn.execute(
                    'DELETE FROM inventory WHERE user_id = $1 AND item_id = $2',
                    user_id, item_id
                )
            else:
                await conn.execute(
                    'UPDATE inventory SET quantity = $1 WHERE user_id = $2 AND item_id = $3',
                    new_quantity, user_id, item_id
                )
            return True
    
    async def has_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        async with self.pool.acquire() as conn:
            item = await conn.fetchrow(
                'SELECT quantity FROM inventory WHERE user_id = $1 AND item_id = $2',
                user_id, item_id
            )
            return item and item['quantity'] >= quantity
    
    async def get_battle_stats(self, user_id: int) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow(
                'SELECT * FROM battle_stats WHERE user_id = $1', user_id
            )
            if stats:
                return dict(stats)
            return {"wins": 0, "losses": 0, "monsters_killed": 0, "total_damage_dealt": 0}
    
    async def update_battle_stats(self, user_id: int, **kwargs):
        set_parts = []
        values = []
        for i, (k, v) in enumerate(kwargs.items()):
            set_parts.append(f'{k} = {k} + ${i+2}')
            values.append(v)
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                f'UPDATE battle_stats SET {", ".join(set_parts)} WHERE user_id = $1',
                user_id, *values
            )
    
    async def check_cooldown(self, user_id: int, cooldown_type: str, seconds: int) -> Optional[int]:
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(
                f'SELECT {cooldown_type} FROM users WHERE user_id = $1', user_id
            )
            
            if user and user[cooldown_type]:
                time_diff = datetime.utcnow() - user[cooldown_type]
                if time_diff.total_seconds() < seconds:
                    remaining = seconds - int(time_diff.total_seconds())
                    return remaining
            return None
    
    async def set_cooldown(self, user_id: int, cooldown_type: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                f'UPDATE users SET {cooldown_type} = $1 WHERE user_id = $2',
                datetime.utcnow(), user_id
            )
    
    async def add_animal(self, user_id: int, animal_data: Dict[str, Any]) -> str:
        animal_uuid = str(uuid.uuid4())[:8]
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO animals (id, user_id, animal_id, nickname, level, exp, current_hp, max_hp, attack, defense)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ''', 
                animal_uuid,
                user_id,
                animal_data['animal_id'],
                animal_data.get('nickname', animal_data['name']),
                1,
                0,
                animal_data['hp'],
                animal_data['hp'],
                animal_data['attack'],
                animal_data['defense']
            )
        return animal_uuid
    
    async def get_user_animals(self, user_id: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            animals = await conn.fetch(
                'SELECT * FROM animals WHERE user_id = $1 ORDER BY captured_at DESC',
                user_id
            )
            return [dict(a) for a in animals]
    
    async def get_animal(self, animal_uuid: str) -> Optional[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            animal = await conn.fetchrow(
                'SELECT * FROM animals WHERE id = $1',
                animal_uuid
            )
            return dict(animal) if animal else None
    
    async def get_animal_team(self, user_id: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            animals = await conn.fetch(
                '''SELECT * FROM animals 
                   WHERE user_id = $1 AND is_in_team = TRUE 
                   ORDER BY team_slot''',
                user_id
            )
            return [dict(a) for a in animals]
    
    async def add_animal_to_team(self, user_id: int, animal_uuid: str) -> bool:
        async with self.pool.acquire() as conn:
            animal = await conn.fetchrow(
                'SELECT * FROM animals WHERE id = $1 AND user_id = $2',
                animal_uuid, user_id
            )
            
            if not animal:
                return False
            
            if animal['is_in_team']:
                return False
            
            team_count = await conn.fetchval(
                'SELECT COUNT(*) FROM animals WHERE user_id = $1 AND is_in_team = TRUE',
                user_id
            )
            
            user = await self.get_user(user_id)
            max_team_size = min(3, 1 + user['level'] // 5)
            
            if team_count >= max_team_size:
                return False
            
            await conn.execute(
                'UPDATE animals SET is_in_team = TRUE, team_slot = $1 WHERE id = $2',
                team_count + 1, animal_uuid
            )
            return True
    
    async def remove_animal_from_team(self, user_id: int, animal_uuid: str) -> bool:
        async with self.pool.acquire() as conn:
            animal = await conn.fetchrow(
                'SELECT * FROM animals WHERE id = $1 AND user_id = $2',
                animal_uuid, user_id
            )
            
            if not animal or not animal['is_in_team']:
                return False
            
            await conn.execute(
                'UPDATE animals SET is_in_team = FALSE, team_slot = NULL WHERE id = $1',
                animal_uuid
            )
            return True
    
    async def add_animal_exp(self, animal_uuid: str, amount: int) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            animal = await conn.fetchrow(
                'SELECT level, exp, max_hp, attack, defense FROM animals WHERE id = $1',
                animal_uuid
            )
            
            if not animal:
                return {"leveled_up": False}
            
            new_exp = animal['exp'] + amount
            level = animal['level']
            leveled_up = False
            
            exp_needed = self.animal_exp_for_level(level)
            while new_exp >= exp_needed and level < 100:
                new_exp -= exp_needed
                level += 1
                leveled_up = True
                exp_needed = self.animal_exp_for_level(level)
            
            new_max_hp = animal['max_hp']
            new_attack = animal['attack']
            new_defense = animal['defense']
            
            if leveled_up:
                level_diff = level - animal['level']
                new_max_hp += level_diff * 5
                new_attack += level_diff * 2
                new_defense += level_diff * 1
            
            await conn.execute(
                '''UPDATE animals 
                   SET exp = $1, level = $2, max_hp = $3, current_hp = $3, attack = $4, defense = $5 
                   WHERE id = $6''',
                new_exp, level, new_max_hp, new_attack, new_defense, animal_uuid
            )
            
            return {"leveled_up": leveled_up, "new_level": level, "exp": new_exp}
    
    async def heal_animal(self, animal_uuid: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                'UPDATE animals SET current_hp = max_hp WHERE id = $1',
                animal_uuid
            )
    
    async def heal_team(self, user_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                'UPDATE animals SET current_hp = max_hp WHERE user_id = $1 AND is_in_team = TRUE',
                user_id
            )
    
    async def update_animal_hp(self, animal_uuid: str, new_hp: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                'UPDATE animals SET current_hp = $1 WHERE id = $2',
                max(0, new_hp), animal_uuid
            )
    
    async def get_max_team_size(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        return min(3, 1 + user['level'] // 5)
