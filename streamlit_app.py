# streamlit_app.py
# 提供新聞自動搜尋、LLM 分析、儲存及歷史紀錄查詢功能
import streamlit as st
import datetime
from apis.news_database import NewsDatabase
from models.llm_helper import LLMHelper
from models.crawler_bnext import BnextNewsCrawler

# 初始化本地 SQLite 資料庫
db = NewsDatabase()
# 顯示 Streamlit 首頁標題
st.title("📡 新聞輿情分析平台")
# 建立分頁介面（分成搜尋與歷史）
tab_search, tab_history = st.tabs(["🔎 搜尋新聞", "📂 已儲存新聞"])

def process_single_article(idx: int, article_detail: dict, llm_helper, crawler) -> dict:
    """
    分析單篇新聞，並於介面中顯示結果，同時儲存到資料庫。
    """
    analysis = llm_helper.analyze_article(article_detail['content'])
    crawler.save_to_db(article_detail, analysis)  # 儲存結果到資料庫

    # 將結果展開在畫面上
    with st.expander(f"【第 {idx} 篇】 {article_detail['publish_date']} - {article_detail['title']}"):
        st.write(f"🔗 [前往原文]({article_detail['url']})")
        st.write(article_detail['content'][:200] + "...")
        st.write("**📄 LLM 摘要**:", analysis["summary"])
        st.write("**😊 情緒判斷**:", analysis["sentiment"])
        st.write("**🏷️ 命名實體**:", analysis["ner"])
    return analysis


def handle_search():
    """
    1. 處理使用者輸入，確認是否適合輿情分析，
    2. 將問題透過 LLM 轉成搜尋關鍵字、爬取新聞、分析並綜合結果。
    """
    st.header("🔎 從『數位時代』自動搜尋並分析")
    crawler = BnextNewsCrawler(headless=True)  # 初始化新聞爬蟲
    llm_helper = LLMHelper()  # 初始化 LLM 輔助工具

    # 輸入欄位
    with st.form(key="search_form"):
        user_query = st.text_input("請輸入新聞主題或問題...").strip()
        start_search = st.form_submit_button("搜尋")

    # 使用者點及搜尋
    if start_search:
        # 驗證輸入問題是否適合輿情分析
        with st.spinner(f"🔎 驗證中..."):
            is_search = llm_helper.is_semantic_search(user_query)
        if not is_search:
            st.warning("⚠️ 此問題不適合輿情分析，請換個描述")
            return

        # 使用 LLM 將問題轉換成搜尋用的關鍵字
        with st.spinner(f"🔎 正在解析出有效關鍵字..."):
            keyword = llm_helper.query_to_keywords(user_query)
        if not keyword:
            st.warning("⚠️ LLM 無法解析出有效關鍵字，請換個描述再試")
            return

        # 使用關鍵字開始新聞搜尋
        with st.spinner(f"🔎 正在搜尋「{keyword}」新聞..."):
            articles = crawler.search_news(keyword, max_results=3)
        if not articles:
            st.error("❗ 沒有找到相關新聞，請嘗試其他關鍵字")
            return

        # 擷取每篇新聞詳細內容
        with st.spinner(f"🔎 抓取相關新聞..."):
            article_details = [crawler.fetch_article_content(article['url']) for article in articles]
        st.success(f"✅ 成功抓取 {len(article_details)} 篇新聞")

        # 對每篇新聞進行分析與畫面展示
        analyses = []
        for idx, article_detail in enumerate(article_details, start=1):
            with st.spinner(f"🧠 正在分析第 {idx} 篇新聞..."):
                analysis = process_single_article(idx, article_detail, llm_helper, crawler)
                analyses.append(analysis)

        # 綜合產出輿情摘要
        with st.spinner("🧠 正在綜合產出輿情摘要..."):
            summary = llm_helper.generate_summary(article_details, analyses)
            st.subheader("📢 綜合輿情摘要")
            st.write(summary)


def show_history():
    """
    顯示最近 30 天內已儲存新聞記錄，並可透過關鍵字篩選。
    """
    st.header("📂 瀏覽已儲存新聞")
    keyword_filter = st.text_input("🔎 可輸入關鍵字篩選（留空則顯示全部）").strip()
    today = datetime.date.today()
    past_30_days = today - datetime.timedelta(days=30)

    # 從資料庫中查詢新聞
    saved_news = db.search_news(keyword=keyword_filter, date_from=str(past_30_days), date_to=str(today))

    if not saved_news:
        st.info("⚠️ 沒有符合條件的新聞記錄")
        return

    st.info(f"📚 最近 30 天內共 {len(saved_news)} 篇新聞：")
    for title, date, content, url in saved_news:
        with st.expander(f"{date} - {title}"):
            st.write(content[:300] + "...")
            st.write(f"👉 [前往原文]({url})")


# Streamlit 執行主流程
if __name__ == "__main__":
    with tab_search:
        handle_search()

    with tab_history:
        show_history()
