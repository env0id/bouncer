from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiohttp import web
import logging
import config
from config import TOKEN, WEBHOOK_URL, ADMIN_ID_LIST
from db import create_db_and_tables


bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

async def on_startup(bot: Bot):
  await create_db_and_tables()
  await bot.set_webhook(WEBHOOK_URL)

  for admin in ADMIN_ID_LIST:
    try:
      await bot.send_message(admin, 'Bot is working')
    except Exception as e:
      logging.warning(e)

async def on_shutdown():
  logging.warning('Shutting down bot...')
  await bot.delete_webhook()
  await dp.storage.close()
  logging.warning('Goodbye!')


def main() -> None:
  dp.startup.register(on_startup)
  dp.shutdown.register(on_shutdown)

  app = web.Application()

  webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
  webhook_requests_handler.register(app, path="telegram-webhook")
  setup_application(app, dp, bot=bot)
  web.run_app(app, host=config.WEBAPP_HOST, port=config.WEBAPP_PORT)

if __name__ == '__main__':
    main()
