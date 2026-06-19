from sqlalchemy.orm import Session
from backend.models.schemas import OptimizationRequest, OptimizationResponse
from backend.database.crud import get_inventory, get_suppliers, get_routes, create_procurement_history
from backend.workflow.graph import build_workflow

app_workflow = build_workflow()

def run_optimization(db: Session, request: OptimizationRequest) -> OptimizationResponse:
    # 1. Fetch data from DB
    inv = get_inventory(db, request.product_name)
    current_stock = inv.stock_level if inv else 0
    
    suppliers = get_suppliers(db)
    # Limit to top 10 suppliers to prevent massive LLM payloads
    suppliers_data = [{"name": s.name, "price": s.price, "delivery_days": s.delivery_days, "rating": s.rating} for s in suppliers][:10]
    
    routes = get_routes(db)
    # Limit to top 10 routes
    routes_data = [{"name": r.name, "distance_km": r.distance_km} for r in routes][:10]
    
    # 2. Prepare State
    initial_state = {
        "product_name": request.product_name,
        "quantity": request.quantity,
        "destination": request.destination,
        "required_delivery_days": request.required_delivery_days,
        "current_stock": current_stock,
        "suppliers_data": suppliers_data,
        "routes_data": routes_data
    }
    
    # 3. Run Workflow
    final_state = app_workflow.invoke(initial_state)
    
    # 4. Extract Results
    inv_res = final_state.get("inventory_result", {})
    supp_res = final_state.get("supplier_result", {})
    risk_res = final_state.get("risk_result", {})
    log_res = final_state.get("logistics_result", {})
    proc_res = final_state.get("procurement_result", {})
    coord_res = final_state.get("coordinator_result", {})
    
    # 5. Save History
    history_data = {
        "product_name": request.product_name,
        "quantity": inv_res.get("quantity_to_order", request.quantity),
        "selected_supplier": supp_res.get("selected_supplier_name", "Unknown"),
        "total_cost": proc_res.get("total_cost", 0.0),
        "status": proc_res.get("recommendation", "Unknown")
    }
    create_procurement_history(db, history_data)
    
    # 6. Return Response
    return OptimizationResponse(
        product_name=request.product_name,
        requested_quantity=request.quantity,
        inventory_analysis=inv_res.get("analysis", "No inventory analysis"),
        selected_supplier=supp_res.get("selected_supplier_name", "Unknown"),
        risk_level=risk_res.get("risk_level", "Unknown"),
        recommended_route=log_res.get("recommended_route_name", "Unknown"),
        total_cost=proc_res.get("total_cost", 0.0),
        procurement_summary=coord_res.get("procurement_summary", "No summary provided.")
    )
