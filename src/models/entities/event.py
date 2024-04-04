from sqlalchemy import Column, Integer, String

from ..settings.base import Base

class Event(Base):
    __tablename__ = 'tb_events'

    id  = Column(String, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    slug = Column(String)
    details = Column(String, nullable=False)
    maximum_attendees = Column(Integer)

