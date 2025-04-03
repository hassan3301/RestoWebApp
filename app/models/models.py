from app import db
from datetime import datetime, timezone
import uuid

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.String(50), primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Sales(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.String(50), primary_key=True)
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

    id = db.Column(db.String(50), primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
