# crawler_bnext.py
import urllib.parse
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from apis.news_database import NewsDatabase

# Bnext（數位時代）新聞爬蟲類別
class BnextNewsCrawler:
    def __init__(self, headless: bool = False):
        # 初始化設定
        self.headless = headless
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
        }
        self.db = NewsDatabase()  # 建立新聞資料庫物件

    def build_search_url(self, keyword: str) -> str:
        """
        輸入關鍵字並編碼後，回傳對應的數位時代搜尋 URL。
        輸入: keyword (str)，輸出: 搜尋結果 URL (str)
        """
        encoded_keyword = urllib.parse.quote(keyword.strip())
        return f"https://www.bnext.com.tw/gsearch?q={encoded_keyword}#gsc.tab=0&gsc.q={encoded_keyword}&gsc.sort="

    # 模擬人類行為（滑鼠移動以降低被封鎖風險）
    def simulate_human_behavior(self, driver):
        actions = ActionChains(driver)
        driver.execute_script("window.scrollTo(0, 0);")  # 滑到頁面頂部
        window_width = driver.execute_script("return window.innerWidth;")
        window_height = driver.execute_script("return window.innerHeight;")
        start_x = window_width // 2
        start_y = window_height // 2
        actions.move_by_offset(start_x, start_y).perform()

        for _ in range(5):
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            actions.move_by_offset(offset_x, offset_y)
        actions.perform()

    # 搜尋新聞標題與網址
    def search_news(self, keyword: str, max_results: int = 10) -> list:
        """
        根據關鍵字自動使用 Selenium 模擬搜尋，回傳包含標題與 URL 的新聞清單。
        輸入: keyword (str), max_results (int)；輸出: list of dict
        """
        search_url = self.build_search_url(keyword)

        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('window-size=1920x1080')
        options.add_argument("user-agent=" + self.headers['User-Agent'])

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(search_url)

        # 模擬滑鼠行為
        self.simulate_human_behavior(driver)
        time.sleep(random.uniform(3, 6))

        # 偵測是否出現 reCAPTCHA
        if "我是機器人" in driver.page_source or "reCAPTCHA" in driver.page_source:
            driver.save_screenshot("captcha_detected.png")
            driver.quit()
            raise Exception("⚠️ 偵測到 reCAPTCHA，請打開 captcha_detected.png 檢查！")

        # 等待搜尋結果出現
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.gsc-webResult .gsc-thumbnail-inside a.gs-title'))
        )

        # 擷取結果連結與標題
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

    # 擷取新聞詳細內容
    def fetch_article_content(self, article_url: str) -> dict:
        """
        根據傳入新聞 URL，擷取新聞標題、日期、內文等詳細資訊。
        輸入: article_url (str)；輸出: dict（包含 title, publish_date, content, url）
        """
        response = requests.get(article_url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 擷取標題
        title_tag = soup.find('h1', class_='article-title')
        if not title_tag:
            og_title = soup.find('meta', property='og:title')
            title = og_title['content'].strip() if og_title else "無法取得標題"
        else:
            title = title_tag.text.strip()

        # 擷取發布日期
        date_div = soup.find('div', class_='flex gap-4 text-sm items-center flex-wrap')
        if not date_div:
            date_div = soup.find('div', class_='flex gap-2 items-center text-sm text-gray-600')
        if date_div:
            publish_date = date_div.find('span').text.strip()
        else:
            meta_date = soup.find('meta', property='article:published_time')
            publish_date = meta_date['content'].split('T')[0] if meta_date else "未知日期"

        # 擷取文章內容
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

    # 儲存到資料庫
    def save_to_db(self, article_data: dict, analysis: dict):
        """
        將文章內容與 LLM 分析結果儲存至 SQLite 資料庫。
        輸入: article_data (dict), analysis (dict)
        """
        self.db.insert_news(article_data, analysis)
        print(f"✅ 已儲存到資料庫：{article_data['title']}")


if __name__ == '__main__':
    keyword = input("請輸入搜尋關鍵字（例如：AI 或 Agent）：").strip()
    crawler = BnextNewsCrawler(headless=False)  # 預設使用有頭模式，方便 debug

    print(f"\n正在搜尋「{keyword}」相關新聞...")
    try:
        search_results = crawler.search_news(keyword, max_results=10)

        if not search_results:
            print("⚠️ 沒有找到新聞，請嘗試其他關鍵字。")
        else:
            print(f"\n共找到 {len(search_results)} 篇新聞，開始抓取並儲存內容...\n")
            for idx, article in enumerate(search_results, start=1):
                detail = crawler.fetch_article_content(article['url'])
                print(f"第 {idx} 篇已完成儲存")
                print(f"標題：{detail['title']}")
                print(f"日期：{detail['publish_date']}")
                print(f"網址：{detail['url']}")
                print(f"內文（前 300 字）：\n{detail['content'][:300]}...")
                print("=" * 80)
    except Exception as e:
        print(str(e))
