# utils/qr_generator.py
import logging
from sqlalchemy.orm import Session
from db.models import VpnClient

# Импортируем настройки из config.py
import config

def get_free_ip(session: Session) -> str:
    """
    Функция для получения следующего доступного IP-адреса в диапазоне.

    Args:
        session (Session): Сессия SQLAlchemy для доступа к базе данных.

    Returns:
        str: Свободный IP-адрес.

    Raises:
        Exception: Если нет доступных IP-адресов.
    """
    logging.info("Starting search for a free IP address.")
    
    # Получаем базовый IP-адрес из config.py
    base_ip = config.BASE_IP

    # Перебор IP-адресов в указанном диапазоне
    for i in range(0, 256):
        for j in range(1, 256):
            ip = f"{base_ip}{i}.{j}"
            # Проверяем, используется ли IP-адрес в базе данных
            if not session.query(VpnClient).filter(VpnClient.address == ip).first():
                logging.info(f"Found free IP address: {ip}")
                return ip

    # Если не найден ни один свободный IP-адрес, логируем ошибку и выбрасываем исключение
    logging.error("No free IP addresses available in the range.")
    raise Exception("Нет свободных IP-адресов в диапазоне.")

