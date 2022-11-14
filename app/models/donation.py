from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.modified_base import ModifiedBase


class Donation(ModifiedBase):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text, nullable=True)
