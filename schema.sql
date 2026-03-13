-- yanfei-db-site schema
-- Source tables: 381.etcitem / 381.npc / 381.droplist

CREATE TABLE IF NOT EXISTS items (
    id                INTEGER PRIMARY KEY,
    name              TEXT NOT NULL,
    name_id           TEXT,
    classname         TEXT,
    item_type         TEXT,
    use_type          TEXT,
    material          TEXT,
    weight            INTEGER DEFAULT 0,
    invgfx            INTEGER DEFAULT 0,
    grdgfx            INTEGER DEFAULT 0,
    itemdesc_id       INTEGER DEFAULT 0,
    stackable         INTEGER DEFAULT 0,
    dmg_small         INTEGER DEFAULT 0,
    dmg_large         INTEGER DEFAULT 0,
    min_lvl           INTEGER DEFAULT 0,
    max_lvl           INTEGER DEFAULT 0,
    bless             INTEGER DEFAULT 0,
    tradeable         INTEGER DEFAULT 0,
    cant_delete       INTEGER DEFAULT 0,
    note              TEXT,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monsters (
    id                INTEGER PRIMARY KEY,
    name              TEXT NOT NULL,
    nameid            TEXT,
    classname         TEXT,
    note              TEXT,
    gfxid             INTEGER DEFAULT 0,
    level             INTEGER DEFAULT 0,
    hp                INTEGER DEFAULT 0,
    mp                INTEGER DEFAULT 0,
    ac                INTEGER DEFAULT 0,
    str               INTEGER DEFAULT 0,
    con               INTEGER DEFAULT 0,
    dex               INTEGER DEFAULT 0,
    wis               INTEGER DEFAULT 0,
    int_stat          INTEGER DEFAULT 0,
    mr                INTEGER DEFAULT 0,
    exp               INTEGER DEFAULT 0,
    lawful            INTEGER DEFAULT 0,
    size              TEXT,
    weak_attr         INTEGER DEFAULT 0,
    ranged            INTEGER DEFAULT 0,
    tamable           INTEGER DEFAULT 0,
    agro              INTEGER DEFAULT 0,
    family            TEXT,
    agrofamily        INTEGER DEFAULT 0,
    teleport          INTEGER DEFAULT 0,
    damage_reduction  INTEGER DEFAULT 0,
    karma             INTEGER DEFAULT 0,
    transform_id      INTEGER DEFAULT 0,
    transform_gfxid   INTEGER DEFAULT 0,
    quest_score       INTEGER DEFAULT 0,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monster_drops (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id        INTEGER NOT NULL REFERENCES monsters(id),
    item_id           INTEGER NOT NULL REFERENCES items(id),
    min_count         INTEGER DEFAULT 1,
    max_count         INTEGER DEFAULT 1,
    chance            INTEGER DEFAULT 0,
    note              TEXT,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(monster_id, item_id)
);

CREATE TABLE IF NOT EXISTS weapons (
    id                INTEGER PRIMARY KEY,
    name              TEXT NOT NULL,
    exp_point         INTEGER DEFAULT 0,
    classname         TEXT,
    name_id           TEXT,
    type              TEXT,
    material          TEXT,
    weight            INTEGER DEFAULT 0,
    invgfx            INTEGER DEFAULT 0,
    grdgfx            INTEGER DEFAULT 0,
    itemdesc_id       INTEGER DEFAULT 0,
    dmg_small         INTEGER DEFAULT 0,
    dmg_large         INTEGER DEFAULT 0,
    attack_range      INTEGER DEFAULT 0,
    safenchant        INTEGER DEFAULT 0,
    use_royal         INTEGER DEFAULT 0,
    use_knight        INTEGER DEFAULT 0,
    use_mage          INTEGER DEFAULT 0,
    use_elf           INTEGER DEFAULT 0,
    use_darkelf       INTEGER DEFAULT 0,
    use_dragonknight  INTEGER DEFAULT 0,
    use_illusionist   INTEGER DEFAULT 0,
    hitmodifier       INTEGER DEFAULT 0,
    dmgmodifier       INTEGER DEFAULT 0,
    add_str           INTEGER DEFAULT 0,
    add_con           INTEGER DEFAULT 0,
    add_dex           INTEGER DEFAULT 0,
    add_int           INTEGER DEFAULT 0,
    add_wis           INTEGER DEFAULT 0,
    add_cha           INTEGER DEFAULT 0,
    add_hp            INTEGER DEFAULT 0,
    add_mp            INTEGER DEFAULT 0,
    add_hpr           INTEGER DEFAULT 0,
    add_mpr           INTEGER DEFAULT 0,
    add_sp            INTEGER DEFAULT 0,
    m_def             INTEGER DEFAULT 0,
    haste_item        INTEGER DEFAULT 0,
    double_dmg_chance INTEGER DEFAULT 0,
    canbedmg          INTEGER DEFAULT 0,
    min_lvl           INTEGER DEFAULT 0,
    max_lvl           INTEGER DEFAULT 0,
    bless             INTEGER DEFAULT 0,
    tradeable         INTEGER DEFAULT 0,
    cant_delete       INTEGER DEFAULT 0,
    max_use_time      INTEGER DEFAULT 0,
    pvp_dmg           INTEGER DEFAULT 0,
    pvp_dmg_reduction INTEGER DEFAULT 0,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS armors (
    id                 INTEGER PRIMARY KEY,
    name               TEXT,
    exp_point          INTEGER DEFAULT 0,
    classname          TEXT,
    name_id            TEXT,
    type               TEXT,
    material           TEXT,
    weight             INTEGER DEFAULT 0,
    invgfx             INTEGER DEFAULT 0,
    grdgfx             INTEGER DEFAULT 0,
    itemdesc_id        INTEGER DEFAULT 0,
    ac                 INTEGER DEFAULT 0,
    safenchant         INTEGER DEFAULT 0,
    use_royal          INTEGER DEFAULT 0,
    use_knight         INTEGER DEFAULT 0,
    use_mage           INTEGER DEFAULT 0,
    use_elf            INTEGER DEFAULT 0,
    use_darkelf        INTEGER DEFAULT 0,
    use_dragonknight   INTEGER DEFAULT 0,
    use_illusionist    INTEGER DEFAULT 0,
    add_str            INTEGER DEFAULT 0,
    add_con            INTEGER DEFAULT 0,
    add_dex            INTEGER DEFAULT 0,
    add_int            INTEGER DEFAULT 0,
    add_wis            INTEGER DEFAULT 0,
    add_cha            INTEGER DEFAULT 0,
    add_hp             INTEGER DEFAULT 0,
    add_mp             INTEGER DEFAULT 0,
    add_hpr            INTEGER DEFAULT 0,
    add_mpr            INTEGER DEFAULT 0,
    add_sp             INTEGER DEFAULT 0,
    min_lvl            INTEGER DEFAULT 0,
    max_lvl            INTEGER DEFAULT 0,
    m_def              INTEGER DEFAULT 0,
    haste_item         INTEGER DEFAULT 0,
    damage_reduction   INTEGER DEFAULT 0,
    weight_reduction   INTEGER DEFAULT 0,
    hit_modifier       INTEGER DEFAULT 0,
    dmg_modifier       INTEGER DEFAULT 0,
    bow_hit_modifier   INTEGER DEFAULT 0,
    bow_dmg_modifier   INTEGER DEFAULT 0,
    bless              INTEGER DEFAULT 0,
    tradeable          INTEGER DEFAULT 0,
    cant_delete        INTEGER DEFAULT 0,
    max_use_time       INTEGER DEFAULT 0,
    defense_water      INTEGER DEFAULT 0,
    defense_wind       INTEGER DEFAULT 0,
    defense_fire       INTEGER DEFAULT 0,
    defense_earth      INTEGER DEFAULT 0,
    regist_stun        INTEGER DEFAULT 0,
    regist_stone       INTEGER DEFAULT 0,
    regist_sleep       INTEGER DEFAULT 0,
    regist_freeze      INTEGER DEFAULT 0,
    regist_sustain     INTEGER DEFAULT 0,
    regist_blind       INTEGER DEFAULT 0,
    greater_flag       INTEGER DEFAULT 0,
    magic_hit_modifier INTEGER DEFAULT 0,
    up_hp_potion       INTEGER DEFAULT 0,
    uhp_number         INTEGER DEFAULT 0,
    pvp_dmg            INTEGER DEFAULT 0,
    pvp_dmg_reduction  INTEGER DEFAULT 0,
    armor_group        INTEGER DEFAULT 0,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
CREATE INDEX IF NOT EXISTS idx_items_name_id ON items(name_id);
CREATE INDEX IF NOT EXISTS idx_items_item_type ON items(item_type);
CREATE INDEX IF NOT EXISTS idx_monsters_name ON monsters(name);
CREATE INDEX IF NOT EXISTS idx_monsters_nameid ON monsters(nameid);
CREATE INDEX IF NOT EXISTS idx_monsters_level ON monsters(level);
CREATE INDEX IF NOT EXISTS idx_drops_monster_id ON monster_drops(monster_id);
CREATE INDEX IF NOT EXISTS idx_drops_item_id ON monster_drops(item_id);
CREATE INDEX IF NOT EXISTS idx_drops_chance ON monster_drops(chance);
CREATE INDEX IF NOT EXISTS idx_weapons_name ON weapons(name);
CREATE INDEX IF NOT EXISTS idx_weapons_name_id ON weapons(name_id);
CREATE INDEX IF NOT EXISTS idx_armors_name ON armors(name);
CREATE INDEX IF NOT EXISTS idx_armors_name_id ON armors(name_id);

-- ===== Characters (synced from game server; used for real-time online count) =====
-- Source: lin2user.characters (or equivalent user-db on the game server).
-- Only the columns needed for online-count and basic identification are stored.
-- OnlineStatus mirrors the L2J `online` / L2OFF `onlinestatus` column (1 = online).
CREATE TABLE IF NOT EXISTS characters (
    char_id      INTEGER PRIMARY KEY,
    account_name TEXT NOT NULL DEFAULT '',
    char_name    TEXT NOT NULL DEFAULT '',
    level        INTEGER DEFAULT 0,
    class        INTEGER DEFAULT 0,
    OnlineStatus INTEGER DEFAULT 0,
    synced_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_characters_online ON characters(OnlineStatus);

-- ===== Site Config (key-value) =====
CREATE TABLE IF NOT EXISTS site_config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);

-- ===== Announcements =====
CREATE TABLE IF NOT EXISTS announcements (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    body         TEXT DEFAULT '',
    category     TEXT DEFAULT '公告',
    url          TEXT DEFAULT '#',
    pinned       INTEGER DEFAULT 0,
    published_at DATE DEFAULT (date('now')),
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Default site config values (INSERT OR IGNORE = safe to re-run)
INSERT OR IGNORE INTO site_config (key, value) VALUES
  ('brand_name',          '妍菲天堂'),
  ('site_subtitle',       '天堂 II 私服官方網站'),
  ('hero_title',          '妍菲天堂'),
  ('hero_subtitle',       '重返榮耀，再創傳奇。最純粹的史詩冒險，正等待你的加入！'),
  ('hero_tags',           '1× 倍率,無商城干擾,公平競技,定期更新,GM 24H 在線'),
  ('hero_cta_primary',    '立即加入冒險'),
  ('hero_cta_secondary',  '進入資料庫'),
  ('server_status_text',  '伺服器運行中'),
  ('server_online_count', '872 人'),
  ('exp_rate',            '1×'),
  ('no_p2w_label',        '無付費優勢'),
  ('download_url',        '/download'),
  ('launcher_url',        '/download'),
  ('patch_url',           '/download'),
  ('guide_url',           '/guide'),
  ('discord_url',         '#discord'),
  ('forum_url',           '#forum'),
  ('line_group_url',      'https://line.me/ti/g2/IlKNIaRrZwDZAaABlz_6EBhtad-KMRNRg3aC0A?utm_source=invitation&utm_medium=link_copy&utm_campaign=default'),
  ('brand_slogan',        '精心打造的天堂 II 私服，還原經典、追求平衡。與志同道合的玩家一起書寫屬於你的傳奇篇章。'),
  ('final_cta_title',     '還在等什麼？'),
  ('final_cta_body',      '你的戰友正在亞丁大陸集結，立即下載遊戲，開啟屬於你的傳奇篇章！');

-- Sample announcements (INSERT OR REPLACE = safe to refresh curated defaults)
INSERT OR REPLACE INTO announcements (id, title, body, category, url, pinned, published_at) VALUES
  (1, '115.02.09 正式開服', '115.02.09 正式開服，歡迎大家加入妍菲天堂，一起回味最初的感動與熱血冒險。', '開服公告', '#', 1, '2026-03-13'),
  (2, '加入官方群組取得下載資訊', '遊戲主程式、補丁與最新消息將優先於 LINE 社群公告，請先加入官方群組取得第一手資訊。', '下載公告', 'https://line.me/ti/g2/IlKNIaRrZwDZAaABlz_6EBhtad-KMRNRg3aC0A?utm_source=invitation&utm_medium=link_copy&utm_campaign=default', 1, '2026-03-13'),
  (3, '每日 18:00 例行重啟', '為維持遊戲環境穩定，伺服器將於每日 18:00 進行例行重啟，請各位玩家提前下線，避免資料異常或進度中斷。', '維護公告', '#', 0, '2026-03-13'),
  (4, '活動預告', '【活動名稱】即將開跑，詳細活動內容與獎勵請鎖定官網與 LINE 社群公告。', '活動公告', '#', 0, '2026-03-13'),
  (5, '更新公告', '本次更新已完成【主要更新內容】，詳細調整請參考更新公告，祝各位玩家遊戲愉快。', '更新公告', '#', 0, '2026-03-13'),
  (6, '公平遊戲公告', '本服禁止使用外掛與不當程式，營運團隊將持續維護公平遊戲環境，敬請玩家共同遵守。', '系統公告', '#', 0, '2026-03-13');
