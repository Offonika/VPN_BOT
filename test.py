from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["vpn_bot"]
collection = db["vpn_configs"]

try:
    documents_count = collection.count_documents({})
    
    if documents_count == 0:
        print("Документы не найдены")
    else:
        for doc in collection.find():
            print(doc)
except Exception as e:
    print(f"Ошибка при попытке найти документы: {e}")
