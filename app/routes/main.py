from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, get_flashed_messages
from app import db
from app.models import Inventory, Sales, SalesItem, Waste, Ingredient, Recipe, RecipeIngredient
from datetime import datetime, timezone

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return "RestoWebApp is running!"


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

@bp.route("/inventory")
def inventory_dashboard():
    from app.models import Ingredient
    ingredients = Ingredient.query.order_by(Ingredient.name).all()
    return render_template("inventory_dashboard.html", ingredients=ingredients)


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


@bp.route("/menu/add", methods=["GET", "POST"])
def add_menu_item():
    from app.models import MenuItem, Recipe, RecipeIngredient, Ingredient
    from datetime import datetime, timezone

    ingredients = Ingredient.query.order_by(Ingredient.name).all()

    if request.method == "POST":
        name = request.form.get("name")
        price = float(request.form.get("price"))

        # Create the MenuItem
        menu_item = MenuItem(name=name, price=price)
        db.session.add(menu_item)
        db.session.flush()  # get ID before creating recipe

        # Create associated Recipe
        recipe = Recipe(menu_item_id=menu_item.id)
        db.session.add(recipe)
        db.session.flush()

        # Loop through ingredients
        for ingredient in ingredients:
            qty_str = request.form.get(f"ingredient_{ingredient.id}")
            if qty_str:
                qty = float(qty_str)
                if qty > 0:
                    ri = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity_required=qty
                    )
                    db.session.add(ri)

        db.session.commit()
        flash("Menu item and recipe added!", "success")
        return redirect(url_for("main.inventory_dashboard"))

    return render_template("add_menu_item.html", ingredients=ingredients)

@bp.route("/ingredients/add", methods=["GET", "POST"])
def add_ingredient():
    from app.models import Ingredient

    if request.method == "POST":
        name = request.form.get("name").strip().lower()  # normalize
        quantity = float(request.form.get("quantity"))
        unit = request.form.get("unit")
        unit_cost = float(request.form.get("unit_cost"))

        # Check for duplicate
        existing = Ingredient.query.filter_by(name=name).first()
        if existing:
            flash(f"Ingredient '{name}' already exists!", "danger")
            return redirect(url_for("main.add_ingredient"))

        ingredient = Ingredient(
            name=name,
            quantity_in_stock=quantity,
            unit=unit,
            unit_cost=unit_cost
        )
        db.session.add(ingredient)
        db.session.commit()
        flash("Ingredient added!", "success")
        return redirect(url_for("main.inventory_dashboard"))

    return render_template("add_ingredient.html")

@bp.route("/ingredients/<ingredient_id>/edit", methods=["GET", "POST"])
def edit_ingredient(ingredient_id):
    from app.models import Ingredient
    ingredient = Ingredient.query.get_or_404(ingredient_id)

    if request.method == "POST":
        ingredient.name = request.form.get("name")
        ingredient.quantity_in_stock = float(request.form.get("quantity"))
        ingredient.unit = request.form.get("unit")
        ingredient.unit_cost = float(request.form.get("unit_cost"))
        db.session.commit()

        flash("Ingredient updated successfully", "success")
        return redirect(url_for("main.inventory_dashboard"))

    return render_template("edit_ingredient.html", ingredient=ingredient)


@bp.route("/ingredients/<ingredient_id>/delete", methods=["POST"])
def delete_ingredient(ingredient_id):
    from app.models import Ingredient
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    db.session.delete(ingredient)
    db.session.commit()
    flash("Ingredient deleted", "success")
    return redirect(url_for("main.inventory_dashboard"))
