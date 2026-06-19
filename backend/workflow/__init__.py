from typing import TypedDict, Any, List

class GraphState(TypedDict):
    product_name: str
    quantity: int
    destination: str
    required_delivery_days: int
    
    # DB data
    current_stock: int
    suppliers_data: List[dict]
    routes_data: List[dict]
    
    # Agent Outputs
    inventory_result: dict
    supplier_result: dict
    risk_result: dict
    logistics_result: dict
    procurement_result: dict
    coordinator_result: dict
