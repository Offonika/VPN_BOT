import requests

API_KEY = 'ВeyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoidGVsZWludmVzMSIsInR5cGUiOiJhcGlfa2V5IiwicG9ydGFsX3Rva2VuIjoiNjM5MjY1NzAtN2I2MS00OWE2LThjNTUtY2UyOTMzNTlhZTMwIiwiYXBpX2tleV9pZCI6IjZjZjJjMjBlLTYwMTItNGI3My04M2NmLTRkMDJjODc4MjU3MiIsImlhdCI6MTcyNTA3MzYwOX0.QerD6Iv6tpphmxE9VxzcsuqTRZ0K4zguLK1ZN3v6WeesVTNAwbxSNdd_UDCM3UeiWqKqHmN29y1qdxdKIOQPgQEBhh8u5Wce8H8hDeuIkMhZtd0cUR44ibg5AmEC8csCF-T-uipM3XAUJo0dDMWVpR8a_sKEV_H1sCsjBdtfXFV0TbNCZndM-iOeuGs9BsxKHpTZnfTxc35Ep1tAE0zSHavP_K9ZJZFV8SPsUDEQjOnLuURxsidch8xnYV9D2SPQHFIZq9Umt7NDOviRP2O9ITonCIWiYk-T8NZGlP1dvbnfSxCugJtk-gv6ZGOIVc0_7WLgB2xTuTqax5R-dRcyd3EMfNcZqUxmmnsyH2rMMhBxqWU084xFKx03uIsQEX8x_I77UqAc9wbkV-5Y-tHTp08_34JA5orXliXvGmt5tkXAgP0wqIvoFGvsRSx3nXV7S7rMqdYOfybsWprupLBu3-yBgjuUtVnVvz8TikpP_ZJVHsibUi68D-ARhKkBhP1J'
ZONE_ID = 'Ваш_ZONE_ID'  # Если используется
RECORD_ID = 'Ваш_RECORD_ID'
DOMAIN = 'offonika.ru'
SUBDOMAIN = 'router1'  # Поддомен для роутера

def update_dns_record(ip):
    url = f"https://api.timeweb.com/v1/domains/{ZONE_ID}/records/{RECORD_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": f"{SUBDOMAIN}.{DOMAIN}",
        "content": ip,
        "ttl": 300
    }

    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"DNS record for {SUBDOMAIN}.{DOMAIN} updated to {ip}")
    else:
        print(f"Failed to update DNS record: {response.status_code} - {response.text}")

# Пример использования
current_ip = "185.125.202.151"  # Получите IP автоматически
update_dns_record(current_ip)
