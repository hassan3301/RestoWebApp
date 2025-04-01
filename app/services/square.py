import requests
import os

SQUARE_BASE_URL = "https://connect.squareupsandbox.com/v2"
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_SANDBOX_TOKEN")
SQUARE_LOCATION_ID = os.getenv("SQUARE_SANDBOX_LOCATION_ID")

HEADERS = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Square-Version": "2023-12-13"
}

def get_payments(start_date=None, end_date=None):
    url = f"{SQUARE_BASE_URL}/payments"
    
    params = {
        "location_id": SQUARE_LOCATION_ID,
        "sort_order": "DESC",
    }

    if start_date:
        params["begin_time"] = start_date  # e.g. '2024-01-01T00:00:00Z'
    if end_date:
        params["end_time"] = end_date

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json().get("payments", [])
    else:
        print("Error:", response.status_code, response.text)
        return []
