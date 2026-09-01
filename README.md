# CrazyFroot Shop

Telegram shop for GTA 5 digital accounts (Epic Games, Social Club). Users buy from balance; admins stock inventory and broadcast messages.

**Stack:** Python 3.13, FastAPI, Aiogram 3, SQLAlchemy 2 (asyncpg), FastStream/RabbitMQ, Crypto Pay, Fernet, Docker, uv.

## Local run

1. Create a PostgreSQL database.
2. Expose `POST /webhook` to Telegram (ngrok, nginx, or similar). See `nginx/default.conf`.
3. Copy `.env.example` to `.env` and fill in values.
4. Start RabbitMQ.
5. Run:

```bash
uv sync
uv run fastapi dev ./src/main.py
```

App listens on `0.0.0.0:8000`. Schema is created with `Base.metadata.create_all` on startup (no Alembic).

## Docker

```bash
cp .env.example .env
docker compose up
```

Compose starts `app`, PostgreSQL (`users`), and RabbitMQ (AMQP `5672`, management `15672`). It overrides `dsn` and `rabbitmq_url` for the internal network.

## Configuration

Copy `.env.example`. Fields consumed by `src/settings/config.py`:

| Variable | Description |
|---|---|
| `bot_token` | Telegram bot token |
| `admin_ids` | JSON list of admin Telegram IDs, e.g. `[123]` |
| `admin_username` | Support handle shown in `/help` |
| `user_agreement` | URL of the user agreement |
| `rabbitmq_url` | AMQP URL |
| `webhook_url` | Public Telegram webhook URL (must end with `/webhook`) |
| `dsn` | `postgresql+asyncpg://...` |
| `fernet_key` | Fernet key for login/password at rest |
| `available_platforms` | JSON map of platforms |
| `crypto_bot_token` | Crypto Pay API token |

`.env` is gitignored. Generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Architecture

```
Telegram  --webhook-->  FastAPI :8000  -->  Aiogram handlers
                              |
                         PostgreSQL
                              |
Admin mailing --> RabbitMQ (exchange notifications) --> consumer --> Telegram
User top-up   --> Crypto Pay invoices
```

- `app` — FastAPI + Aiogram webhook (`POST /webhook`).
- PostgreSQL — `User`, `Account` (encrypted credentials).
- RabbitMQ — durable mailing queue `send-mailing`.
- Crypto Pay — balance top-up invoices.

Layout: `src/` (handlers, service, repo, mailing, client, settings), `nginx/`, `Dockerfile`, `docker-compose.yaml`.

## Features

- Catalog and purchase of Social Club / Epic Games accounts (600 RUB).
- Balance top-up via Crypto Pay (create / check / cancel invoice).
- Admin: import accounts from `.txt` (`type_platform:login:password`), user list, broadcasts (text/photo/document).
- Account login/password encrypted with Fernet in PostgreSQL.
- Pydantic settings, structured logging, mailing retry on Telegram flood control.

## Links

- Swagger UI: `http://localhost:8000/` (`docs_url="/"`).
- Webhook: `POST /webhook`.
- Bot: set `webhook_url` to a public HTTPS endpoint pointing at that path.
