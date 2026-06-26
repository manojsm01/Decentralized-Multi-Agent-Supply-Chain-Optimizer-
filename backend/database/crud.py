from sqlalchemy.orm import Session
from . import models, database
import bcrypt

import pandas as pd
import os

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def init_db(db: Session):
    # Create tables
    models.Base.metadata.create_all(bind=database.engine)
    
    # Initialize default admin user if no users exist
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_user:
        admin = models.User(
            username="admin",
            hashed_password=get_password_hash("password123"),
            role="admin",
            organization="System"
        )
        db.add(admin)
        db.commit()
    
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


def get_suppliers(db: Session, org: str):
    return db.query(models.Supplier).filter(models.Supplier.organization == org).all()

def get_routes(db: Session, org: str):
    return db.query(models.Route).filter(models.Route.organization == org).all()

from sqlalchemy import func

def get_inventory(db: Session, product_name: str, org: str):
    search_term = product_name.lower().strip()
    if search_term.endswith('s'):
        search_term = search_term[:-1]
    
    return db.query(models.Inventory).filter(
        func.lower(models.Inventory.product_name).contains(search_term),
        models.Inventory.organization == org
    ).first()

def get_all_inventory(db: Session, org: str):
    return db.query(models.Inventory).filter(models.Inventory.organization == org).all()

def get_procurement_history(db: Session, org: str):
    return db.query(models.ProcurementHistory).filter(models.ProcurementHistory.organization == org).all()

def create_procurement_history(db: Session, history_data: dict, org: str):
    history_data['organization'] = org
    db_history = models.ProcurementHistory(**history_data)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def insert_suppliers_from_df(db: Session, df, org: str):
    required = {'name'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected at least: {required}")
    # Upsert logic based on name
    for _, row in df.iterrows():
        existing = db.query(models.Supplier).filter_by(name=row['name'], organization=org).first()
        if existing:
            existing.price = row.get('price', existing.price)
            existing.delivery_days = row.get('delivery_days', existing.delivery_days)
            existing.rating = row.get('rating', existing.rating)
        else:
            new_sup = models.Supplier(
                name=row['name'],
                price=row.get('price', 0),
                delivery_days=row.get('delivery_days', 0),
                rating=row.get('rating', 0.0),
                organization=org
            )
            db.add(new_sup)
    db.commit()

def insert_routes_from_df(db: Session, df, org: str):
    required = {'name'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected at least: {required}")
    for _, row in df.iterrows():
        existing = db.query(models.Route).filter_by(name=row['name'], organization=org).first()
        if existing:
            existing.distance_km = row.get('distance_km', existing.distance_km)
        else:
            new_route = models.Route(
                name=row['name'],
                distance_km=row.get('distance_km', 0),
                organization=org
            )
            db.add(new_route)
    db.commit()

def insert_inventory_from_df(db: Session, df, org: str):
    required = {'product_name'}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected at least: {required}")
    for _, row in df.iterrows():
        existing = db.query(models.Inventory).filter_by(product_name=row['product_name'], organization=org).first()
        if existing:
            existing.stock_level = row.get('stock_level', existing.stock_level)
        else:
            new_inv = models.Inventory(
                product_name=row['product_name'],
                stock_level=row.get('stock_level', 0),
                organization=org
            )
            db.add(new_inv)
    db.commit()

def get_recommendation_history(db: Session, org: str, skip: int = 0, limit: int = 100):
    # Assuming timestamp was changed to created_at in models, wait let's use created_at
    return db.query(models.RecommendationHistory).filter(models.RecommendationHistory.organization == org).order_by(models.RecommendationHistory.created_at.desc()).offset(skip).limit(limit).all()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: dict):
    hashed_password = get_password_hash(user["password"])
    db_user = models.User(
        username=user["username"],
        hashed_password=hashed_password,
        role=user.get("role", "user"),
        organization=user.get("organization")
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_recommendation_history(db: Session, agent_name: str, recommendation: str, org: str):
    db_history = models.RecommendationHistory(agent_name=agent_name, recommendation=recommendation, organization=org)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def create_order(db: Session, order_data: dict, org: str):
    order_data['organization'] = org
    db_order = models.Order(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, org: str):
    return db.query(models.Order).filter(models.Order.organization == org).all()

def update_order_status(db: Session, order_id: str, status: str, org: str):
    order = db.query(models.Order).filter(models.Order.order_id == order_id, models.Order.organization == org).first()
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order


def get_all_users(db: Session):
    return db.query(models.User).all()

def update_user(db: Session, username: str, update_data: dict):
    db_user = get_user_by_username(db, username)
    if db_user:
        if 'role' in update_data and update_data['role'] is not None:
            db_user.role = update_data['role']
        if 'organization' in update_data and update_data['organization'] is not None:
            db_user.organization = update_data['organization']
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, username: str):
    db_user = get_user_by_username(db, username)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def update_user_profile(db: Session, current_username: str, new_username: str = None, new_password: str = None):
    db_user = get_user_by_username(db, current_username)
    if not db_user:
        return None
        
    if new_username and new_username != current_username:
        # Check if username is already taken
        existing_user = get_user_by_username(db, new_username)
        if existing_user:
            raise ValueError("Username already taken")
        db_user.username = new_username
        
    if new_password:
        db_user.hashed_password = get_password_hash(new_password)
        
    db.commit()
    db.refresh(db_user)
    return db_user
