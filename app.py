from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, abort, g, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "yanfei.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get("YANFEI_DB_PATH", str(DEFAULT_DB_PATH))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "yanfei-dev")

    # 弱點屬性對照
    WEAK_ATTR_NAMES: dict[int, str] = {
        0: "無",
        1: "水 💧",
        2: "火 🔥",
        4: "地 ⛰️",
        8: "風 🌪️",
    }

    # 家族中文對照
    FAMILY_NAMES: dict[str, str] = {
        "wolf": "狼族", "vampire": "吸血鬼", "ant": "螞蟻", "bat": "蝙蝠",
        "bear": "熊族", "beast": "野獸", "brute": "蠻族", "dragon": "龍族",
        "undead": "不死族", "devil": "惡魔", "insect": "昆蟲", "plant": "植物",
        "humanoid": "人形", "animal": "動物", "orc": "獸人", "giant": "巨人",
        "fairy": "精靈", "fish": "魚族", "bird": "鳥族", "slime": "史萊姆",
        "lizard": "蜥蜴族", "snake": "蛇族", "frog": "青蛙族", "golem": "魔像",
        "skeleton": "骷髏", "zombie": "殭屍", "ghost": "鬼魂", "elemental": "元素",
        "demon": "惡魔", "kobold": "地精", "gnoll": "鬣狗人", "goblin": "哥布林",
        "troll": "巨魔", "ogre": "食人魔", "bandit": "盜賊", "pirate": "海盜",
        "knight": "騎士", "mage": "法師", "assassin": "刺客",
        "alligator": "鱷魚", "angler": "釣魚人", "antiking": "叛王",
        "asitagio": "阿西塔基歐", "balbados": "巴爾巴多斯", "basilisk": "蛇怪",
        "beastsummoner": "召獸師", "blackwizard": "黑魔法師",
        "bombflower": "爆炸花", "Ifrit": "伊芙利特", "PIQUEST": "試煉",
    }

    # 武器類型中文對照
    WEAPON_TYPE_NAMES: dict[str, str] = {
        "sword": "單手劍", "tohandsword": "雙手劍", "dagger": "匕首",
        "bow": "弓箭(雙手)", "singlebow": "弩槍(單手)",
        "blunt": "鈍器(單手)", "tohandblunt": "鈍器(雙手)",
        "staff": "魔杖", "tohandstaff": "魔杖(雙手)",
        "spear": "長槍(雙手)", "singlespear": "矛(單手)",
        "edoryu": "雙刀", "claw": "鋼爪",
        "chainsword": "鎖鏈劍", "kiringku": "奇古獸", "gauntlet": "鐵手甲",
    }

    # 物品類型中文對照
    ITEM_TYPE_NAMES: dict[str, str] = {
        "arrow": "箭矢", "potion": "藥水", "scroll": "卷軸", "food": "食物",
        "spellbook": "魔法書/技術書", "wand": "魔杖", "gem": "寶石",
        "material": "材料", "treasure_box": "寶箱", "light": "照明道具",
        "totem": "任務圖騰", "questitem": "任務道具", "sting": "飛刀",
        "petitem": "寵物裝備", "other": "其他/雜物", "ItemIntegration": "綜合道具",
        "weapon": "武器", "armor": "防具", "accessory": "飾品",
    }

    # 物品用途中文對照
    USE_TYPE_NAMES: dict[str, str] = {
        "normal": "一般", "hpr": "體力回復", "mpr": "魔力回復",
        "power": "強化/加速", "choice": "選擇性使用", "zel": "盔甲強化",
        "dai": "武器強化", "sosc": "變身效果", "identify": "鑑定",
        "home": "祝瞬/回歸", "blank": "空白魔法卷軸", "ntele": "瞬間移動",
    }

    # 材質中文對照
    MATERIAL_NAMES: dict[str, str] = {
        "iron": "鐵", "steel": "鋼", "mithril": "秘銀", "oriharukon": "奧裡哈魯根",
        "silver": "銀", "gold": "黃金", "platinum": "白金", "blackmithril": "暗黑秘銀",
        "bone": "骨頭", "wood": "木頭", "leather": "皮革", "cloth": "布料",
        "glass": "玻璃", "gemstone": "寶石", "mineral": "礦物", "copper": "銅",
        "vegetation": "植物", "web": "蜘蛛網", "animalmatter": "獸材",
        "dragonscale": "龍鱗", "paper": "紙", "none": "無",
    }

    # 防具類型中文對照
    ARMOR_TYPE_NAMES: dict[str, str] = {
        "helm": "頭盔", "armor": "鎧甲", "boots": "靴子",
        "gloves": "手套", "cloak": "披風", "shield": "盾牌",
        "ring": "戒指", "amulet": "項鍊", "belt": "腰帶",
        "underwear": "內衣", "light_armor": "輕甲", "heavy_armor": "重甲",
    }

    # Doll type -> human-readable label
    DOLL_NAMES: dict[str, str] = {
        "Doll_Ac":  "防禦 (AC)",
        "Doll_Hp":  "血量 (HP)",
        "Doll_Mp":  "魔力 (MP)",
        "Doll_Str": "力量 (STR)",
        "Doll_Dex": "敏捷 (DEX)",
        "Doll_Int": "智力 (INT)",
        "Doll_Wis": "精神 (WIS)",
        "Doll_Con": "體質 (CON)",
        "Doll_Cha": "魅力 (CHA)",
    }

    @app.template_filter("commas")
    def fmt_commas(n: object) -> str:
        if n is None:
            return "—"
        try:
            return f"{int(n):,}"
        except (ValueError, TypeError):
            return str(n) if n else "—"

    @app.template_filter("drop_chance")
    def fmt_drop_chance(n: object) -> str:
        """將掉落機率轉為百分比（1,000,000 = 100%）。"""
        try:
            v = int(n)
            if v <= 0:
                return "—"
            pct = v / 10_000  # 1000000 / 10000 = 100.00%
            return f"{pct:.2f}%"
        except (ValueError, TypeError):
            return str(n) if n else "—"

    @app.template_filter("weak_attr")
    def fmt_weak_attr(n: object) -> str:
        try:
            return WEAK_ATTR_NAMES.get(int(n), str(n))
        except (ValueError, TypeError):
            return str(n) if n else "—"

    @app.template_filter("family_cn")
    def fmt_family(s: object) -> str:
        if not s:
            return "—"
        return FAMILY_NAMES.get(str(s), str(s))

    @app.template_filter("material_cn")
    def fmt_material(s: object) -> str:
        if not s:
            return "—"
        return MATERIAL_NAMES.get(str(s), str(s))

    @app.template_filter("item_type_cn")
    def fmt_item_type(s: object) -> str:
        if not s:
            return "—"
        return ITEM_TYPE_NAMES.get(str(s), str(s))

    @app.template_filter("use_type_cn")
    def fmt_use_type(s: object) -> str:
        if not s:
            return "—"
        return USE_TYPE_NAMES.get(str(s), str(s))

    @app.template_filter("safe_name")
    def fmt_safe_name(s: object) -> str:
        """過濾未映射的 $xxx 字串，只顯示 name 欄位即可。"""
        if not s:
            return "—"
        text = str(s)
        if text.startswith("$"):
            return "—"
        return text

    @app.template_filter("clean_name")
    def fmt_clean_name(s: object) -> str:
        """移除天堂名稱中的顏色/格式代碼，如 \\aH、\\f3 等。"""
        import re
        if not s:
            return "—"
        text = str(s)
        text = re.sub(r'(\\+a[A-Za-z])|(\\+f[A-Za-z0-9=@<>])', '', text)
        return text.strip() or "—"

    @app.template_filter("safe_enchant")
    def fmt_safe_enchant(n: object) -> str:
        """格式化安全強化值。"""
        try:
            v = int(n)
            if v == -1:
                return "不可強化"
            if v == 0:
                return "⚠️ 0"
            return f"+{v}"
        except (ValueError, TypeError):
            return str(n) if n else "—"

    @app.template_filter("weapon_type_cn")
    def fmt_weapon_type(s: object) -> str:
        if not s:
            return "—"
        return WEAPON_TYPE_NAMES.get(str(s), str(s))

    @app.template_filter("armor_type_cn")
    def fmt_armor_type(s: object) -> str:
        if not s:
            return "—"
        return ARMOR_TYPE_NAMES.get(str(s), str(s))

    @app.template_filter("exp_highlight")
    def fmt_exp_highlight(s: object) -> str:
        import re
        if not s:
            return "—"
        text = str(s)
        exp_match = re.search(r'經驗值\+(\d+)%', text)
        if exp_match:
            pct = exp_match.group(1)
            return f"📈 EXP+{pct}% | {text}"
        return text

    # Lineage I class ID -> name mapping (common Taiwan server IDs)
    CLASS_NAMES: dict[int, str] = {
        0: "君主",
        1: "騎士",
        2: "妖精",
        3: "法師",
        4: "黑暗妖精",
        5: "龍騎士",
        6: "幻術師",
        7: "忍者",
        8: "君主(暗)",
        61: "騎士",
        138: "妖精",
        734: "法師",
        2786: "黑暗妖精",
        4096: "妖精",
        6658: "龍騎士",
    }

    def stats_payload() -> dict[str, int]:
        db = get_db()
        return {
            "items": db.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"],
            "monsters": db.execute("SELECT COUNT(*) AS c FROM monsters").fetchone()["c"],
            "drops": db.execute("SELECT COUNT(*) AS c FROM monster_drops").fetchone()["c"],
            "weapons": db.execute("SELECT COUNT(*) AS c FROM weapons").fetchone()["c"],
            "armors": db.execute("SELECT COUNT(*) AS c FROM armors").fetchone()["c"],
            "characters": db.execute("SELECT COUNT(*) AS c FROM characters").fetchone()["c"],
        }

    @app.route("/")
    def home():
        db = get_db()
        stats = stats_payload()
        announcements = db.execute(
            "SELECT id, title, body, category, url, pinned, published_at FROM announcements ORDER BY pinned DESC, published_at DESC LIMIT 5"
        ).fetchall()
        top_chars = db.execute(
            "SELECT char_name, level, class, OnlineStatus FROM characters ORDER BY level DESC LIMIT 10"
        ).fetchall()
        return render_template("home.html", stats=stats, announcements=announcements, top_chars=top_chars, class_names=CLASS_NAMES)

    @app.route("/ranking")
    def ranking():
        db = get_db()
        rows = db.execute(
            "SELECT char_name, level, class, OnlineStatus FROM characters ORDER BY level DESC, char_name ASC LIMIT 200"
        ).fetchall()
        return render_template("ranking.html", rows=rows, class_names=CLASS_NAMES)

    @app.route("/items")
    def items():
        q = request.args.get("q", "").strip()
        item_type = request.args.get("item_type", "").strip()
        sql = """
            SELECT id, name, name_id, item_type, use_type, material, weight, stackable, note
            FROM items
            WHERE 1=1
        """
        params: list[Any] = []
        if q:
            sql += " AND (name LIKE ? OR name_id LIKE ? OR classname LIKE ? OR note LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like, like, like])
        if item_type:
            sql += " AND item_type = ?"
            params.append(item_type)
        sql += " ORDER BY id LIMIT 200"
        rows = get_db().execute(sql, params).fetchall()
        types = get_db().execute(
            "SELECT DISTINCT item_type FROM items WHERE item_type <> '' ORDER BY item_type"
        ).fetchall()
        return render_template("items.html", rows=rows, q=q, item_type=item_type, types=types)

    @app.route("/monsters")
    def monsters():
        q = request.args.get("q", "").strip()
        min_level = request.args.get("min_level", "").strip()
        max_level = request.args.get("max_level", "").strip()
        sql = """
            SELECT id, name, nameid, level, hp, mp, ac, exp, family, note, gfxid
            FROM monsters
            WHERE level < 500 AND hp < 5000000
        """
        params: list[Any] = []
        if q:
            sql += " AND (name LIKE ? OR nameid LIKE ? OR classname LIKE ? OR note LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like, like, like])
        if min_level.isdigit():
            sql += " AND level >= ?"
            params.append(int(min_level))
        if max_level.isdigit():
            sql += " AND level <= ?"
            params.append(int(max_level))
        sql += " ORDER BY level DESC, id ASC LIMIT 200"
        rows = get_db().execute(sql, params).fetchall()
        return render_template(
            "monsters.html",
            rows=rows,
            q=q,
            min_level=min_level,
            max_level=max_level,
        )

    @app.route("/drops")
    def drops():
        q = request.args.get("q", "").strip()
        sql = """
            SELECT md.id,
                   md.monster_id,
                   md.item_id,
                   md.min_count,
                   md.max_count,
                   md.chance,
                   md.note,
                   m.name AS monster_name,
                   m.level AS monster_level,
                   i.name AS item_name,
                   i.item_type AS item_type
            FROM monster_drops md
            JOIN monsters m ON m.id = md.monster_id
            JOIN items i ON i.id = md.item_id
            WHERE 1=1
        """
        params: list[Any] = []
        if q:
            sql += " AND (m.name LIKE ? OR i.name LIKE ? OR i.name_id LIKE ? OR md.note LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like, like, like])
        sql += " ORDER BY md.chance DESC, m.level DESC LIMIT 300"
        rows = get_db().execute(sql, params).fetchall()
        return render_template("drops.html", rows=rows, q=q)

    @app.route("/dolls")
    def dolls():
        q = request.args.get("q", "").strip()
        grade = request.args.get("grade", "").strip()
        db = get_db()

        DOLL_GRADES = ["神話", "傳說", "英雄", "稀有", "一般"]

        sql = """
            SELECT id, name, doll_effects,
              CASE
                WHEN name LIKE '神話娃娃%' THEN '神話'
                WHEN name LIKE '傳說娃娃%' THEN '傳說'
                WHEN name LIKE '英雄娃娃%' THEN '英雄'
                WHEN name LIKE '稀有娃娃%' THEN '稀有'
                WHEN name LIKE '魔法娃娃%' THEN '一般'
                ELSE '一般'
              END AS grade
            FROM items
            WHERE (name LIKE '%娃娃%' OR name LIKE '%魔法娃娃%')
              AND name NOT LIKE '%袋子%'
              AND name NOT LIKE '%幣%'
              AND name NOT LIKE '%藥劑%'
              AND name NOT LIKE '%能量石%'
        """
        params: list[Any] = []
        if q:
            sql += " AND name LIKE ?"
            params.append(f"%{q}%")
        if grade:
            grade_prefix = {
                "神話": "神話娃娃%",
                "傳說": "傳說娃娃%",
                "英雄": "英雄娃娃%",
                "稀有": "稀有娃娃%",
                "一般": "魔法娃娃%",
            }.get(grade, "%")
            sql += " AND name LIKE ?"
            params.append(grade_prefix)
        sql += " ORDER BY grade, id LIMIT 500"
        rows = db.execute(sql, params).fetchall()
        return render_template("dolls.html", rows=rows, q=q, grade=grade, doll_grades=DOLL_GRADES)

    @app.route("/polymorphs")
    def polymorphs():
        q = request.args.get("q", "").strip()
        db = get_db()

        sql = """
            SELECT id, name, note, polyid, atkspeed, movespeed, magic_speed
            FROM polymorphs
            WHERE 1=1
        """
        params: list[Any] = []
        if q:
            sql += " AND (name LIKE ? OR note LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        sql += " ORDER BY id LIMIT 500"
        rows = db.execute(sql, params).fetchall()
        return render_template("polymorphs.html", rows=rows, q=q)

    @app.route("/poly-speed")
    def poly_speed():
        q = request.args.get("q", "").strip()
        sql = """
            SELECT id, name, note, atkspeed, movespeed, magic_speed
            FROM polymorphs
            WHERE atkspeed IS NOT NULL OR movespeed IS NOT NULL
        """
        params: list[Any] = []
        if q:
            sql += " AND (name LIKE ? OR note LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        sql += " ORDER BY atkspeed ASC LIMIT 200"
        rows = get_db().execute(sql, params).fetchall()
        return render_template("poly_speed.html", rows=rows, q=q)

    @app.route("/monster/<int:monster_id>")
    def monster_detail(monster_id: int):
        db = get_db()
        monster = db.execute("SELECT * FROM monsters WHERE id = ?", (monster_id,)).fetchone()
        if not monster:
            abort(404)
        drops = db.execute(
            """
            SELECT md.*, i.name AS item_name, i.name_id, i.item_type
            FROM monster_drops md
            JOIN items i ON i.id = md.item_id
            WHERE md.monster_id = ?
            ORDER BY md.chance DESC, i.name ASC
            """,
            (monster_id,),
        ).fetchall()
        return render_template("monster_detail.html", monster=monster, drops=drops)

    @app.route("/item/<int:item_id>")
    def item_detail(item_id: int):
        db = get_db()
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not item:
            abort(404)
        drop_sources = db.execute(
            """
            SELECT md.*, m.name AS monster_name, m.level, m.family
            FROM monster_drops md
            JOIN monsters m ON m.id = md.monster_id
            WHERE md.item_id = ?
            ORDER BY md.chance DESC, m.level DESC
            """,
            (item_id,),
        ).fetchall()
        return render_template("item_detail.html", item=item, drop_sources=drop_sources)

    @app.route("/api/stats")
    def api_stats():
        return jsonify({"ok": True, "stats": stats_payload()})

    @app.route("/api/items")
    def api_items():
        q = request.args.get("q", "").strip()
        item_type = request.args.get("item_type", "").strip()
        limit = min(int(request.args.get("limit", 100)), 500)
        sql = "SELECT * FROM items WHERE 1=1"
        params: list[Any] = []
        if q:
            like = f"%{q}%"
            sql += " AND (name LIKE ? OR name_id LIKE ? OR classname LIKE ? OR note LIKE ?)"
            params.extend([like, like, like, like])
        if item_type:
            sql += " AND item_type = ?"
            params.append(item_type)
        sql += " ORDER BY id LIMIT ?"
        params.append(limit)
        rows = get_db().execute(sql, params).fetchall()
        return jsonify({"ok": True, "count": len(rows), "rows": rows_to_dicts(rows)})

    @app.route("/api/item/<int:item_id>")
    def api_item_detail(item_id: int):
        db = get_db()
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not item:
            return jsonify({"ok": False, "error": "item_not_found"}), 404
        drop_sources = db.execute(
            """
            SELECT md.*, m.name AS monster_name, m.level, m.family
            FROM monster_drops md
            JOIN monsters m ON m.id = md.monster_id
            WHERE md.item_id = ?
            ORDER BY md.chance DESC, m.level DESC
            """,
            (item_id,),
        ).fetchall()
        return jsonify({"ok": True, "item": row_to_dict(item), "drop_sources": rows_to_dicts(drop_sources)})

    @app.route("/api/monsters")
    def api_monsters():
        q = request.args.get("q", "").strip()
        min_level = request.args.get("min_level", "").strip()
        max_level = request.args.get("max_level", "").strip()
        limit = min(int(request.args.get("limit", 100)), 500)
        sql = "SELECT * FROM monsters WHERE 1=1"
        params: list[Any] = []
        if q:
            like = f"%{q}%"
            sql += " AND (name LIKE ? OR nameid LIKE ? OR classname LIKE ? OR note LIKE ?)"
            params.extend([like, like, like, like])
        if min_level.isdigit():
            sql += " AND level >= ?"
            params.append(int(min_level))
        if max_level.isdigit():
            sql += " AND level <= ?"
            params.append(int(max_level))
        sql += " ORDER BY level DESC, id ASC LIMIT ?"
        params.append(limit)
        rows = get_db().execute(sql, params).fetchall()
        return jsonify({"ok": True, "count": len(rows), "rows": rows_to_dicts(rows)})

    @app.route("/api/monster/<int:monster_id>")
    def api_monster_detail(monster_id: int):
        db = get_db()
        monster = db.execute("SELECT * FROM monsters WHERE id = ?", (monster_id,)).fetchone()
        if not monster:
            return jsonify({"ok": False, "error": "monster_not_found"}), 404
        drops = db.execute(
            """
            SELECT md.*, i.name AS item_name, i.name_id, i.item_type
            FROM monster_drops md
            JOIN items i ON i.id = md.item_id
            WHERE md.monster_id = ?
            ORDER BY md.chance DESC, i.name ASC
            """,
            (monster_id,),
        ).fetchall()
        return jsonify({"ok": True, "monster": row_to_dict(monster), "drops": rows_to_dicts(drops)})

    @app.route("/api/drops")
    def api_drops():
        q = request.args.get("q", "").strip()
        monster_id = request.args.get("monster_id", "").strip()
        item_id = request.args.get("item_id", "").strip()
        limit = min(int(request.args.get("limit", 200)), 1000)
        sql = """
            SELECT md.id,
                   md.monster_id,
                   md.item_id,
                   md.min_count,
                   md.max_count,
                   md.chance,
                   md.note,
                   m.name AS monster_name,
                   m.level AS monster_level,
                   i.name AS item_name,
                   i.name_id AS item_name_id,
                   i.item_type AS item_type
            FROM monster_drops md
            JOIN monsters m ON m.id = md.monster_id
            JOIN items i ON i.id = md.item_id
            WHERE 1=1
        """
        params: list[Any] = []
        if q:
            like = f"%{q}%"
            sql += " AND (m.name LIKE ? OR i.name LIKE ? OR i.name_id LIKE ? OR md.note LIKE ?)"
            params.extend([like, like, like, like])
        if monster_id.isdigit():
            sql += " AND md.monster_id = ?"
            params.append(int(monster_id))
        if item_id.isdigit():
            sql += " AND md.item_id = ?"
            params.append(int(item_id))
        sql += " ORDER BY md.chance DESC, m.level DESC LIMIT ?"
        params.append(limit)
        rows = get_db().execute(sql, params).fetchall()
        return jsonify({"ok": True, "count": len(rows), "rows": rows_to_dicts(rows)})

    @app.route("/weapons")
    def weapons():
        q = request.args.get("q", "").strip()
        w_type = request.args.get("type", "").strip()
        sql = "SELECT id, name, type, dmg_small, dmg_large, safenchant, material FROM weapons WHERE 1=1"
        params: list[Any] = []
        if q:
            sql += " AND (name LIKE ? OR name_id LIKE ? OR classname LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like, like])
        if w_type:
            sql += " AND type = ?"
            params.append(w_type)
        sql += " ORDER BY id LIMIT 500"
        rows = get_db().execute(sql, params).fetchall()
        types = get_db().execute(
            "SELECT DISTINCT type FROM weapons WHERE type <> '' ORDER BY type"
        ).fetchall()
        return render_template("weapons.html", rows=rows, q=q, w_type=w_type, types=types)

    @app.route("/armors")
    def armors():
        q = request.args.get("q", "").strip()
        a_type = request.args.get("type", "").strip()
        sql = "SELECT id, name, type, ac, safenchant, material FROM armors WHERE 1=1"
        params: list[Any] = []
        if q:
            sql += " AND (name LIKE ? OR name_id LIKE ? OR classname LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like, like])
        if a_type:
            sql += " AND type = ?"
            params.append(a_type)
        sql += " ORDER BY id LIMIT 500"
        rows = get_db().execute(sql, params).fetchall()
        types = get_db().execute(
            "SELECT DISTINCT type FROM armors WHERE type <> '' ORDER BY type"
        ).fetchall()
        return render_template("armors.html", rows=rows, q=q, a_type=a_type, types=types)

    @app.route("/api/weapons")
    def api_weapons():
        q = request.args.get("q", "").strip()
        limit = min(int(request.args.get("limit", 100)), 500)
        sql = "SELECT * FROM weapons WHERE 1=1"
        params: list[Any] = []
        if q:
            like = f"%{q}%"
            sql += " AND (name LIKE ? OR name_id LIKE ? OR classname LIKE ?)"
            params.extend([like, like, like])
        sql += " ORDER BY id LIMIT ?"
        params.append(limit)
        rows = get_db().execute(sql, params).fetchall()
        return jsonify({"ok": True, "count": len(rows), "rows": rows_to_dicts(rows)})

    @app.route("/api/weapon/<int:weapon_id>")
    def api_weapon_detail(weapon_id: int):
        row = get_db().execute("SELECT * FROM weapons WHERE id = ?", (weapon_id,)).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "weapon_not_found"}), 404
        return jsonify({"ok": True, "weapon": row_to_dict(row)})

    @app.route("/api/armors")
    def api_armors():
        q = request.args.get("q", "").strip()
        limit = min(int(request.args.get("limit", 100)), 500)
        sql = "SELECT * FROM armors WHERE 1=1"
        params: list[Any] = []
        if q:
            like = f"%{q}%"
            sql += " AND (name LIKE ? OR name_id LIKE ? OR classname LIKE ?)"
            params.extend([like, like, like])
        sql += " ORDER BY id LIMIT ?"
        params.append(limit)
        rows = get_db().execute(sql, params).fetchall()
        return jsonify({"ok": True, "count": len(rows), "rows": rows_to_dicts(rows)})

    @app.route("/api/armor/<int:armor_id>")
    def api_armor_detail(armor_id: int):
        row = get_db().execute("SELECT * FROM armors WHERE id = ?", (armor_id,)).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "armor_not_found"}), 404
        return jsonify({"ok": True, "armor": row_to_dict(row)})

    @app.route("/healthz")
    def healthz():
        return {"ok": True, "stats": stats_payload()}

    @app.teardown_appcontext
    def close_db(_: BaseException | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    init_db(app)
    return app


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [row_to_dict(row) for row in rows]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db_path = Path(current_app().config["DATABASE"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


def current_app() -> Flask:
    from flask import current_app as flask_current_app

    return flask_current_app


def init_db(app: Flask) -> None:
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        return
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    finally:
        conn.close()


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
