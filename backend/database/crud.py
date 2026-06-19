from sqlalchemy.orm import Session
from . import models, database

import pandas as pd
import os

def init_db(db: Session):
    # Create tables
    models.Base.metadata.create_all(bind=database.engine)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data")
    
    if db.query(models.Supplier).count() == 0 and os.path.exists(os.path.join(data_dir, "suppliers.csv")):
        df = pd.read_csv(os.path.join(data_dir, "suppliers.csv"))
        for _, row in df.iterrows():
            db.add(models.Supplier(**row.to_dict()))
        db.commit()

    if db.query(models.Route).count() == 0 and os.path.exists(os.path.join(data_dir, "routes.csv")):
        df = pd.read_csv(os.path.join(data_dir, "routes.csv"))
        for _, row in df.iterrows():
            db.add(models.Route(**row.to_dict()))
        db.commit()

    if db.query(models.Inventory).count() == 0 and os.path.exists(os.path.join(data_dir, "inventory.csv")):
        df = pd.read_csv(os.path.join(data_dir, "inventory.csv"))
        for _, row in df.iterrows():
            db.add(models.Inventory(**row.to_dict()))
        db.commit()

    if db.query(models.Order).count() == 0 and os.path.exists(os.path.join(data_dir, "orders.csv")):
        df = pd.read_csv(os.path.join(data_dir, "orders.csv"))
        for _, row in df.iterrows():
            db.add(models.Order(**row.to_dict()))
        db.commit()

    if db.query(models.RFQ).count() == 0 and os.path.exists(os.path.join(data_dir, "rfq.csv")):
        df = pd.read_csv(os.path.join(data_dir, "rfq.csv"))
        for _, row in df.iterrows():
            db.add(models.RFQ(**row.to_dict()))
        db.commit()

    if db.query(models.ProcurementRequest).count() == 0 and os.path.exists(os.path.join(data_dir, "procurement_requests.csv")):
        df = pd.read_csv(os.path.join(data_dir, "procurement_requests.csv"))
        for _, row in df.iterrows():
            db.add(models.ProcurementRequest(**row.to_dict()))
        db.commit()


def get_suppliers(db: Session):
    return db.query(models.Supplier).all()

def get_routes(db: Session):
    return db.query(models.Route).all()

from sqlalchemy import func

def get_inventory(db: Session, product_name: str):
    # Use ilike for case-insensitive matching. We also strip trailing 's' to help with basic plurals.
    search_term = product_name.lower().strip()
    if search_term.endswith('s'):
        search_term = search_term[:-1]
    
    return db.query(models.Inventory).filter(
        func.lower(models.Inventory.product_name).contains(search_term)
    ).first()

def get_all_inventory(db: Session):
    return db.query(models.Inventory).all()

def get_procurement_history(db: Session):
    return db.query(models.ProcurementHistory).all()

def create_procurement_history(db: Session, history_data: dict):
    db_history = models.ProcurementHistory(**history_data)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def insert_suppliers_from_df(db: Session, df):
    required = {'name'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected at least: {required}")
    # Upsert logic based on name
    for _, row in df.iterrows():
        existing = db.query(models.Supplier).filter_by(name=row['name']).first()
        if existing:
            existing.price = row.get('price', existing.price)
            existing.delivery_days = row.get('delivery_days', existing.delivery_days)
            existing.rating = row.get('rating', existing.rating)
        else:
            new_sup = models.Supplier(
                name=row['name'],
                price=row.get('price', 0),
                delivery_days=row.get('delivery_days', 0),
                rating=row.get('rating', 0.0)
            )
            db.add(new_sup)
    db.commit()

def insert_routes_from_df(db: Session, df):
    required = {'name'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected at least: {required}")
    for _, row in df.iterrows():
        existing = db.query(models.Route).filter_by(name=row['name']).first()
        if existing:
            existing.distance_km = row.get('distance_km', existing.distance_km)
        else:
            new_route = models.Route(
                name=row['name'],
                distance_km=row.get('distance_km', 0)
            )
            db.add(new_route)
    db.commit()

def insert_inventory_from_df(db: Session, df):
    required = {'product_name'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected at least: {required}")
    for _, row in df.iterrows():
        existing = db.query(models.Inventory).filter_by(product_name=row['product_name']).first()
        if existing:
            existing.stock_level = row.get('stock_level', existing.stock_level)
        else:
            new_inv = models.Inventory(
                product_name=row['product_name'],
                stock_level=row.get('stock_level', 0)
            )
            db.add(new_inv)
    db.commit()

def get_recommendation_history(db: Session, limit: int = 100):
    return db.query(models.RecommendationHistory).order_by(models.RecommendationHistory.created_at.desc()).limit(limit).all()

def create_recommendation_history(db: Session, agent_name: str, recommendation: str):
    db_history = models.RecommendationHistory(agent_name=agent_name, recommendation=recommendation)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_orders(db: Session):
    return db.query(models.Order).all()

def update_order_status(db: Session, order_id: str, status: str):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order
