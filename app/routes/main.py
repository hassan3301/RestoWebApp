from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, get_flashed_messages
from app import db
from app.models import Inventory, Sales, SalesItem, Waste
from datetime import datetime, timezone

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return "RestoWebApp is running!"

@bp.route('/inventory', methods=['GET'])
def get_inventory():
    inventory = Inventory.query.all()
    data = [
        {
            'id': item.id,
            'item_name': item.item_name,
            'quantity': item.quantity,
            'unit_cost': item.unit_cost,
            'last_updated': item.last_updated.isoformat()
        }
        for item in inventory
    ]
    return jsonify(data), 200


# --- Waste Logging ---

@bp.route('/waste', methods=['POST'])
def log_waste():
    data = request.json
    waste = Waste(
        item_name=data['item_name'],
        quantity=data['quantity'],
        reason=data.get('reason', ''),
        timestamp=datetime.now(timezone.utc)
    )

    # Deduct from inventory if exists
    inventory_item = Inventory.query.filter_by(item_name=data['item_name']).first()
    if inventory_item:
        inventory_item.quantity -= data['quantity']

    db.session.add(waste)
    db.session.commit()
    return jsonify({'message': 'Waste logged'}), 201

# --- Sales Logging ---

@bp.route('/sales', methods=['POST'])
def record_sale():
    data = request.json
    sale = Sales(
        sale_date=datetime.strptime(data['sale_date'], '%Y-%m-%d').date(),
        total_amount=data['total_amount']
    )
    db.session.add(sale)
    db.session.commit()

    for item in data['items']:
        sale_item = SalesItem(
            sale_id=sale.id,
            item_name=item['item_name'],
            quantity_sold=item['quantity_sold']
        )
        db.session.add(sale_item)

        # Deduct from inventory
        inventory_item = Inventory.query.filter_by(item_name=item['item_name']).first()
        if inventory_item:
            inventory_item.quantity -= item['quantity_sold']

    db.session.commit()
    return jsonify({'message': 'Sale recorded'}), 201

@bp.route('/sales', methods=['GET'])
def get_sales():
    sales = Sales.query.all()
    data = [
        {
            'id': sale.id,
            'sale_date': sale.sale_date.isoformat(),
            'total_amount': sale.total_amount,
            'items': [
                {
                    'item_name': item.item_name,
                    'quantity_sold': item.quantity_sold
                } for item in sale.items
            ]
        }
        for sale in sales
    ]
    return jsonify(data), 200

@bp.route("/sales_dashboard")
def sales_dashboard():
    sales = Sales.query.order_by(Sales.sale_date.desc()).all()
    return render_template("sales_dashboard.html", sales=sales)

@bp.route("/inventory_dashboard")
def inventory_dashboard():
    inventory = Inventory.query.order_by(Inventory.item_name).all()
    return render_template("inventory_dashboard.html", inventory=inventory)

@bp.route("/inventory/add", methods=["GET", "POST"])
def add_inventory_item():
    if request.method == "POST":
        item_name = request.form.get("item_name")
        quantity = float(request.form.get("quantity"))
        unit_cost = float(request.form.get("unit_cost"))

        from datetime import datetime, timezone
        new_item = Inventory(
            item_name=item_name,
            quantity=quantity,
            unit_cost=unit_cost,
            last_updated=datetime.now(timezone.utc)
        )
        db.session.add(new_item)
        db.session.commit()

        flash("Inventory item added!", "success")
        return redirect(url_for("main.inventory_dashboard"))

    return render_template("add_inventory.html")

@bp.route("/inventory/<item_id>/edit", methods=["GET", "POST"])
def edit_inventory_item(item_id):
    item = Inventory.query.get_or_404(item_id)

    if request.method == "POST":
        item.item_name = request.form["item_name"]
        item.quantity = float(request.form["quantity"])
        item.unit_cost = float(request.form["unit_cost"])

        from datetime import datetime, timezone
        item.last_updated = datetime.now(timezone.utc)

        db.session.commit()
        flash("Item updated successfully", "success")
        return redirect(url_for("main.inventory_dashboard"))

    return render_template("edit_inventory.html", item=item)


@bp.route("/inventory/<item_id>/delete", methods=["POST"])
def delete_inventory_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted", "success")
    return redirect(url_for("main.inventory_dashboard"))