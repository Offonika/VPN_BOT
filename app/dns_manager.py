import requests
from app.config import API_TOKEN, BASE_URL, DOMAIN_NAME
from app.config import SessionLocal
from db.models import Router

def create_subdomain(mac_address):
    """Создание поддомена для указанного MAC-адреса."""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    url = f"{BASE_URL}/domains/{DOMAIN_NAME}/subdomains"
    data = {
        "subdomain": f"{mac_address}"
    }
    
    print(f"Создание поддомена {mac_address}:")
    print(f"URL: {url}, Headers: {headers}, Data: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Ответ сервера: {response.status_code}, {response.text}")
        
        if response.status_code == 201:
            subdomain_id = response.json().get('subdomain', {}).get('id')
            print(f"Поддомен успешно создан. ID поддомена: {subdomain_id}")
            return subdomain_id
        elif response.status_code == 409:
            print("Поддомен уже существует.")
            return None
        else:
            print(f"Ошибка создания поддомена: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Ошибка при создании поддомена: {e}")
        return None

def create_dns_record(mac_address, ip_address, subdomain_id=None):
    """Создание DNS-записи для поддомена, используя его ID."""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    fqdn = f"{mac_address}.{DOMAIN_NAME}"
    url = f"{BASE_URL}/domains/{fqdn}/dns-records"
    
    data = {
        "type": "A",
        "value": ip_address
    }
    
    print(f"Создание DNS-записи для поддомена {mac_address}:")
    print(f"URL: {url}, Headers: {headers}, Data: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Ответ сервера: {response.status_code}, {response.text}")
        
        if response.status_code == 201:
            dns_record_id = response.json().get('dns_record', {}).get('id')
            print(f"DNS-запись успешно создана. ID записи: {dns_record_id}")
            return dns_record_id
        else:
            print(f"Ошибка создания DNS-записи: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Ошибка при создании DNS-записи: {e}")
        return None

def update_dns_record(mac_address, record_id, ip_address):
    """Обновление существующей DNS-записи для поддомена."""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    fqdn = f"{mac_address}.{DOMAIN_NAME}"
    url = f"{BASE_URL}/domains/{fqdn}/dns-records/{record_id}"
    
    data = {
        "type": "A",
        "value": ip_address
    }
    
    print(f"Обновление DNS-записи для поддомена {mac_address}:")
    print(f"URL: {url}, Headers: {headers}, Data: {data}")
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        print(f"Ответ сервера: {response.status_code}, {response.text}")
        
        if response.status_code == 200:
            print(f"DNS-запись для {mac_address} успешно обновлена на {ip_address}")
        else:
            print(f"Ошибка обновления DNS-записи: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Ошибка при обновлении DNS-записи: {e}")

def handle_dns_update(mac_address, ip_address):
    """Основная функция для обработки обновлений DNS."""
    session = SessionLocal()
    
    try:
        print(f"Начало обработки обновления DNS для роутера с MAC {mac_address}")
        
        router = session.query(Router).filter_by(mac_address=mac_address).first()
        if router is None:
            print(f"Роутер с MAC {mac_address} не найден.")
            return
        
        print(f"Проверка и/или создание поддомена для MAC {mac_address}.")
        
        subdomain_id = create_subdomain(mac_address)
        if subdomain_id is None:
            print(f"Поддомен уже существует или возникла ошибка при создании, продолжаем...")
        else:
            print(f"Поддомен для {mac_address} создан. ID: {subdomain_id}")
        
        if not router.dns_record_id:
            print(f"DNS-запись не найдена для {mac_address}, создаем новую DNS-запись...")
            dns_record_id = create_dns_record(mac_address, ip_address)
            if dns_record_id:
                router.dns_record_id = dns_record_id
                session.commit()
                print(f"DNS-запись успешно создана и сохранена. dns_record_id: {dns_record_id}")
            else:
                print(f"Ошибка создания DNS-записи для {mac_address}")
                return
        else:
            print(f"DNS-запись {router.dns_record_id} уже существует для {mac_address}, обновляем...")
            update_dns_record(mac_address, router.dns_record_id, ip_address)
            session.commit()
            print(f"DNS-запись успешно обновлена.")
    except Exception as e:
        session.rollback()
        print(f"Ошибка базы данных: {e}")
    finally:
        session.close()