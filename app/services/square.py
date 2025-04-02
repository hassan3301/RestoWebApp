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

def get_order_details(order_id):
    url = f"{SQUARE_BASE_URL}/orders/{order_id}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("order", {})
    else:
        print(f"Error getting order {order_id}:", response.status_code, response.text)
        return {}
    
def get_sales_with_items():
    url = f"{SQUARE_BASE_URL}/payments"
    params = {
        "location_id": SQUARE_LOCATION_ID,
        "sort_order": "DESC",
        "limit": 10  # Adjust as needed
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return []

    payments = response.json().get("payments", [])
    detailed_sales = []

    for payment in payments:
        sale = {
            "payment_id": payment["id"],
            "amount": int(payment["amount_money"]["amount"]) / 100.0,
            "sale_date": payment["created_at"],
            "items": []
        }

        order_id = payment.get("order_id")
        if order_id:
            order = get_order_details(order_id)
            for item in order.get("line_items", []):
                sale["items"].append({
                    "name": item["name"],
                    "quantity": float(item["quantity"]),
                    "total": int(item["total_money"]["amount"]) / 100.0
                })

        detailed_sales.append(sale)

    return detailed_sales
