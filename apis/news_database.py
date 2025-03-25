#  news_database.py
import sqlite3

# 新聞資料庫管理類別
class NewsDatabase:
    def __init__(self, db_name="./data/news_all.db"):
        """
        建構函式，初始化資料庫。
        輸入：db_name (str) - SQLite 資料庫檔案名稱。
        """
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """
        建立資料表（若尚未存在），包含新聞標題、日期、內容、URL 及分析欄位。
        無輸入 / 無輸出，執行資料表初始化。
        """
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS news (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            publish_date TEXT,
                            content TEXT,
                            url TEXT,
                            summary TEXT,
                            sentiment TEXT,
                            ner TEXT
                        )''')
            conn.commit()

    def insert_news(self, article_data, analysis):
        """
        將新聞資料及分析結果插入資料庫。
        輸入：article_data (dict)、analysis (dict)；無輸出。
        """
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO news "
                      "(title, publish_date, content, url, summary, sentiment, ner) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (article_data['title'], article_data['publish_date'], article_data['content'],
                       article_data['url'], analysis["summary"], analysis["sentiment"], analysis["ner"]))
            conn.commit()

    def search_news(self, keyword: str, date_from: str, date_to: str):
        """
        根據關鍵字與日期範圍搜尋新聞，回傳前 10 筆結果。
        輸入：keyword (str)、date_from (str)、date_to (str)；輸出：list (搜尋結果清單)。
        """
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""SELECT title, publish_date, content, url FROM news 
                         WHERE content LIKE ? AND publish_date BETWEEN ? AND ?
                         ORDER BY publish_date DESC LIMIT 10""",
                      (f"%{keyword}%", date_from, date_to))
            return c.fetchall()
