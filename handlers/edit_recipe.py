from aiogram import Router, F, types
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_update_product
from kbds.reply import get_main_kb, change_type_kb

user_private_router = Router()


class RecipeEditing(StatesGroup):
    choosing_field = State()
    editing_field = State()


@user_private_router.callback_query(or_f(
    F.data.startswith("edit_")
))
async def start_editing_field(callback_query: types.CallbackQuery, state: FSMContext):
    action, cocktail_id = callback_query.data.split('_')[0], callback_query.data.split('_')[2]
    field_to_edit = callback_query.data.split('_')[1]
    await state.set_state(RecipeEditing.editing_field)
    await state.update_data(field_to_edit=field_to_edit, cocktail_id=cocktail_id)

    if field_to_edit == "type":
        await callback_query.message.answer("Выберите новый тип:", reply_markup=change_type_kb(cocktail_id))
    else:
        await callback_query.message.answer(f"Введите новое значение для поля '{field_to_edit}':")
    await callback_query.answer()


@user_private_router.message(RecipeEditing.editing_field)
async def process_new_data(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    field_to_edit, cocktail_id = user_data['field_to_edit'], user_data['cocktail_id']
    changes = user_data.get('changes', {})
    # Обработка ввода изображения
    if field_to_edit == "image":
        if message.photo:
            new_value = message.photo[-1].file_id
            changes["photo_id"] = new_value
        else:
            await message.answer("Пожалуйста, отправьте изображение.")
            return  # Выходим из функции, если не было получено изображение
    else:
        changes[field_to_edit] = message.text
    await state.update_data(changes=changes)

    await message.answer(f"Поле '{field_to_edit}' готово к обновлению. Вы можете продолжить редактирование или сохранить изменения.")


@user_private_router.callback_query(F.data.startswith("change_type_"), RecipeEditing.editing_field)
async def process_type_change(callback_query: types.CallbackQuery, state: FSMContext):
    _, __, cocktail_id, new_type = callback_query.data.split('_')
    new_value = True if new_type == "True" else False  # Преобразование строки в булево значение

    # Аккумулируем изменения в контексте состояния
    user_data = await state.get_data()
    changes = user_data.get('changes', {})
    changes['is_cocktail'] = new_value
    await state.update_data(changes=changes)

    await callback_query.message.answer(f"Тип успешно изменён на {'коктейль' if new_value else 'твёрдое блюдо'}. Вы можете продолжить редактирование или сохранить изменения.")
    await callback_query.answer()


@user_private_router.callback_query(F.data.startswith("save_"), RecipeEditing.editing_field)
async def save_changes(callback_query: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    changes = user_data.get('changes', {})
    cocktail_id = user_data.get('cocktail_id')

    if changes:
        await orm_update_product(session, cocktail_id, changes)
        await callback_query.message.answer("Все изменения сохранены.")
    else:
        await callback_query.message.answer("Нет изменений для сохранения.")

    await state.clear()
    await callback_query.answer()


@user_private_router.callback_query(StateFilter('*'), F.data.startswith("cancel_editing"))
async def cancel_editing(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем все изменения
    await callback_query.message.answer("Редактирование отменено.", reply_markup=get_main_kb(is_admin=True))
    await callback_query.answer()
