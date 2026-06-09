from sqlalchemy import Column, Integer, String, Text
from .base import BASE


class ItemRequest(BASE):
    __tablename__ = "item_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    request_type = Column(String, nullable=False)
    data = Column(Text, nullable=False)
    status = Column(String, default="pending")
