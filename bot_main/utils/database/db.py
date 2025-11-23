from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", " ")

# Создаём async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async сессии
AsyncSessionLocal = sessionmaker(bind=engine,expire_on_commit=False,class_=AsyncSession)

# Базовый класс для моделей
Base = declarative_base()
