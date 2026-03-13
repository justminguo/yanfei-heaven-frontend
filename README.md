# yanfei-db-site

妍菲天堂資料查詢站 MVP。

## 第一版功能
- 物品查詢
- 怪物查詢
- 掉落查詢
- 怪物詳情 + 掉落列表
- 物品詳情 + 掉落來源

## 技術棧
- Flask
- SQLite
- Gunicorn
- Docker（可直接丟 Zeabur）

## 本地執行
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_sample.py
python app.py
```

開啟 <http://127.0.0.1:5000>

## 資料庫位置
預設 SQLite：`data/yanfei.db`

可用環境變數覆蓋：
```bash
export YANFEI_DB_PATH=/absolute/path/to/yanfei.db
```

## 之後怎麼接 381 的資料
目前先用 SQLite 作為雲端只讀資料庫。

後續建議流程：
1. 從 Windows 本機 MySQL `381` 匯出 `etcitem` / `npc` / `droplist`
2. 轉成 CSV 或 SQL dump
3. 用 `scripts/import_from_csv.py`（之後補完）匯入 SQLite，或直接跑 `scripts/sync_from_windows_mysql.py`
4. Zeabur 網站直接查 SQLite

## 直接從 Windows MySQL 381 同步
```bash
python scripts/sync_from_windows_mysql.py \
  --host 211.20.245.169 \
  --ssh-user user \
  --ssh-key /path/to/key \
  --mysql-user root \
  --mysql-password root \
  --mysql-db 381
```

同步完成後可再用：
```bash
python scripts/deploy_zeabur_upload.py \
  --api-key <ZEABUR_API_KEY> \
  --service-id <SERVICE_ID> \
  --environment-id <ENV_ID>
```

## 對應關聯
- `items.id` ← `381.etcitem.item_id`
- `monsters.id` ← `381.npc.npcid`
- `monster_drops.monster_id` ← `381.droplist.mobId`
- `monster_drops.item_id` ← `381.droplist.itemId`

## 在線人數顯示

首頁在線人數欄位使用以下 SQL 即時查詢：

```sql
SELECT COUNT(*) FROM characters WHERE OnlineStatus = 1
```

查詢對象為同一 SQLite 資料庫中的 `characters` 資料表。若該資料表不存在（例如尚未從遊戲伺服器同步），會自動回退顯示 `site_config` 表中的 `server_online_count` 設定值，不會造成頁面錯誤。

**部署注意事項：**
- 若需顯示真實在線人數，需將遊戲伺服器 MySQL 中的 `characters` 表（含 `OnlineStatus` 欄位）同步至此 SQLite。
- 若使用靜態資料庫（僅道具/怪物查詢），在線人數會永遠顯示 `site_config.server_online_count` 的值（預設 `872 人`），可在資料庫中更新此設定。

### 如何同步真實在線人數（characters 表）

`sync_from_windows_mysql.py` 支援 `--mysql-char-db` 與 `--char-style` 兩個參數來控制角色資料庫同步。

#### 步驟一：確認伺服器端資料庫名稱

在 Windows MySQL 執行（可透過 SSH 登入後執行）：

```sql
SHOW DATABASES;
-- 找到包含 characters 表的資料庫（常見名稱：lin2user、l1jdb、lineage、lin、user）

USE <你的資料庫名稱>;
SHOW TABLES;
SHOW COLUMNS FROM characters;
-- 確認欄位名稱，判斷是 L2J 還是 L1J 格式
```

#### 步驟二：選擇正確的 `--char-style`

| 伺服器類型 | level 欄位 | class 欄位 | online 欄位 | `--char-style` |
|-----------|-----------|-----------|------------|----------------|
| Lineage 2 Java (L2J) / L2OFF | `level` | `base_class` | `online` | `l2j` |
| Lineage 1 Java (L1J / 381) | `Lev` | `classtype` | `OnlineStatus` | `l1j` |

#### 步驟三：執行同步

**已知資料庫名稱（推薦）：**
```bash
python scripts/sync_from_windows_mysql.py \
  --host 211.20.245.169 \
  --ssh-user user \
  --ssh-key /path/to/key \
  --mysql-db 381 \
  --mysql-char-db l1jdb \
  --char-style l1j
```

**不確定資料庫名稱（自動探查）：**
```bash
# 省略 --mysql-char-db 即啟動自動探查模式
# 依序嘗試：lin2user、l1jdb、lineage、lin、user
python scripts/sync_from_windows_mysql.py \
  --host 211.20.245.169 \
  --ssh-user user \
  --ssh-key /path/to/key \
  --mysql-db 381 \
  --char-style l1j
```

**略過角色同步（只同步道具/怪物/掉落）：**
```bash
python scripts/sync_from_windows_mysql.py \
  --host 211.20.245.169 \
  --ssh-user user \
  --ssh-key /path/to/key \
  --mysql-db 381 \
  --mysql-char-db none
```

#### 診斷輸出說明

同步時會顯示每次嘗試的結果：

```
Starting character sync (char-db='l1jdb', style='l1j') ...
  [char-sync] Trying DB='l1jdb'  style='l1j' ... OK — 1234 rows
  [char-sync] SUCCESS: 1234 characters from l1jdb.characters [l1j columns]
```

若失敗，腳本會印出具體的診斷指令與建議動作，不會靜默忽略。

## Zeabur 部署
專案已加上 `Dockerfile`，可用 Docker 型服務部署。
容器啟動命令：
```bash
gunicorn -w 2 -b 0.0.0.0:${PORT} app:app
```

健康檢查：
- `/healthz`

## JSON API
- `/api/stats`
- `/api/items?q=&item_type=&limit=`
- `/api/item/<id>`
- `/api/monsters?q=&min_level=&max_level=&limit=`
- `/api/monster/<id>`
- `/api/drops?q=&monster_id=&item_id=&limit=`
- `/api/weapons?q=&limit=`
- `/api/weapon/<id>`
- `/api/armors?q=&limit=`
- `/api/armor/<id>`
