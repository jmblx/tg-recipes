from aiogram import Router, F, types
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_LIST
from database.orm_query import orm_delete_product
from kbds.reply import change_type_kb, get_main_kb

user_private_router = Router()


@user_private_router.callback_query(or_f(
    F.data.startswith("delete_")
))
async def start_editing_field(callback_query: types.CallbackQuery, session: AsyncSession):
    recipe_id = callback_query.data.split("_")[1]
    await orm_delete_product(session, int(recipe_id))
    await callback_query.message.answer(
        "Рецепт удалён!",
        reply_markup=get_main_kb(str(callback_query.from_user.id) in ADMIN_LIST)
    )
    await callback_query.answer()
