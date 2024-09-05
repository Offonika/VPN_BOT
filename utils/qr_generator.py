# utils/qr_generator.py
import qrcode
import os

def generate_qr_code(data, client_id):
    """
    Генерирует QR-код для заданных данных и сохраняет его в файл.

    Args:
        data (str): Данные для кодирования в QR-код.
        client_id (int): Идентификатор клиента для создания уникального имени файла.

    Returns:
        str: Путь к сохраненному изображению QR-кода.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Путь для сохранения QR-кода
    qr_code_path = f"/var/www/html/configs/{client_id}_qrcode.png"
    img.save(qr_code_path)

    return qr_code_path
