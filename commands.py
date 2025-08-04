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
        self.db.add_user(interaction.user.id, interaction.user.name)
        view = NewsView(self.db, self.news_service, self.topics, interaction.guild)
        await interaction.response.send_message(
            "Bem-vindo ao News Bot! Escolha uma ação:",
            view=view,
            ephemeral=True
        )
        logging.info(f"Comando /news executado por {interaction.user}")

class NewsView(discord.ui.View):
    def __init__(self, db: Database, news_service: NewsService, topics: list, guild: discord.Guild):
        super().__init__(timeout=None)
        self.db = db
        self.news_service = news_service
        self.topics = topics
        self.guild = guild

        button_subscribe = Button(label="Assinar Tópicos", style=discord.ButtonStyle.primary)
        button_subscribe.callback = self.subscribe_button_callback
        self.add_item(button_subscribe)

        button_view = Button(label="Ver Notícias", style=discord.ButtonStyle.secondary)
        button_view.callback = self.view_news_button_callback
        self.add_item(button_view)

        button_summary = Button(label="Resumo Diário", style=discord.ButtonStyle.secondary)
        button_summary.callback = self.summary_button_callback
        self.add_item(button_summary)

    async def subscribe_button_callback(self, interaction: discord.Interaction):
        view = SubscribeView(self.db, self.topics, interaction.user.id)
        await interaction.response.send_message(
            "Selecione um ou mais tópicos para assinar/desassinar:",
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
        view = DeliveryView(self.db, self.news_service, subscriptions, self.guild, interaction.user)
        await interaction.followup.send(
            "Escolha onde receber as notícias:",
            view=view,
            ephemeral=True
        )
        logging.info(f"Botão 'Ver Notícias' clicado por {interaction.user}")

    async def summary_button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Resumo diário será implementado no futuro!",
            ephemeral=True
        )
        logging.info(f"Botão 'Resumo Diário' clicado por {interaction.user}")

class SubscribeView(discord.ui.View):
    def __init__(self, db: Database, topics: list, user_id: int):
        super().__init__(timeout=60.0)
        self.db = db
        self.user_id = user_id
        select = Select(
            placeholder="Escolha um ou mais tópicos",
            options=[
                discord.SelectOption(label=topic.capitalize(), value=topic)
                for topic in topics
            ],
            min_values=1,
            max_values=len(topics)
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        selected_topics = interaction.data["values"]
        current_subscriptions = set(self.db.get_subscriptions(self.user_id))
        added = []
        removed = []

        for topic in selected_topics:
            if topic in current_subscriptions:
                self.db.remove_subscription(self.user_id, topic)
                removed.append(topic)
            else:
                self.db.add_subscription(self.user_id, topic)
                added.append(topic)

        message = []
        if added:
            message.append(f"Assinados: {', '.join(added)}")
        if removed:
            message.append(f"Desassinados: {', '.join(removed)}")
        updated_subscriptions = self.db.get_subscriptions(self.user_id)
        if updated_subscriptions:
            message.append(f"Tópicos atuais: {', '.join(updated_subscriptions)}")
        else:
            message.append("Você não tem tópicos assinados.")

        await interaction.response.send_message(
            "\n".join(message),
            ephemeral=True
        )
        logging.info(
            f"Usuário {interaction.user} atualizou assinaturas: "
            f"Adicionados={added}, Removidos={removed}"
        )

class DeliveryView(discord.ui.View):
    def __init__(self, db: Database, news_service: NewsService, subscriptions: list, guild: discord.Guild, user: discord.User):
        super().__init__(timeout=60.0)
        self.db = db
        self.news_service = news_service
        self.subscriptions = subscriptions
        self.guild = guild
        self.user = user
        select = Select(
            placeholder="Escolha o destino das notícias",
            options=[
                discord.SelectOption(label="Mensagem Privada", value="dm"),
                discord.SelectOption(label="Canal Atual", value="channel")
            ]
        )
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        destination = interaction.data["values"][0]
        news_list = []
        for topic in self.subscriptions:
            news_list.extend(self.news_service.fetch_news(topic, limit=2))
        if not news_list:
            await interaction.followup.send("Nenhuma notícia encontrada para seus tópicos.", ephemeral=True)
            return

        # Salvar notícias e obter news_id
        news_ids = self.news_service.save_news(news_list)
        response = "\n".join([f"- {news['title']} ({news['url']})" for news in news_list])

        try:
            if destination == "dm":
                message = await self.user.send(f"Notícias para seus tópicos:\n{response}")
            else:
                message = await interaction.channel.send(f"Notícias para {self.user.mention}:\n{response}")

            # Atualizar message_id no banco
            for news_id in news_ids:
                self.db.update_news_message_id(news_id, message.id)

            await interaction.followup.send("Notícias enviadas com sucesso!", ephemeral=True)
            logging.info(
                f"Notícias enviadas para {destination} por {self.user}, "
                f"{len(news_list)} notícias, message_id={message.id}"
            )
        except discord.errors.Forbidden as e:
            await interaction.followup.send(
                "Erro: Não tenho permissão para enviar mensagens no destino escolhido.",
                ephemeral=True
            )
            logging.error(f"Erro ao enviar notícias para {destination}: {e}")

async def setup(bot):
    db = Database()
    news_service = NewsService(db, bot.config.NEWS_API_KEY)
    await bot.add_cog(NewsCog(bot, db, news_service))