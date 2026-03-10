# 🚀 妍菲天堂 - Zeabur 部署指南

我已經為您的「妍菲天堂」查詢網站準備好了所有必要檔案。請按照以下步驟在 Zeabur 上完成發布：

### 1. 準備檔案 (已在您的 workspace 生成)
*   **`app.py`**: 網頁主程式 (Streamlit)
*   **`requirements.txt`**: 運行環境依賴
*   **`Dockerfile`**: (新增) 用於更穩定地部署
*   **`yanfei_deploy.tar.gz`**: (新增) 懶人包，可直接下載並上傳到 Zeabur

### 2. 部署到 Zeabur
1.  **登入 Zeabur 控制台**: [https://zeabur.com/](https://zeabur.com/)
2.  **建立新專案 (Create Project)**: 選擇一個區域 (如 Singapore 或 Tokyo)。
3.  **部署方式 (Deploy Service)**:
    *   **方式 A (推薦)**: 將這三個檔案上傳到您的 GitHub Repo，然後在 Zeabur 連結該 Repo。
    *   **方式 B (Zip 上傳)**: 將 `yanfei_deploy.tar.gz` 下載後，在 Zeabur Dashboard 直接拖拽上傳。
4.  **設定啟動指令 (Start Command)** (若使用方式 B 且未偵測到):
    在服務設定中找到 **"Start Command"**，輸入：
    ```bash
    streamlit run app.py --server.port 8080 --server.address 0.0.0.0 --browser.gatherUsageStats false
    ```
5.  **綁定網域 (Domain)**:
    在 **"Networking"** 標籤下點擊 **"Generate Domain"**，即可獲得一個公開網址 (例如 `yanfei.zeabur.app`)。

---

### 🛡️ 未來與 Windows MySQL 對接
一旦您的 Windows Node 配對成功，我會幫您更新 `app.py`，加入遠端讀取指令，讓網頁資料與遊戲資料庫即時同步！

**如果您在 Zeabur 部署過程中遇到任何問題（例如報錯或連線失敗），請隨時告訴我！**
