import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import all_routers


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.error("Будь ласка, вкажіть ваш BOT_TOKEN у файлі .env!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    for router in all_routers:
        dp.include_router(router)

    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Головне меню"),
        BotCommand(command="admin", description="Панель адміністратора")
    ]
    await bot.set_my_commands(commands)

    logging.info("Бот запускається...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот зупинений.")
