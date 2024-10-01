# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Настройка URL базы данных из переменной окружения или напрямую
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://Admin:0F9CS7NPxKpOYV1DCzm7q@localhost/OffonikaBaza')

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Создание двигателя для взаимодействия с базой данных MySQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание локальной сессии базы данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()

# Функция для создания базы данных
def init_db():
    """
    Инициализация базы данных: создание таблиц.
    """
    Base.metadata.create_all(bind=engine)

# Функция для получения сессии базы данных
def get_db():
    """
    Функция, создающая сессию для работы с базой данных.
    Используйте этот метод для получения доступа к базе данных в функциях.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

