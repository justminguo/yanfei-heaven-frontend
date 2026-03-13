from __future__ import annotations

import argparse
import base64
import csv
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT / "data" / "yanfei.db"
SCHEMA_PATH = ROOT / "schema.sql"

ITEM_COLUMNS = [
    "id", "name", "name_id", "classname", "item_type", "use_type", "material",
    "weight", "invgfx", "grdgfx", "itemdesc_id", "stackable", "dmg_small", "dmg_large",
    "min_lvl", "max_lvl", "bless", "tradeable", "cant_delete", "note",
]
MONSTER_COLUMNS = [
    "id", "name", "nameid", "classname", "note", "gfxid", "level", "hp", "mp", "ac",
    "str", "con", "dex", "wis", "int_stat", "mr", "exp", "lawful", "size", "weak_attr",
    "ranged", "tamable", "agro", "family", "agrofamily", "teleport", "damage_reduction",
    "karma", "transform_id", "transform_gfxid", "quest_score",
]
DROP_COLUMNS = ["monster_id", "item_id", "min_count", "max_count", "chance", "note"]
CHARACTER_COLUMNS = ["char_id", "account_name", "char_name", "level", "class", "OnlineStatus"]
WEAPON_COLUMNS = [
    "id", "name", "exp_point", "classname", "name_id", "type", "material", "weight", "invgfx", "grdgfx",
    "itemdesc_id", "dmg_small", "dmg_large", "attack_range", "safenchant", "use_royal", "use_knight", "use_mage",
    "use_elf", "use_darkelf", "use_dragonknight", "use_illusionist", "hitmodifier", "dmgmodifier", "add_str",
    "add_con", "add_dex", "add_int", "add_wis", "add_cha", "add_hp", "add_mp", "add_hpr", "add_mpr", "add_sp",
    "m_def", "haste_item", "double_dmg_chance", "canbedmg", "min_lvl", "max_lvl", "bless", "tradeable",
    "cant_delete", "max_use_time", "pvp_dmg", "pvp_dmg_reduction",
]
ARMOR_COLUMNS = [
    "id", "name", "exp_point", "classname", "name_id", "type", "material", "weight", "invgfx", "grdgfx",
    "itemdesc_id", "ac", "safenchant", "use_royal", "use_knight", "use_mage", "use_elf", "use_darkelf",
    "use_dragonknight", "use_illusionist", "add_str", "add_con", "add_dex", "add_int", "add_wis", "add_cha",
    "add_hp", "add_mp", "add_hpr", "add_mpr", "add_sp", "min_lvl", "max_lvl", "m_def", "haste_item",
    "damage_reduction", "weight_reduction", "hit_modifier", "dmg_modifier", "bow_hit_modifier", "bow_dmg_modifier",
    "bless", "tradeable", "cant_delete", "max_use_time", "defense_water", "defense_wind", "defense_fire",
    "defense_earth", "regist_stun", "regist_stone", "regist_sleep", "regist_freeze", "regist_sustain", "regist_blind",
    "greater_flag", "magic_hit_modifier", "up_hp_potion", "uhp_number", "pvp_dmg", "pvp_dmg_reduction", "armor_group",
]


def powershell_encoded(script: str) -> str:
    return base64.b64encode(script.encode("utf-16le")).decode()


def run_remote_mysql(query: str, *, host: str, user: str, key_path: str, mysql_path: str, mysql_user: str, mysql_password: str) -> str:
    ps = f"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$mysql = '{mysql_path}'
& $mysql -u{mysql_user} -p{mysql_password} --default-character-set=utf8 -N -B -e @'
{query}
'@
"""
    encoded = powershell_encoded(ps)
    cmd = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-i",
        key_path,
        f"{user}@{host}",
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-EncodedCommand",
        encoded,
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.decode("utf-8", "ignore") or res.stdout.decode("utf-8", "ignore"))
    return res.stdout.decode("utf-8", "ignore")


def parse_tsv(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in csv.reader(text.splitlines(), delimiter="\t"):
        if row:
            rows.append(row)
    return rows


def to_int(v: str) -> int:
    if v == "" or v is None:
        return 0
    return int(v)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Lineage MySQL data from Windows to local SQLite")
    parser.add_argument("--host", required=True)
    parser.add_argument("--ssh-user", default="user")
    parser.add_argument("--ssh-key", required=True)
    parser.add_argument("--mysql-path", default=r"C:\Program Files\MySQL\MySQL Server 5.5\bin\mysql.exe")
    parser.add_argument("--mysql-user", default="root")
    parser.add_argument("--mysql-password", default="root")
    parser.add_argument("--mysql-db", default="381")
    parser.add_argument(
        "--mysql-char-db",
        default="lin2user",
        help="MySQL database containing the characters table (default: lin2user). "
             "Set to empty string to skip character sync.",
    )
    parser.add_argument("--out", default=str(DEFAULT_DB_PATH))
    args = parser.parse_args()

    db_name = args.mysql_db.replace('`', '')
    clean = lambda col: f"REPLACE(REPLACE(REPLACE(IFNULL({col}, ''), '\\r', ' '), '\\n', ' '), '\\t', ' ')"

    item_query = f"""
