# llm_helper.py
import json
import re
from apis.llm_api import LLMAPI

# LLM 輔助工具類別
class LLMHelper:
    def __init__(self):
        # 設定使用的 LLM 模型與模式
        self.llm_option = "Gemma2:27b"
        self.mode = "內部LLM"

    def analyze_article(self, article: str) -> dict:
        """
        使用 LLM 對輸入新聞內容進行分析，回傳摘要、情緒判斷、NER 實體辨識結果。
        輸入: 單篇新聞文字 (str)，輸出: 字典格式 (dict)。
        """
        prompt = (
            "請根據以下新聞內容，同時產生：\n"
            "1. 新聞摘要（200 字內）\n"
            "2. 情緒判斷（正面、中性、負面擇一）\n"
            "3. 命名實體（包含人名、公司、地名，以逗號分隔）\n"
            "⚠️ 最後請務必以以下 JSON 格式輸出：\n"
            '{ "summary": "...", "sentiment": "...", "ner": "..." }\n\n'
            "以下為新聞內容：\n" + article
        )

        llm = LLMAPI().get_llm(self.mode, self.llm_option)
        response_text = llm.invoke(prompt)
        print("🧠 LLM 回傳原始結果：", response_text)

        # 嘗試解析 JSON 格式結果
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # 若 LLM 回傳格式不正確，嘗試從字串中提取 JSON
            cleaned_text = response_text.replace("\n", " ").replace("\r", "").strip()
            match = re.search(r'\{.*\}', cleaned_text)
            if match:
                try:
                    result = json.loads(match.group(0))
                except:
                    result = {"summary": "無法生成摘要", "sentiment": "未知", "ner": "無"}
            else:
                result = {"summary": "無法生成摘要", "sentiment": "未知", "ner": "無"}
        return result

    def generate_summary(self, articles: list, analyses: list) -> str:
        """
        整合多篇新聞及分析結果，請 LLM 產出 300 字內的輿情總結。
        輸入: articles (list), analyses (list)；輸出: 總結文字 (str)
        """
        combined_text = []
        for i, (article, analysis) in enumerate(zip(articles, analyses), start=1):
            block = (
                f"【第 {i} 則新聞】\n"
                f"標題：{article['title']}\n"
                f"日期：{article['publish_date']}\n"
                f"摘要：{analysis['summary']}\n"
                f"情緒：{analysis['sentiment']}\n"
                f"NER：{analysis['ner']}\n"
            )
            combined_text.append(block)

        prompt = (
            "以下為多篇新聞內容及 AI 分析結果，請綜合以下內容產出 300 字以內的輿情總結，"
            "並說明輿論趨勢及潛在風險：\n\n" + "\n\n".join(combined_text)
        )

        llm = LLMAPI().get_llm(self.mode, self.llm_option)
        response_text = llm.invoke(prompt)

        if response_text.startswith("查詢失敗"):
            return "⚠️ 無法生成摘要，請稍後再試。"

        return response_text

    def query_to_keywords(self, query: str) -> str:
        """
        將使用者輸入問題轉換為 1-3 個新聞搜尋用的關鍵字。
        輸入: query (str)；輸出: 關鍵字 (str)。
        """
        import streamlit as st
        prompt = f"""
        請根據以下使用者問題，產生 1-3 個最適合新聞搜尋的短關鍵字（逗號分隔），
        關鍵字應簡潔且代表主題重點。
        請以此格式回應：
        <qtkeywords> 關鍵字1, 關鍵字2, 關鍵字3 <qtkeywords>

        使用者輸入: {query}
        """

        llm = LLMAPI().get_llm(self.mode, self.llm_option)
        response_text = llm.invoke(prompt)
        print(f"🔎 LLM 關鍵字回應: {response_text}")

        match = re.search(r"<qtkeywords>\s*(.*?)\s*<qtkeywords>", response_text)
        if match:
            keywords_str = match.group(1)
            keywords_list = [kw.strip() for kw in re.split(r"[，,]", keywords_str)]
            print(f"✅ 關鍵字清單: {keywords_list}")
            return keywords_list[0]
        else:
            # 若無法符合格式，使用回傳文字前幾個字作為備用關鍵字
            fallback_keyword = response_text.strip().split('\n')[0][:10]
            print(f"⚠️ 使用 fallback keyword: {fallback_keyword}")
            st.warning(f"⚠️ LLM 回傳原始結果：{response_text}")
            return fallback_keyword or ""

    def is_semantic_search(self, query: str) -> bool:
        """
        判斷使用者問題是否適合新聞搜尋或輿情分析。
        只要 LLM 回覆 <is_ss> 區塊中沒有包含 'false'，就判定為 True。
        """
        prompt = f"""
        請根據以下使用者問題，判斷是否可能用於'新聞搜尋'或'輿情分析'，或是與科技新聞有關。
        大部分問題可通過，但與聊天者請拒答。
        請簡短說明原因，最後請用 <is_ss> True <is_ss> 或 <is_ss> False <is_ss> 格式回覆。
        ---
        使用者輸入: {query}
        """

        llm = LLMAPI().get_llm(self.mode, self.llm_option)
        response_text = llm.invoke(prompt).lower().strip()
        print(f"🔎 LLM 判斷回覆: {response_text}")

        # 從 LLM 回應中取出 <is_ss> 標籤區域文字
        match = re.search(r"<is_ss>\s*(.*?)\s*<is_ss>", response_text)
        if match:
            inside_tag = match.group(1).strip()
            # 只要沒有 false 字樣就回傳 True
            return "false" not in inside_tag.lower()

        # 若無標籤則預設 False
        return False
