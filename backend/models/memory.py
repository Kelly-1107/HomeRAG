from sqlalchemy import Column, String, JSON, Integer, DateTime
from datetime import datetime

from db.sqlite import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True, nullable=False)
    raw_text = Column(String, nullable=False)
    type = Column(String, nullable=False)  # item / consumption / emotion / other
    structured_data = Column(JSON, nullable=False)
    embedding = Column(String, nullable=True)  # 存储为 JSON 字符串
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
