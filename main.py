import asyncio
import logging
import sys
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import all_routers
from database.models import create_db


async def handle(request):
    return web.Response(text="Bot is alive!")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    create_db()

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.error("Будь ласка, вкажіть ваш BOT_TOKEN у файлі .env!")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    for router in all_routers:
        dp.include_router(router)

    commands = [
        BotCommand(command="start", description="Головне меню"),
        BotCommand(command="suggest", description="Запропонувати напрямок/професію/програму"),
        BotCommand(command="admin", description="Панель адміністратора")
    ]
    await bot.set_my_commands(commands)

    # Запуск dummy веб-сервера для Render (Free tier вимагає відкриття порту)
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/healthz', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Dummy веб-сервер запущено на порту {port}")

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
