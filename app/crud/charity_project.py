from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    @staticmethod
    async def get_charity_project_id_by_name(
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_charity_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_charity_project_id.scalars().first()

    @staticmethod
    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession
    ) -> List[Dict[str, str]]:
        projects = await session.execute(
            select(CharityProject).where(CharityProject.fully_invested)
        )
        return projects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
