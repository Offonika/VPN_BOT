# barcode_scanner.py

from PIL import Image
import requests
from io import BytesIO
import pytesseract
import os
from dotenv import load_dotenv
from PIL import Image
import pytesseract
from io import BytesIO


load_dotenv()

async def scan_label(file_data):
    """Сканирует этикетку на изображении и извлекает данные."""
    try:
        # Открываем изображение
        img = Image.open(file_data)

        # Применяем OCR для извлечения текста
        text = pytesseract.image_to_string(img, lang='eng')

        # Логика извлечения серийного номера и модели из текста
        # Можно использовать регулярные выражения или строковые методы
        print("Распознанный текст:", text)

        # Предположим, что мы извлекаем серийный номер и модель
        serial_number = "не найден"  # Пример: замените логикой извлечения серийного номера
        model = "не найден"  # Пример: замените логикой извлечения модели
        return {"serial_number": serial_number, "model": model}
    except Exception as e:
        print(f"Ошибка при распознавании изображения: {e}")
        return None

def extract_serial_number(text):
    # Реализуйте логику для извлечения серийного номера
    return "SN123456789"

def extract_model(text):
    # Реализуйте логику для извлечения модели устройства
    return "Model XYZ"
