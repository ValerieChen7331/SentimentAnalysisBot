import json
from typing import List
from on_premises_llm import OnPremisesLLM
import re

class LLMHelper:
    @staticmethod
    def analyze_article(article: str) -> dict:
        """
        一次性丟給 LLM，取得摘要、情緒分析、命名實體辨識 (NER)
        :param article: 新聞內文字串
        :return: dict 格式結果
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

        llm_instance = OnPremisesLLM()
        response_text = llm_instance.on_premises_llm("Taiwan-Llama3-16f", prompt)
        print("🧠 LLM 回傳原始結果：", response_text)

        # JSON 解析與自動修復
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
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

    @staticmethod
    def generate_summary(articles: list, analyses: list) -> str:
        """
        將多篇新聞和分析結果綜合交給 LLM，產出 300 字以內輿情摘要
        :param articles: list of dicts，包含 title, publish_date, content
        :param analyses: list of dicts，包含 summary, sentiment, ner
        :return: LLM 產出摘要
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

        llm_instance = OnPremisesLLM()
        response_text = llm_instance.on_premises_llm("Taiwan-Llama3-16f", prompt)

        if response_text.startswith("查詢失敗"):
            return "⚠️ 無法生成摘要，請稍後再試。"

        return response_text

    @staticmethod
    def query_to_keywords(query: str) -> str:
        """
        將自然語言問題轉換為 1-3 個搜尋用關鍵字
        """
        prompt = f"""
        請根據以下使用者問題，產生 1-3 個最適合新聞搜尋的短關鍵字（逗號分隔），
        關鍵字應簡潔且代表主題重點。
        請以此格式回應：
        <qtkeywords> 關鍵字1, 關鍵字2, 關鍵字3 <qtkeywords>

        使用者輸入: {query}
        """

        llm_instance = OnPremisesLLM()
        response_text = llm_instance.on_premises_llm("Taiwan-Llama3-16f", prompt)
        print(f"🔎 LLM 關鍵字回應: {response_text}")

        match = re.search(r"<qtkeywords>\s*(.*?)\s*<qtkeywords>", response_text)
        if match:
            keywords_str = match.group(1)
            keywords_list = [kw.strip() for kw in re.split(r"[，,]", keywords_str)]
            return keywords_list[0]  # 回傳第一組關鍵字
        else:
            return ""
