from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BASE


class Category(BASE):
    __tablename__ = "categories"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    professions = relationship("Profession", back_populates="category", cascade="all, delete-orphan")
