from langchain_community.llms import Ollama


# 本地部署 LLM 呼叫類別
class OnPremisesLLM:
    def __init__(self):
        """
        建構函式：設定本地 LLM API 的 base_url 與模型名稱對應表
        """
        # 本地 LLM API 伺服器的 URL
        self.api_base = "http://10.5.61.81:11436"


        # 模型名稱對應表，將自訂名稱映射到實際模型 ID
        self.llm_model_names = {
            "Gemma2:27b": "gemma2:27b-instruct-q5_0",
            "deepseek-r1:32b": "deepseek-r1:32b",
            "Taiwan-Llama3-16f": "cwchang/llama-3-taiwan-8b-instruct-dpo:f16"
        }

    def on_premises_llm(self, model_name: str, query: str) -> str:
        """
        呼叫指定模型進行推論
        :param model_name: 預設使用者輸入的模型代稱
        :param query: 要送給模型的 prompt (問題或指令)
        :return: 模型回應文字
        """
        try:
            # 透過映射字典取得模型名稱
            model = self.llm_model_names.get(model_name)

            # 建立 LLM 客戶端物件
            llm = Ollama(base_url=self.api_base, model=model)

            # 呼叫模型執行推論
            return llm.invoke(query)
        except Exception as e:
            # 如果出現錯誤，回傳錯誤訊息字串
            return f"查詢失敗: {str(e)}"
