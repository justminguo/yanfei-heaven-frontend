"""CSV 匯入占位腳本。

之後可把 381 的 etcitem / npc / droplist 匯成 CSV，丟進 data/imports/，
再依實際欄位 mapping 補這支腳本。
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IMPORT_DIR = BASE_DIR / 'data' / 'imports'

print('Placeholder only. Put exported CSV files under:', IMPORT_DIR)
print('Expected later files: etcitem.csv / npc.csv / droplist.csv')
