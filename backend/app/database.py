import random
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

master_engine = create_async_engine(settings.db_master_url, echo=False)
MasterSession = async_sessionmaker(master_engine, class_=AsyncSession, expire_on_commit=False)

replica_engines = [create_async_engine(url, echo=False) for url in settings.replica_url_list]
replica_sessions = [
    async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    for engine in replica_engines
]


async def get_master_session():
    async with MasterSession() as session:
        yield session


async def get_replica_session():
    session_maker = random.choice(replica_sessions)
    async with session_maker() as session:
        yield session
