import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from dotenv import find_dotenv, load_dotenv

from config import ADMIN_LIST

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession

from database.engine import create_db, drop_db, session_maker

from dotenv import find_dotenv, load_dotenv

from kbds.reply import get_main_kb, admin_check

from handlers.delete_recipe import user_private_router as delete_recipe_router
from handlers.edit_recipe import user_private_router as edit_recipe_router
from handlers.recipes_add_message import user_private_router as recipes_add_message_handler
from handlers.get_recipes import user_private_router as get_recipes_handler
from handlers.solid_add_message import user_private_router as solid_add_message_handler

load_dotenv(find_dotenv())

ALLOWED_UPDATES = ['message, edited_message']

bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(default=bot_properties, token=os.getenv('TOKEN'))
bot.my_admins_list = []

storage = MemoryStorage()
# При создании Dispatcher передайте storage:
dp = Dispatcher(storage=storage)

dp.include_router(delete_recipe_router)
dp.include_router(edit_recipe_router)
dp.include_router(recipes_add_message_handler)
dp.include_router(get_recipes_handler)
dp.include_router(solid_add_message_handler)


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        """
Привет! Я белковый диетолог. У меня Вы можете найти множество интересных протеиновых блюд. Жмите на кнопку "Рецепт коктейля" или "Рецепт твердого блюда" и наслаждайтесь вкусной и полезной едой!
        """,
        reply_markup=get_main_kb(await admin_check(message))
    )


async def on_startup(bot):

    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    # await drop_db()
    print("blin((")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

asyncio.run(main())
