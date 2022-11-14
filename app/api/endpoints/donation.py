from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.dontaion import donation_crud
from app.models import Donation, User
from app.schemas.donation import DonationCreate, DonationDB, DonationDBAll
from app.services.transaction import transaction

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationDBAll],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session)
) -> List[Donation]:
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=List[DonationDB],
    response_model_exclude_none=True
)
async def get_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
) -> Donation:
    return await donation_crud.get_dontaions_by_user(session=session, user=user)


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
) -> Donation:
    dontaion = await donation_crud.create(donation, session, user)
    investment = await transaction(dontaion, session)
    if investment:
        session.add_all([*investment, dontaion])
        await session.commit()
        await session.refresh(dontaion)
    return dontaion