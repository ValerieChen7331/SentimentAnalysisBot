import sqlite3

# 資料庫管理類別
class NewsDatabase:
    def __init__(self, db_name="news_all.db"):
        """
        建構函式，初始化資料庫
        :param db_name: SQLite 資料庫檔案名稱
        """
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """
        建立資料表（若尚未存在）
        """
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 建立 news 資料表，包括 id、標題、日期、內容、URL
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
        將新聞資料插入資料庫
        :param article_data: 字典格式新聞資料（title, publish_date, content, url）
        """
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 將新聞資料插入到資料表中
            c.execute("INSERT INTO news "
                      "(title, publish_date, content, url, summary, sentiment, ner) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (article_data['title'], article_data['publish_date'], article_data['content'],
                       article_data['url'], analysis["summary"], analysis["sentiment"], analysis["ner"]))
            conn.commit()

    def search_news(self, keyword: str, date_from: str, date_to: str):
        """
        根據關鍵字與日期範圍搜尋新聞
        :param keyword: 要搜尋的關鍵字
        :param date_from: 搜尋的開始日期 (YYYY-MM-DD)
        :param date_to: 搜尋的結束日期 (YYYY-MM-DD)
        :return: 搜尋結果（標題、日期、內容、URL）
        """
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 執行 SQL 查詢，篩選出符合條件的前 10 筆新聞
            c.execute("""SELECT title, publish_date, content, url FROM news 
                         WHERE content LIKE ? AND publish_date BETWEEN ? AND ?
                         ORDER BY publish_date DESC LIMIT 10""",
                      (f"%{keyword}%", date_from, date_to))
            return c.fetchall()
