from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.excel import schemas


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
