# app/auth.py

# Пример проверки API-токенов (здесь может быть любая ваша логика проверки)
def check_token(token):
    # Список валидных токенов (это просто пример, в реальном проекте токены могут храниться в базе данных)
    valid_tokens = ["token_for_router1", "token_for_router2"]

    # Проверка, что токен валиден
    if token and token.split(" ")[1] in valid_tokens:
        return True
    return False
