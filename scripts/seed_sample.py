from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'data' / 'yanfei.db'
SCHEMA_PATH = BASE_DIR / 'schema.sql'

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))

conn.executemany(
    'INSERT OR REPLACE INTO items (id, name, name_id, item_type, use_type, material, weight, stackable, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
    [
        (1, '試作赤焰之劍', '$5001', 'weapon', 'equip', 'steel', 35, 0, '展示用樣本'),
        (2, '龍族治癒藥水', '$5002', 'potion', 'drink', 'glass', 3, 1, '展示用樣本'),
    ],
)
conn.executemany(
    'INSERT OR REPLACE INTO monsters (id, name, nameid, level, hp, mp, ac, exp, family, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
    [
        (1001, '試作骷髏戰士', '$1001', 12, 180, 20, -5, 220, 'undead', '展示用樣本'),
        (1002, '試作火焰龍', '$1002', 52, 4200, 600, -70, 8200, 'dragon', '展示用樣本'),
    ],
)
conn.executemany(
    'INSERT OR REPLACE INTO monster_drops (monster_id, item_id, min_count, max_count, chance, note) VALUES (?, ?, ?, ?, ?, ?)',
    [
        (1001, 2, 1, 3, 250000, '展示用樣本'),
        (1002, 1, 1, 1, 5000, '展示用樣本'),
    ],
)
conn.commit()
conn.close()
print(f'Seeded sample data into {DB_PATH}')
