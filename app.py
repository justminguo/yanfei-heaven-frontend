import streamlit as st
import pandas as pd
import json
import os

# 設置頁面配置
st.set_page_config(page_title="妍菲天堂 - 全能數據搜尋中心 v5.2", page_icon="🔍", layout="wide")

# API 基礎設定
LINE_URL = "https://line.me/ti/g2/IlKNIaRrZwDZAaABlz_6EBhtad-KMRNRg3aC0A?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
LOCAL_DATA_FILE = "data.json"

# --- 自定義 CSS ---
st.markdown(f"""
    <style>
    .main {{ background-color: #f0f2f5; color: #333; font-family: 'Microsoft JhengHei', sans-serif; }}
    .header-bar {{
        background: linear-gradient(90deg, #004494 0%, #0066cc 100%);
        color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
    }}
    [data-testid="stSidebar"] {{ background-color: #1c2331 !important; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
        color: #ffffff !important; font-weight: 700 !important;
    }}
    .line-button {{
        display: block; width: 100%; padding: 12px; background-color: #00b900;
        color: white !important; text-align: center; font-weight: bold;
        border-radius: 8px; text-decoration: none; margin-bottom: 15px;
    }}
    .result-card {{
        background-color: #ffffff; border-radius: 8px; padding: 15px; 
        margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #004494;
    }}
    .category-header {{ color: #004494; font-size: 1.4em; font-weight: bold; margin-top: 20px; margin-bottom: 10px; border-bottom: 3px solid #004494; width: fit-content; }}
    .stat-label {{ color: #666; font-size: 0.9em; }}
    .stat-value {{ font-weight: bold; color: #004494; font-size: 1.1em; }}
    </style>
    """, unsafe_allow_html=True)

# --- 資料讀取邏輯 (不緩存以確保即時性) ---
def load_all_data():
    all_data = {"weapons": [], "armors": [], "items": [], "monsters": [], "drops": []}
    if os.path.exists(LOCAL_DATA_FILE):
        try:
            with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                all_data.update(loaded)
        except Exception as e:
            st.error(f"資料讀取錯誤: {e}")
    return all_data

# --- 側邊欄 ---
st.sidebar.markdown('<div style="text-align:center;"><img src="https://static-s3.skyworkcdn.com/fe/skywork-site-assets/images/skybot/avatar2-new.png" width="80"></div>', unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align:center; color:white;'>妍菲天堂 v5.2</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{LINE_URL}" target="_blank" class="line-button">🟢 加入官方 LINE 社群</a>', unsafe_allow_html=True)

# 把搜尋框放到側邊欄，隨時都能搜
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 智能快速搜尋")
query = st.sidebar.text_input("輸入名稱或關鍵字：", placeholder="例如：劍、黑豹...", key="sidebar_search")

menu = st.sidebar.radio("🏛️ 導航入口", ["首頁入口", "✨ 特色系統介紹", "🎁 新手大禮包"])

data_source = load_all_data()

# 顯示載入狀態（Debug 用，點開可看）
with st.sidebar.expander("📊 資料庫狀態 (管理員)"):
    st.write(f"武器: {len(data_source.get('weapons', []))}")
    st.write(f"防具: {len(data_source.get('armors', []))}")
    st.write(f"怪物: {len(data_source.get('monsters', []))}")
    st.write(f"掉落: {len(data_source.get('drops', []))}")

