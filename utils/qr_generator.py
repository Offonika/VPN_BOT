# utils/qr_generator.py

import qrcode
import os
import logging

def generate_qr_code(config_content: str, client_id: str, output_directory: str = "qr_codes") -> str:
    """
    Генерирует QR-код из содержимого конфигурационного файла WireGuard и сохраняет его в указанной директории.

    Args:
        config_content (str): Содержимое конфигурационного файла WireGuard.
        client_id (str): Уникальный идентификатор клиента для создания уникального имени файла.
        output_directory (str): Директория, в которой будет сохранен QR-код.

    Returns:
        str: Путь к сгенерированному файлу QR-кода.

    Raises:
        Exception: Если не удалось создать QR-код.
    """
    try:
        # Создание директории для QR-кодов, если она не существует
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            logging.info(f"Output directory {output_directory} created.")

        # Уникальное имя файла для QR-кода
        qr_code_path = os.path.join(output_directory, f"vpn_config_qr_{client_id}.png")

        # Генерация QR-кода
        qr = qrcode.make(config_content)
        qr.save(qr_code_path)
        logging.info(f"QR code generated and saved to {qr_code_path}.")

        return qr_code_path

    except Exception as e:
        logging.error(f"Failed to generate QR code: {e}")
        raise Exception(f"Не удалось создать QR-код: {e}")
