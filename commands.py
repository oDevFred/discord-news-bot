import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, Select, View
from database import Database
from news import NewsService
import logging

# Configurar logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

class NewsCog(commands.Cog):
    def __init__(self, bot, db: Database, news_service: NewsService):
        self.bot = bot
        self.db = db
        self.news_service = news_service
        self.topics = ["tecnologia", "games", "ciberseguranca"]

    @app_commands.command(name="news", description="Acessa o menu de notícias")
    async def news(self, interaction: discord.Interaction):
        # Adicionar usuário ao banco
        self.db.add_user(interaction.user.id, interaction.user.name)
        # Criar interface gráfica
        view = NewsView(self.db, self.news_service, self.topics)
        await interaction.response.send_message(
            "Bem-vindo ao News Bot! Escolha uma ação:",
            view=view,
            ephemeral=True
        )
        logging.info(f"Comando /news executado por {interaction.user}")

class NewsView(discord.ui.View):
    def __init__(self, db: Database, news_service: NewsService, topics: list):
        super().__init__(timeout=None)  # Persistente
        self.db = db
        self.news_service = news_service
        self.topics = topics

        # Botão: Assinar Tópicos
        button_subscribe = Button(label="Assinar Tópicos", style=discord.ButtonStyle.primary)
        button_subscribe.callback = self.subscribe_button_callback
        self.add_item(button_subscribe)

        # Botão: Ver Notícias
        button_view = Button(label="Ver Notícias", style=discord.ButtonStyle.secondary)
        button_view.callback = self.view_news_button_callback
        self.add_item(button_view)

        # Botão: Resumo Diário (placeholder)
        button_summary = Button(label="Resumo Diário", style=discord.ButtonStyle.secondary)
        button_summary.callback = self.summary_button_callback
        self.add_item(button_summary)

    async def subscribe_button_callback(self, interaction: discord.Interaction):
        # Exibir dropdown de tópicos
        view = SubscribeView(self.db, self.topics, interaction.user.id)
        await interaction.response.send_message(
            "Selecione um tópico para assinar/desassinar:",
            view=view,
            ephemeral=True
        )
        logging.info(f"Botão 'Assinar Tópicos' clicado por {interaction.user}")

    async def view_news_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        subscriptions = self.db.get_subscriptions(interaction.user.id)
        if not subscriptions:
            await interaction.followup.send("Você não assinou nenhum tópico!", ephemeral=True)
            return
        news_list = []
        for topic in subscriptions:
            news_list.extend(self.news_service.fetch_news(topic, limit=2))
        if not news_list:
            await interaction.followup.send("Nenhuma notícia encontrada para seus tópicos.", ephemeral=True)
            return
        response = "\n".join([f"- {news['title']} ({news['url']})" for news in news_list])
        await interaction.followup.send(f"Notícias para seus tópicos:\n{response}", ephemeral=True)
        self.news_service.save_news(news_list)
        logging.info(f"Botão 'Ver Notícias' clicado por {interaction.user}, exibidas {len(news_list)} notícias")

    async def summary_button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Resumo diário será implementado no futuro!",
            ephemeral=True
        )
        logging.info(f"Botão 'Resumo Diário' clicado por {interaction.user}")

class SubscribeView(discord.ui.View):
    def __init__(self, db: Database, topics: list, user_id: int):
        super().__init__(timeout=60.0)  # Expira após 60 segundos
        self.db = db
        self.user_id = user_id
        select = Select(
            placeholder="Escolha um tópico",
            options=[
                discord.SelectOption(label=topic.capitalize(), value=topic)
                for topic in topics
            ]
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        topic = interaction.data["values"][0]
        subscriptions = self.db.get_subscriptions(self.user_id)
        if topic in subscriptions:
            self.db.remove_subscription(self.user_id, topic)
            await interaction.response.send_message(
                f"Você desassinou o tópico '{topic}'!", ephemeral=True
            )
            logging.info(f"Usuário {interaction.user} desassinou o tópico {topic}")
        else:
            self.db.add_subscription(self.user_id, topic)
            await interaction.response.send_message(
                f"Você assinou o tópico '{topic}'!", ephemeral=True
            )
            logging.info(f"Usuário {interaction.user} assinou o tópico {topic}")

async def setup(bot):
    db = Database()
    news_service = NewsService(db, bot.config.NEWS_API_KEY)
    await bot.add_cog(NewsCog(bot, db, news_service))