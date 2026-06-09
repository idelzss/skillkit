from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BASE


class Profession(BASE):
    __tablename__ = "professions"

    id = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

    category = relationship("Category", back_populates="professions")
    software = relationship("Software", back_populates="profession", cascade="all, delete-orphan")
