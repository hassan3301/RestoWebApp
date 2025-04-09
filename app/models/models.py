from app import db
from datetime import datetime, timezone
import uuid

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Sales(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    sale_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)

    # For tracking item-wise sales
    items = db.relationship('SalesItem', backref='sale', lazy=True)

class SalesItem(db.Model):
    __tablename__ = 'sales_item'

    id = db.Column(db.String(50), primary_key=True, default = lambda: str(uuid.uuid4()))
    sale_id = db.Column(db.String(50), db.ForeignKey('sales.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    quantity_sold = db.Column(db.Float, nullable=False)

class Waste(db.Model):
    __tablename__ = 'waste'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    quantity_in_stock = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # e.g., grams, ml, units
    unit_cost = db.Column(db.Float, nullable=False)


class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    menu_item_id = db.Column(db.String(50), db.ForeignKey('menu_item.id'), nullable=False)
    menu_item = db.relationship('MenuItem', back_populates='recipe')

    ingredients = db.relationship('RecipeIngredient', back_populates='recipe', cascade="all, delete-orphan")



class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipe_id = db.Column(db.String(50), db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.String(50), db.ForeignKey('ingredient.id'), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)

    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient')

class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)

    # One-to-one with Recipe
    recipe = db.relationship("Recipe", back_populates="menu_item", uselist=False)
