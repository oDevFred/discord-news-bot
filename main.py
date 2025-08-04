import discord
from discord import app_commands
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config
from database import Database
import logging

# Configurar logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

# Inicializar o bot
class NewsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.config = config
        self.scheduler = AsyncIOScheduler()
        self.db = Database()

    async def setup_hook(self):
        from commands import setup
        await setup(self)
        # Configurar tarefa agendada
        self.scheduler.add_job(
            self.send_daily_summary,
            "cron",
            hour=8, minute=0,  # Executa às 8h diariamente
            id="daily_summary"
        )
        self.scheduler.start()
        logging.info("Tarefa agendada para resumo diário configurada.")

    async def send_daily_summary(self):
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Obter usuários com assinaturas
                cursor.execute("SELECT DISTINCT user_id FROM subscriptions")
                user_ids = [row["user_id"] for row in cursor.fetchall()]
                if not user_ids:
                    logging.info("Nenhum usuário com assinaturas para resumo diário.")
                    return

                for user_id in user_ids:
                    subscriptions = self.db.get_subscriptions(user_id)
                    top_news = self.db.get_top_voted_news(subscriptions, limit=3)
                    if not top_news:
                        continue
                    response = "\n".join([f"- {news['title']} ({news['url']}) [{news['vote_count']} votos]" for news in top_news])
                    user = await self.fetch_user(user_id)
                    if not user:
                        continue
                    try:
                        if config.SUMMARY_CHANNEL_ID:
                            channel = self.get_channel(config.SUMMARY_CHANNEL_ID)
                            if channel:
                                await channel.send(f"Resumo diário para {user.mention}:\n{response}")
                            else:
                                logging.warning(f"Canal {config.SUMMARY_CHANNEL_ID} não encontrado.")
                                await user.send(f"Resumo diário:\n{response}")
                        else:
                            await user.send(f"Resumo diário:\n{response}")
                        logging.info(f"Resumo diário enviado para usuário {user_id}")
                    except discord.errors.Forbidden as e:
                        logging.error(f"Erro ao enviar resumo diário para usuário {user_id}: {e}")
        except Exception as e:
            logging.error(f"Erro ao executar tarefa de resumo diário: {e}")

bot = NewsBot()

# Evento: Bot pronto
@bot.event
async def on_ready():
    logging.info(f"Bot conectado como {bot.user}")
    print(f"Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        logging.info(f"Comandos sincronizados: {synced}")
        print(f"Comandos sincronizados: {synced}")
    except Exception as e:
        logging.error(f"Erro ao sincronizar comandos: {e}")
        print(f"Erro ao sincronizar comandos: {e}")

# Comando: /ping
@app_commands.command(name="ping", description="Testa a conexão do bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")
    logging.info(f"Comando /ping executado por {interaction.user}")

# Registrar o comando no CommandTree
bot.tree.add_command(ping)

# Executar o bot
if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)