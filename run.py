from app.api import app

if __name__ == "__main__":
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=5000, debug=True)
