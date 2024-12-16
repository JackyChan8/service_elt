from sqlalchemy import select, exists, update, null
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.models import InsuranceElt, Insurance


async def check_exist_insurance(calc_reso_id: int, session: AsyncSession):
    result = await session.execute(
        select(exists(Insurance.id).where(Insurance.calc_reso_id == calc_reso_id))
    )
    return result.scalar()


async def get_all_insurance_accept(calc_id: int, session: AsyncSession):
    """
        Get Insurance Elt
    """
    query = (
        select(InsuranceElt)
        .where(
            InsuranceElt.calc_id == calc_id,
            InsuranceElt.Error == null(),
        )
    )
    result = await session.execute(query)
    return result.scalars().all()


async def create_insurance_elt(calc_id: int, calc_reso_id: int, rl_actions_data: dict, data: list, session: AsyncSession):
    """
        Create Insurance Elt
    """
    try:
        # Создание Страхования
        new_insurance = Insurance(
            calc_id=int(calc_id),
            calc_reso_id=calc_reso_id,
            quote_id=rl_actions_data.get('quote_id'),
            police_id=rl_actions_data.get('police_id'),
        )
        session.add(new_insurance)
        await session.commit()

        # Добавление ELT Котировок
        for company_data in data:
            for company_name, company_info in company_data.items():
                insurance_data = company_info['data']
                payment_periods = insurance_data.get('PaymentPeriods')
                insurance_elt = InsuranceElt(
                    calc_id=int(calc_id),
                    insurance_id=new_insurance.id,
                    insurance_name=company_name,
                    RequestId=insurance_data.get('RequestId'),
                    SKCalcId=insurance_data.get('SKCalcId'),
                    Message=insurance_data.get('Message'),
                    Error=insurance_data.get('Error'),
                    PremiumSum=insurance_data.get('PremiumSum'),
                    KASKOSum=insurance_data.get('KASKOSum'),
                    DOSum=insurance_data.get('DOSum'),
                    GOSum=insurance_data.get('GOSum'),
                    NSSum=insurance_data.get('NSSum'),
                    GAPSum=insurance_data.get('GAPSum'),
                    TotalFranchise=insurance_data.get('TotalFranchise'),
                    payments_period=payment_periods.get('PaymentPeriod') if payment_periods else None,
                )
                session.add(insurance_elt)

        # Подтвердите изменения в базе данных
        await session.commit()
    except Exception as exc:
        logger.error(exc)


async def update_insurance(calc_id: int, values: dict, session: AsyncSession):
    """
        Update Insurance
    """
    query = (
        update(Insurance)
        .where(Insurance.calc_id == calc_id)
        .values(**values)
        .execution_options(synchronize_session='fetch')
    )
    await session.execute(query)
    await session.commit()


async def delete_insurance_by_calc_reso_id(calc_reso_id: int, session: AsyncSession):
    try:
        # Получаем объект Insurance по calc_reso_id
        result = await session.execute(
            select(Insurance).filter(Insurance.calc_reso_id == calc_reso_id)
        )

        insurance = result.scalars().one()  # Получаем единственный объект Insurance

        # Удаляем объект Insurance
        await session.delete(insurance)

        # Сохраняем изменения в базе данных
        await session.commit()
    except Exception as e:
        # В случае ошибки откатываем транзакцию
        await session.rollback()
        print(f"An error occurred: {e}")
