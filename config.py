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

# Настройки VPN
VPN_ENDPOINT = "147.45.232.192:443"
VPN_DNS = "8.8.8.8"

# Настройки сети
BASE_IP = "10.20."

# Другие настройки по умолчанию
DEFAULT_LANGUAGE = "en"
TIME_ZONE = "UTC"
