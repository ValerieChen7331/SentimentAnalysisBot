FROM python:3.11.11

# 安裝系統套件與 Chromium 瀏覽器及其 Driver
RUN apt-get update && \
    apt-get install -y wget gnupg unzip curl \
                       chromium chromium-driver \
                       fonts-liberation libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libx11-xcb1 && \
    rm -rf /var/lib/apt/lists/*

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    CHROME_BIN=/usr/bin/chromium \
    PATH=$PATH:/usr/bin

# 設定工作目錄
WORKDIR /app

# 複製依賴並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案所有檔案
COPY . .

# 開放 Streamlit 預設埠
EXPOSE 8501

# 啟動 Streamlit 應用
CMD ["streamlit", "run", "streamlit_app.py"]
