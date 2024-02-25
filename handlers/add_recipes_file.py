import pandas as pd
from aiogram import Router, F, types
from aiogram.filters import or_f, Command
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Recipe

user_private_router = Router()


@user_private_router.message(
    or_f(
        Command("add_recipes"),
        (F.text.lower().contains("добавить рецепты файлом"))
    )
)
async def send_all_recipes(message: types.Message, session: AsyncSession):
    df = pd.read_excel('recipes.xlsx')

    for index, row in df.iterrows():
        recipe = Recipe(name=row['name'], photo=row['photo'], category=row['category'], recipe=row['recipe'])
        session.add(recipe)

    await session.commit()