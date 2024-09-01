# utils/qr_generator.pyimport qrcode

def generate_qr_code(data: str, client_id: int) -> str:
    """
    Функция для генерации QR-кода.

    Args:
        data (str): Данные, которые будут закодированы в QR-коде.
        client_id (int): Идентификатор клиента, используемый для именования файла.

    Returns:
        str: Путь к сгенерированному файлу QR-кода.
    """
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Создаем изображение QR-кода
    img = qr.make_image(fill='black', back_color='white')

    # Генерируем путь для сохранения файла
    qr_code_path = f"configs/qr_{client_id}.png"
    
    # Сохраняем изображение
    img.save(qr_code_path)
    
    return qr_code_path
