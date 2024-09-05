# /mnt/data/mongodb.py

from pymongo import MongoClient
import config
import logging

# Настройка логирования
logging.basicConfig(filename='mongo_operations.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Подключение к MongoDB с использованием URI из config.py
client = MongoClient(config.MONGO_URI)
db = client.get_database()

def get_mongo_collection(collection_name):
    """
    Получение коллекции из базы данных MongoDB.
    :param collection_name: Имя коллекции.
    :return: Коллекция MongoDB.
    """
    logging.info(f"Получение коллекции: {collection_name}")
    return db[collection_name]
