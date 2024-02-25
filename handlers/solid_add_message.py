from aiogram import Router, F, types
from aiogram.filters import or_f, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_LIST
from database.orm_query import orm_add_recipe
from kbds.reply import default_add_kb, get_main_kb

user_private_router = Router()


class AddSolidRecipe(StatesGroup):
    name = State()
    ingredients = State()
    description = State()
    image = State()


@user_private_router.message(
    or_f(Command("add_solid"),
                (F.text.lower().contains("новое твёрдое")) |
                (F.text.lower().contains("добавить твёрдое"))
    )
)
async def start_trouble_reporting(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in ADMIN_LIST:
        await message.answer("Название блюда:", reply_markup=default_add_kb)
        await state.set_state(AddSolidRecipe.name)
    else:
        await message.answer("У вас недостаточно прав для этого действия.")


@user_private_router.message(StateFilter('*'), Command("отмена"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=get_main_kb(is_admin=True))


@user_private_router.message(StateFilter('*'), Command("назад"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddSolidRecipe.name:
        await message.answer('Предыдущего шага нет, или введите название блюда или напишите "отмена"')
        return

    previous = None
    for step in AddSolidRecipe.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddSolidRecipe.texts[previous.state]}")
            return
        previous = step


@user_private_router.message(AddSolidRecipe.name, F.text)
async def process_category_id(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Необходимые ингредиенты:")
    await state.set_state(AddSolidRecipe.ingredients)


@user_private_router.message(AddSolidRecipe.ingredients, F.text)
async def process_category_id(message: types.Message, state: FSMContext):
    await state.update_data(ingredients=message.text)
    await message.answer("Рецепт:")
    await state.set_state(AddSolidRecipe.description)


@user_private_router.message(AddSolidRecipe.description, F.text)
async def process_category_id(message: types.Message, state: FSMContext):
    # Здесь можно добавить проверку на валидность введенной категории
    await state.update_data(description=message.text)
    await message.answer("Сопроводительное фото:")
    await state.set_state(AddSolidRecipe.image)


@user_private_router.message(AddSolidRecipe.image, F.photo)
async def process_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    data = await state.get_data()
    print(data)
    data["is_cocktail"] = False
    await orm_add_recipe(session=session, data=data)
    await message.answer("Рецепт твердого блюда зареган с кайфом", reply_markup=get_main_kb(is_admin=True))
    await state.clear()
