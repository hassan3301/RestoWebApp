from app import db
from app.models import Sales, SalesItem, Inventory
from .square import get_sales_with_items
from datetime import datetime

def sync_sales_from_square():
    sales = get_sales_with_items()
    if not sales:
        print("No sales data returned from Square.")
        return

    for s in sales:
        try:
            # Check for existing sale
            existing = Sales.query.filter_by(id=s["payment_id"]).first()
            if existing:
                continue

            # Parse the sale date (handle timezone-aware datetime)
            sale_date = datetime.strptime(
                s["sale_date"].split('.')[0],  # Remove microseconds if present
                '%Y-%m-%dT%H:%M:%S'
            ).date()

            new_sale = Sales(
                id=s["payment_id"],
                sale_date=sale_date,
                total_amount=s["amount"]
            )
            db.session.add(new_sale)
            db.session.flush()

            for item in s["items"]:
                sale_item = SalesItem(
                    sale_id=new_sale.id,
                    item_name=item["name"],
                    quantity_sold=item["quantity"]
                )
                db.session.add(sale_item)

                # Deduct from inventory
                inventory_item = Inventory.query.filter_by(item_name=item["name"]).first()
                if inventory_item:
                    inventory_item.quantity -= item["quantity"]

        except Exception as e:
            db.session.rollback()
            print(f"Error processing sale {s.get('payment_id', '[unknown]')}: {e}")

    db.session.commit()
    print(f"{len(sales)} Square sales synced.")

