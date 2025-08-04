# Discord News Bot

Um bot do Discord para curadoria e entrega de notícias personalizadas. Ele permite que usuários assinem tópicos de interesse (ex.: tecnologia, games, cibersegurança), recebam notícias filtradas de APIs (News API) e feeds RSS, votem em notícias com reações (👍/⭐) ou botões, visualizem resumos diários das notícias mais votadas e traduzam títulos para idiomas como português, espanhol, francês ou inglês.

## Funcionalidades

- **Assinatura de Tópicos**: Assine/desassine tópicos (tecnologia, games, cibersegurança) via um menu interativo com dropdown.
- **Busca de Notícias**: Obtém notícias de fontes como News API e feeds RSS (BBC, Engadget, Dark Reading).
- **Votação**: Vote em notícias usando reações (👍 para upvote, ⭐ para star) ou um botão "Votar" com dropdown.
- **Resumo Diário**: Receba um resumo diário das notícias mais votadas às 8h, enviado para um canal configurado ou DMs, com suporte a tradução.
- **Tradução de Notícias**: Escolha o idioma (português, espanhol, francês, inglês) para traduzir os títulos das notícias ao visualizar ou no resumo diário.
- **Logging**: Todas as ações (eventos, erros, traduções, votos) são registradas em `bot.log` para depuração.
- **Banco de Dados**: Usa SQLite (`news.db`) para armazenar usuários, assinaturas, notícias e votos.

## Pré-requisitos

