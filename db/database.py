# db/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение URL базы данных из переменной окружения
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Проверьте, что SQLALCHEMY_DATABASE_URL не равно None
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the .env file.")

# Создание двигателя для подключения к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание фабрики сессий (sessionmaker), которая будет создавать новые сессии для взаимодействия с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для всех моделей данных (классов, представляющих таблицы в базе данных)
Base = declarative_base()

