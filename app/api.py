from flask import Flask, request, jsonify
from app.auth import check_token
from app.dns_manager import handle_dns_update  # Импорт функции для обработки обновлений DNS
from app.config import DOMAIN_NAME, SessionLocal  # Импортируем SessionLocal из config.py
from db.models import Router  # Импортируем модели напрямую

app = Flask(__name__)

@app.route('/update_dns', methods=['POST'])
def update_dns():
    """Обработчик для обновления DNS-записи через POST-запрос от роутера."""
    auth_header = request.headers.get('Authorization')

    router = check_token(auth_header)
    if router is None:
        return jsonify({"error": "Unauthorized"}), 401

    ip_address = request.json.get('ip')
    if not ip_address:
        return jsonify({"error": "IP address is missing"}), 400

    session = SessionLocal()
    try:
        handle_dns_update(router.mac_address, ip_address)
        session.commit()
        return jsonify({"message": "DNS record updated successfully"}), 200
    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
        session.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        session.close()

def check_token(auth_header):
    print(f"Received auth_header: {auth_header}")
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        print(f"Extracted token: {token}")
        session = SessionLocal()
        router = session.query(Router).filter_by(auth_token=token).first()
        session.close()
        if router:
            print(f"Router found: {router.serial_number}")
        else:
            print("Router not found or token is invalid.")
        return router if router else None
    print("Authorization header missing or malformed.")
    return None

@app.route('/some_secure_endpoint', methods=['POST'])
def secure_endpoint():
    router = check_token(request.headers.get('Authorization'))
    if not router:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"message": "Authorized", "router": router.serial_number})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)