from langgraph.graph import StateGraph, END
from . import GraphState
from backend.agents.inventory import run_inventory_agent
from backend.agents.supplier import run_supplier_agent
from backend.agents.risk import run_risk_agent
from backend.agents.logistics import run_logistics_agent
from backend.agents.procurement import run_procurement_agent
from backend.agents.coordinator import run_coordinator_agent

import time

def inventory_node(state: GraphState):
    time.sleep(2)
    result = run_inventory_agent(
        product_name=state["product_name"],
        required_quantity=state["quantity"],
        current_stock=state["current_stock"]
    )
    return {"inventory_result": result}

def supplier_node(state: GraphState):
    time.sleep(2)
    # If inventory says no procurement needed, we might still proceed for the sake of the project flow, 
    # but let's assume we always evaluate suppliers for the requested quantity.
    result = run_supplier_agent(
        suppliers_data=state["suppliers_data"],
        required_delivery_days=state["required_delivery_days"]
    )
    return {"supplier_result": result}

def risk_node(state: GraphState):
    time.sleep(2)
    supplier_info = state.get("supplier_result", {})
    supplier_name = supplier_info.get("selected_supplier_name", "Unknown")
    delivery_days = supplier_info.get("delivery_days", 0)
    
    result = run_risk_agent(
        supplier_name=supplier_name,
        delivery_days=delivery_days,
        required_delivery_days=state["required_delivery_days"]
    )
    return {"risk_result": result}

def logistics_node(state: GraphState):
    time.sleep(2)
    result = run_logistics_agent(
        routes_data=state["routes_data"],
        destination=state["destination"]
    )
    return {"logistics_result": result}

def procurement_node(state: GraphState):
    time.sleep(2)
    inv_info = state.get("inventory_result", {})
    quantity_to_order = inv_info.get("quantity_to_order", state["quantity"])
    
    supp_info = state.get("supplier_result", {})
    supplier_name = supp_info.get("selected_supplier_name", "Unknown")
    supplier_price = supp_info.get("price", 0.0)
    
    risk_info = state.get("risk_result", {})
    risk_level = risk_info.get("risk_level", "Unknown")
    
    logistics_info = state.get("logistics_result", {})
    route_name = logistics_info.get("recommended_route_name", "Unknown")
    
    result = run_procurement_agent(
        product_name=state["product_name"],
        quantity_to_order=quantity_to_order,
        supplier_name=supplier_name,
        supplier_price=supplier_price,
        risk_level=risk_level,
        route_name=route_name
    )
    return {"procurement_result": result}

def coordinator_node(state: GraphState):
    time.sleep(2)
    result = run_coordinator_agent(
        inventory_data=state.get("inventory_result", {}),
        supplier_data=state.get("supplier_result", {}),
        risk_data=state.get("risk_result", {}),
        logistics_data=state.get("logistics_result", {}),
        procurement_data=state.get("procurement_result", {})
    )
    return {"coordinator_result": result}

def build_workflow():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("Inventory", inventory_node)
    workflow.add_node("Supplier", supplier_node)
    workflow.add_node("Risk", risk_node)
    workflow.add_node("Logistics", logistics_node)
    workflow.add_node("Procurement", procurement_node)
    workflow.add_node("Coordinator", coordinator_node)
    
    workflow.set_entry_point("Inventory")
    workflow.add_edge("Inventory", "Supplier")
    workflow.add_edge("Supplier", "Risk")
    workflow.add_edge("Risk", "Logistics")
    workflow.add_edge("Logistics", "Procurement")
    workflow.add_edge("Procurement", "Coordinator")
    workflow.add_edge("Coordinator", END)
    
    return workflow.compile()
