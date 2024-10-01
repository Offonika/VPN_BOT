#config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Timeweb API Token и URL
API_TOKEN = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoidGVsZWludmVzMSIsInR5cGUiOiJhcGlfa2V5IiwicG9ydGFsX3Rva2VuIjoiNjM5MmJjMmEtMzBiZi00MmVkLThmMDAtMDdiNTMwYjhjZmM4IiwiYXBpX2tleV9pZCI6ImI1MjgyOGNiLWRkZWYtNGM5NC1iNTQ0LTg3YjRmMjQzNDE4NCIsImlhdCI6MTcyNjczNjgzMX0.KHAJmqPjrv93pq8g-v33N2JsrbXnpCFRHfRkLpiZGdomWsDGjGTJTlxneu_Lc35Hmp3qTa6qEbPxcByerwmK8jQ1b290GFeaiyO5RcZZ-xhSgqCOI2bL9AXRM0Fk2yM4o3dp22lP6LiRSAB77KorG7wbNJlrVFRqobd3eyNaKDUPqJWwZFHZsGpiZEgb4mesigp0S7y7HcCAoCZiuefqoXVu6HeSuyge1w33qJK7B1wO_P-3jRlNZxh0xTBC0y32GjR-VeVfAjHmEyzXTfIxl9TY37eKmBFlt7Z_iY8YA_rrMFJ_bHW3zc4GkfsufIHKmkroDaRHy6da_VRBRis-e8PPCxHDoRKp4AVsNconzkm_8q1dOMYmiOJOI3b0e5yVgONp7JR6-j5UsW9ikJ3cPgkSKJCGo5NEOJFc6FSq5qNfVfReSiLN2HhH6U2vH2-SJdBkhkJiyURAVEEWO4E5nQklXu6i9inyDBJIIX0XZ1fKEPFx2cyecNtqe-2Ldcjp'
BASE_URL = 'https://api.timeweb.cloud/api/v1'
DOMAIN_NAME = 'offonika.ru'

# Настройки подключения к базе данных
DATABASE_URL = 'mysql+pymysql://Office:e5nx3uUXAc1chklFsrb0@localhost/OffonikaBaza'

# SQLAlchemy настройки
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        'use_unicode': True,
        'init_command': "SET NAMES utf8mb4",
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

