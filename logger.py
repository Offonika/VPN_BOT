# logger.py
import logging
import os

# Установка пути для лог-файла
log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'bot.log')

# Создание директории для логов, если она не существует
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Настройка формата логов
log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(log_file_path),  # Логи в файл
        logging.StreamHandler()              # Логи в консоль
    ]
)

# Создание отдельного логгера для проекта
logger = logging.getLogger('VPN_BOT')
