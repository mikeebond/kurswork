# Модуль опису моделей бази даних (SQLAlchemy)

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "app_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    accounts = relationship("Account", back_populates="owner")

class Account(Base):
    __tablename__ = "app_accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    initial_balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("app_users.id"))
    owner = relationship("User", back_populates="accounts")

class Transaction(Base):
    __tablename__ = "app_transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String)
    category_id = Column(Integer)

    # Зовнішній ключ для зв'язку з рахунком
    account_id = Column(Integer, ForeignKey("app_accounts.id"))
    account = relationship("Account")


