# utils/vpn_config.py

import subprocess
import logging
from sqlalchemy.orm import Session
from db.models import VpnClient

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
        str: Путь к созданному конфигурационному файлу.
    """
    config_content = f"""
[Interface]
PrivateKey = {client.private_key}
Address = {client.address}/32
DNS = {client.dns}

[Peer]
PublicKey = {client.public_key}
Endpoint = {client.endpoint}
AllowedIPs = {client.allowed_ips}
PersistentKeepalive = {client.persistent_keepalive}
"""
    
    config_path = f"/etc/wireguard/configs/{client.telegram_id}.conf"

    try:
        with open(config_path, 'w') as config_file:
            config_file.write(config_content)
        logging.info(f"VPN configuration file generated at {config_path}.")
        return config_path
    except IOError as e:
        logging.error(f"Failed to write VPN configuration file: {e}")
        raise Exception(f"Не удалось создать конфигурационный файл VPN: {e}")

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
