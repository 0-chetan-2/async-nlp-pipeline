from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg://",
)

engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)