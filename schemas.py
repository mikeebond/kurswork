# Модуль опису схем валідації даних (Pydantic)

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import List, Optional


# Схеми для Користувача (User)

class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    registration_date: date

    model_config = ConfigDict(from_attributes=True) # можливість читати дані прямо з SQLAlchemy моделі


# Схеми для Категорій (Category)

class CategoryCreate(BaseModel):
    category_name: str
    type: str = Field(..., pattern="^(income|expense)$")

class CategoryResponse(CategoryCreate):
    category_id: int
    model_config = ConfigDict(from_attributes=True)


# Схеми для Тегів (Tag)

class TagCreate(BaseModel):
    tag_name: str

class TagResponse(TagCreate):
    tag_id: int
    model_config = ConfigDict(from_attributes=True)


# Схеми для Рахунків (Account)

class AccountCreate(BaseModel):
    currency_code: str = Field(..., min_length=3, max_length=3)
    account_name: str
    balance: float = 0.0

class AccountResponse(AccountCreate):
    account_id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


# Схеми для Транзакцій (Transaction)
# Схема для ПРИЙОМУ даних з браузера
class TransactionCreate(BaseModel):
    amount: float
    description: str
    category_id: int
    account_id: int

# Схема для ВІДПРАВКИ даних назад у браузер
class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    category_id: int
    account_id: int

    class Config:
        orm_mode = True  # Дозволяє читати дані з SQLAlchemy бази
        from_attributes = True