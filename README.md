# 新聞輿情分析聊天機器人

## 📌 專案簡介
本專案是一個專為「輿情分析」打造的聊天機器人與新聞分析平台。
它結合本地部署大型語言模型（LLM）與即時新聞爬蟲，能根據使用者提出的問題：
- 自動爬取「數位時代」新聞網站的相關新聞
- 進行新聞內容摘要、情緒分析、命名實體辨識（NER）
- 綜合多篇新聞產出輿情總結
- 支援 SQLite 本地資料庫儲存與查詢

⚠️ 本平台僅回應與輿情分析相關問題，若為無關問題將適當拒答。
影片連結: https://drive.google.com/drive/folders/1p7Ccy189vC_j33v-KGm1js9Pyw8XuE9l?usp=drive_link

---

## 📂 專案目錄
```
├── 📄 streamlit_app.py         # Streamlit 前端應用主程式
├── 📄 bnext_news_crawler.py    # 數位時代新聞爬蟲模組
├── 📄 llm_helper.py            # 串接本地 LLM、輿情分析邏輯
├── 📄 on_premises_llm.py       # 本地 LLM API 呼叫封裝
├── 📄 news_database.py         # 本地新聞資料庫操作
├── news_all.db              # SQLite 資料庫（範例）
├── requirements.txt         # Python 依賴列表
└── Dockerfile               # Docker 部署設定
```

---

## 🔎 主要功能

### 1️⃣ 聊天機器人功能
- 僅回答輿情分析相關問題
- 自動將使用者問題轉換為搜尋關鍵字

### 2️⃣ 網路新聞爬取
- 自動搜尋「數位時代」新聞網站
- 同時可搜尋 1~10 則新聞並批次爬取詳細內容

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

## 🚀 快速開始

### 1️⃣ 安裝依賴
```bash
pip install -r requirements.txt
```

### 2️⃣ 啟動本地 LLM (請先確認 Ollama 已在本地端啟動)
- API URL 與模型設定可在 `on_premises_llm.py` 修改

### 3️⃣ 啟動 Streamlit 應用
```bash
streamlit run streamlit_app.py
```

### 4️⃣ 使用方式
- 輸入輿情相關問題
- 自動爬取、分析新聞並產出摘要、NER、情緒判斷與綜合報告
- 查看或篩選儲存的歷史新聞記錄
---.
## 📧 聯絡
如需協助或有任何問題，請透過 GitHub Issue 提出！
valerie7331@gmail.com
