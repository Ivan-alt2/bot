import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiohttp import web

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.critical("Ошибка: Переменная окружения BOT_TOKEN не найдена!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик команды /start. Приветствует пользователя."""
    await message.answer(
        f"Привет, {message.from_user.full_name}! "
        "Я эхо-бот. Напиши мне что-нибудь."
    )


@dp.message(F.text)
async def echo_handler(message: types.Message):
    """Обработчик текстовых сообщений. Повторяет текст пользователя."""
    await message.answer(f"Вы написали: {message.text}")


async def handle_webhook(request: web.Request):
    """Обработчик вебхука для PythonAnywhere (бесплатный тариф)."""
    update = types.Update.parse_raw(await request.text())
    await dp.feed_update(bot, update)
    return web.Response(status=200)


async def main():
    """
    Точка входа в приложение.
    Запускает либо вебхук, либо long-polling в зависимости от переменных окружения.
    """
    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(webhook_url)
        app = web.Application()
        app.router.add_post("/", handle_webhook)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()

        logging.info(
            f"Вебхук запущен. Ожидаю запросы на {webhook_url}"
        )
        while True:
            await asyncio.sleep(3600)
    else:
        logging.info("Запуск в режиме long-polling...")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
