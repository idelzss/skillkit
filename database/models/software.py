from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BASE


class Software(BASE):
    __tablename__ = "software"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profession_id = Column(String, ForeignKey("professions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String)
    desc = Column(String)
    feature = Column(String)
    url = Column(String)
    youtube_tutorial = Column(String)

    profession = relationship("Profession", back_populates="software")
