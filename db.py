from pathlib import Path

from sqlalchemy import event, Engine, inspect, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import DB_NAME
from models.base import Base


url = f"sqlite+aiosqlite:///data/{DB_NAME}"
data_folder = Path("data")
if data_folder.exists() is False:
  data_folder.mkdir()
engine = create_async_engine(url, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
  cursor = dbapi_connection.cursor()
  cursor.execute("PRAGMA foreign_keys=ON")
  cursor.close()


async def check_all_tables_exist(db_engine):
  async with db_engine.begin() as conn:
    for table in Base.metadata.tables.values():
      result = await conn.execute(
        text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table.name}'"))
      if result.scalar() is None:
        return False
  return True


async def create_db_and_tables():
  async with engine.begin() as conn:
    if await check_all_tables_exist(engine):
      pass
    else:
      await conn.run_sync(Base.metadata.drop_all)
      await conn.run_sync(Base.metadata.create_all)
