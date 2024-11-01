from aiogram import Router

from bot import dp, main
import logging

from handlers.user.start import start_router
from handlers.user.select_language import select_language_router

logging.basicConfig(level=logging.INFO)

main_router = Router()
dp.include_router(main_router)
main_router.include_router(start_router)
main_router.include_router(select_language_router)


if __name__ == '__main__':
  main()