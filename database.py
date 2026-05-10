# Модуль підключення до бази даних PostgreSQL

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345@localhost:5432/myweb_budget"
# Створення engine для спілкування з БД
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Фабрика сесій (дозволяє створювати тимчасові сесії для кожного запиту)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)