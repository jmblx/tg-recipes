from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.utils.formatting import Text
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_recipes, \
    orm_get_random_recipe
from kbds.reply import get_main_kb, get_admin_keyboard, admin_check

user_private_router = Router()


@user_private_router.message(
    or_f(
        Command("all_recipes"),
        (F.text.lower().contains("все рецепты"))
    )
)
async def send_all_recipes(message: types.Message, session: AsyncSession):
    recipes = await orm_get_recipes(session)
    if not recipes:
        await message.answer("Рецептов пока нет.")
        return

    for recipe in recipes:
        # Форматируем текст сообщения
        dish_type = "Коктейль" if recipe.is_cocktail else "Твёрдое блюдо"
        text = (f"Название: {recipe.name}\n"
                f"Описание: {recipe.description}\n"
                f"Тип: {dish_type}")

        # Отправляем сообщение с текстом
        await message.answer(text, reply_markup=get_main_kb(await admin_check(message)))

        # Отправляем изображение, если оно есть
        if recipe.photo_id:
            await message.answer_photo(recipe.photo_id, reply_markup=get_main_kb(await admin_check(message)))


@user_private_router.message(or_f(Command("random-solid"),
                (F.text.lower().contains("рецепт твёрдого блюда")),
                (F.text.lower().contains("рецепт твердого блюда"))
))
async def send_random_solid_food(message: types.Message, session: AsyncSession):
    solid = await orm_get_random_recipe(session, is_cocktail=False)
    print(solid, "sda")
    if not solid:
        await message.answer("Твёрдых блюд пока нет.", reply_markup=get_main_kb(await admin_check(message)))
        return

    if solid.photo_id:
        await message.answer_photo(solid.photo_id, reply_markup=get_main_kb(await admin_check(message)))
    admin_kb = get_admin_keyboard(solid.id, message.from_user.id)
    formatted_text = (f"<b>Название:</b> <pre>{solid.name}</pre>\n"
                      f"<b>Рецепт</b> <pre>{solid.ingredients}</pre>\n"
                      f"<b>Приготовление:</b> <pre>{solid.description}</pre>\n"
                      f"<b>Тип:</b> <pre>Твёрдое блюдо</pre>")
    if admin_kb:
        await message.answer(formatted_text, reply_markup=admin_kb, parse_mode="HTML")
    else:
        await message.answer(formatted_text, reply_markup=get_main_kb(await admin_check(message)), parse_mode="HTML")


@user_private_router.message(or_f(Command("random-cocktail"),
                                  F.text.lower().contains("рецепт коктейля")))
async def send_random_cocktail(message: types.Message, session: AsyncSession):
    cocktail = await orm_get_random_recipe(session, is_cocktail=True)
    print(cocktail, 'asd')
    if not cocktail:
        await message.answer("Коктейлей пока нет.", reply_markup=get_main_kb(await admin_check(message)))
        return

    if cocktail.photo_id:
        print(cocktail.photo_id)
        await message.answer_photo(cocktail.photo_id, reply_markup=get_main_kb(await admin_check(message)))
    admin_kb = get_admin_keyboard(cocktail.id, message.from_user.id)
    formatted_text = (f"<b>Название:</b> <pre>{cocktail.name}</pre>\n"
                      f"<b>Рецепт</b> <pre>{cocktail.ingredients}</pre>\n"
                      f"<b>Приготовление:</b> <pre>{cocktail.description}</pre>\n"
                      f"<b>Тип:</b> <pre>Коктейль</pre>")
    if admin_kb:
        await message.answer(formatted_text, reply_markup=admin_kb, parse_mode="HTML")
    else:
        await message.answer(formatted_text, reply_markup=get_main_kb(await admin_check(message)), parse_mode="HTML")
