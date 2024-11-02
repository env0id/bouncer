from sqlalchemy import select, update, func
from db import async_session_maker

from models.user import User
from services.language import LanguageService

class UserService:
  @staticmethod
  async def update_subscription(telegram_id: int, subscription_status: bool):
    async with async_session_maker() as session:
      user_from_db = await UserService.get_by_tgid(telegram_id)
      if user_from_db and user_from_db.subscription != subscription_status:
        stmt = update(User).where(User.telegram_id == telegram_id).values(subscription=subscription_status)
        await session.execute(stmt)
        await session.commit()

  @staticmethod
  async def is_exist(telegram_id: int) -> bool:
    async with async_session_maker() as session:
      stmt = select(User).where(User.telegram_id == telegram_id)
      is_exist = await session.execute(stmt)
      return is_exist.scalar() is not None

  @staticmethod
  async def get_next_user_id() -> int:
    async with async_session_maker() as session:
      query = select(User.id).order_by(User.id.desc()).limit(1)
      last_user_id = await session.execute(query)
      last_user_id = last_user_id.scalar()
      if last_user_id is None:
        return 0
      else:
        return int(last_user_id) + 1

  @staticmethod
  async def create(telegram_id: int, stripe_id: str, telegram_username: str):
    async with async_session_maker() as session:
      next_user_id = await UserService.get_next_user_id()
      new_user = User(
        id=next_user_id,
        telegram_id=telegram_id,
        stripe_id=stripe_id,
        telegram_username=telegram_username,
      )
      session.add(new_user)
      await session.commit()

  @staticmethod
  async def user_logged(telegram_id: int, stripe_id: str, telegram_username: str):
    is_exist = await UserService.is_exist(telegram_id)
    if is_exist is False:
      await UserService.create(telegram_id, stripe_id, telegram_username)
    else:
      await UserService.update_username(telegram_id, telegram_username)

  @staticmethod
  async def update_username(telegram_id: int, telegram_username: str):
    async with async_session_maker() as session:
      user_from_db = await UserService.get_by_tgid(telegram_id)
      if user_from_db and user_from_db.telegram_username != telegram_username:
        stmt = update(User).where(User.telegram_id == telegram_id).values(telegram_username=telegram_username)
        await session.execute(stmt)
        await session.commit()

  @staticmethod
  async def get_by_tgid(telegram_id: int) -> User:
    async with async_session_maker() as session:
      stmt = select(User).where(User.telegram_id == telegram_id)
      user_from_db = await session.execute(stmt)
      user_from_db = user_from_db.scalar()
      return user_from_db
    
  @staticmethod
  async def get_by_stid(stripe_id: int) -> User:
    async with async_session_maker() as session:
      stmt = select(User).where(User.stripe_id == stripe_id )
      user_from_db = await session.execute(stmt)
      user_from_db = user_from_db.scalar()
      return user_from_db

  @staticmethod
  async def update_language(telegram_id: int, language_code):
    async with async_session_maker() as session:
      user_from_db = await UserService.get_by_tgid(telegram_id)
      if user_from_db and user_from_db.language != language_code:
        stmt = update(User).where(User.telegram_id == telegram_id).values(language=language_code)
        await session.execute(stmt)
        await session.commit()

  @staticmethod
  async def get_all_users_count():
    async with async_session_maker() as session:
      stmt = func.count(User.id)
      users_count = await session.execute(stmt)
      return users_count.scalar()
 
  @staticmethod
  async def get_translations(telegram_id):
    user = await UserService.get_by_tgid(telegram_id)
    if user is None:
      return LanguageService.get_default_translation()
    return LanguageService.get_by_code(user.language)