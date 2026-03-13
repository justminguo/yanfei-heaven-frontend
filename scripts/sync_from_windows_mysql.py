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

# ---------------------------------------------------------------------------
# Character DB probe order — tried in sequence when --mysql-char-db is not set.
# Add your actual DB name first if you know it, or just pass --mysql-char-db.
# Common names:
#   lin2user  — L2J / L2OFF standard user DB
#   l1jdb     — L1J (Lineage 1 Java) default DB
#   lineage   — some L1J/custom packs use this
#   lin       — short alias sometimes used
#   user      — some older setups
# ---------------------------------------------------------------------------
CANDIDATE_CHAR_DBS = ["lin2user", "l1jdb", "lineage", "lin", "user"]

# ---------------------------------------------------------------------------
# Column name styles for the `characters` table.
#
#   l2j  — Lineage 2 Java / L2OFF:  level, base_class, online
#   l1j  — Lineage 1 Java (381):    Lev,   classtype,  OnlineStatus
#
# Use --char-style to pick explicitly, or leave as "auto" to try l2j then l1j.
# ---------------------------------------------------------------------------
CHAR_QUERY_TEMPLATES = {
    "l2j": """\
USE `{db}`;
SELECT char_id,
       {c('account_name')},
       {c('char_name')},
       IFNULL(level, 0),
       IFNULL(base_class, 0),
       IFNULL(online, 0)
FROM characters
ORDER BY char_id;
""",
    "l1j": """\
USE `{db}`;
SELECT char_id,
       {c('account_name')},
       {c('char_name')},
       IFNULL(Lev, 0),
       IFNULL(classtype, 0),
       IFNULL(OnlineStatus, 0)
FROM characters
ORDER BY char_id;
""",
}


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


def _clean(col: str) -> str:
    return f"REPLACE(REPLACE(REPLACE(IFNULL({col}, ''), '\\r', ' '), '\\n', ' '), '\\t', ' ')"


def build_char_query(db: str, style: str) -> str:
    template = CHAR_QUERY_TEMPLATES[style]
    return template.format(db=db.replace("`", ""), c=_clean)


def try_char_sync(
    db: str,
    style: str,
    remote_kw: dict,
) -> tuple[list[list[str]], str] | None:
    """
    Attempt to fetch characters from `db` using `style` column names.
    Returns (rows, description) on success, None on failure.
    A zero-row result is considered a failure for auto-probe (logs a warning).
    """
    query = build_char_query(db, style)
    print(f"  [char-sync] Trying DB={db!r}  style={style!r} ...", end=" ", flush=True)
    try:
        rows = parse_tsv(run_remote_mysql(query, **remote_kw))
    except Exception as exc:
        print(f"FAILED ({exc!s:.120})")
        return None

    if not rows:
        print(f"OK but 0 rows returned — skipping (DB exists but table may be empty or wrong columns)")
        return None

    desc = f"{db}.characters [{style} columns]"
    print(f"OK — {len(rows)} rows")
    return rows, desc


