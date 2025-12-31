from aiogram import Bot, Dispatcher

from notes.settings import TELEGRAM_BOT_TOKEN
from notes.telegram.handlers import routers
from notes.telegram.middlewares import ErrorMiddleware

bot = Bot(token=TELEGRAM_BOT_TOKEN)  # type: ignore[invalid-argument-type]
dp = Dispatcher()

error_mw = ErrorMiddleware()
dp.message.middleware(error_mw)
dp.inline_query.middleware(error_mw)

dp.include_routers(*routers)
