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

CREATE TABLE IF NOT EXISTS dolls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    doll_type   TEXT NOT NULL,
    bonus_value INTEGER NOT NULL,
    note        TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS polymorphs (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    polyid  INTEGER NOT NULL,
    note    TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dolls_type ON dolls(doll_type);
CREATE INDEX IF NOT EXISTS idx_polymorphs_name ON polymorphs(name);
CREATE INDEX IF NOT EXISTS idx_polymorphs_polyid ON polymorphs(polyid);
