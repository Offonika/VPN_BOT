# db/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from dotenv import load_dotenv
from config import MONGO_URI

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройки для PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Проверьте, что SQLALCHEMY_DATABASE_URL не равно None
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the .env file.")

# Создание двигателя для подключения к базе данных PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание фабрики сессий (sessionmaker), которая будет создавать новые сессии для взаимодействия с базой данных PostgreSQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для всех моделей данных (классов, представляющих таблицы в базе данных)
Base = declarative_base()

# Настройки для MongoDB
client = MongoClient(MONGO_URI)
mongo_db = client.get_database()  # Это подключит вас к базе данных 'vpn_bot'

# Проверка подключения к MongoDB
try:
    # Пробуем получить список коллекций
    mongo_db.list_collection_names()
    print("Подключение к MongoDB успешно установлено.")
except Exception as e:
    raise ValueError(f"Не удалось подключиться к MongoDB: {e}")
