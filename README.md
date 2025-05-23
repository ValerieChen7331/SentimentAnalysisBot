# 📡 新聞輿情分析聊天機器人

## 📌 專案簡介
本專案是一個專為「輿情分析」打造的聊天機器人與新聞分析平台。
它結合本地部署大型語言模型（LLM）與即時新聞爬蟲，能根據使用者提出的問題：
- 自動爬取「數位時代」新聞網站的相關新聞
- 進行新聞內容摘要、情緒分析、命名實體辨識（NER）
- 綜合多篇新聞產出輿情總結
- 支援 SQLite 本地資料庫儲存與查詢
- 影片連結: 
![Demo Video](01_SentimentAnalysisBot_20250325.gif)

⚠️ 本平台僅回應與輿情分析相關問題，若為無關問題將適當拒答。

---

## 🚀 執行步驟

### 1️⃣ 安裝依賴
```bash
pip install -r requirements.txt
```

### 2️⃣ 啟動本地 LLM (請先確認 Ollama 已在本地端啟動)
- API URL 與模型設定可在 `llm_api.py` 和 `env` 修改

### 3️⃣ 啟動 Streamlit 應用
```bash
streamlit run streamlit_app.py
```

### 4️⃣ 使用方式
- 輸入輿情相關問題
- 自動爬取、分析新聞並產出摘要、NER、情緒判斷與綜合報告
- 查看或篩選儲存的歷史新聞記錄

---

## ✅ 主要功能

### 1️⃣ 聊天機器人功能
- 僅回答輿情分析相關問題
- 自動將使用者問題轉換為搜尋關鍵字

### 2️⃣ 網路新聞爬取
- 自動搜尋「數位時代」新聞網站
- 可搜尋 1~10 則新聞並批次爬取詳細內容

### 3️⃣ 輿情分析 (透過本地 LLM)
- 自動生成新聞摘要（200 字以內）
- 情緒判斷（正面 / 中性 / 負面）
- 命名實體辨識（人名 / 公司 / 地名）
- 綜合多篇新聞產出輿情摘要及風險提示

### 4️⃣ 本地資料儲存與查詢
- 使用 SQLite 儲存新聞全文、分析結果
- 可透過前端介面關鍵字搜尋最近 30 天新聞

---

## 🛠️ 技術架構
| 元件               | 技術                                    |
|--------------------|-----------------------------------------|
| 前端介面          | Streamlit                               |
| 爬蟲工具          | Selenium + BeautifulSoup                |
| 本地語言模型（LLM）| Ollama API，支援本地模型（Taiwan-Llama3）|
| 資料庫            | SQLite                                  |


---

## 📈 流程圖  
![workflow](workflow.png)  
[workflow](https://www.canva.com/design/DAGip48-pIo/bx9DFPr341IQno54AC2TyQ/view?utm_content=DAGip48-pIo&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=hb127ce56f4)

---

## 📂 專案結構

* 避免耦合: 📄 streamlit_app.py ➡ 📂 models ➡ 📂 apis
```
SentimentAnalysisBot/
📄 streamlit_app.py  ➡ 主應用程式入口，可呼叫 models
│
├─ 📂 models/        ➡ 邏輯層，例如爬取新聞，可以呼叫 apis 功能  
│   ├─ 📄 crawler_bnext.py      # 專職 Bnext 爬蟲邏輯  
│   └─ 📄 llm_helper.py         # 專職 LLM 分析工具（摘要、情緒判斷、NER）  
│
├─ 📂 apis/          ➡ 最底層工具層，封裝（LLM / SQLite）的 API 呼叫  
│   ├─ 📄 llm_api.py            # 提供本地 LLM / Azure OpenAI 模型存取介面  
│   └─ 📄 news_database.py      # 提供 SQLite 資料庫存取方法  
│
├─ 📂 data/          ➡ 純資料儲存層（資料庫或檔案）  
│   └─ news_all.db              # 爬取結果與分析結果的儲存  
│
├─ .env                         # 環境變數設定（API Key、URL 等）  
├─ Dockerfile                   # Docker 容器建置設定  
├─ requirements.txt             # Python 相依套件版本清單  
└─ README.md                    # 專案介紹與使用說明文件  
```
---

## 📧 聯絡
如需協助或有任何問題，請透過 GitHub Issue 提出！
valerie7331@gmail.com
