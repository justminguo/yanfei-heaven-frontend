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

    @app.context_processor
    def inject_site_cfg() -> dict:
        try:
            return {"site_cfg": get_site_config()}
        except Exception:
            return {"site_cfg": {}}

    def stats_payload() -> dict[str, int]:
        db = get_db()
        return {
            "items": db.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"],
            "monsters": db.execute("SELECT COUNT(*) AS c FROM monsters").fetchone()["c"],
            "drops": db.execute("SELECT COUNT(*) AS c FROM monster_drops").fetchone()["c"],
            "weapons": db.execute("SELECT COUNT(*) AS c FROM weapons").fetchone()["c"],
            "armors": db.execute("SELECT COUNT(*) AS c FROM armors").fetchone()["c"],
        }

    @app.route("/")
    def home():
        db = get_db()
        stats = stats_payload()
        # 查詢角色在線人數；若 characters 資料表不存在（尚未同步）則回退至設定值
        try:
            row = db.execute(
                "SELECT COUNT(*) AS c FROM characters WHERE OnlineStatus = 1"
            ).fetchone()
            online_count = str(row["c"])
        except Exception:
            online_count = get_site_config().get("server_online_count", "—")
        latest_items = db.execute(
            "SELECT id, name, item_type, note FROM items ORDER BY id DESC LIMIT 8"
        ).fetchall()
        latest_monsters = db.execute(
            "SELECT id, name, level, note FROM monsters ORDER BY id DESC LIMIT 8"
        ).fetchall()
        announcements = db.execute(
            """SELECT id, title, category, url, published_at
               FROM announcements
               ORDER BY pinned DESC, published_at DESC
               LIMIT 8"""
        ).fetchall()
        return render_template(
            "home.html",
            stats=stats,
            online_count=online_count,
            latest_items=latest_items,
            latest_monsters=latest_monsters,
            announcements=announcements,
        )

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
            SELECT id, name, nameid, level, hp, mp, ac, exp, family, note
            FROM monsters
            WHERE 1=1
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

    @app.route("/download")
    def download_page():
        return render_template("download.html")

    @app.route("/guide")
    def guide_page():
        return render_template("guide.html")

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


def get_site_config() -> dict[str, str]:
    """Return all site_config rows as a plain dict."""
    rows = get_db().execute("SELECT key, value FROM site_config").fetchall()
    return {row["key"]: row["value"] for row in rows}


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
    """Apply schema.sql to the database.

    Uses CREATE TABLE IF NOT EXISTS / INSERT OR IGNORE throughout, so it is
    safe to run on every startup — new tables and seed rows are added without
    touching existing data.
    """
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    finally:
        conn.close()


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
