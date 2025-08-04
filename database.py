import sqlite3
import logging
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

class Database:
    def __init__(self, db_name="news.db"):
        self.db_name = db_name
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Gerencia a conexão com o banco de dados."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Inicializa o banco de dados e cria as tabelas."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        user_id INTEGER,
                        topic TEXT NOT NULL,
                        PRIMARY KEY (user_id, topic),
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS news (
                        news_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        published_at TEXT,
                        message_id INTEGER
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS votes (
                        news_id INTEGER,
                        user_id INTEGER,
                        vote_type TEXT NOT NULL,  -- 'upvote' ou 'star'
                        PRIMARY KEY (news_id, user_id),
                        FOREIGN KEY (news_id) REFERENCES news(news_id),
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                conn.commit()
                logging.info("Banco de dados inicializado com sucesso.")
        except sqlite3.Error as e:
            logging.error(f"Erro ao inicializar o banco de dados: {e}")
            raise

    def add_user(self, user_id: int, username: str):
        """Adiciona um usuário ao banco."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)",
                    (user_id, username)
                )
                conn.commit()
                logging.info(f"Usuário {username} ({user_id}) adicionado.")
        except sqlite3.Error as e:
            logging.error(f"Erro ao adicionar usuário {user_id}: {e}")
            raise

    def add_subscription(self, user_id: int, topic: str):
        """Adiciona uma assinatura de tópico para um usuário."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO subscriptions (user_id, topic) VALUES (?, ?)",
                    (user_id, topic)
                )
                conn.commit()
                logging.info(f"Assinatura de {topic} adicionada para usuário {user_id}.")
        except sqlite3.Error as e:
            logging.error(f"Erro ao adicionar assinatura para usuário {user_id}: {e}")
            raise

    def get_subscriptions(self, user_id: int) -> list:
        """Retorna a lista de tópicos assinados por um usuário."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT topic FROM subscriptions WHERE user_id = ?",
                    (user_id,)
                )
                topics = [row["topic"] for row in cursor.fetchall()]
                logging.info(f"Tópicos recuperados para usuário {user_id}: {topics}")
                return topics
        except sqlite3.Error as e:
            logging.error(f"Erro ao recuperar assinaturas para usuário {user_id}: {e}")
            raise

    def remove_subscription(self, user_id: int, topic: str):
        """Remove uma assinatura de tópico de um usuário."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM subscriptions WHERE user_id = ? AND topic = ?",
                    (user_id, topic)
                )
                conn.commit()
                logging.info(f"Assinatura de {topic} removida para usuário {user_id}.")
        except sqlite3.Error as e:
            logging.error(f"Erro ao remover assinatura para usuário {user_id}: {e}")
            raise

    def update_news_message_id(self, news_id: int, message_id: int):
        """Atualiza o message_id de uma notícia no banco."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE news SET message_id = ? WHERE news_id = ?",
                    (message_id, news_id)
                )
                conn.commit()
                logging.info(f"Message ID {message_id} atualizado para notícia {news_id}.")
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar message_id para notícia {news_id}: {e}")
            raise

    def add_vote(self, news_id: int, user_id: int, vote_type: str):
        """Adiciona ou atualiza um voto para uma notícia."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO votes (news_id, user_id, vote_type) VALUES (?, ?, ?)",
                    (news_id, user_id, vote_type)
                )
                conn.commit()
                logging.info(f"Voto {vote_type} adicionado para notícia {news_id} por usuário {user_id}.")
        except sqlite3.Error as e:
            logging.error(f"Erro ao adicionar voto para notícia {news_id} por usuário {user_id}: {e}")
            raise

    def get_votes(self, news_id: int) -> list:
        """Retorna a lista de votos para uma notícia."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, vote_type FROM votes WHERE news_id = ?",
                    (news_id,)
                )
                votes = [{"user_id": row["user_id"], "vote_type": row["vote_type"]} for row in cursor.fetchall()]
                logging.info(f"Votos recuperados para notícia {news_id}: {votes}")
                return votes
        except sqlite3.Error as e:
            logging.error(f"Erro ao recuperar votos para notícia {news_id}: {e}")
            raise

    def get_top_voted_news(self, topics: list, limit: int = 5) -> list:
        """Retorna as notícias mais votadas para os tópicos especificados."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT n.news_id, n.title, n.url, n.topic, n.published_at, 
                           COUNT(v.vote_type) as vote_count
                    FROM news n
                    LEFT JOIN votes v ON n.news_id = v.news_id
                    WHERE n.topic IN ({})
                    GROUP BY n.news_id
                    ORDER BY vote_count DESC, n.published_at DESC
                    LIMIT ?
                """
                placeholders = ",".join("?" for _ in topics)
                cursor.execute(query.format(placeholders), topics + [limit])
                news = [
                    {
                        "news_id": row["news_id"],
                        "title": row["title"],
                        "url": row["url"],
                        "topic": row["topic"],
                        "vote_count": row["vote_count"]
                    }
                    for row in cursor.fetchall()
                ]
                logging.info(f"Notícias mais votadas recuperadas: {len(news)} para tópicos {topics}")
                return news
        except sqlite3.Error as e:
            logging.error(f"Erro ao recuperar notícias mais votadas: {e}")
            raise