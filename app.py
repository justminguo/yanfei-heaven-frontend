import streamlit as st
import pandas as pd
import json
import os

# 設置頁面配置
st.set_page_config(page_title="妍菲天堂 - 全能數據搜尋中心 v5.4", page_icon="🔍", layout="wide")

# API 基礎設定
LINE_URL = "https://line.me/ti/g2/IlKNIaRrZwDZAaABlz_6EBhtad-KMRNRg3aC0A?utm_source=invitation&utm_medium=link_copy&utm_campaign=default"
LOCAL_DATA_FILE = "data.json"

# --- 自定義 CSS (強化顏色對比，防止白底白字) ---
st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{ background-color: #f8f9fa; }}
    
    .main {{ color: #333333; font-family: 'Microsoft JhengHei', sans-serif; }}
    
    /* 頂部標題列 */
    .header-bar {{
        background: linear-gradient(90deg, #004494 0%, #0066cc 100%);
        color: #ffffff !important; padding: 25px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,68,148,0.2); text-align: center;
    }}
    .header-bar h1, .header-bar h2, .header-bar p {{
        color: #ffffff !important; margin: 0;
    }}
    
    /* 側邊欄樣式 */
    [data-testid="stSidebar"] {{ background-color: #1c2331 !important; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
        color: #ffffff !important; font-weight: 700 !important;
    }}
    
    /* LINE 按鈕 */
    .line-button {{
        display: block; width: 100%; padding: 12px; background-color: #00b900;
        color: white !important; text-align: center; font-weight: bold;
        border-radius: 8px; text-decoration: none; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,185,0,0.2);
    }}
    
    /* 特色系統卡片 (強制設定文字顏色) */
    .result-card {{
        background-color: #ffffff !important; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        border-left: 8px solid #004494;
    }}
    .result-card h3 {{ 
        color: #004494 !important; 
        margin-top: 0; 
        font-weight: bold;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }}
    .result-card p {{ 
        color: #444444 !important; 
        line-height: 1.6;
        font-size: 1.1em;
    }}
    
    /* 搜尋結果類別標題 */
    .category-header {{ 
        color: #004494; 
        font-size: 1.5em; 
        font-weight: bold; 
        margin-top: 30px; 
        margin-bottom: 15px; 
        border-bottom: 4px solid #004494; 
        width: fit-content; 
        padding-right: 20px;
    }}
    
    /* 數據卡片欄位標籤 */
    .stat-label {{ color: #777777; font-size: 0.95em; }}
    .stat-value {{ font-weight: bold; color: #004494; font-size: 1.2em; }}
    </style>
    """, unsafe_allow_html=True)

# --- 資料讀取邏輯 ---
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
st.sidebar.markdown("<h2 style='text-align:center; color:white;'>妍菲天堂 v5.4</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{LINE_URL}" target="_blank" class="line-button">🟢 加入官方 LINE 社群</a>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 智能快速搜尋")
query = st.sidebar.text_input("輸入名稱或關鍵字：", placeholder="例如：劍、黑豹...", key="sidebar_search")

menu = st.sidebar.radio("🏛️ 導航入口", ["首頁入口", "✨ 特色系統介紹", "🎁 新手大禮包"])

with st.sidebar.expander("📊 資料庫狀態 (管理員)"):
    st.write(f"武器: {len(data_source.get('weapons', []))}")
    st.write(f"防具: {len(data_source.get('armors', []))}")
    st.write(f"怪物: {len(data_source.get('monsters', []))}")

# --- 主畫面邏輯 ---
if query:
    st.markdown(f'<div class="header-bar"><h2>🔍 快速搜尋中："{query}"</h2></div>', unsafe_allow_html=True)
    q = query.strip().lower()
    found_any = False

    # 搜尋結果區塊
    search_container = st.container()
    with search_container:
        # 武器區
        w_res = [w for w in data_source.get("weapons", []) if q in w.get('name','').lower()]
        if w_res:
            found_any = True
            st.markdown('<div class="category-header">🗡️ 武器數據</div>', unsafe_allow_html=True)
            for w in w_res:
                with st.expander(f"【{w.get('hands','單手')}】{w.get('name')}", expanded=True):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"<span class='stat-label'>攻擊力:</span> <br><span class='stat-value'>{w.get('dmg_small')}/{w.get('dmg_large')}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span class='stat-label'>額外/命中:</span> <br><span class='stat-value'>+{w.get('dmg_add',0)} / +{w.get('hit',0)}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span class='stat-label'>材質/重量:</span> <br><span class='stat-value'>{w.get('material')} / {w.get('weight')}</span>", unsafe_allow_html=True)
                    c4.markdown(f"<span class='stat-label'>力量加成:</span> <br><span class='stat-value'>+{w.get('str',0)}</span>", unsafe_allow_html=True)
                    st.info(f"✨ 說明：{w.get('info', '暫無詳細描述')}")

        # 防具區
        a_res = [a for a in data_source.get("armors", []) if q in a.get('name','').lower()]
        if a_res:
            found_any = True
            st.markdown('<div class="category-header">🛡️ 防禦數據</div>', unsafe_allow_html=True)
            for a in a_res:
                with st.expander(f"【防具】{a.get('name')}", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<span class='stat-label'>防禦力 (AC):</span> <br><span class='stat-value'>{a.get('ac')}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span class='stat-label'>材質:</span> <br><span class='stat-value'>{a.get('material')}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span class='stat-label'>力量/其他:</span> <br><span class='stat-value'>+{a.get('str',0)}</span>", unsafe_allow_html=True)
                    st.info(f"✨ 說明：{a.get('info', '暫無詳細描述')}")

        # 怪物區
        m_res = [m for m in data_source.get("monsters", []) if q in m.get('name','').lower()]
        if m_res:
            found_any = True
            st.markdown('<div class="category-header">👹 怪物圖鑑</div>', unsafe_allow_html=True)
            for m in m_res:
                with st.expander(f"Lv.{m.get('level')} - {m.get('name')}", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<span class='stat-label'>HP/MP:</span> <br><span class='stat-value'>{m.get('hp')}/{m.get('mp')}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span class='stat-label'>AC/經驗值:</span> <br><span class='stat-value'>{m.get('ac')} / {m.get('exp')}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span class='stat-label'>棲息地:</span> <br><span class='stat-value'>{m.get('info')}</span>", unsafe_allow_html=True)
                    mdrops = [d for d in data_source.get("drops", []) if d.get('monster_name') == m.get('name')]
                    if mdrops:
                        st.write("💰 **掉落物：** " + ", ".join([f"{d.get('item_name')}({d.get('rate')})" for d in mdrops]))

    if not found_any:
        st.warning(f"搜尋不到與「{query}」相關的項目。")
    st.markdown("---")

# --- 目錄分頁內容 ---
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
            <p>透過收集特定的怪物材料，玩家可以強化專屬聖物，獲得永久性的力量、敏捷或魔法加成。不同階段的聖物將呈現不同特效，是展現強大實力的象徵。</p>
        </div>
        <div class="result-card">
            <h3>🤖 智能自動練功</h3>
            <p>專為上班族玩家設計，提供最穩定的掛機環境。智能判斷回城補給、自動販賣垃圾物品，讓您在忙碌之餘也能穩步提升角色等級。</p>
        </div>
        <div class="result-card">
            <h3>🗡️ 裝備覺醒系統</h3>
            <p>達到指定等級後，部分頂級武器可透過覺醒石進行二次強化，解鎖隱藏的命中與傷害屬性，讓您的角色在戰場上所向披靡。</p>
        </div>
    """, unsafe_allow_html=True)

elif menu == "🎁 新手大禮包":
    st.markdown('<div class="header-bar"><h2>🎁 新手福利與衝等獎勵</h2></div>', unsafe_allow_html=True)
    st.info("💡 提示：等級獎勵將在角色達到指定等級後，自動發送至遊戲內信箱。")
    st.table(pd.DataFrame({
        "目標等級": ["45 級", "52 級", "60 級", "70 級"], 
        "獎勵內容": ["5,000 元寶 + 新手藥水包", "10,000 元寶 + 英雄變身卷軸", "神之飾品袋 + 強化武卷", "傳說武器箱(限時) + 傲慢之塔傳送卷"]
    }))

st.markdown("---")
st.markdown('<div style="text-align:center; color:#999;">© 2026 妍菲天堂 v5.4 | 視覺優化穩定版</div>', unsafe_allow_html=True)
