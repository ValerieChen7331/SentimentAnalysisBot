# llm_api.py
from dotenv import load_dotenv
import os
from langchain_openai import AzureChatOpenAI
from langchain_community.llms import Ollama

# LLM API 工具類別，根據模式提供內部或外部 LLM 實例
class LLMAPI:
    @staticmethod
    def get_llm(mode, llm_option):
        """
        根據傳入的模式 (mode) 及模型選項 (llm_option)，
        返回內部 Ollama 模型或外部 Azure OpenAI 模型實例。
        輸入：mode (str)、llm_option (str)；輸出：LLM 實例。
        """
        if mode == '內部LLM':
            return LLMAPI._get_internal_llm(llm_option)
        else:
            return LLMAPI._get_external_llm(llm_option)

    @staticmethod
    def _get_internal_llm(llm_option):
        """
        建立並回傳內部 LLM (透過 Ollama API) 實例。
        輸入：llm_option (str) 模型代稱；輸出：Ollama LLM 實例。
        """
        api_base = "http://10.5.61.81:11437"  # 內部 Ollama API 伺服器位址

        # 可用的內部模型清單
        llm_model_names = {
            "Taiwan-Llama3-16f": "cwchang/llama-3-taiwan-8b-instruct:f16",
            "Gemma2:27b": "gemma2:27b-instruct-q5_0",
        }

        # 根據傳入模型選項取得實際模型名稱
        model = llm_model_names.get(llm_option)
        if not model:
            raise ValueError(f"無效的內部模型選項：{llm_option}")

        # 使用 Ollama API 建立並回傳 LLM 實例
        llm = Ollama(base_url=api_base, model=model)
        return llm

    @staticmethod
    def _get_external_llm(llm_option):
        """
        建立並回傳外部 Azure OpenAI 的 LLM 實例。
        輸入：llm_option (str) 為 Azure 上部署名稱；輸出：AzureChatOpenAI LLM 實例。
        """
        deployment_name = llm_option
        load_dotenv()  # 載入 .env 設定檔

        # 從環境變數中取得 Azure API 設定參數
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        # 確認必要參數存在
        if not all([api_key, api_base, api_version]):
            raise ValueError("缺少 API Key、Endpoint 或 API Version")

        # 建立並回傳 AzureChatOpenAI LLM 實例
        llm = AzureChatOpenAI(
            openai_api_key=api_key,
            azure_endpoint=api_base,
            api_version=api_version,
            deployment_name=deployment_name
        )
        return llm


if __name__ == "__main__":
    # 範例測試：呼叫內部 LLM 並回覆結果
    llm = LLMAPI.get_llm("內部LLM", "Taiwan-Llama3-16f")
    # 呼叫 LLM 進行範例對話
    result = llm.invoke([
        {"role": "user", "content": "我要如何設定自動寄送的警報信？"}
    ])
    # 顯示回傳結果
    print(result)