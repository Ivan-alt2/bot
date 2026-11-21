import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Получение токена из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.critical("Ошибка: Переменная окружения BOT_TOKEN не найдена!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}! Я эхо-бот. Напиши мне что-нибудь.")

@dp.message(F.text)
async def echo_handler(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")

# Обработчик входящих запросов от Telegram (для вебхука)
async def handle_webhook(request: web.Request):
    update = types.Update.parse_raw(await request.text())
    await dp.feed_update(bot, update)
    return web.Response(status=200)

async def main():
    # Режим 1: Вебхук (бесплатный PythonAnywhere)
    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(webhook_url)
        app = web.Application()
        app.router.add_post("/", handle_webhook)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        
        logging.info(f"Вебхук запущен. Ожидаю запросы на {webhook_url}")
        while True:
            await asyncio.sleep(3600)

    # Режим 2: Long-polling (платный PythonAnywhere или локальный запуск)
    else:
        logging.info("Запуск в режиме long-polling...")
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
