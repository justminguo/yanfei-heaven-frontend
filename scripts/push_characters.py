#!/usr/bin/env python3
"""
私服蝦端執行：從本地 MySQL 讀玩家資料，推送到前端網站。
使用方式：
  python push_characters.py \
    --mysql-host 127.0.0.1 --mysql-user root --mysql-password xxxx --mysql-db lineage \
    --api-url https://yanfei.zeabur.app/api/push/characters \
    --token yanfei-push-secret
可加入 cron 定期執行，例如每 30 分鐘：
  */30 * * * * python /path/to/push_characters.py ...
"""

import argparse
import json
import sys
try:
    import pymysql
    import urllib.request
except ImportError:
    print("需要安裝 pymysql: pip install pymysql")
    sys.exit(1)


def fetch_characters(host, user, password, db_name, port=3306):
    conn = pymysql.connect(host=host, user=user, password=password,
                           database=db_name, port=port, charset="utf8")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT char_id, account_name, char_name, level, class, online
            FROM characters
            ORDER BY level DESC
            LIMIT 1000
        """)
        rows = cur.fetchall()
    conn.close()
    return [
        {
            "char_id": r[0],
            "account_name": r[1] or "",
            "char_name": r[2] or "",
            "level": r[3] or 1,
            "class": r[4] or 0,
            "OnlineStatus": r[5] or 0,
        }
        for r in rows
    ]


def push(api_url, token, characters):
    payload = json.dumps({"token": token, "characters": characters}).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mysql-host", default="127.0.0.1")
    parser.add_argument("--mysql-user", default="root")
    parser.add_argument("--mysql-password", required=True)
    parser.add_argument("--mysql-db", default="lineage")
    parser.add_argument("--mysql-port", type=int, default=3306)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()

    print("從 MySQL 讀取玩家資料...")
    chars = fetch_characters(args.mysql_host, args.mysql_user,
                             args.mysql_password, args.mysql_db, args.mysql_port)
    print(f"讀到 {len(chars)} 筆，推送中...")
    result = push(args.api_url, args.token, chars)
    print(f"結果：{result}")


if __name__ == "__main__":
    main()
