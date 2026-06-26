from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserUpdate(BaseModel):
    role: Optional[str] = None
    organization: Optional[str] = None

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class UserProfileUpdateResponse(BaseModel):
    user: "UserResponse"
    access_token: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    organization: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    organization: Optional[str] = None

class OptimizationRequest(BaseModel):
    product_name: str
    quantity: int
    destination: str
    required_delivery_days: int

class OptimizationResponse(BaseModel):
    product_name: str
    requested_quantity: int
    inventory_analysis: str
    selected_supplier: str
    risk_level: str
    recommended_route: str
    total_cost: float
    procurement_summary: str

class SupplierSchema(BaseModel):
    id: int
    name: str
    price: float
    delivery_days: int
    rating: float

    class Config:
        from_attributes = True

class RouteSchema(BaseModel):
    id: int
    name: str
    distance_km: float

    class Config:
        from_attributes = True

class ProcurementHistorySchema(BaseModel):
    id: int
    product_name: str
    quantity: int
    selected_supplier: str
    total_cost: float
    status: str

    class Config:
        from_attributes = True

class InventorySchema(BaseModel):
    id: int
    product_name: str
    stock_level: int

    class Config:
        from_attributes = True

class ForecastRequest(BaseModel):
    product_name: str
    quantity: int

class ForecastResponse(BaseModel):
    analysis: str
    quantity_to_order: int

class SupplierRequest(BaseModel):
    required_delivery_days: int

class SupplierResponse(BaseModel):
    selected_supplier_name: str
    price: float
    delivery_days: int
    rating: float
    analysis: str

class InventoryRequest(BaseModel):
    product_name: str
    required_quantity: int
    current_stock: int

class InventoryResponse(BaseModel):
    needs_procurement: bool
    analysis: str
    quantity_to_order: int

class RouteRequest(BaseModel):
    destination: str

class RouteResponse(BaseModel):
    recommended_route_name: str
    distance_km: float
    analysis: str

class RiskRequest(BaseModel):
    supplier_name: str
    delivery_days: int
    required_delivery_days: int

class RiskResponse(BaseModel):
    risk_level: str
    reasoning: str

class ProcurementRequest(BaseModel):
    product_name: str
    quantity_to_order: int
    supplier_name: str
    supplier_price: float
    risk_level: str
    route_name: str

class ProcurementResponse(BaseModel):
    recommendation: str
    total_cost: float
    analysis: str

class RecommendationHistorySchema(BaseModel):
    id: int
    agent_name: str
    recommendation: str
    created_at: datetime

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    order_id: str
    product_name: str
    quantity: int
    supplier_name: str
    total_cost: float
    status: str
    date: str

class OrderSchema(BaseModel):
    id: int
    order_id: str
    product_name: str
    quantity: int
    supplier_name: str
    total_cost: float
    status: str
    date: str

    class Config:
        from_attributes = True

class OrderStatusUpdateRequest(BaseModel):
    status: str