# --- 主畫面顯示邏輯 ---
if query:
    st.markdown(f'<div class="header-bar"><h2>🔍 搜尋結果："{query}"</h2><p>系統已為您匹配到以下數據</p></div>', unsafe_allow_html=True)
    q = query.strip().lower()
    found_any = False

    # 武器區
    w_res = [w for w in data_source.get("weapons", []) if q in w.get('name','').lower()]
    if w_res:
        found_any = True
        st.markdown('<div class="category-header">🗡️ 武器數據</div>', unsafe_allow_html=True)
        for w in w_res:
            with st.expander(f"【{w.get('hands','單手')}】{w.get('name')}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"<span class='stat-label'>攻擊力:</span> <span class='stat-value'>{w.get('dmg_small')}/{w.get('dmg_large')}</span>", unsafe_allow_html=True)
                c2.markdown(f"<span class='stat-label'>額外/命中:</span> <span class='stat-value'>+{w.get('dmg_add',0)} / +{w.get('hit',0)}</span>", unsafe_allow_html=True)
                c3.markdown(f"<span class='stat-label'>材質/重量:</span> <span class='stat-value'>{w.get('material')} / {w.get('weight')}</span>", unsafe_allow_html=True)
                c4.markdown(f"<span class='stat-label'>力量加成:</span> <span class='stat-value'>+{w.get('str',0)}</span>", unsafe_allow_html=True)
                st.info(f"✨ 說明：{w.get('info', '暫無詳細描述')}")

    # 防具區
    a_res = [a for a in data_source.get("armors", []) if q in a.get('name','').lower()]
    if a_res:
        found_any = True
        st.markdown('<div class="category-header">🛡️ 防禦數據</div>', unsafe_allow_html=True)
        for a in a_res:
            with st.expander(f"【防具】{a.get('name')}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<span class='stat-label'>防禦力 (AC):</span> <span class='stat-value'>{a.get('ac')}</span>", unsafe_allow_html=True)
                c2.markdown(f"<span class='stat-label'>材質:</span> <span class='stat-value'>{a.get('material')}</span>", unsafe_allow_html=True)
                c3.markdown(f"<span class='stat-label'>力量/其他:</span> <span class='stat-value'>+{a.get('str',0)}</span>", unsafe_allow_html=True)
                st.info(f"✨ 說明：{a.get('info', '暫無詳細描述')}")

    # 怪物區
    m_res = [m for m in data_source.get("monsters", []) if q in m.get('name','').lower()]
    if m_res:
        found_any = True
        st.markdown('<div class="category-header">👹 怪物圖鑑</div>', unsafe_allow_html=True)
        for m in m_res:
            with st.expander(f"Lv.{m.get('level')} - {m.get('name')}", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<span class='stat-label'>HP/MP:</span> <span class='stat-value'>{m.get('hp')}/{m.get('mp')}</span>", unsafe_allow_html=True)
                c2.markdown(f"<span class='stat-label'>AC/經驗值:</span> <span class='stat-value'>{m.get('ac')} / {m.get('exp')}</span>", unsafe_allow_html=True)
                c3.markdown(f"<span class='stat-label'>棲息地:</span> <span class='stat-value'>{m.get('info')}</span>", unsafe_allow_html=True)
                mdrops = [d for d in data_source.get("drops", []) if d.get('monster_name') == m.get('name')]
                if mdrops:
                    st.write("💰 **掉落物：** " + ", ".join([f"{d.get('item_name')}({d.get('rate')})" for d in mdrops]))

    # 道具區
    i_res = [i for i in data_source.get("items", []) if q in i.get('name','').lower()]
    if i_res:
        found_any = True
        st.markdown('<div class="category-header">📦 道具與材料</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(i_res), use_container_width=True)

    if not found_any:
        st.warning(f"抱歉，資料庫中找不到與「{query}」相關的項目。請換個關鍵字試試看！")
        st.info("提示：目前資料庫中包含 瑟魯基之劍、細劍、黑豹、金幣 等範例數據。")

else:
    # 正常導航頁面
    if menu == "首頁入口":
        st.markdown('<div class="header-bar"><h1>🛡️ 妍菲天堂 - 數據中心</h1><p>穩定、精準、即時的遊戲百科</p></div>', unsafe_allow_html=True)
        cols = st.columns(5)
        cols[0].metric("📦 物品", len(data_source.get("items", [])) + len(data_source.get("weapons", [])))
        cols[1].metric("👹 怪物", len(data_source.get("monsters", [])))
        cols[2].metric("💎 掉落", len(data_source.get("drops", [])))
        cols[3].metric("🗡️ 武器", len(data_source.get("weapons", [])))
        cols[4].metric("🛡️ 防具", len(data_source.get("armors", [])))
        st.markdown("### 📢 公告板")
        st.success("✨ 2026/03/10 數據搜尋系統 v5.2 已修復連線問題，並新增側邊欄快速搜尋！")
        st.image("https://static-s3.skyworkcdn.com/fe/skywork-site-assets/images/skybot/avatar2-new.png", width=200)

    elif menu == "✨ 特色系統介紹":
        st.markdown('<div class="header-bar"><h2>✨ 獨家特色系統</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="result-card"><h3>🏺 聖物系統</h3><p>收集怪物材料強化角色屬性。</p></div>', unsafe_allow_html=True)

    elif menu == "🎁 新手大禮包":
        st.header("🎁 衝等獎勵")
        st.table(pd.DataFrame({"目標等級": ["45", "52", "60"], "獎勵": ["5000 元寶", "10000 元寶", "神之飾品袋"]}))

st.markdown("---")
st.markdown('<div style="text-align:center; color:#999;">© 2026 妍菲天堂 v5.2 | 極速搜尋穩定版</div>', unsafe_allow_html=True)
