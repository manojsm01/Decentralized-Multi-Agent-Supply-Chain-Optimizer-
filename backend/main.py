from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database.database import engine, get_db, Base
from backend.database import crud
from backend.models import schemas
from backend.services.optimization import run_optimization

app = FastAPI(title="AI Multi-Agent Supply Chain Optimizer")

@app.get("/")
def read_root():
    return {"status": "online", "message": "Supply Chain Optimizer API is running. Access /docs for Swagger UI."}

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    crud.init_db(db)

@app.post("/optimize", response_model=schemas.OptimizationResponse)
def optimize_supply_chain(request: schemas.OptimizationRequest, db: Session = Depends(get_db)):
    try:
        return run_optimization(db, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[schemas.ProcurementHistorySchema])
def get_history(db: Session = Depends(get_db)):
    return crud.get_procurement_history(db)

@app.get("/api/orders", response_model=List[schemas.OrderSchema])
def api_get_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)

@app.put("/api/orders/{order_id}/status", response_model=schemas.OrderSchema)
def api_update_order_status(order_id: str, request: schemas.OrderStatusUpdateRequest, db: Session = Depends(get_db)):
    updated_order = crud.update_order_status(db, order_id, request.status)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order

@app.get("/suppliers", response_model=List[schemas.SupplierSchema])
def get_suppliers(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)

@app.get("/routes", response_model=List[schemas.RouteSchema])
def get_routes(db: Session = Depends(get_db)):
    return crud.get_routes(db)

@app.get("/inventory", response_model=List[schemas.InventorySchema])
def get_inventory(db: Session = Depends(get_db)):
    return crud.get_all_inventory(db)

import pandas as pd
import io
from fastapi import UploadFile, File

@app.post("/upload/suppliers")
async def upload_suppliers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        crud.insert_suppliers_from_df(db, df)
        return {"message": f"Successfully uploaded/upserted {len(df)} suppliers"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

@app.post("/upload/routes")
async def upload_routes(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        crud.insert_routes_from_df(db, df)
        return {"message": f"Successfully uploaded/upserted {len(df)} routes"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

@app.post("/upload/inventory")
async def upload_inventory(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        crud.insert_inventory_from_df(db, df)
        return {"message": f"Successfully uploaded/upserted {len(df)} inventory items"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

from backend.agents.inventory import run_inventory_agent
from backend.agents.supplier import run_supplier_agent
from backend.agents.risk import run_risk_agent
from backend.agents.logistics import run_logistics_agent
from backend.agents.procurement import run_procurement_agent
from backend.agents.forecast import run_forecast_agent
import json

@app.post("/api/forecast", response_model=schemas.ForecastResponse)
def api_forecast(request: schemas.ForecastRequest, db: Session = Depends(get_db)):
    res = run_forecast_agent(request.product_name, request.quantity)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Forecast", rec)
    return res

@app.post("/api/suppliers/recommend", response_model=schemas.SupplierResponse)
def api_suppliers_recommend(request: schemas.SupplierRequest, db: Session = Depends(get_db)):
    suppliers = crud.get_suppliers(db)
    suppliers_data = [{"name": s.name, "price": s.price, "delivery_days": s.delivery_days, "rating": s.rating} for s in suppliers][:10]
    res = run_supplier_agent(suppliers_data, request.required_delivery_days)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Supplier", rec)
    return res

@app.post("/api/inventory/analyze", response_model=schemas.InventoryResponse)
def api_inventory_analyze(request: schemas.InventoryRequest, db: Session = Depends(get_db)):
    res = run_inventory_agent(request.product_name, request.required_quantity, request.current_stock)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Inventory", rec)
    return res

@app.post("/api/routes/optimize", response_model=schemas.RouteResponse)
def api_routes_optimize(request: schemas.RouteRequest, db: Session = Depends(get_db)):
    routes = crud.get_routes(db)
    routes_data = [{"name": r.name, "distance_km": r.distance_km} for r in routes][:10]
    res = run_logistics_agent(routes_data, request.destination)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Route", rec)
    return res

@app.post("/api/risk/analyze", response_model=schemas.RiskResponse)
def api_risk_analyze(request: schemas.RiskRequest, db: Session = Depends(get_db)):
    res = run_risk_agent(request.supplier_name, request.delivery_days, request.required_delivery_days)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Risk", rec)
    return res

@app.post("/api/procurement/generate", response_model=schemas.ProcurementResponse)
def api_procurement_generate(request: schemas.ProcurementRequest, db: Session = Depends(get_db)):
    res = run_procurement_agent(request.product_name, request.quantity_to_order, request.supplier_name, request.supplier_price, request.risk_level, request.route_name)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Procurement", rec)
    return res

@app.get("/api/recommendations", response_model=List[schemas.RecommendationHistorySchema])
def get_recommendations(db: Session = Depends(get_db)):
    return crud.get_recommendation_history(db)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "agents": {
            "forecast": "active",
            "inventory": "active",
            "procurement": "active",
            "supplier": "active",
            "risk": "active",
            "route": "active"
        },
        "database": "active"
    }
