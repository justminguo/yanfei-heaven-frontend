import streamlit as st
import pandas as pd
import json
import os

# 設置頁面配置
st.set_page_config(page_title="妍菲天堂 - 全能數據搜尋中心 v5.6", page_icon="🔍", layout="wide")

# API 基礎設定
LINE_URL = "https://line.me/ti/g2/IlKNIaRrZwDZAaABlz_6EBhtad-KMRNRg3aC0A?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
LOCAL_DATA_FILE = "data.json"

# --- 全站視覺強化鎖定 CSS v5.6 (徹底解決 Expander 與深色模式衝突) ---
st.markdown(f"""
    <style>
    /* 1. 全域背景與基礎文字 */
    html, body, [data-testid="stAppViewContainer"], .main {{
        background-color: #f8f9fa !important;
        color: #31333F !important;
    }}
    
    /* 2. 標題列 */
    .header-bar {{
        background: linear-gradient(90deg, #004494 0%, #0066cc 100%) !important;
        color: #ffffff !important; 
        padding: 25px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,68,148,0.2); text-align: center;
    }}
    .header-bar h1, .header-bar h2, .header-bar p {{ color: #ffffff !important; }}
    
    /* 3. 側邊欄 */
    [data-testid="stSidebar"] {{ background-color: #1c2331 !important; }}
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: #ffffff !important;
    }}
    
    /* 4. 強制鎖定 Expander (摺疊選單) 的文字顏色 (解決展開後字體變白問題) */
    /* 標題部分 */
    [data-testid="stExpander"] details summary p {{
        color: #004494 !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
    }}
    /* 展開後的內容部分 */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] b {{
        color: #31333F !important;
    }}
    
    /* 5. 修正 Metric (首頁數據) */
    [data-testid="stMetricLabel"] > div {{ color: #555555 !important; }}
    [data-testid="stMetricValue"] > div {{ color: #004494 !important; font-weight: bold !important; }}
    
    /* 6. 特色卡片 */
    .result-card {{
        background-color: #ffffff !important; 
        border-radius: 12px; padding: 20px; margin-bottom: 20px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 8px solid #004494;
    }}
    .result-card h3 {{ color: #004494 !important; }}
    .result-card p {{ color: #444444 !important; }}
    
    /* 7. 表格 */
    [data-testid="stTable"] {{ background-color: #ffffff !important; color: #31333F !important; }}
    [data-testid="stTable"] th {{ background-color: #f0f2f6 !important; color: #004494 !important; }}

    /* LINE 按鈕 */
    .line-button {{
        display: block; width: 100%; padding: 12px; background-color: #00b900;
        color: white !important; text-align: center; font-weight: bold;
        border-radius: 8px; text-decoration: none; margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 資料讀取 ---
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

data_source = load_all_data()

# --- 側邊欄 ---
st.sidebar.markdown('<div style="text-align:center;"><img src="https://static-s3.skyworkcdn.com/fe/skywork-site-assets/images/skybot/avatar2-new.png" width="80"></div>', unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align:center; color:white;'>妍菲天堂 v5.6</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{LINE_URL}" target="_blank" class="line-button">🟢 加入官方 LINE 社群</a>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 智能快速搜尋")
query = st.sidebar.text_input("輸入名稱或關鍵字：", placeholder="例如：劍、黑豹...", key="sidebar_search")

menu = st.sidebar.radio("🏛️ 導航入口", ["首頁入口", "✨ 特色系統介紹", "🎁 新手大禮包"])

# --- 主畫面邏輯 ---
if query:
    st.markdown(f'<div class="header-bar"><h2>🔍 快速搜尋中："{query}"</h2></div>', unsafe_allow_html=True)
    q = query.strip().lower()
    found_any = False

    # 武器區
    w_res = [w for w in data_source.get("weapons", []) if q in w.get('name','').lower()]
    if w_res:
        found_any = True
        st.markdown('<div style="color:#004494; font-size:1.5em; font-weight:bold; border-bottom:4px solid #004494; width:fit-content; margin-bottom:15px;">🗡️ 武器數據</div>', unsafe_allow_html=True)
        for w in w_res:
            with st.expander(f"【{w.get('hands','單手')}】{w.get('name')}", expanded=True):
                st.markdown(f"**名稱：{w.get('name')}**")
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"攻擊力: <br>**{w.get('dmg_small')}/{w.get('dmg_large')}**", unsafe_allow_html=True)
                c2.markdown(f"額外/命中: <br>**+{w.get('dmg_add',0)} / +{w.get('hit',0)}**", unsafe_allow_html=True)
                c3.markdown(f"材質/重量: <br>**{w.get('material')} / {w.get('weight')}**", unsafe_allow_html=True)
                c4.markdown(f"力量加成: <br>**+{w.get('str',0)}**", unsafe_allow_html=True)
                st.info(f"✨ 說明：{w.get('info', '暫無詳細描述')}")

    # 怪物區
    m_res = [m for m in data_source.get("monsters", []) if q in m.get('name','').lower()]
    if m_res:
        found_any = True
        st.markdown('<div style="color:#004494; font-size:1.5em; font-weight:bold; border-bottom:4px solid #004494; width:fit-content; margin-bottom:15px;">👹 怪物圖鑑</div>', unsafe_allow_html=True)
        for m in m_res:
            with st.expander(f"Lv.{m.get('level')} - {m.get('name')}", expanded=True):
                st.markdown(f"**名稱：{m.get('name')}**")
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"HP/MP: <br>**{m.get('hp')}/{m.get('mp')}**", unsafe_allow_html=True)
                c2.markdown(f"AC/經驗值: <br>**{m.get('ac')} / {m.get('exp')}**", unsafe_allow_html=True)
                c3.markdown(f"棲息地: <br>**{m.get('info')}**", unsafe_allow_html=True)
                mdrops = [d for d in data_source.get("drops", []) if d.get('monster_name') == m.get('name')]
                if mdrops:
                    st.write(f"💰 **掉落物：** " + ", ".join([f"{d.get('item_name')}({d.get('rate')})" for d in mdrops]))

    if not found_any:
        st.warning(f"搜尋不到與「{query}」相關的項目。")
    st.markdown("---")

# --- 分頁內容 ---
if menu == "首頁入口":
    if not query:
        st.markdown('<div class="header-bar"><h1>🛡️ 妍菲天堂 - 數據中心</h1><p>穩定、精準、即時的遊戲百科</p></div>', unsafe_allow_html=True)
    st.subheader("📊 伺服器數據概覽")
    cols = st.columns(5)
    cols[0].metric("📦 物品", len(data_source.get("items", [])) + len(data_source.get("weapons", [])))
    cols[1].metric("👹 怪物", len(data_source.get("monsters", [])))
    cols[2].metric("💎 掉落", len(data_source.get("drops", [])))
    cols[3].metric("🗡️ 武器", len(data_source.get("weapons", [])))
    cols[4].metric("🛡️ 防具", len(data_source.get("armors", [])))
    if not query:
        st.image("https://static-s3.skyworkcdn.com/fe/skywork-site-assets/images/skybot/avatar2-new.png", width=200)

elif menu == "✨ 特色系統介紹":
    st.markdown('<div class="header-bar"><h2>✨ 妍菲天堂 - 獨家特色系統</h2></div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="result-card">
            <h3>🏺 聖物系統</h3>
            <p>透過收集特定的怪物材料，玩家可以強化專屬聖物，獲得永久屬性加成。</p>
        </div>
        <div class="result-card">
            <h3>🤖 智能自動練功</h3>
            <p>專為上班族設計，提供最穩定的掛機環境。智能判斷回城補給。</p>
        </div>
    """, unsafe_allow_html=True)

elif menu == "🎁 新手大禮包":
    st.markdown('<div class="header-bar"><h2>🎁 新手福利與衝等獎勵</h2></div>', unsafe_allow_html=True)
    st.table(pd.DataFrame({
        "目標等級": ["45 級", "52 級", "60 級", "70 級"], 
        "獎勵內容": ["5,000 元寶", "10,000 元寶", "神之飾品袋", "傳說武器箱"]
    }))

st.markdown("---")
st.markdown('<div style="text-align:center; color:#999;">© 2026 妍菲天堂 v5.6 | 搜尋視覺修正版</div>', unsafe_allow_html=True)
