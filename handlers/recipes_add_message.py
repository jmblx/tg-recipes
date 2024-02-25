from aiogram import Router, F, types
from aiogram.filters import or_f, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_LIST
from database.orm_query import orm_add_recipe
from kbds.reply import get_main_kb, default_add_kb

user_private_router = Router()


class AddCocktailRecipe(StatesGroup):
    name = State()
    ingredients = State()
    description = State()
    image = State()


@user_private_router.message(
    or_f(Command("new_cocktail"),
                (F.text.lower() == "новый котейль") |
                (F.text.lower().contains("добавить коктейль"))
    )
)
async def start_trouble_reporting(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in ADMIN_LIST:
        await message.answer("Название коктейля:", reply_markup=default_add_kb)
        await state.set_state(AddCocktailRecipe.name)
    else:
        await message.answer("У вас недостаточно прав для этого действия.")


@user_private_router.message(StateFilter('*'), Command("отмена"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=get_main_kb)


@user_private_router.message(StateFilter('*'), Command("назад"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddCocktailRecipe.name:
        await message.answer('Предыдущего шага нет, или введите название коктейля или напишите "отмена"')
        return

    previous = None
    for step in AddCocktailRecipe.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddCocktailRecipe.texts[previous.state]}")
            return
        previous = step


@user_private_router.message(AddCocktailRecipe.name, F.text)
async def process_category_id(message: types.Message, state: FSMContext):
    # Здесь можно добавить проверку на валидность введенной категории
    await state.update_data(name=message.text)
    await message.answer("Необходимые ингредиенты:")
    await state.set_state(AddCocktailRecipe.ingredients)


@user_private_router.message(AddCocktailRecipe.ingredients, F.text)
async def process_category_id(message: types.Message, state: FSMContext):
    await state.update_data(ingredients=message.text)
    await message.answer("Рецепт:")
    await state.set_state(AddCocktailRecipe.description)


@user_private_router.message(AddCocktailRecipe.description, F.text)
async def process_category_id(message: types.Message, state: FSMContext):
    # Здесь можно добавить проверку на валидность введенной категории
    await state.update_data(description=message.text)
    await message.answer("Сопроводительное фото:")
    await state.set_state(AddCocktailRecipe.image)


@user_private_router.message(AddCocktailRecipe.image, F.photo)
async def process_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    # Здесь data будет содержать file_id вместо локального пути
    data = await state.get_data()
    data["is_cocktail"] = True
    await orm_add_recipe(session=session, data=data)
    await message.answer("Рецепт коктейля зареган с кайфом", reply_markup=get_main_kb(is_admin=True))
    await state.clear()


