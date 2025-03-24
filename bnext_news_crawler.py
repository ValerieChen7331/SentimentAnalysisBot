# -*- coding: utf-8 -*-
import urllib.parse
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from news_database import NewsDatabase  # 匯入本地資料庫類別
from llm_helper import LLMHelper

class BnextNewsCrawler:
    """
    數位時代新聞爬蟲類別：
    - 使用 Selenium 搜尋新聞標題與 URL
    - 使用 requests + BeautifulSoup 抓取新聞內容
    - 可儲存到本地 SQLite
    """

    def __init__(self, headless: bool = True):
        """
        初始化爬蟲設定
        :param headless: 是否以無頭模式執行 (預設True)
        """
        self.headless = headless
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
        }
        self.db = NewsDatabase()  # 同時建立資料庫連線物件

    def build_search_url(self, keyword: str) -> str:
        """
        組合搜尋 URL
        """
        if keyword.strip():
            encoded_keyword = urllib.parse.quote(keyword.strip())
            return f"https://www.bnext.com.tw/gsearch?q={encoded_keyword}#gsc.tab=0&gsc.q={encoded_keyword}&gsc.sort="
        else:
            return "https://www.bnext.com.tw/gsearch?#gsc.tab=0"

    def search_news(self, keyword: str, max_results: int = 10) -> list:
        """
        使用 Selenium 搜尋新聞並取得前 max_results 筆結果
        :return: list 包含 {title, url}
        """
        search_url = self.build_search_url(keyword)

        # 設定 Chrome 參數
        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument("user-agent=" + self.headers['User-Agent'])

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(search_url)
        time.sleep(3)

        # 等待搜尋結果元素出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.gsc-webResult .gsc-thumbnail-inside a.gs-title'))
        )

        result_elements = driver.find_elements(By.CSS_SELECTOR, '.gsc-webResult .gsc-thumbnail-inside a.gs-title')
        urls = []
        for elem in result_elements:
            href = elem.get_attribute('href')
            title = elem.text.strip()
            if href and title:
                urls.append({'title': title, 'url': href})
            if len(urls) >= max_results:
                break

        driver.quit()
        return urls

    def fetch_article_content(self, article_url: str) -> dict:
        """
        擷取文章詳細內容（標題、日期、內文）
        """
        response = requests.get(article_url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 標題 (優先找 h1，如果沒有則從 meta 裡找)
        title_tag = soup.find('h1', class_='article-title')
        if not title_tag:
            og_title = soup.find('meta', property='og:title')
            title = og_title['content'].strip() if og_title else "無法取得標題"
        else:
            title = title_tag.text.strip()

        # 發佈日期，多層 fallback
        date_div = soup.find('div', class_='flex gap-4 text-sm items-center flex-wrap')
        if not date_div:
            date_div = soup.find('div', class_='flex gap-2 items-center text-sm text-gray-600')
        if date_div:
            publish_date = date_div.find('span').text.strip()
        else:
            meta_date = soup.find('meta', property='article:published_time')
            publish_date = meta_date['content'].split('T')[0] if meta_date else "未知日期"

        # 文章內容
        content_div = soup.find('div', class_='article-content')
        if content_div:
            paragraphs = content_div.find_all('p')
            content = '\n'.join(p.text.strip() for p in paragraphs)
        else:
            content = "無法取得內文"

        return {
            "title": title,
            "publish_date": publish_date,
            "content": content,
            "url": article_url
        }

    def save_to_db(self, article_data: dict, analysis: dict):
        """
        將單篇文章資料儲存到本地資料庫
        """
        self.db.insert_news(article_data, analysis)
        print(f"✅ 已儲存到資料庫：{article_data['title']}")


if __name__ == '__main__':
    keyword = input("請輸入搜尋關鍵字（例如：AI 或 Agent）：").strip()
    crawler = BnextNewsCrawler(headless=True)

    print(f"\n正在搜尋「{keyword}」相關新聞...")
    search_results = crawler.search_news(keyword, max_results=10)

    if not search_results:
        print("⚠️ 沒有找到新聞，請嘗試其他關鍵字。")
    else:
        print(f"\n共找到 {len(search_results)} 篇新聞，開始抓取並儲存內容...\n")
        for idx, article in enumerate(search_results, start=1):
            detail = crawler.fetch_article_content(article['url'])
            analysis = LLMHelper.analyze_article(detail['content'])
            crawler.save_to_db(detail, analysis)
            print(f"第 {idx} 篇已完成儲存")
            print(f"標題：{detail['title']}")
            print(f"日期：{detail['publish_date']}")
            print(f"網址：{detail['url']}")
            print(f"內文（前 300 字）：\n{detail['content'][:300]}...")
            print("=" * 80)