- **Python 3.8+**
- Conta no [Discord Developer Portal](https://discord.com/developers)
- Token do bot com intents habilitados (`Server Members`, `Message Content`, `Reactions`)
- Chave da [News API](https://newsapi.org) para busca de notícias
- Conexão à internet para APIs de notícias e tradução

## Instalação

1. **Clone o repositório**:
   ```zsh
   git clone <url-do-repositorio>
   cd discord-news-bot
   ```

2. **Crie e ative um ambiente virtual**:
   ```zsh
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**:
   ```zsh
   pip install -r requirements.txt
   ```

   Dependências (exemplo, verifique `requirements.txt` para versões exatas):
   ```txt
   aiohappyeyeballs==2.6.1
   aiohttp==3.12.15
   aiosignal==1.4.0
   APScheduler==3.11.0
   attrs==25.3.0
   audioop-lts==0.2.1
   beautifulsoup4==4.13.4
   certifi==2025.8.3
   cffi==1.17.1
   charset-normalizer==3.4.2
   deep-translator==1.11.4
   discord.py==2.5.2
   feedparser==6.0.11
   frozenlist==1.7.0
   idna==3.10
   multidict==6.6.3
   propcache==0.3.2
   pycparser==2.22
   PyNaCl==1.5.0
   python-dotenv==1.1.1
   requests==2.32.4
   sgmllib3k==1.0.0
   soupsieve==2.7
   typing_extensions==4.14.1
   tzlocal==5.3.1
   urllib3==2.5.0
   yarl==1.20.1
   ```

4. **Crie o arquivo `.env`** na raiz do projeto:
   ```txt
   DISCORD_TOKEN=seu_token_aqui
   NEWS_API_KEY=sua_chave_aqui
   SUMMARY_CHANNEL_ID=123456789012345678  # (Opcional) ID do canal para resumo diário
   ```
   - Obtenha o `DISCORD_TOKEN` no Discord Developer Portal.
   - Obtenha o `NEWS_API_KEY` em [newsapi.org](https://newsapi.org).
   - Obtenha o `SUMMARY_CHANNEL_ID` clicando com o botão direito no canal no Discord e selecionando "Copiar ID" (ative o Modo Desenvolvedor no Discord).

5. **Configure o bot no Discord Developer Portal**:
   - Crie uma aplicação e um bot em [Discord Developer Portal](https://discord.com/developers).
   - Habilite os intents: `Server Members`, `Message Content`, e `Reactions`.
   - Copie o token do bot para o `.env`.
   - Gere um URL de convite com permissões:
     - `send_messages`
     - `read_message_history`
     - `add_reactions`
     - `use_application_commands`
   - Convide o bot para seu servidor usando o URL gerado.

## Executando o Bot

```bash
python3 main.py
```

- **Resultado esperado**:
  - Terminal: `Bot conectado como <nome_do_bot>` e `Comandos sincronizados: [<Command ...>]`.
  - `bot.log`: `<data_hora>:INFO:Bot conectado como <nome_do_bot>`.

## Comandos

- **/ping**: Testa a conexão do bot. Resposta: `Pong!`.
- **/news**: Abre um menu interativo com três botões:
  - **Assinar Tópicos**: Dropdown para assinar/desassinar tópicos (ex.: tecnologia, games, cibersegurança). Exibe tópicos adicionados, removidos e atuais.
  - **Ver Notícias**: Dropdown para escolher o idioma (português, espanhol, francês, inglês), seguido de um dropdown para o destino (canal atual ou DM). Envia notícias traduzidas com reações (👍/⭐) e botão "Votar".
  - **Resumo Diário**: Dropdown para escolher o idioma e exibe as 3 notícias mais votadas para os tópicos assinados, com títulos traduzidos.

## Sistema de Votação

- **Reações**: Adicione 👍 (upvote) ou ⭐ (star) às mensagens de notícias para votar. Os votos são registrados na tabela `votes` do SQLite.
- **Botão "Votar"**: Clique para abrir um dropdown e selecionar o tipo de voto (Upvote ou Star). Apenas um voto por usuário por notícia é permitido (atualiza com `INSERT OR REPLACE`).

## Resumo Diário

- **Agendado**: Executado diariamente às 8h, envia as 3 notícias mais votadas (traduzidas para português) para:
  - Um canal configurado (`SUMMARY_CHANNEL_ID` no `.env`), se definido.
  - DMs dos usuários com assinaturas, caso contrário.
- **Sob Demanda**: O botão "Resumo Diário" exibe as notícias mais votadas imediatamente, com opção de idioma.

## Tradução de Notícias

- Escolha o idioma (português, espanhol, francês, inglês) ao visualizar notícias ou resumo.
- Títulos são traduzidos usando a biblioteca `deep-translator` (Google Translate).
- Os dados originais (em inglês) são mantidos no banco, com traduções aplicadas apenas na exibição.

## Estrutura do Banco de Dados

O bot usa SQLite (`news.db`) com as seguintes tabelas:

- **users**: Armazena IDs e nomes de usuários.
  ```sql
  CREATE TABLE users (
      user_id INTEGER PRIMARY KEY,
      username TEXT NOT NULL
  );
  ```
- **subscriptions**: Registra tópicos assinados por usuários.
  ```sql
  CREATE TABLE subscriptions (
      user_id INTEGER,
      topic TEXT NOT NULL,
      PRIMARY KEY (user_id, topic),
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );
  ```
- **news**: Armazena notícias (título original, URL, tópico, etc.).
  ```sql
  CREATE TABLE news (
      news_id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      url TEXT NOT NULL,
      topic TEXT NOT NULL,
      published_at TEXT,
      message_id INTEGER
  );
  ```
- **votes**: Registra votos em notícias.
  ```sql
  CREATE TABLE votes (
      news_id INTEGER,
      user_id INTEGER,
      vote_type TEXT NOT NULL,  -- 'upvote' ou 'star'
      PRIMARY KEY (news_id, user_id),
      FOREIGN KEY (news_id) REFERENCES news(news_id),
      FOREIGN KEY (user_id) REFERENCES users(user_id)
  );
  ```

O banco é inicializado automaticamente ao executar o bot.

## Integração com APIs

- **News API**: Busca notícias por tópico usando a chave fornecida no `.env`.
- **RSS Feeds**:
  - Tecnologia: BBC (`http://feeds.bbci.co.uk/news/technology/rss.xml`)
  - Games: Engadget (`https://www.engadget.com/rss.xml`)
  - Cibersegurança: Dark Reading (`https://www.darkreading.com/rss.xml`)
- **Tradução**: Usa `deep-translator` (Google Translate) para traduzir títulos dinamicamente.

Para testar a integração com APIs:
```zsh
python3 test_news.py
```

> **Nota**: O arquivo `test_news.py` não está incluído, mas pode ser criado para testar `NewsService.fetch_news`.

## Depuração

- **Logs**: Todas as ações (conexão, comandos, erros, traduções, votos, resumos) são registradas em `bot.log`.
- **Verificar o banco de dados**:
  ```zsh
  sqlite3 news.db
  .schema  # Exibe o esquema das tabelas
  SELECT * FROM news;  # Verifica notícias
  SELECT * FROM votes;  # Verifica votos
  ```
- **Erros comuns e soluções**:
  - **Erro 403 (Forbidden)**: Verifique permissões do bot no servidor ou DMs. Reinvite com permissões adequadas.
  - **Database locked**: Feche outros processos acessando `news.db` ou delete o arquivo e reinicie.
  - **Falha na tradução**: Verifique a conexão com a internet. O bot usa títulos originais como fallback.
  - **Tarefa agendada não executa**: Confirme que `apscheduler` está instalado (`pip show apscheduler`) e verifique `bot.log`.

## Exemplos de Uso

1. **Comando `/news`**:
   - Executar `/news` → Exibe botões: "Assinar Tópicos", "Ver Notícias", "Resumo Diário" (ephemeral).
2. **Assinar Tópicos**:
   - Clique em "Assinar Tópicos" → Selecione "Tecnologia" e "Games" → Resposta: `Assinados: tecnologia, games\nTópicos atuais: tecnologia, games`.
3. **Ver Notícias**:
   - Clique em "Ver Notícias" → Selecione "Português" → Selecione "Canal Atual" → Mensagem no canal: `Notícias para @usuário (pt): - Título Traduzido (URL)` com reações 👍/⭐ e botão "Votar".
4. **Votação**:
   - Adicione reação 👍 → Voto registrado como "upvote" no banco.
   - Clique em "Votar" → Selecione "Star" → Resposta: `Voto 'star' registrado para X notícias!`.
5. **Resumo Diário**:
   - Clique em "Resumo Diário" → Selecione "Espanhol" → Resposta: `Resumo diário (es): - Título Traduzido (URL) [X votos]`.
   - Diariamente às 8h → Recebe por DM ou no canal configurado: `Resumo diário (pt): - Título Traduzido (URL) [X votos]`.

## Estrutura do Projeto

```txt
discord-news-bot/
├── .env                # Configurações (DISCORD_TOKEN, NEWS_API_KEY, SUMMARY_CHANNEL_ID)
├── .gitignore          # Ignora venv, *.pyc, news.db, bot.log
├── bot.log             # Logs de execução
├── config.py           # Carrega variáveis de ambiente
├── database.py         # Gerencia SQLite (usuários, assinaturas, notícias, votos)
├── main.py             # Inicializa o bot e tarefa agendada
├── news.py             # Busca e traduz notícias (News API, RSS, deep-translator)
├── commands.py         # Comandos e interações (menus, botões, reações)
├── requirements.txt    # Dependências do projeto
├── README.md           # Documentação do projeto
```

## Próximos Passos

- **Testes Automatizados**: Adicionar testes com `pytest` para validar `database.py`, `news.py`, e `commands.py`.
- **Busca por Palavra-Chave**: Implementar um comando `/search` para buscar notícias por termo específico.
- **Administração**: Adicionar comandos para administradores gerenciarem tópicos ou assinaturas.
- **Caching de Traduções**: Armazenar traduções em cache para reduzir chamadas à API de tradução.

## Contribuição

1. Faça um fork do repositório.
2. Crie uma branch para sua funcionalidade: `git checkout -b feature/nova-funcionalidade`.
3. Commit suas alterações: `git commit -m "feat: Descrição da funcionalidade"`.
4. Envie para o repositório remoto: `git push origin feature/nova-funcionalidade`.
5. Abra um Pull Request.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).