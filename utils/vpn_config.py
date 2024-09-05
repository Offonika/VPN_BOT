import subprocess
import logging
from sqlalchemy.orm import Session
from db.models import VpnClient
import config  # Импортируем настройки из config.py
import os
from pymongo import MongoClient
from datetime import datetime
from db.mongodb import get_mongo_collection

# Настройка логирования
logging.basicConfig(filename='mongo_operations.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def generate_vpn_keys():
    """
    Генерирует приватный и публичный ключи для нового клиента VPN.

    Returns:
        tuple: (private_key, public_key)

    Raises:
        Exception: Если не удалось сгенерировать ключи.
    """
    try:
        private_key = subprocess.run(["wg", "genkey"], stdout=subprocess.PIPE, check=True).stdout.decode().strip()
        public_key = subprocess.run(["wg", "pubkey"], input=private_key.encode(), stdout=subprocess.PIPE, check=True).stdout.decode().strip()
        logging.info("VPN keys generated successfully.")
        return private_key, public_key
    except subprocess.CalledProcessError as e:
        logging.error(f"Error generating VPN keys: {e}")
        raise Exception("Не удалось сгенерировать ключи VPN.")

def add_vpn_user(public_key: str, ip_address: str):
    """
    Добавляет нового VPN пользователя в конфигурацию WireGuard.
    
    Args:
        public_key (str): Публичный ключ нового клиента.
        ip_address (str): IP-адрес, выделенный для нового клиента.
    
    Returns:
        bool: True, если команда выполнена успешно, иначе False.
    """
    try:
        command = f"wg set wg0 peer {public_key} allowed-ips {ip_address}/32"
        result = subprocess.run(command, shell=True, check=True)
        logging.info(f"VPN user added with public key: {public_key} and IP: {ip_address}.")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to add VPN user: {e}")
        return False

def remove_vpn_user(public_key: str):
    """
    Удаляет VPN пользователя из конфигурации WireGuard.
    
    Args:
        public_key (str): Публичный ключ клиента для удаления.
    
    Returns:
        bool: True, если команда выполнена успешно, иначе False.
    """
    try:
        command = f"wg set wg0 peer {public_key} remove"
        result = subprocess.run(command, shell=True, check=True)
        logging.info(f"VPN user removed with public key: {public_key}.")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to remove VPN user: {e}")
        return False

def restart_wireguard():
    """
    Перезапускает сервис WireGuard для применения изменений.
    
    Returns:
        bool: True, если сервис успешно перезапущен, иначе False.
    """
    try:
        result = subprocess.run(['systemctl', 'restart', 'wg-quick@wg0'], check=True)
        logging.info("WireGuard service restarted successfully.")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart WireGuard service: {e}")
        return False


def generate_vpn_config(client: VpnClient):
    """
    Генерирует конфигурационный файл WireGuard для нового клиента.
    
    Args:
        client (VpnClient): Объект клиента VPN.
    
    Returns:
        str: Конфигурационный файл в виде строки.
    """
    # Чтение публичного ключа сервера из конфигурационного файла
    with open("/etc/wireguard/server_publickey", "r") as f:
        server_public_key = f.read().strip()

    config_content = f"""
[Interface]
PrivateKey = {client.private_key}
Address = {client.address}/32
DNS = {client.dns}

[Peer]
PublicKey = {server_public_key}
AllowedIPs = 0.0.0.0/0
Endpoint = {client.endpoint}
PersistentKeepalive = 25
"""
    return config_content


def add_client_to_wg_config(client: VpnClient):
    """
    Добавляет нового клиента в конфигурационный файл WireGuard (wg0.conf).
    
    Args:
        client (VpnClient): Объект клиента VPN.
    """
    # Чтение публичного ключа клиента
    client_public_key = client.public_key
    
    wg_config_path = '/etc/wireguard/wg0.conf'  # Путь к конфигурационному файлу WireGuard
    
    new_peer_config = f"""
[Peer] # Клиент {client.id} ({client.user.username})
PublicKey = {client_public_key}
AllowedIPs = {client.address}/32
"""
    
    try:
        with open(wg_config_path, 'a') as wg_config_file:  # Открываем файл в режиме добавления
            wg_config_file.write(new_peer_config)
        logging.info(f"Added new client to WireGuard config: {client.address}")
    except IOError as e:
        logging.error(f"Failed to add new client to WireGuard config: {e}")
        raise Exception(f"Не удалось добавить нового клиента в конфигурацию WireGuard: {e}")


def check_wireguard_status():
    """
    Проверяет состояние сервера WireGuard.
    
    Returns:
        bool: True, если сервер активен, иначе False.
    """
    try:
        result = subprocess.run(['systemctl', 'is-active', 'wg-quick@wg0'], stdout=subprocess.PIPE, check=True)
        is_active = result.stdout.strip() == b'active'
        logging.info(f"WireGuard status is {'active' if is_active else 'inactive'}.")
        return is_active
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to check WireGuard status: {e}")
        return False

def save_config_to_mongodb(config_content: str, telegram_id: int):
    collection = get_mongo_collection('vpn_configs')

    # Логирование поиска документа
    logging.info(f"Поиск существующей конфигурации для пользователя {telegram_id}")
    existing_doc = collection.find_one({"telegram_id": telegram_id})
    if existing_doc:
        logging.info(f"Конфигурация для пользователя {telegram_id} уже существует в MongoDB.")
        return existing_doc['_id']  # Возвращаем существующий ObjectId

    # Логирование вставки нового документа
    document = {
        "telegram_id": telegram_id,
        "config": config_content,
        "created_at": datetime.utcnow()
    }

    try:
        result = collection.insert_one(document)
        logging.info(f"Конфигурация сохранена в MongoDB с ID {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logging.error(f"Ошибка при сохранении конфигурации в MongoDB для пользователя {telegram_id}: {e}")
        raise

