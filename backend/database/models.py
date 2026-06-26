from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user") # 'admin' or 'user'
    organization = Column(String, nullable=True)

class Supplier(Base):
    __tablename__ = "suppliers"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    delivery_days = Column(Integer)
    rating = Column(Float)

class Inventory(Base):
    __tablename__ = "inventory"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    stock_level = Column(Integer)

class Route(Base):
    __tablename__ = "routes"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    distance_km = Column(Float)

class ProcurementHistory(Base):
    __tablename__ = "procurement_history"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    quantity = Column(Integer)
    selected_supplier = Column(String)
    total_cost = Column(Float)
    status = Column(String)

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    recommendation = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, index=True)
    product_name = Column(String)
    quantity = Column(Integer)
    supplier_name = Column(String)
    total_cost = Column(Float)
    status = Column(String)
    date = Column(String)

class RFQ(Base):
    __tablename__ = "rfqs"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(String, index=True)
    product_name = Column(String)
    quantity = Column(Integer)
    target_price = Column(Float)
    status = Column(String)

class ProcurementRequest(Base):
    __tablename__ = "procurement_requests_table"
    organization = Column(String, default="System")

    id = Column(Integer, primary_key=True, index=True)
    pr_id = Column(String, index=True)
    product_name = Column(String)
    quantity = Column(Integer)
    department = Column(String)
    status = Column(String)

