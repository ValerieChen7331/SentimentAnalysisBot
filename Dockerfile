FROM python:3.10-slim

# 安裝系統相依套件
RUN apt-get update && \
    apt-get install -y chromium-driver chromium-browser && \
    rm -rf /var/lib/apt/lists/*

# 設定環境變數，避免 Streamlit 問答提示
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# 安裝 Python 依賴
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

EXPOSE 8501

# 啟動應用
CMD ["streamlit", "run", "streamlit_app.py"]