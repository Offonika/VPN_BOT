import os

# Определение базовой директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Определение пути для конфигурационных файлов
CONFIG_PATH_BASE = os.path.join(BASE_DIR, 'configs')

# Создание директории, если она не существует
if not os.path.exists(CONFIG_PATH_BASE):
    os.makedirs(CONFIG_PATH_BASE)
    print(f"Директория {CONFIG_PATH_BASE} была создана.")

# Другие настройки
QR_CODE_OUTPUT_DIR = os.path.join(BASE_DIR, 'qr_codes')

# Создание директории для QR-кодов, если она не существует
if not os.path.exists(QR_CODE_OUTPUT_DIR):
    os.makedirs(QR_CODE_OUTPUT_DIR)
    print(f"Директория {QR_CODE_OUTPUT_DIR} была создана.")

# Функция для чтения параметров из файла wg0.conf
def read_wg_config(file_path):
    config = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config

# Путь к файлу WireGuard
WG_CONFIG_PATH = "/etc/wireguard/wg0.conf"

# Чтение конфигурации WireGuard
wg_config = read_wg_config(WG_CONFIG_PATH)

# Получение VPN_ENDPOINT из конфигурации WireGuard
VPN_ENDPOINT = wg_config.get("Endpoint", "147.45.232.192:8443")
VPN_DNS = "8.8.8.8"  # Этот параметр можно оставить фиксированным или тоже парсить, если он есть в конфигурации

# Настройки сети
BASE_IP = "10.20."

# MongoDB URI
MONGO_URI = "mongodb://localhost:27017/vpn_bot"

# Другие настройки по умолчанию
DEFAULT_LANGUAGE = "en"
TIME_ZONE = "UTC"

print(f"VPN Endpoint: {VPN_ENDPOINT}")
