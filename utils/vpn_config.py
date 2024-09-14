import subprocess
import logging
from sqlalchemy.orm import Session
from db.models import VpnClient
import config  # Импортируем настройки из config.py
import os
from pymongo import MongoClient
from datetime import datetime
from db.mongodb import get_mongo_collection
from db.models import User
from utils.ip_manager import get_free_ip
from bson.objectid import ObjectId

# Настройка логирования
logging.basicConfig(filename='mongo_operations.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def generate_vpn_keys():
    """
    Генерирует приватный и публичный ключи для нового клиента VPN.
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
    """
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
    Добавляет или обновляет клиента в конфигурационном файле WireGuard (wg0.conf).
    """
    remove_vpn_user(client.public_key)
    add_vpn_user(client.public_key, client.address)


def check_wireguard_status():
    """
    Проверяет состояние сервера WireGuard.
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
    """
    Сохраняет конфигурацию клиента VPN в MongoDB.
    """
    collection = get_mongo_collection('vpn_configs')

    existing_doc = collection.find_one({"telegram_id": telegram_id})
    if existing_doc:
        logging.info(f"Конфигурация для пользователя {telegram_id} уже существует в MongoDB.")
        return existing_doc['_id']

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


def update_vpn_client_config(session: Session, telegram_id: int):
    """
    Обновляет конфигурацию клиента в PostgreSQL, MongoDB и WireGuard.
    """
    try:
        # Получаем клиента из PostgreSQL по Telegram ID
        client = session.query(VpnClient).join(User).filter(User.telegram_id == telegram_id).first()
        if not client:
            logging.error(f"Клиент с Telegram ID {telegram_id} не найден в PostgreSQL.")
            return

        # Проверяем наличие клиента в WireGuard
        client_in_wg = get_client_info_from_wg(client.public_key)
        if not client_in_wg:
            logging.info(f"Клиент {client.public_key} не найден в WireGuard. Создаем запись.")
            private_key, public_key = generate_vpn_keys()
            ip_address = get_free_ip(session)
            client.private_key = private_key
            client.public_key = public_key
            client.address = ip_address
            session.commit()
        else:
            logging.info(f"Клиент найден в WireGuard с IP {client_in_wg['ip_address']}.")
            client.address = client_in_wg['ip_address']
            session.commit()

        config_content = generate_vpn_config(client)

        # Сохраняем новую конфигурацию в MongoDB
        config_file_id = save_config_to_mongodb(config_content, telegram_id)
        client.config_file_id = str(config_file_id)  # Обновляем config_file_id в PostgreSQL
        session.commit()  # Сохраняем изменения в PostgreSQL

        add_client_to_wg_config(client)
        logging.info(f"Конфигурация для клиента с Telegram ID {telegram_id} обновлена.")

    except Exception as e:
        logging.error(f"Ошибка при обновлении конфигурации клиента: {e}")




def update_config_in_mongodb(client, config_content):
    """
    Обновление конфигурации клиента в MongoDB.
    """
    collection = get_mongo_collection('vpn_configs')
    
    if client.config_file_id:
        existing_doc = collection.find_one({"_id": ObjectId(client.config_file_id)})
        if existing_doc:
            collection.update_one(
                {"_id": ObjectId(client.config_file_id)},
                {"$set": {"config": config_content, "updated_at": datetime.utcnow()}}
            )
        else:
            result = collection.insert_one({
                "telegram_id": client.user.telegram_id,
                "config": config_content,
                "created_at": datetime.utcnow()
            })
            client.config_file_id = str(result.inserted_id)
    else:
        result = collection.insert_one({
            "telegram_id": client.user.telegram_id,
            "config": config_content,
            "created_at": datetime.utcnow()
        })
        client.config_file_id = str(result.inserted_id)


def get_client_info_from_wg(public_key: str):
    """
    Получает информацию о клиенте из WireGuard.
    """
    try:
        result = subprocess.run(['wg', 'show', 'wg0', 'allowed-ips'], stdout=subprocess.PIPE)
        output = result.stdout.decode().strip()

        for line in output.splitlines():
            if public_key in line:
                parts = line.split()
                if len(parts) >= 3:
                    return {"public_key": public_key, "ip_address": parts[1]}
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при получении информации о клиенте из WireGuard: {e}")
        return None
