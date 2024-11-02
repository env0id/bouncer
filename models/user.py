from sqlalchemy import Column, Integer, DateTime, String, Boolean, Float, func, ForeignKey
from sqlalchemy.orm import relationship, backref

from services.language import LanguageService
from models.base import Base


class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True)
  telegram_username = Column(String, unique=True)
  telegram_id = Column(Integer, nullable=False)
  stripe_id = Column(Integer, nullable=False)
  subscription = Column(Boolean, default=False)
  registered_at = Column(DateTime, default=func.now())
  language = Column(String, default=LanguageService.get_default_code())
