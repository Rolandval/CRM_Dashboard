import requests
from datetime import datetime
    
def get_unitalk_data(api_key: str) -> dict:
    url = "https://api.unitalk.cloud/api/history/get"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Дати тільки за сьогодні
    today = datetime.now().strftime("%Y-%m-%d")
    date_from = f"{today} 00:00:00"
    date_to = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Пропущені дзвінки (на які не відповіли)
    missed_payload = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "limit": 100,
        "offset": 0,
        "filter": {
            "direction": "IN",
            "answered": False,
        }
    }
    missed_resp = requests.post(url, headers=headers, json=missed_payload)
    missed_calls = missed_resp.json()

    # Втрачені дзвінки (пропущені, на які не передзвонили)
    lost_payload = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "limit": 100,
        "offset": 0,
        "filter": {
            "direction": "IN",
            "lost": True,
        }
    }
    lost_resp = requests.post(url, headers=headers, json=lost_payload)
    lost_calls = lost_resp.json()

    missed_phones = set()
    lost_phones = set()

    missed_data = missed_calls['calls']
    for data in missed_data:
        phone_number = data['from']
        missed_phones.add(phone_number)


    lost_data = lost_calls['calls']
    for data in lost_data:
        phone_number = data['from']
        lost_phones.add(phone_number)

    unique_missed_phones_count = len(missed_phones)
    unique_lost_phones_count = len(lost_phones)

    return {
        'missed_calls': missed_calls['count'],
        'lost_calls': lost_calls['count'],
        'unique_missed_phones': unique_missed_phones_count,
        'unique_lost_phones': unique_lost_phones_count
    }