USE `{db_name}`;
SELECT item_id,
       {clean('name')},
       {clean('name_id')},
       {clean('classname')},
       {clean('item_type')},
       {clean('use_type')},
       {clean('material')},
       weight, invgfx, grdgfx, itemdesc_id, stackable, dmg_small, dmg_large,
       min_lvl, max_lvl, bless, trade, cant_delete,
       {clean('note')}
FROM etcitem
ORDER BY item_id;
"""
    monster_query = f"""
USE `{db_name}`;
SELECT npcid,
       {clean('name')},
       {clean('nameid')},
       {clean('classname')},
       {clean('note')},
       gfxid, lvl, hp, mp, ac,
       str, con, dex, wis, intel, mr, exp, lawful,
       {clean('size')},
       weakAttr,
       ranged, tamable, agro,
       {clean('family')},
       agrofamily, teleport, damage_reduction,
       karma, transform_id, transform_gfxid, quest_score
FROM npc
ORDER BY npcid;
"""
    drop_query = f"""
USE `{db_name}`;
SELECT mobId, itemId, min, max, chance, {clean('note')}
FROM droplist
ORDER BY mobId, itemId;
"""
    weapon_query = f"""
USE `{db_name}`;
SELECT item_id, {clean('name')}, exp_point, {clean('classname')}, {clean('name_id')}, {clean('type')}, {clean('material')},
       weight, invgfx, grdgfx, itemdesc_id, dmg_small, dmg_large, `range`, safenchant,
       use_royal, use_knight, use_mage, use_elf, use_darkelf, use_dragonknight, use_illusionist,
       hitmodifier, dmgmodifier, add_str, add_con, add_dex, add_int, add_wis, add_cha,
       add_hp, add_mp, add_hpr, add_mpr, add_sp, m_def, haste_item, double_dmg_chance,
       canbedmg, min_lvl, max_lvl, bless, trade, cant_delete, max_use_time, PVPdmg, PVPdmgReduction
FROM weapon
ORDER BY item_id;
"""
    armor_query = f"""
USE `{db_name}`;
SELECT item_id, {clean('name')}, exp_point, {clean('classname')}, {clean('name_id')}, {clean('type')}, {clean('material')},
       weight, invgfx, grdgfx, itemdesc_id, ac, safenchant,
       use_royal, use_knight, use_mage, use_elf, use_darkelf, use_dragonknight, use_illusionist,
       add_str, add_con, add_dex, add_int, add_wis, add_cha, add_hp, add_mp, add_hpr, add_mpr, add_sp,
       min_lvl, max_lvl, m_def, haste_item, damage_reduction, weight_reduction,
       hit_modifier, dmg_modifier, bow_hit_modifier, bow_dmg_modifier,
       bless, trade, cant_delete, max_use_time,
       defense_water, defense_wind, defense_fire, defense_earth,
       regist_stun, regist_stone, regist_sleep, regist_freeze, regist_sustain, regist_blind,
       greater, magic_hit_modifier, up_hp_potion, uhp_number, PVPdmg, PVPdmgReduction, `group`
FROM armor
ORDER BY item_id;
"""

    remote_kw = dict(
        host=args.host,
        user=args.ssh_user,
        key_path=args.ssh_key,
        mysql_path=args.mysql_path,
        mysql_user=args.mysql_user,
        mysql_password=args.mysql_password,
    )

    # Build character query if a char-db is specified.
    # Assumes L2J-style columns: char_id, account_name, char_name, level, base_class, online.
    # Adjust column names here if your server uses different names (e.g. Lev, class, onlinestatus).
    char_db = args.mysql_char_db.strip()
    if char_db:
        clean_char = lambda col: f"REPLACE(REPLACE(REPLACE(IFNULL({col}, ''), '\\r', ' '), '\\n', ' '), '\\t', ' ')"
        char_query = f"""
USE `{char_db.replace('`', '')}`;
SELECT char_id,
       {clean_char('account_name')},
       {clean_char('char_name')},
       IFNULL(level, 0),
       IFNULL(base_class, 0),
       IFNULL(online, 0)