def sync_characters(
    char_db: str,
    char_style: str,
    remote_kw: dict,
) -> tuple[list[list[str]], str]:
    """
    Return (character_rows, source_description).
    Raises RuntimeError with actionable guidance if nothing works.
    """
    # Explicit DB name given — try it with the requested style(s).
    if char_db:
        styles = [char_style] if char_style != "auto" else ["l2j", "l1j"]
        for style in styles:
            result = try_char_sync(char_db, style, remote_kw)
            if result is not None:
                return result
        # All styles failed for the explicit DB.
        tried = " and ".join(styles)
        raise RuntimeError(
            f"Character sync failed for DB '{char_db}' (tried column styles: {tried}).\n"
            f"  Verify the DB/table exists and check column names with:\n"
            f"    USE `{char_db}`; SHOW COLUMNS FROM characters;\n"
            f"  Then re-run with the correct --char-style (l2j or l1j)."
        )

    # No DB name — auto-probe the candidate list.
    print(f"  [char-sync] --mysql-char-db not set; probing candidates: {CANDIDATE_CHAR_DBS}")
    styles = [char_style] if char_style != "auto" else ["l2j", "l1j"]
    for candidate in CANDIDATE_CHAR_DBS:
        for style in styles:
            result = try_char_sync(candidate, style, remote_kw)
            if result is not None:
                return result

    raise RuntimeError(
        "Character auto-probe exhausted all candidates without success.\n"
        f"  Candidates tried: {CANDIDATE_CHAR_DBS}\n"
        f"  Styles tried: {styles}\n"
        "\n"
        "  ACTION REQUIRED — find the correct DB name on the Windows MySQL:\n"
        "    SHOW DATABASES;\n"
        "    SHOW TABLES FROM <db_name>;\n"
        "    USE <db_name>; SHOW COLUMNS FROM characters;\n"
        "\n"
        "  Then re-run with:\n"
        "    --mysql-char-db <db_name>   (e.g. lin2user, l1jdb, lineage)\n"
        "    --char-style l1j            (if server is Lineage 1 / L1J)\n"
        "    --char-style l2j            (if server is Lineage 2 / L2J)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync Lineage MySQL data from Windows to local SQLite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Characters / Online Count sync
-------------------------------
The --mysql-char-db argument controls which MySQL database contains the
`characters` table used for the real-time online player count on the website.

If you do NOT pass --mysql-char-db, the script will automatically probe a
list of common database names (%(char_candidates)s).

Use --char-style to select the right column naming convention for your server:
  l2j  Lineage 2 Java / L2OFF: level, base_class, online
  l1j  Lineage 1 Java (381):   Lev,   classtype,  OnlineStatus
  auto Try l2j first, then l1j (default)

Pass --mysql-char-db=none  (or --mysql-char-db='') to skip character sync entirely.

Example — explicit DB + L1J columns:
  python scripts/sync_from_windows_mysql.py \\
    --host 211.20.245.169 --ssh-user user --ssh-key /path/to/key \\
    --mysql-db 381 --mysql-char-db l1jdb --char-style l1j
""" % {"char_candidates": ", ".join(CANDIDATE_CHAR_DBS)},
    )
    parser.add_argument("--host", required=True)
    parser.add_argument("--ssh-user", default="user")
    parser.add_argument("--ssh-key", required=True)
    parser.add_argument("--mysql-path", default=r"C:\Program Files\MySQL\MySQL Server 5.5\bin\mysql.exe")
    parser.add_argument("--mysql-user", default="root")
    parser.add_argument("--mysql-password", default="root")
    parser.add_argument("--mysql-db", default="381")
    parser.add_argument(
        "--mysql-char-db",
        default="",
        metavar="DB_NAME",
        help=(
            "MySQL database that contains the `characters` table. "
            "Leave empty (default) to auto-probe common names. "
            "Pass 'none' to skip character sync entirely. "
            "Common values: lin2user (L2J), l1jdb (L1J/381), lineage, lin, user."
        ),
    )
    parser.add_argument(
        "--char-style",
        default="auto",
        choices=["auto", "l2j", "l1j"],
        help=(
            "Column name style for the characters table. "
            "l2j=level/base_class/online (Lineage 2 Java). "
            "l1j=Lev/classtype/OnlineStatus (Lineage 1 Java / 381 servers). "
            "auto=try l2j first, then l1j (default)."
        ),
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

    # ------------------------------------------------------------------
    # Decide whether to attempt character sync.
    # ------------------------------------------------------------------
    char_db_arg = args.mysql_char_db.strip()
    skip_chars = char_db_arg.lower() in ("none", "-")

    items = parse_tsv(run_remote_mysql(item_query, **remote_kw))
    monsters = parse_tsv(run_remote_mysql(monster_query, **remote_kw))
    drops = parse_tsv(run_remote_mysql(drop_query, **remote_kw))
    weapons = parse_tsv(run_remote_mysql(weapon_query, **remote_kw))
    armors = parse_tsv(run_remote_mysql(armor_query, **remote_kw))

    characters: list[list[str]] = []
    char_source: str = "(none)"

    if skip_chars:
        print("Character sync skipped (--mysql-char-db=none).")
    else:
        print(f"Starting character sync (char-db={char_db_arg or '<auto-probe>'!r}, style={args.char_style!r}) ...")
        try:
            characters, char_source = sync_characters(char_db_arg, args.char_style, remote_kw)
            print(f"  [char-sync] SUCCESS: {len(characters)} characters from {char_source}")
            if len(characters) == 0:
                print("  [char-sync] WARNING: 0 characters written — online count will fall back to site_config value.")
        except RuntimeError as exc:
            print(f"\nWARNING: character sync failed — {exc}\n")
            print("  Online count will fall back to site_config.server_online_count value.")

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
    if counts["characters"] == 0 and not skip_chars:
        print(
            "\nNOTE: characters table is empty — real online count is unavailable.\n"
            "  The website will display the fallback value from site_config.server_online_count.\n"
            "  To fix this, re-run with the correct --mysql-char-db and --char-style."
        )


if __name__ == "__main__":
    main()
