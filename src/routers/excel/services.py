from sqlalchemy import text, select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.excel import schemas
from src.models import Cars


async def add_cars_to_db(data: list[schemas.CarsCreate], session: AsyncSession):
    """
        Add Cars
    """
    try:
        data_execute = [item.model_dump() for item in data]
        insert_stmt = text("INSERT INTO cars (brand, model, modif, sk_brand, sk_model, type) VALUES (:brand, :model, :modif, :sk_brand, :sk_model, :type) ON CONFLICT DO NOTHING")
        await session.execute(insert_stmt, data_execute)
        await session.commit()
        return True
    except:
        return False


async def find_car_info(brand: str, model: str, session: AsyncSession):
    """
        Get Car
    """
    query = select(Cars).where(
        and_(
            func.lower(Cars.brand) == brand.lower(),
            func.lower(Cars.model) == model.lower()
        )
    )

    # Выполняем запрос и получаем первый найденный объект
    result = await session.execute(query)
    car = result.scalars().first()  # Получаем только первый найденный объект

    # Если объект найден, возвращаем его поля brand и model
    if car:
        return {
            "brand": car.brand,
            "model": car.model
        }
    return None
