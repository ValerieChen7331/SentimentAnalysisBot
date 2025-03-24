import streamlit as st
from news_database import NewsDatabase
from llm_helper import LLMHelper
from bnext_news_crawler import BnextNewsCrawler
import datetime

# 增加記憶功能，記得資料
# 應僅回答與輿情分析相關的問題，對於無關問題應適當拒答。

# 初始化 SQLite 資料庫
db = NewsDatabase()

# 標題
st.title("📡 新聞輿情分析平台")

# 建立分頁
tab1, tab2 = st.tabs(["🔎 搜尋新聞", "📂 已儲存新聞"])

# === Tab1: 自動搜尋 + 自動分析 ===
with tab1:
    st.header("🔎 從『數位時代』自動搜尋並分析")
    crawler = BnextNewsCrawler(headless=True)

    # 使用 form 支援 Enter 觸發
    with st.form(key="search_form"):
        query = st.text_input("請輸入新聞主題或問題...").strip()
        submit_button = st.form_submit_button("搜尋")  # 按 Enter 或按此按鈕都可以觸發

    if submit_button:
        # 透過 LLM 抽取最適搜尋關鍵字
        keyword = LLMHelper.query_to_keywords(query)
        if not keyword:
            st.warning("⚠️ LLM 無法解析出有效關鍵字，請換個描述試試。")
        else:
            with st.spinner(f"🔎 正在搜尋「{keyword}」新聞..."):
                search_results = crawler.search_news(keyword, max_results=3)

            if not search_results:
                st.error("❗ 沒有找到新聞，請換其他關鍵字。")
            else:
                all_details = []

                # ✅ 第 1 步：先批次抓取詳細文章內容
                with st.spinner(f"🔎 正在爬蟲「{keyword}」新聞..."):
                    for idx, article in enumerate(search_results, start=1):
                        detail = crawler.fetch_article_content(article['url'])
                        all_details.append(detail)
                # ✅ 爬蟲完成後才提示「開始分析」
                st.success(f"✅ 已成功抓取 {len(all_details)} 篇新聞")

                all_analyses = []

                # ✅ 第 2 步：逐篇進行 LLM 分析
                for idx, detail in enumerate(all_details, start=1):
                    with st.spinner(f"🧠 分析第 {idx} 篇新聞中..."):
                        analysis = LLMHelper.analyze_article(detail['content'])
                        crawler.save_to_db(detail, analysis)  # 同步儲存至資料庫
                        all_analyses.append(analysis)

                    # 顯示每篇新聞分析結果
                    with st.expander(f"【第 {idx} 篇】 {detail['publish_date']} - {detail['title']}"):
                        st.write(f"🔗 [前往原文]({detail['url']})")
                        st.write(detail['content'][:200] + "...")
                        st.write("**📄 LLM 摘要**:", analysis["summary"])
                        st.write("**😊 情緒判斷**:", analysis["sentiment"])
                        st.write("**🏷️ 命名實體**:", analysis["ner"])

                # ✅ 第 3 步：綜合多篇新聞產出輿情總結
                with st.spinner("🧠 正在生成綜合輿情摘要..."):
                    all_news_summary = LLMHelper.generate_summary(all_details, all_analyses)
                    st.subheader("📢 綜合輿情摘要")
                    st.write(all_news_summary)

# === Tab2: 查看已儲存新聞 ===
with tab2:
    st.header("📂 瀏覽已儲存新聞")
    keyword_filter = st.text_input("🔎 可輸入關鍵字篩選（留空顯示全部）").strip()
    today = datetime.date.today()
    past_30_days = today - datetime.timedelta(days=30)

    saved_news = db.search_news(
        keyword=keyword_filter,
        date_from=str(past_30_days),
        date_to=str(today)
    )

    if saved_news:
        st.info(f"📚 最近 30 天共 {len(saved_news)} 篇已儲存新聞：")
        for idx, record in enumerate(saved_news, start=1):
            with st.expander(f"{record[1]} - {record[0]}"):
                st.write(record[2][:300] + "...")
                st.write(f"👉 [前往原文連結]({record[3]})")
    else:
        st.info("⚠️ 沒有符合條件的新聞記錄。")
