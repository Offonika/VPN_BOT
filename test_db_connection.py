import asyncio
import asyncpg

async def test_connection():
    conn = None
    try:
        conn = await asyncpg.connect(
            user='vpn_bot_user',  # измените 'vpnuser' на 'vpn_bot_user'
            password='yfhnn;e54o98hhbvg',  # тот же пароль, который вы установили
            host='147.45.232.192',
            port='5432',
            database='vpn_db'
        )
        print("Подключение установлено успешно!")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
    finally:
        if conn:
            await conn.close()

asyncio.run(test_connection())
