from pyzbar.pyzbar import decode
from PIL import Image
import requests
from io import BytesIO

async def scan_barcode(file_id):
    file_url = f'https://api.telegram.org/file/bot<TOKEN>/{file_id}'
    response = requests.get(file_url)
    img = Image.open(BytesIO(response.content))
    barcode = decode(img)

    if barcode:
        return {
            'serial_number': barcode.data.decode("utf-8"),
            'model': 'Model XYZ',  # Здесь используйте реальные данные
            'vpn_config': 'VPN Config',
            'admin_access': 'Admin Access Details'
        }
    else:
        return None
