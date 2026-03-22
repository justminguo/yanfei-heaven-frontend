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
  --host <YOUR_SERVER_IP> \
  --ssh-user <SSH_USER> \
  --ssh-key /path/to/key \
  --mysql-user <MYSQL_USER> \
  --mysql-password <MYSQL_PASSWORD> \
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
