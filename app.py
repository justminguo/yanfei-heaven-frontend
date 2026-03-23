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
        """移除天堂名稱中的顏色/格式代碼，如 \\f=f1、\\f4、\\aH 等。"""
        import re
        if not s:
            return "—"
        text = str(s)
        text = re.sub(r'\\+[a-zA-Z0-9=@<>]+', '', text)
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
        # 統一 exp+X% 為 狩獵經驗值+X%
        text = re.sub(r'(?i)exp\+(\d+)%', r'狩獵經驗值+\1%', text)
        # 去重
        parts = [p.strip() for p in text.split(',')]
        seen, deduped = set(), []
        for p in parts:
            key = re.sub(r'\s+', '', p).lower()
            if key not in seen:
                seen.add(key)
                deduped.append(p)
        return ','.join(deduped)

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
            "SELECT char_name, MAX(level) as level, class, OnlineStatus FROM characters GROUP BY char_name ORDER BY level DESC LIMIT 10"
        ).fetchall()
        return render_template("home.html", stats=stats, announcements=announcements, top_chars=top_chars, class_names=CLASS_NAMES)

    @app.route("/ranking")
    def ranking():
        db = get_db()
        rows = db.execute("""
            SELECT char_name, class,
                   MAX(level) as level,
                   MAX(rebirth_count) as rebirth_count
            FROM characters
            GROUP BY char_name
            ORDER BY level DESC, rebirth_count DESC
            LIMIT 100
        """).fetchall()
        return render_template("ranking.html", rows=rows, class_names=CLASS_NAMES)

    @app.route("/items")
    def items():
        q = request.args.get("q", "").strip()
        item_type = request.args.get("item_type", "").strip()
        sql = """
            SELECT id, name, name_id, item_type, use_type, material, weight, stackable, note
            FROM items
            WHERE name NOT LIKE '%娃娃%'
              AND name NOT LIKE '%變身%'
              AND name NOT LIKE '%魔法娃娃%'
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
              AND doll_effects IS NOT NULL AND doll_effects != ''
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
        grade = request.args.get("grade", "").strip()
        db = get_db()

        POLY_GRADES = [
            ("覺醒", "覺醒/支配者"),
            ("神話", "神話變身"),
            ("傳說", "傳說變身"),
            ("英雄", "英雄變身"),
            ("稀有", "稀有變身"),
            ("高級", "高級變身"),
            ("一般", "一般變身"),
        ]

        # 直接查 polymorphs 表，有速度資料
        # 覺醒判斷：name 以「覺醒-」或「支配者-」開頭（排除「英雄變身-[覺醒xxx]」這類）
        sql = """
            SELECT id, name, note, polyid, atkspeed, movespeed, magic_speed, atk_boost, mov_boost, mag_boost, minlevel,
              CASE
                WHEN name LIKE '覺醒-%' OR name LIKE '支配者-%' THEN '覺醒'
                WHEN name LIKE '神話變身%' OR note LIKE '%神話%' THEN '神話'
                WHEN name LIKE '傳說變身%' OR note LIKE '%傳說%' THEN '傳說'
                WHEN name LIKE '英雄變身%' OR note LIKE '%英雄%' THEN '英雄'
                WHEN name LIKE '稀有變身%' OR note LIKE '%稀有%' THEN '稀有'
                WHEN name LIKE '高級變身%' OR note LIKE '%高級%' THEN '高級'
                ELSE '一般'
              END AS grade
            FROM polymorphs
            WHERE note NOT LIKE '%圖鑑%' AND id >= 600000000
        """
        params: list[Any] = []
        if q:
            sql += " AND (name LIKE ? OR note LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        if grade:
            if grade == "覺醒":
                sql += " AND (name LIKE '覺醒-%' OR name LIKE '支配者-%')"
            elif grade == "神話":
                sql += " AND (name LIKE '神話變身%' OR note LIKE '%神話%') AND name NOT LIKE '覺醒-%'"
            elif grade == "傳說":
                sql += " AND (name LIKE '傳說變身%' OR note LIKE '%傳說%') AND name NOT LIKE '覺醒-%'"
            elif grade == "英雄":
                sql += " AND (name LIKE '英雄變身%' OR note LIKE '%英雄%') AND name NOT LIKE '覺醒-%'"
            elif grade == "稀有":
                sql += " AND (name LIKE '稀有變身%' OR note LIKE '%稀有%') AND name NOT LIKE '覺醒-%'"
            elif grade == "高級":
                sql += " AND (name LIKE '高級變身%' OR note LIKE '%高級%') AND name NOT LIKE '覺醒-%'"
            elif grade == "一般":
                sql += """ AND name NOT LIKE '覺醒-%' AND name NOT LIKE '支配者-%'
                           AND name NOT LIKE '神話變身%' AND note NOT LIKE '%神話%'
                           AND name NOT LIKE '傳說變身%' AND note NOT LIKE '%傳說%'
                           AND name NOT LIKE '英雄變身%' AND note NOT LIKE '%英雄%'
                           AND name NOT LIKE '稀有變身%' AND note NOT LIKE '%稀有%'
                           AND name NOT LIKE '高級變身%' AND note NOT LIKE '%高級%'"""
        sql += " ORDER BY id LIMIT 500"
        rows = db.execute(sql, params).fetchall()
        return render_template("polymorphs.html", rows=rows, q=q, grade=grade, poly_grades=POLY_GRADES)

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

    @app.route("/card-album")
    def card_album():
        import json as _json
        q = request.args.get("q", "").strip()
        db = get_db()
        sql = "SELECT seq, name, attrs FROM card_album WHERE 1=1"
        params: list[Any] = []
        if q:
            sql += " AND name LIKE ?"
            params.append(f"%{q}%")
        sql += " ORDER BY seq"
        raw_cards = db.execute(sql, params).fetchall()

        def fmt_attrs(attrs_json):
            if not attrs_json: return None
            try:
                d = _json.loads(attrs_json)
                return ', '.join(f"{k}+{v}" if v > 0 else f"{k}{v}" for k, v in d.items())
            except: return attrs_json

        # 只顯示有屬性加成的卡
        cards = [{"seq": r["seq"], "name": r["name"], "attrs": fmt_attrs(r["attrs"])} 
                 for r in raw_cards if r["attrs"] and r["attrs"] != '{}']
        raw_suits = db.execute("SELECT seq, name, required_cards, attrs FROM card_suit ORDER BY seq").fetchall()

        def fmt_req_cards(req_json):
            if not req_json: return []
            try:
                items = _json.loads(req_json)
                # 找包含中文名稱的那個（最後一個通常是名稱列表）
                for item in reversed(items):
                    if ',' in item and not item.replace(',','').isdigit():
                        return item.split(',')
                return []
            except: return []

        suits = [{"seq": r["seq"], "name": r["name"], 
                  "required_cards": fmt_req_cards(r["required_cards"]),
                  "attrs": fmt_attrs(r["attrs"])} for r in raw_suits]
        return render_template("card_album.html", cards=cards, suits=suits, q=q)

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

    # ── 合成系統 ────────────────────────────────────────────────
    @app.route("/synthesis")
    def synthesis():
        db = get_db()
        doll_rows = db.execute("SELECT * FROM synthesis_doll ORDER BY id").fetchall()
        poly_rows = db.execute("SELECT * FROM synthesis_polymorph ORDER BY id").fetchall()
        system_rows = db.execute("SELECT * FROM synthesis_system ORDER BY id").fetchall()
        return render_template(
            "synthesis.html",
            doll_rows=doll_rows,
            poly_rows=poly_rows,
            system_rows=system_rows,
        )

    # ── 每日狩獵任務 ──────────────────────────────────────────
    @app.route("/daily-hunt")
    def daily_hunt():
        db = get_db()
        hunts = db.execute("SELECT * FROM daily_hunt ORDER BY quest_id, quest_step").fetchall()
        maps = db.execute("SELECT * FROM daily_hunt_map ORDER BY id").fetchall()
        return render_template("daily_hunt.html", hunts=hunts, maps=maps)

    # ── 裝備贖回 ──────────────────────────────────────────────
    @app.route("/equipment-redeem")
    def equipment_redeem():
        rows = get_db().execute("SELECT enchant_level, need_item, need_count FROM equipment_redeem ORDER BY enchant_level").fetchall()
        return render_template("equipment_redeem.html", rows=rows)

    # ── 抽獎系統 ──────────────────────────────────────────────
    @app.route("/lottery")
    def lottery():
        db = get_db()
        slots = db.execute("SELECT * FROM lottery_slot ORDER BY id").fetchall()
        npcs = db.execute("SELECT * FROM lottery_npc ORDER BY id").fetchall()
        return render_template("lottery.html", slots=slots, npcs=npcs)

    # ── 轉生系統 ──────────────────────────────────────────────
    @app.route("/rebirth")
    def rebirth():
        db = get_db()
        stats = db.execute(
            "SELECT * FROM rebirth_stats ORDER BY mete_level, type"
        ).fetchall()
        items = db.execute("SELECT * FROM rebirth_items ORDER BY id").fetchall()
        return render_template("rebirth.html", stats=stats, items=items)

    # ── 紋樣系統 ──────────────────────────────────────────────
    @app.route("/tattoo")
    def tattoo():
        tab = request.args.get("tab", "eva").strip()
        db = get_db()
        table_map = {
            "eva": "tattoo_eva",
            "saha": "tattoo_saha",
            "pagliuo": "tattoo_pagliuo",
            "enhaisa": "tattoo_enhaisa",
            "mapule": "tattoo_mapule",
        }
        tbl = table_map.get(tab, "tattoo_eva")
        rows = db.execute(f"SELECT * FROM {tbl} ORDER BY level").fetchall()
        return render_template("tattoo.html", rows=rows, tab=tab)

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

    @app.route("/search")
    def search():
        q = request.args.get("q", "").strip()
        items_rows = []
        weapons_rows = []
        armors_rows = []
        if q:
            like = f"%{q}%"
            db = get_db()
            items_rows = db.execute(
                "SELECT id, name FROM items WHERE name LIKE ? ORDER BY id LIMIT 50", (like,)
            ).fetchall()
            weapons_rows = db.execute(
                "SELECT id, name FROM weapons WHERE name LIKE ? ORDER BY id LIMIT 50", (like,)
            ).fetchall()
            armors_rows = db.execute(
                "SELECT id, name FROM armors WHERE name LIKE ? ORDER BY id LIMIT 50", (like,)
            ).fetchall()
        return render_template("search.html", q=q, items_rows=items_rows, weapons_rows=weapons_rows, armors_rows=armors_rows)

    @app.route("/monster-search")
    def monster_search():
        q = request.args.get("q", "").strip()
        results = []
        if q:
            like = f"%{q}%"
            db = get_db()
            monsters = db.execute(
                "SELECT id, name, level FROM monsters WHERE name LIKE ? ORDER BY level DESC LIMIT 50", (like,)
            ).fetchall()
            for m in monsters:
                drops = db.execute("""
                    SELECT md.id, i.name AS item_name
                    FROM monster_drops md
                    JOIN items i ON i.id = md.item_id
                    WHERE md.monster_id = ?
                """, (m["id"],)).fetchall()
                results.append({"id": m["id"], "name": m["name"], "level": m["level"], "drops": drops})
        return render_template("monster_search.html", q=q, results=results)

    @app.route("/healthz")
    def healthz():
        return {"ok": True, "stats": stats_payload()}

    @app.teardown_appcontext
    def close_db(_: BaseException | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # ── 私服蝦推送 API ──────────────────────────────────────────
    PUSH_TOKEN = os.environ.get("PUSH_TOKEN", "yanfei-push-secret")

    @app.route("/api/push/characters", methods=["POST"])
    def api_push_characters():
        """私服蝦定期 POST 玩家等級資料來更新。
        Body: { "token": "...", "characters": [{"char_id":1,"char_name":"xx","level":50,"class":1,"OnlineStatus":0}, ...] }
        """
        data = request.get_json(silent=True)
        if not data or data.get("token") != PUSH_TOKEN:
            return jsonify({"ok": False, "error": "unauthorized"}), 401
        chars = data.get("characters", [])
        if not chars:
            return jsonify({"ok": False, "error": "no data"}), 400
        db = get_db()
        updated = 0
        for c in chars:
            char_id = c.get("char_id")
            char_name = c.get("char_name", "")
            level = c.get("level", 1)
            cls = c.get("class", 0)
            online = c.get("OnlineStatus", 0)
            account = c.get("account_name", "")
            existing = db.execute("SELECT char_id FROM characters WHERE char_id=?", (char_id,)).fetchone()
            if existing:
                db.execute("""UPDATE characters SET char_name=?, level=?, class=?, OnlineStatus=?,
                               account_name=?, synced_at=datetime('now') WHERE char_id=?""",
                           (char_name, level, cls, online, account, char_id))
            else:
                db.execute("""INSERT INTO characters (char_id, account_name, char_name, level, class, OnlineStatus, synced_at)
                               VALUES (?,?,?,?,?,?,datetime('now'))""",
                           (char_id, account, char_name, level, cls, online))
            updated += 1
        db.commit()
        return jsonify({"ok": True, "updated": updated})

    # ── 屬性武器強化系統（硬碼資料，來自私服 w_屬性強化系統） ──────────
    WEAPON_ENHANCE_DATA = {
        "地": [
            {"stage": 1, "chance": 100, "scroll_count": 10, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x1.0"},
            {"stage": 2, "chance": 70,  "scroll_count": 20, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x1.5"},
            {"stage": 3, "chance": 30,  "scroll_count": 30, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x2.0"},
            {"stage": 4, "chance": 20,  "scroll_count": 40, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x2.5"},
            {"stage": 5, "chance": 10,  "scroll_count": 55, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x3.0"},
            {"stage": 6, "chance": 5,   "scroll_count": 60, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x3.5"},
            {"stage": 7, "chance": 3,   "scroll_count": 65, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x4.0"},
            {"stage": 8, "chance": 4,   "scroll_count": 70, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x4.5"},
            {"stage": 9, "chance": 2,   "scroll_count": 80, "scroll_name": "地之武器強化卷軸", "effect_text": "地縛傷害倍率 x5.0"},
        ],
        "水": [
            {"stage": 1, "chance": 100, "scroll_count": 10, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 3"},
            {"stage": 2, "chance": 70,  "scroll_count": 20, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 5"},
            {"stage": 3, "chance": 30,  "scroll_count": 30, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 7"},
            {"stage": 4, "chance": 20,  "scroll_count": 40, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 10"},
            {"stage": 5, "chance": 10,  "scroll_count": 55, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 13"},
            {"stage": 6, "chance": 5,   "scroll_count": 60, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 16"},
            {"stage": 7, "chance": 3,   "scroll_count": 65, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 20"},
            {"stage": 8, "chance": 4,   "scroll_count": 70, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 25"},
            {"stage": 9, "chance": 2,   "scroll_count": 80, "scroll_name": "水之武器強化卷軸", "effect_text": "吸魔 30"},
        ],
        "火": [
            {"stage": 1, "chance": 100, "scroll_count": 10, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 10"},
            {"stage": 2, "chance": 70,  "scroll_count": 20, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 20"},
            {"stage": 3, "chance": 30,  "scroll_count": 30, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 30"},
            {"stage": 4, "chance": 20,  "scroll_count": 40, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 40"},
            {"stage": 5, "chance": 10,  "scroll_count": 55, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 50"},
            {"stage": 6, "chance": 5,   "scroll_count": 60, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 60"},
            {"stage": 7, "chance": 3,   "scroll_count": 65, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 70"},
            {"stage": 8, "chance": 4,   "scroll_count": 70, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 80"},
            {"stage": 9, "chance": 100, "scroll_count": 80, "scroll_name": "火之武器強化卷軸", "effect_text": "燃燒傷害 100"},
        ],
        "風": [
            {"stage": 1, "chance": 100, "scroll_count": 10, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x0.8"},
            {"stage": 2, "chance": 70,  "scroll_count": 20, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.0"},
            {"stage": 3, "chance": 30,  "scroll_count": 30, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.2"},
            {"stage": 4, "chance": 20,  "scroll_count": 40, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.3"},
            {"stage": 5, "chance": 10,  "scroll_count": 55, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.4"},
            {"stage": 6, "chance": 5,   "scroll_count": 60, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.5"},
            {"stage": 7, "chance": 3,   "scroll_count": 65, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.6"},
            {"stage": 8, "chance": 4,   "scroll_count": 70, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.7"},
            {"stage": 9, "chance": 2,   "scroll_count": 80, "scroll_name": "風之武器強化卷軸", "effect_text": "攻擊速度加成 x1.8"},
        ],
    }

    @app.route("/weapon-enhance")
    def weapon_enhance():
        tab = request.args.get("tab", "地")
        if tab not in WEAPON_ENHANCE_DATA:
            tab = "地"
        return render_template(
            "weapon_enhance.html",
            tab=tab,
            elements=list(WEAPON_ENHANCE_DATA.keys()),
            rows=WEAPON_ENHANCE_DATA[tab],
        )

    # ── 隨機炫色系統（硬碼資料，來自私服 w_隨機能力炫色*） ──────────
    COLOR_ENHANCE_GRADES = [
        {"type": 1,  "note": "霸王色", "css_color": "#FFD700"},
        {"type": 2,  "note": "武裝色", "css_color": "#FF8C00"},
        {"type": 3,  "note": "見聞色", "css_color": "#9B59B6"},
        {"type": 4,  "note": "菁英",   "css_color": "#4169E1"},
        {"type": 5,  "note": "宗師",   "css_color": "#4169E1"},
        {"type": 6,  "note": "大師",   "css_color": "#4169E1"},
        {"type": 7,  "note": "鑽石",   "css_color": "#20B2AA"},
        {"type": 8,  "note": "白金",   "css_color": "#20B2AA"},
        {"type": 9,  "note": "黃金",   "css_color": "#A9A9A9"},
        {"type": 10, "note": "白銀",   "css_color": "#A9A9A9"},
        {"type": 11, "note": "青銅",   "css_color": "#A9A9A9"},
        {"type": 12, "note": "黑鐵",   "css_color": "#A9A9A9"},
    ]

    COLOR_ENHANCE_WEAPON = [
        {"type": 1,  "ran": 5,  "Attack": 25, "Hit": 25, "Sp": 5, "Str": 4, "Dex": 4, "Int": 4, "Con": 2, "Cha": 2, "Wis": 2, "Hp": 200, "Mp": 200, "Mr": 15, "ReductionDmg": 3},
        {"type": 2,  "ran": 8,  "Attack": 21, "Hit": 21, "Sp": 4, "Str": 3, "Dex": 3, "Int": 3, "Con": 1, "Cha": 1, "Wis": 1, "Hp": 100, "Mp": 100, "Mr": 10, "ReductionDmg": 2},
        {"type": 3,  "ran": 10, "Attack": 19, "Hit": 19, "Sp": 4, "Str": 2, "Dex": 2, "Int": 2, "Con": 1, "Cha": 1, "Wis": 1, "Hp": 50,  "Mp": 50,  "Mr": 5,  "ReductionDmg": 1},
        {"type": 4,  "ran": 15, "Attack": 17, "Hit": 17, "Sp": 3, "Str": 2, "Dex": 2, "Int": 2, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 5,  "ran": 20, "Attack": 15, "Hit": 15, "Sp": 3, "Str": 2, "Dex": 2, "Int": 2, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 6,  "ran": 30, "Attack": 13, "Hit": 13, "Sp": 3, "Str": 1, "Dex": 1, "Int": 1, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 7,  "ran": 60, "Attack": 11, "Hit": 11, "Sp": 2, "Str": 1, "Dex": 1, "Int": 1, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 8,  "ran": 70, "Attack": 9,  "Hit": 9,  "Sp": 2, "Str": 1, "Dex": 1, "Int": 1, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 9,  "ran": 80, "Attack": 7,  "Hit": 7,  "Sp": 2, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 10, "ran": 90, "Attack": 5,  "Hit": 5,  "Sp": 1, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 11, "ran": 90, "Attack": 3,  "Hit": 3,  "Sp": 1, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
        {"type": 12, "ran": 90, "Attack": 1,  "Hit": 1,  "Sp": 1, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 0,   "Mp": 0,   "Mr": 0,  "ReductionDmg": 0},
    ]

    COLOR_ENHANCE_ARMOR = [
        {"type": 1,  "ran": 5,  "Str": 2, "Dex": 2, "Int": 2, "Con": 2, "Cha": 2, "Wis": 2, "Hp": 60, "Mp": 60, "Mr": 5, "ReductionDmg": 5, "Hpr": 10, "Mpr": 10},
        {"type": 2,  "ran": 8,  "Str": 1, "Dex": 1, "Int": 1, "Con": 1, "Cha": 1, "Wis": 1, "Hp": 55, "Mp": 55, "Mr": 4, "ReductionDmg": 4, "Hpr": 8,  "Mpr": 8},
        {"type": 3,  "ran": 10, "Str": 1, "Dex": 1, "Int": 1, "Con": 1, "Cha": 1, "Wis": 1, "Hp": 50, "Mp": 50, "Mr": 3, "ReductionDmg": 4, "Hpr": 8,  "Mpr": 8},
        {"type": 4,  "ran": 15, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 45, "Mp": 45, "Mr": 2, "ReductionDmg": 3, "Hpr": 6,  "Mpr": 6},
        {"type": 5,  "ran": 20, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 40, "Mp": 40, "Mr": 1, "ReductionDmg": 3, "Hpr": 6,  "Mpr": 6},
        {"type": 6,  "ran": 30, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 35, "Mp": 35, "Mr": 0, "ReductionDmg": 3, "Hpr": 6,  "Mpr": 6},
        {"type": 7,  "ran": 60, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 30, "Mp": 30, "Mr": 0, "ReductionDmg": 2, "Hpr": 4,  "Mpr": 4},
        {"type": 8,  "ran": 70, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 25, "Mp": 25, "Mr": 0, "ReductionDmg": 2, "Hpr": 4,  "Mpr": 4},
        {"type": 9,  "ran": 80, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 20, "Mp": 20, "Mr": 0, "ReductionDmg": 2, "Hpr": 4,  "Mpr": 4},
        {"type": 10, "ran": 90, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 15, "Mp": 15, "Mr": 0, "ReductionDmg": 1, "Hpr": 2,  "Mpr": 2},
        {"type": 11, "ran": 90, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 10, "Mp": 10, "Mr": 0, "ReductionDmg": 1, "Hpr": 2,  "Mpr": 2},
        {"type": 12, "ran": 90, "Str": 0, "Dex": 0, "Int": 0, "Con": 0, "Cha": 0, "Wis": 0, "Hp": 5,  "Mp": 5,  "Mr": 0, "ReductionDmg": 1, "Hpr": 2,  "Mpr": 2},
    ]

    COLOR_ENHANCE_SCROLLS = [
        {"item_id": 92159, "name": "洗煉(炫裝武色)"},
        {"item_id": 95185, "name": "洗煉武器石"},
        {"item_id": 95183, "name": "洗煉防具石"},
        {"item_id": 92232, "name": "炫色卷軸箱"},
        {"item_id": 92100, "name": "對單屬性武器洗煉卷軸(捨棄)"},
        {"item_id": 92101, "name": "對雙屬性武器洗煉卷軸(捨棄)"},
        {"item_id": 92102, "name": "對三屬性武器洗煉卷軸(捨棄)"},
        {"item_id": 92097, "name": "對單屬性防具洗煉卷軸(捨棄)"},
        {"item_id": 92098, "name": "對雙屬性防具洗煉卷軸(捨棄)"},
        {"item_id": 92099, "name": "對三屬性防具洗煉卷軸(捨棄)"},
    ]

    @app.route("/color-enhance")
    def color_enhance():
        tab = request.args.get("tab", "weapon")
        if tab not in ("weapon", "armor"):
            tab = "weapon"
        grades_map = {g["type"]: g for g in COLOR_ENHANCE_GRADES}
        data = COLOR_ENHANCE_WEAPON if tab == "weapon" else COLOR_ENHANCE_ARMOR
        rows = []
        for d in data:
            g = grades_map.get(d["type"], {})
            rows.append({**d, **g})
        return render_template(
            "color_enhance.html",
            tab=tab,
            rows=rows,
            scrolls=COLOR_ENHANCE_SCROLLS,
        )

    # ── 娃娃卡冊 ────────────────────────────────────────────────
    @app.route("/doll-card-album")
    def doll_card_album():
        # 單卡共同能力
        SINGLE_CARD_ATTRS = "血量+25、回血量+1、回魔量+1、近距離傷害+1、遠距離傷害+1、近距離命中+1、遠戰攻擊命中+1、魔法命中+1、魔法防禦+1、火屬性防禦+1、風屬性防禦+1、地屬性防禦+1、水屬性防禦+1"

        RARITY_MAP = {
            "金": ("神話", "badge-legend"),
            "紫": ("傳說", "badge-myth"),
            "紅": ("英雄", "badge-epic"),
            "藍": ("稀有", "badge-hero"),
            "綠": ("高級", "badge-rare"),
            "白": ("一般", "badge-normal"),
        }

        _raw = [
            # 白色(一般) 1-8
            (1, "肥肥", "白"), (2, "雪怪", "白"), (3, "蛇女", "白"), (4, "石頭高侖", "白"),
            (5, "野狼寶寶", "白"), (6, "木偶", "白"), (7, "希爾戴絲", "白"), (8, "奎斯坦修", "白"),
            # 藍色(稀有) 9
            (9, "老虎", "藍"),
            # 綠色(高級) 10-29
            (10, "亞力安", "綠"), (11, "黑暗騎士", "綠"), (12, "熔岩高崙", "綠"),
            (13, "稻草人", "綠"), (14, "史巴托", "綠"), (15, "長者", "綠"),
            (16, "王族(♂)", "綠"), (17, "王族(♀)", "綠"), (18, "騎士(♂)", "綠"),
            (19, "騎士(♀)", "綠"), (20, "妖精(♂)", "綠"), (21, "妖精(♀)", "綠"),
            (22, "法師(♂)", "綠"), (23, "法師(♀)", "綠"), (24, "黑妖(♂)", "綠"),
            (25, "黑妖(♀)", "綠"), (26, "槍手(♀)", "綠"), (27, "槍手(♂)", "綠"),
            (28, "狂戰士", "綠"), (29, "神聖劍士", "綠"),
            # 藍色(稀有) 30-42
            (30, "力卡溫", "藍"), (31, "巨大守護螞蟻", "藍"), (32, "拉拉", "藍"),
            (33, "哈維(藍)", "藍"), (34, "曼波兔", "藍"), (35, "黃金安迪斯", "藍"),
            (36, "黃金騎士", "藍"), (37, "樹精", "藍"), (38, "達伊諾思打者", "藍"),
            (39, "達伊諾思投手", "藍"), (40, "法令軍王蕾雅", "藍"), (41, "榭莉", "藍"),
            (42, "黃金巡守", "藍"),
            # 紅色(英雄) 43-60
            (43, "大腳瑪幽", "紅"), (44, "巴克休", "紅"), (45, "巴風特", "紅"),
            (46, "伊弗利特", "紅"), (47, "克特", "紅"), (48, "狂風的夏斯奇(紅)", "紅"),
            (49, "疾風的夏斯奇(綠)", "紅"), (50, "阿努比斯", "紅"), (51, "阿勒尼亞", "紅"),
            (52, "浮士德", "紅"), (53, "傑克吳燈籠", "紅"), (54, "賽尼斯", "紅"),
            (55, "依詩蒂", "紅"), (56, "聖誕妖精", "紅"), (57, "暗黑騎士-莉爾利", "紅"),
            (58, "潔尼斯女王", "紅"), (59, "艾依爾", "紅"), (60, "殭屍王", "紅"),
            # 紫色(傳說) 61-69, 71, 78
            (61, "鐮刀死神", "紫"), (62, "不死鳥", "紫"), (63, "冰之女王", "紫"),
            (64, "帕拉丁", "紫"), (65, "黑暗長老", "紫"), (66, "墮落", "紫"),
            (67, "歐吉王", "紫"), (68, "獨角獸", "紫"), (69, "甘特", "紫"),
            (71, "黑暗之星-宙斯", "紫"), (78, "千年九尾狐", "紫"),
            # 金色(神話) 70, 72-77, 80-82
            (70, "屠龍者", "金"), (72, "安塔瑞斯", "金"), (73, "法利昂", "金"),
            (74, "淘氣龍", "金"), (75, "奧拉奇里亞", "金"), (76, "哈爾巴斯", "金"),
            (77, "貝希摩斯", "金"), (80, "林德拜爾", "金"), (81, "巴拉卡斯", "金"),
            (82, "吉爾塔斯", "金"),
            # 紅色(英雄) 79
            (79, "烏格奴斯", "紅"),
        ]

        DOLL_CARDS = [
            {"seq": s, "name": n, "rarity": r, "rarity_label": RARITY_MAP[r][0], "css": RARITY_MAP[r][1]}
            for s, n, r in _raw
        ]

        RARITY_ORDER = ["金", "紫", "紅", "藍", "綠", "白"]
        card_groups = []
        for rk in RARITY_ORDER:
            group_cards = sorted([c for c in DOLL_CARDS if c["rarity"] == rk], key=lambda c: c["seq"])
            if group_cards:
                card_groups.append({
                    "rarity": rk,
                    "label": RARITY_MAP[rk][0],
                    "css": RARITY_MAP[rk][1],
                    "cards": group_cards,
                })

        # 套卡組合（硬碼）
        DOLL_SUITS = [
            {"seq": 1, "name": "我曾住過的故鄉是北島", "required": ["石頭高崙", "狼人"], "attrs": "近距離命中+1"},
            {"seq": 2, "name": "圓圓的", "required": ["食人妖精", "雪怪"], "attrs": "血量+10"},
            {"seq": 3, "name": "不是吃的", "required": ["奎斯坦修", "木刻人偶"], "attrs": "魔量+5"},
            {"seq": 4, "name": "頭上戴了什麼", "required": ["石頭高崙", "木刻人偶"], "attrs": "遠戰攻擊命中+1"},
            {"seq": 5, "name": "要一起游泳嗎", "required": ["奎斯坦修", "希爾黛斯", "蛇女"], "attrs": "回魔量+2"},
            {"seq": 6, "name": "不需要減肥", "required": ["食人妖精", "石頭高崙", "雪怪"], "attrs": "近距離傷害+1"},
            {"seq": 7, "name": "意外的敏捷啊", "required": ["蛇女", "狼人", "木刻人偶"], "attrs": "魔法命中+1"},
            {"seq": 8, "name": "敢惹我就咬你", "required": ["雪怪", "奎斯坦修", "食人妖精", "狼人"], "attrs": "防禦+1"},
            {"seq": 9, "name": "歐瑞的吉祥物", "required": ["雪怪"], "attrs": "血量+15"},
            {"seq": 10, "name": "亞丁的皮諾丘", "required": ["木刻人偶", "稻草人"], "attrs": "魔量+10"},
            {"seq": 11, "name": "我們不太一樣了", "required": ["雪怪", "蛇女"], "attrs": "魔量+10"},
            {"seq": 12, "name": "哥是在熔岩裡出生的", "required": ["熔岩高崙", "石頭高崙"], "attrs": "遠戰攻擊命中+1"},
            {"seq": 13, "name": "可怕的姐姐們", "required": ["蛇女", "希爾黛絲"], "attrs": "魔攻+1"},
            {"seq": 14, "name": "法師曾經很風光", "required": ["法師(♂)", "法師(♀)"], "attrs": "智力+1"},
            {"seq": 15, "name": "我會在海音裡活下來的", "required": ["槍手(♂)", "妖精(♂)", "希爾黛絲"], "attrs": "遠距離傷害+1"},
            {"seq": 16, "name": "他們來自龍界", "required": ["亞力安", "史巴托"], "attrs": "防禦+1"},
            {"seq": 17, "name": "一起玩吧", "required": ["稻草人", "史巴托", "雪人", "亞力安"], "attrs": "防禦+2"},
            {"seq": 18, "name": "上鉤拳姐妹", "required": ["騎士(♀)", "黑妖(♀)"], "attrs": "近距離傷害+1"},
            {"seq": 19, "name": "妹妹有比較貴一點", "required": ["妖精(♀)", "槍手(♀)"], "attrs": "遠距離傷害+1"},
            {"seq": 20, "name": "龍監入口由我來守護", "required": ["神聖劍士", "狂戰士", "黑暗騎士"], "attrs": "物理減免傷害+1"},
            {"seq": 21, "name": "黃金鎧甲!", "required": ["黃金騎士", "黃金安迪斯", "黃金巡守"], "attrs": "智力+1"},
            {"seq": 22, "name": "他們被稱為古代的怪物", "required": ["阿勒尼亞", "樹精", "巨大守護螞蟻"], "attrs": "遠戰攻擊命中+1"},
            {"seq": 23, "name": "夢想成為大魔法師", "required": ["拉拉", "長者", "法令軍王蕾雅"], "attrs": "魔法減免傷害+1"},
            {"seq": 24, "name": "看看誰比較高吧", "required": ["榭莉", "老虎", "力卡溫"], "attrs": "血量+70"},
            {"seq": 25, "name": "視力至少 2.0", "required": ["達伊諾思打者", "曼波兔", "達伊諾思投手"], "attrs": "敏捷+1"},
            {"seq": 26, "name": "在傲慢之塔見吧", "required": ["潔尼斯女王", "殭屍王", "烏格奴斯"], "attrs": "魔法減免傷害+2"},
            {"seq": 27, "name": "遇到的話,就快跑吧", "required": ["克特", "巴風特", "阿努比斯", "伊弗利特"], "attrs": "智力+2"},
            {"seq": 28, "name": "你是龍吧", "required": ["狂風的夏斯奇(紅)", "疾風的夏斯奇(綠)"], "attrs": "力量+1"},
            {"seq": 29, "name": "誰的法術最強呢", "required": ["莉爾利", "依詩蒂", "賽尼斯"], "attrs": "魔法減免傷害+1"},
            {"seq": 30, "name": "想到地監去", "required": ["傑克吳燈籠", "浮士德", "大腳瑪幽"], "attrs": ""},
            {"seq": 31, "name": "我血不夠多", "required": ["歐吉王", "獨角獸", "千年九尾狐"], "attrs": "血量+200"},
            {"seq": 32, "name": "老美女老俊男", "required": ["黑暗之星-宙斯", "冰之女王"], "attrs": "智力+2, 魔攻+2"},
            {"seq": 33, "name": "傲慢之巔頂上戰爭", "required": ["鐮刀死神", "墮落", "甘特"], "attrs": "近距離傷害+2, 遠距離傷害+2"},
            {"seq": 34, "name": "燃盡之後只剩灰燼", "required": ["不死鳥", "帕拉丁", "黑暗長老"], "attrs": "遠距離傷害+2, 近距離命中+2"},
            {"seq": 35, "name": "冷酷與熱情", "required": ["不死鳥", "冰之女王"], "attrs": "血量+50"},
            {"seq": 36, "name": "有名的惡魔們", "required": ["鐮刀死神", "巴風特", "殭屍王", "克特"], "attrs": "遠戰攻擊命中+2, 物理減免傷害+2"},
            {"seq": 37, "name": "一團貪婪", "required": ["巴風特", "黑暗長老"], "attrs": "智力+1"},
            {"seq": 38, "name": "金髮美女", "required": ["王族(♀)", "菈菈", "妖精(女)"], "attrs": "魔法減免傷害+1"},
            {"seq": 39, "name": "我們是男子漢", "required": ["王族(男)", "騎士(男)", "妖精(男)", "法師(男)", "黑妖(男)"], "attrs": "血量+30"},
            {"seq": 40, "name": "美女折磨人", "required": ["王族(女)", "騎士(女)", "妖精(女)", "法師(女)", "黑妖(女)"], "attrs": "魔量+30"},
        ]

        return render_template(
            "doll_card_album.html",
            cards=DOLL_CARDS,
            card_groups=card_groups,
            single_card_attrs=SINGLE_CARD_ATTRS,
            suits=DOLL_SUITS,
        )

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
