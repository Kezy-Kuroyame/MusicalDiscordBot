from sqlalchemy import Column, Integer, String, BigInteger, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(BigInteger, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

class TrackHistory(Base):
    __tablename__ = "track_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=True)  # можно None, если трек включен без конкретного пользователя
    guild_id = Column(BigInteger, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    duration = Column(Float, nullable=True)
    played_at = Column(DateTime(timezone=True), server_default=func.now())
