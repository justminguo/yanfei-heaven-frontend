import streamlit as st
import pandas as pd
import requests
import json
import os

# 設置頁面配置
st.set_page_config(page_title="妍菲天堂 - 全能數據搜尋中心 v4.5", page_icon="🔍", layout="wide")

# API 基礎設定
BASE_URL = "https://yanfei-db-site.zeabur.app"
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
    .result-section {{
        background-color: #ffffff; border-left: 5px solid #004494;
        padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    .category-header {{ color: #004494; font-size: 1.3em; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #f0f0f0; }}
    </style>
    """, unsafe_allow_html=True)

# --- 資料讀取邏輯 (本地優先，API 備份) ---
@st.cache_data(ttl=300)
def load_all_data():
    all_data = {
        "weapons": [], "armors": [], "items": [], "monsters": [], "drops": []
    }
    
    # 嘗試從本地 JSON 讀取
    if os.path.exists(LOCAL_DATA_FILE):
        try:
            with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
                all_data.update(json.load(f))
        except: pass
    
    # 如果本地沒資料，嘗試連線 API
    if not any(all_data.values()):
        for key in all_data.keys():
            try:
                res = requests.get(f"{BASE_URL}/api/{key}", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    all_data[key] = data.get("rows", data) if isinstance(data, dict) else data
            except: pass
    
    return all_data

# --- 側邊欄 ---
st.sidebar.markdown('<div style="text-align:center;"><img src="https://static-s3.skyworkcdn.com/fe/skywork-site-assets/images/skybot/avatar2-new.png" width="80"></div>', unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align:center; color:white;'>妍菲天堂 v4.5</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{LINE_URL}" target="_blank" class="line-button">🟢 加入官方 LINE 社群</a>', unsafe_allow_html=True)

menu = st.sidebar.radio("🏛️ 官網導航入口", ["首頁入口", "🔍 全能快速搜尋", "✨ 特色系統介紹", "🎁 新手大禮包"])

# 載入資料
data_source = load_all_data()

if menu == "首頁入口":
    st.markdown('<div class="header-bar"><h1>🛡️ 妍菲天堂 - 官方數據資料中心</h1><p>2.0 經典仿正官方百科</p></div>', unsafe_allow_html=True)
    
    cols = st.columns(5)
    cols[0].metric("📦 物品", len(data_source.get("items", [])))
    cols[1].metric("👹 怪物", len(data_source.get("monsters", [])))
    cols[2].metric("💎 掉落", len(data_source.get("drops", [])))
    cols[3].metric("🗡️ 武器", len(data_source.get("weapons", [])))
    cols[4].metric("🛡️ 防具", len(data_source.get("armors", [])))
    
    st.image("https://static-s3.skyworkcdn.com/fe/skywork-site-assets/images/skybot/avatar2-new.png", caption="掃碼加入社群", width=200)

elif menu == "🔍 全能快速搜尋":
    st.markdown('<div class="header-bar"><h2>🔍 全能快速搜尋系統</h2><p>輸入一個關鍵字，同時檢索武器、防具、道具與怪物</p></div>', unsafe_allow_html=True)
    
    query = st.text_input("💡 請輸入要查詢的名稱 (例如：劍、黑豹、金幣...)", placeholder="在此輸入關鍵字...")
    
    if query:
        with st.spinner("正在檢索中..."):
            # --- 顯示武器結果 ---
            weapons = data_source.get("weapons", [])
            w_res = [w for w in weapons if query in str(w.get('name',''))]
            if w_res:
                st.markdown('<div class="category-header">🗡️ 武器相關結果</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(w_res), use_container_width=True)

            # --- 顯示防具結果 ---
            armors = data_source.get("armors", [])
            a_res = [a for a in armors if query in str(a.get('name',''))]
            if a_res:
                st.markdown('<div class="category-header">🛡️ 防具相關結果</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(a_res), use_container_width=True)

            # --- 顯示怪物結果 ---
            monsters = data_source.get("monsters", [])
            m_res = [m for m in monsters if query in str(m.get('name',''))]
            if m_res:
                st.markdown('<div class="category-header">👹 怪物圖鑑結果</div>', unsafe_allow_html=True)
                for mon in m_res[:10]:
                    with st.expander(f"Lv.{mon.get('level')} - {mon.get('name')}"):
                        st.write(f"HP: {mon.get('hp')} | MP: {mon.get('mp')} | AC: {mon.get('ac')}")

            # --- 顯示掉落結果 ---
            drops = data_source.get("drops", [])
            d_res = [d for d in drops if query in str(d.get('item_name','')) or query in str(d.get('monster_name',''))]
            if d_res:
                st.markdown('<div class="category-header">💰 掉落關聯結果</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(d_res), use_container_width=True)

            # --- 顯示其他道具 ---
            items = data_source.get("items", [])
            i_res = [i for i in items if query in str(i.get('name',''))]
            if i_res:
                st.markdown('<div class="category-header">🧪 其他道具/材料結果</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(i_res), use_container_width=True)
    else:
        st.info("請在上方輸入框輸入關鍵字開始搜尋。")

elif menu == "✨ 特色系統介紹":
    st.markdown('<div class="header-bar"><h2>✨ 妍菲天堂 - 獨家特色</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="result-section"><h3>🏺 聖物系統</h3><p>收集材料強化角色屬性。</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="result-section"><h3>🤖 智能自動練功</h3><p>上班族最愛，24小時穩定掛機。</p></div>', unsafe_allow_html=True)

elif menu == "🎁 新手大禮包":
    st.header("🎁 升級獎勵")
    st.table(pd.DataFrame({"目標等級": ["45", "52"], "元寶獎勵": ["5000", "10000"]}))

st.markdown("---")
st.markdown('<div style="text-align:center; color:#999;">© 2026 妍菲天堂 Lineage Portal v4.5 | 穩定引擎版</div>', unsafe_allow_html=True)