FROM characters
ORDER BY char_id;
"""

    items = parse_tsv(run_remote_mysql(item_query, **remote_kw))
    monsters = parse_tsv(run_remote_mysql(monster_query, **remote_kw))
    drops = parse_tsv(run_remote_mysql(drop_query, **remote_kw))
    weapons = parse_tsv(run_remote_mysql(weapon_query, **remote_kw))
    armors = parse_tsv(run_remote_mysql(armor_query, **remote_kw))

    characters: list[list[str]] = []
    if char_db:
        try:
            characters = parse_tsv(run_remote_mysql(char_query, **remote_kw))
            print(f"Fetched {len(characters)} character rows from {char_db}.characters")
        except Exception as exc:
            print(f"WARNING: character sync skipped — {exc}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Preserve site-owned tables before destroying the DB.
    preserved_site_config: list[tuple] = []
    preserved_announcements: list[tuple] = []
    if out_path.exists():
        try:
            _old = sqlite3.connect(out_path)
            try:
                preserved_site_config = _old.execute(
                    "SELECT key, value FROM site_config"
                ).fetchall()
                preserved_announcements = _old.execute(
                    "SELECT id, title, body, category, url, pinned, published_at, created_at"
                    " FROM announcements"
                ).fetchall()
            except Exception:
                pass  # tables may not exist in very old DBs
            finally:
                _old.close()
        except Exception:
            pass
        out_path.unlink()

    conn = sqlite3.connect(out_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executemany(
            f"INSERT INTO items ({','.join(ITEM_COLUMNS)}) VALUES ({','.join(['?'] * len(ITEM_COLUMNS))})",
            [
                (
                    to_int(r[0]), r[1], r[2], r[3], r[4], r[5], r[6],
                    to_int(r[7]), to_int(r[8]), to_int(r[9]), to_int(r[10]), to_int(r[11]), to_int(r[12]), to_int(r[13]),
                    to_int(r[14]), to_int(r[15]), to_int(r[16]), to_int(r[17]), to_int(r[18]), r[19] if len(r) > 19 else "",
                )
                for r in items
            ],
        )
        conn.executemany(
            f"INSERT INTO monsters ({','.join(MONSTER_COLUMNS)}) VALUES ({','.join(['?'] * len(MONSTER_COLUMNS))})",
            [
                (
                    to_int(r[0]), r[1], r[2], r[3], r[4], to_int(r[5]), to_int(r[6]), to_int(r[7]), to_int(r[8]), to_int(r[9]),
                    to_int(r[10]), to_int(r[11]), to_int(r[12]), to_int(r[13]), to_int(r[14]), to_int(r[15]), to_int(r[16]), to_int(r[17]), r[18], to_int(r[19]),
                    to_int(r[20]), to_int(r[21]), to_int(r[22]), r[23], to_int(r[24]), to_int(r[25]), to_int(r[26]),
                    to_int(r[27]), to_int(r[28]), to_int(r[29]), to_int(r[30]),
                )
                for r in monsters
            ],
        )
        conn.executemany(
            f"INSERT INTO monster_drops ({','.join(DROP_COLUMNS)}) VALUES ({','.join(['?'] * len(DROP_COLUMNS))})",
            [
                (
                    to_int(r[0]), to_int(r[1]), to_int(r[2]), to_int(r[3]), to_int(r[4]), r[5] if len(r) > 5 else "",
                )
                for r in drops
            ],
        )
        conn.executemany(
            f"INSERT INTO weapons ({','.join(WEAPON_COLUMNS)}) VALUES ({','.join(['?'] * len(WEAPON_COLUMNS))})",
            [
                tuple(to_int(v) if i not in {1, 3, 4, 5, 6} else v for i, v in enumerate(r))
                for r in weapons
            ],
        )
        conn.executemany(
            f"INSERT INTO armors ({','.join(ARMOR_COLUMNS)}) VALUES ({','.join(['?'] * len(ARMOR_COLUMNS))})",
            [
                tuple(to_int(v) if i not in {1, 3, 4, 5, 6} else v for i, v in enumerate(r))
                for r in armors
            ],
        )
        if characters:
            conn.executemany(
                f"INSERT OR REPLACE INTO characters ({','.join(CHARACTER_COLUMNS)}) "
                f"VALUES ({','.join(['?'] * len(CHARACTER_COLUMNS))})",
                [
                    (
                        to_int(r[0]), r[1], r[2],
                        to_int(r[3]), to_int(r[4]), to_int(r[5]),
                    )
                    for r in characters
                ],
            )
        # Restore site-owned tables (overrides schema defaults with live data).
        if preserved_site_config:
            conn.executemany(
                "INSERT OR REPLACE INTO site_config (key, value) VALUES (?, ?)",
                preserved_site_config,
            )
        if preserved_announcements:
            conn.executemany(
                "INSERT OR REPLACE INTO announcements"
                " (id, title, body, category, url, pinned, published_at, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                preserved_announcements,
            )

        conn.commit()
        counts = {
            "items": conn.execute("SELECT COUNT(*) FROM items").fetchone()[0],
            "monsters": conn.execute("SELECT COUNT(*) FROM monsters").fetchone()[0],
            "drops": conn.execute("SELECT COUNT(*) FROM monster_drops").fetchone()[0],
            "weapons": conn.execute("SELECT COUNT(*) FROM weapons").fetchone()[0],
            "armors": conn.execute("SELECT COUNT(*) FROM armors").fetchone()[0],
            "characters": conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0],
        }
    finally:
        conn.close()

    print(f"Wrote SQLite DB: {out_path}")
    print(counts)


if __name__ == "__main__":
    main()
