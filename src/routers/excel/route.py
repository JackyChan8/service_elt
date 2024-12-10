import pandas as pd

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends,UploadFile, File, status

from src.routers.excel import (
    schemas,
    services,
)
from src.database import get_async_session
from src.schemas import schemas as global_schemas
from src.exceptions import exceptions as global_exceptions


router = APIRouter(prefix='/excel', tags=['excel'])


@router.post(path='/parse_excel',
             status_code=status.HTTP_201_CREATED,
             responses={
                 status.HTTP_201_CREATED: {
                     'description': 'Данные успешно добавленны',
                     'content': {
                         'application/json': {
                             'schema': {
                                 'type': 'object',
                                 'properties': {'detail': 'string'}
                             }
                         }
                     }
                 },
                 status.HTTP_500_INTERNAL_SERVER_ERROR: {
                     'description': 'Произошла ошибка при добавлении данных',
                     'content': {
                         'application/json': {
                             'schema': {
                                 'type': 'object',
                                 'properties': {'detail': 'string'}
                             }
                         }
                     }
                 },
             },
             description='Parse Cars from Excel File')
async def parse_cars_from_excel(file: UploadFile = File(...),
                                session: AsyncSession = Depends(get_async_session)):
    """
        Parse Cars From Excel File
    """

    # Чтение файла Excel
    df = pd.read_excel(file.file)

    # Заменяем пустые строки на None
    df = df.where(pd.notnull(df), None)

    # Преобразование DataFrame в список словарей
    data = df.to_dict(orient='records')

    data = [schemas.CarsCreate(**item) for item in data]

    # Добавление в БД
    result = await services.add_cars_to_db(data, session)
    if result:
        raise global_exceptions.MyHTTPException(
            status=global_schemas.StatusResponseEnum.SUCCESS,
            status_code=status.HTTP_201_CREATED,
            message='Данные успешно добавленны',
        )
    raise global_exceptions.MyHTTPException(
        status=global_schemas.StatusResponseEnum.ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message='Произошла ошибка при добавлении данных',
    )
