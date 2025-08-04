import discord
from discord import app_commands
from discord.ext import commands
import config
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
bot = commands.Bot(command_prefix="!", intents=intents)

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