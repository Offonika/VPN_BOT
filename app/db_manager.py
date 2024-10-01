#db_manager.py
from app.config import SessionLocal
from sqlalchemy import text
from app.config import SessionLocal
from app.models import Router  # Импорт модели Router

def save_to_database(mac_address, subdomain_full, record_id):
    """Сохранение данных о роутере и его DNS-записи в базу данных."""
    session = SessionLocal()
    try:
        session.execute("""
            INSERT INTO routers (mac_address, subdomain, dns_record_id)
            VALUES (:mac_address, :subdomain_full, :record_id)
            ON DUPLICATE KEY UPDATE subdomain = :subdomain_full, dns_record_id = :record_id
        """, {'mac_address': mac_address, 'subdomain_full': subdomain_full, 'record_id': record_id})
        session.commit()
    except Exception as e:
        print(f"Ошибка при сохранении в базу: {e}")
    finally:
        session.close()

def get_routers_from_db():
    """Получение списка роутеров из базы данных."""
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT mac_address, subdomain, dns_record_id FROM routers"))
        return result.fetchall()
    except Exception as e:
        print(f"Ошибка получения роутеров: {e}")
        return []
    finally:
        session.close()


