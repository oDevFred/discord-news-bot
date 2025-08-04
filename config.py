from dotenv import load_dotenv
import os

load_dotenv()

# Configurações do bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SUMMARY_CHANNEL_ID = int(os.getenv("SUMMARY_CHANNEL_ID", 0))  # ID do canal para resumo diário