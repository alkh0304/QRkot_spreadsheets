from sqlalchemy import Column, String, Text

from app.models.modified_base import ModifiedBase


class CharityProject(ModifiedBase):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
