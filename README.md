# Notes Bot

![Python](https://img.shields.io/badge/Python-3.13-blue)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.24-green)](https://github.com/aiogram/aiogram)
![License](https://img.shields.io/badge/License-MIT-yellow)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

Inline Telegram бот для сохранения заметок в Notion.

## Возможности

- Сохранение текстовых сообщений в Notion базу данных
- Webhook и Polling режимы работы
- Асинхронная очередь задач
- Ограничение доступа по списку пользователей
- Docker и CI/CD

## Установка

### Предварительные требования

1. Python 3.13+ 
2. пакетный менеджер [uv](https://github.com/astral-sh/uv)
3. Токен телеграм бота от [@BotFather](https://t.me/BotFather)
4. Notion Integration Token

### Шаги установки

```bash
git clone https://github.com/Trum-ok/notes_bot
cd notes_bot

cp .env.example .env
echo Отредактируйте .env файл

uv sync

uv run python -m notes.main
```

## Конфигурация

Создайте `.env` файл на основе `.env.example`:

| Переменная | Описание | Обязательно |
|------------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | Да |
| `NOTION_SECRET` | API ключ Notion Integration | Да |
| `NOTION_DB_ID` | ID базы данных Notion | Да |
| `TELEGRAM_ALLOWED_USER_IDS` | Список ID пользователей через запятую | Нет |
| `DEV` | `true` для polling режима | Нет |
| `WEBHOOK_PUBLIC_URL` | Публичный URL для webhook | Для production |
| `WEBHOOK_SECRET` | Секретный токен webhook | Для production |
| `PORT` | Порт сервера (по умолчанию 8080) | Нет |


## Развёртывание

### Docker Compose

```bash
docker compose -f deploy/docker-compose.yaml up -d
```

### Webhook режим

Для production установите `DEV=false` и настройте переменные webhook:

```env
DEV=false
WEBHOOK_PUBLIC_URL=https://your-domain.com/webhook
WEBHOOK_SECRET=your-secret-token
PORT=8080
```

Для локальной разработки с webhook можно использовать [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/):

```bash
brew install cloudflared

cloudflared tunnel --url http://localhost:8080
```

### Polling режим

Для локальной разработки используйте polling:

```env
DEV=true
```

## Архитектура

```
notes_bot/
├── notes/
│   ├── main.py           # Точка входа
│   ├── settings.py       # Конфигурация
│   ├── jobs.py           # Модели задач
│   ├── workers.py        # Воркеры очереди
│   ├── telegram/         # Telegram модуль
│   │   ├── bot.py        # Инициализация бота
│   │   ├── handlers/     # Обработчики сообщений
│   │   └── middlewares.py
│   └── notion/           # Notion API клиент
│       ├── client.py     # HTTP клиент
│       ├── wrapper.py    # Высокоуровневый интерфейс
│       └── schemas.py    # Pydantic модели
├── deploy/               # Docker конфиги
└── .github/workflows/    # CI/CD
```

## Лицензия

MIT License
