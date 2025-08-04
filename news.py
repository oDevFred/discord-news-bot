import requests
import feedparser
import logging
import sqlite3
from datetime import datetime
from database import Database

# Configurar logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

class NewsService:
    def __init__(self, db: Database, news_api_key: str):
        self.db = db
        self.news_api_key = news_api_key
        self.rss_feeds = {
            "tecnologia": "http://feeds.bbci.co.uk/news/technology/rss.xml",
            "games": "https://www.engadget.com/rss.xml",
            "ciberseguranca": "https://www.darkreading.com/rss.xml"
        }

    def fetch_news_api(self, topic: str, limit: int = 5) -> list:
        """Busca notícias da News API por tópico."""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": topic,
                "apiKey": self.news_api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": limit
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            news_list = [
                {
                    "title": article["title"],
                    "url": article["url"],
                    "topic": topic,
                    "published_at": article["publishedAt"]
                }
                for article in articles
            ]
            logging.info(f"Buscou {len(news_list)} notícias da News API para tópico {topic}")
            return news_list
        except requests.RequestException as e:
            logging.error(f"Erro ao buscar notícias da News API para {topic}: {e}")
            return []

    def fetch_rss_feed(self, topic: str, limit: int = 5) -> list:
        """Busca notícias de um feed RSS por tópico."""
        try:
            feed_url = self.rss_feeds.get(topic, "")
            if not feed_url:
                logging.warning(f"Nenhum feed RSS configurado para tópico {topic}")
                return []
            feed = feedparser.parse(feed_url)
            news_list = [
                {
                    "title": entry.title,
                    "url": entry.link,
                    "topic": topic,
                    "published_at": entry.get("published", datetime.now().isoformat())
                }
                for entry in feed.entries[:limit]
            ]
            logging.info(f"Buscou {len(news_list)} notícias do RSS para tópico {topic}")
            return news_list
        except Exception as e:
            logging.error(f"Erro ao buscar notícias do RSS para {topic}: {e}")
            return []

    def fetch_news(self, topic: str, limit: int = 5) -> list:
        """Busca notícias combinando News API e RSS, removendo duplicatas."""
        news_list = []
        if self.news_api_key:
            news_list.extend(self.fetch_news_api(topic, limit))
        if len(news_list) < limit:
            news_list.extend(self.fetch_rss_feed(topic, limit - len(news_list)))
        seen_urls = set()
        unique_news = [
            news for news in news_list
            if news["url"] not in seen_urls and not seen_urls.add(news["url"])
        ]
        return unique_news[:limit]

    def save_news(self, news_list: list) -> list:
        """Salva notícias no banco de dados e retorna os news_id."""
        news_ids = []
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for news in news_list:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO news (title, url, topic, published_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (news["title"], news["url"], news["topic"], news["published_at"])
                    )
                    if cursor.rowcount > 0:  # Nova notícia inserida
                        cursor.execute(
                            "SELECT news_id FROM news WHERE url = ?",
                            (news["url"],)
                        )
                        news_id = cursor.fetchone()["news_id"]
                        news_ids.append(news_id)
                conn.commit()
                logging.info(f"Salvas {len(news_list)} notícias no banco, IDs: {news_ids}")
                return news_ids
        except sqlite3.Error as e:
            logging.error(f"Erro ao salvar notícias: {e}")
            raise