from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.logger import logger
from src.models import InsuranceElt


async def get_all_insurance_elt(session: AsyncSession):
    result = await session.execute(select(InsuranceElt))
    return result.scalars().all()

async def create_insurance_elt(calc_id: int, data: list, session: AsyncSession):
    """
        Create Insurance Elt
    """
    try:
        for company_data in data:
            for company_name, company_info in company_data.items():
                insurance_data = company_info['data']
                insurance_elt = InsuranceElt(
                    insurance_id=int(calc_id),
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
                    TotalFranchise=insurance_data.get('TotalFranchise')
                )
                session.add(insurance_elt)

        # Подтвердите изменения в базе данных
        await session.commit()
    except Exception as exc:
        logger.error(exc)
