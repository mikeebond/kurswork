from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from pydantic import BaseModel
import bcrypt
from jose import JWTError, jwt

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wallet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- НАЛАШТУВАННЯ БЕЗПЕКИ (JWT) ---
SECRET_KEY = "super-secret-key-for-kursova"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


class UserCreate(BaseModel):
    email: str
    password: str


# 1. Реєстрація нового користувача
@app.post("/api/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Користувач з таким email вже існує")

    # --- ШИФРУВАННЯ  ---
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')

    new_user = models.User(email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "Успішно зареєстровано!"}


# 2. Логін та видача Токена
@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    # --- ПЕРЕВІРКА ПАРОЛЯ ---
    if not user:
        raise HTTPException(status_code=400, detail="Неправильний email або пароль")

    is_password_correct = bcrypt.checkpw(
        form_data.password.encode('utf-8'),
        user.hashed_password.encode('utf-8')
    )

    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Неправильний email або пароль")

    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


# --- СХЕМА ДЛЯ РАХУНКУ ---
class AccountCreate(BaseModel):
    name: str
    initial_balance: float


# --- ФУНКЦІЯ ПЕРЕВІРКИ АВТОРИЗАЦІЇ ---
# Функція читає токен з браузера і знаходить користувача в базі
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Недійсний токен або ви не авторизовані",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Розшифровка токену
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    #Пошук користувача по email
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# --- ЕНДПОІНТИ ДЛЯ РАХУНКІВ ---

# 1. Створення нового рахуноку
@app.post("/api/accounts/")
def create_account(account: AccountCreate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    new_account = models.Account(
        name=account.name,
        initial_balance=account.initial_balance,
        user_id=current_user.id  # Прив'язка рахунок до того, хто онлайн
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


# 2. Отримати всі рахунки ПОТОЧНОГО користувача
@app.get("/api/accounts/")
def get_accounts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    accounts = db.query(models.Account).filter(models.Account.user_id == current_user.id).all()
    return accounts


# РОУТИ (ENDPOINTS)


# 5. Створення нової транзакції (POST)
@app.post("/api/transactions/", response_model=schemas.TransactionResponse, status_code=201)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):

    # Створення об'єкту транзакції для бази даних
    db_transaction = models.Transaction(
        account_id=transaction.account_id,
        category_id=transaction.category_id,
        amount=transaction.amount,
        description=transaction.description
    )

    db.add(db_transaction)  # Додавання в сесію
    db.commit()  # коміт
    db.refresh(db_transaction)  # Оновлення для ID

    return db_transaction


# 6. Отримання списку всіх транзакцій (GET)
@app.get("/api/transactions/", response_model=list[schemas.TransactionResponse])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = db.query(models.Transaction).offset(skip).limit(limit).all()
    return transactions

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    # 1. Пошук рахунку у базі
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Рахунок не знайдено")

    db.query(models.Transaction).filter(models.Transaction.account_id == account_id).delete()
    db.delete(account)
    db.commit()
    return {"message": "Рахунок та його транзакції успішно видалено"}

# Видалення транзакції
@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    tx = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Транзакцію не знайдено")
    db.delete(tx)
    db.commit()
    return {"message": "Транзакцію успішно видалено"}