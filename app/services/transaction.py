from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject, Donation


async def close_investment(
    data: Union[CharityProject, Donation]
) -> None:
    data.fully_invested = True
    data.close_date = datetime.now()


async def transaction(
    objects: Union[Donation, CharityProject],
    session: AsyncSession
):
    targets = await CRUDBase.get_investment_ready(
        CharityProject if isinstance(objects, Donation) else Donation,
        session
    )
    if not targets:
        return None
    a = 0
    while a < len(targets):
        obj_balance = objects.full_amount - objects.invested_amount
        target_balance = targets[a].full_amount - targets[a].invested_amount
        investment = min(obj_balance, target_balance)
        for source in (objects, targets[a]):
            source.invested_amount += investment
            if source.full_amount == source.invested_amount:
                await close_investment(source)
                a += 1
        if objects.fully_invested:
            break
    return targets
