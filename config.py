from dotenv import load_dotenv
import os

load_dotenv()

# Configurações do bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")