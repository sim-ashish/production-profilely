from datetime import datetime
from app.config.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(128), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    def get_context(self):
        return f'{self.email}{self.updated_at}'.strip()
