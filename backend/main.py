import os
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "1"

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from backend.database.database import engine, get_db, Base
from backend.database import crud
from backend.models import schemas
from backend.services.optimization import run_optimization

from fastapi.security import OAuth2PasswordRequestForm
from backend import auth

app = FastAPI(title="AI Multi-Agent Supply Chain Optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"DEBUG: Login attempt for username: '{form_data.username}', password: '{form_data.password}'")
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user:
        print("DEBUG: User not found")
    elif not crud.verify_password(form_data.password, user.hashed_password):
        print("DEBUG: Password mismatch")
    
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/admin/users", response_model=schemas.UserResponse)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin_user = Depends(auth.get_current_admin_user)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user.model_dump())

@app.get("/api/admin/users", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db), admin_user = Depends(auth.get_current_admin_user)):
    return crud.get_all_users(db)

@app.put("/api/admin/users/{username}", response_model=schemas.UserResponse)
def update_existing_user(username: str, update_data: schemas.UserUpdate, db: Session = Depends(get_db), admin_user = Depends(auth.get_current_admin_user)):
    user = crud.update_user(db, username, update_data.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/api/admin/users/{username}")
def delete_existing_user(username: str, db: Session = Depends(get_db), admin_user = Depends(auth.get_current_admin_user)):
    if username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete root admin")
    success = crud.delete_user(db, username)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}

@app.get("/api/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user = Depends(auth.get_current_user)):
    return current_user

@app.put("/api/users/me", response_model=schemas.UserProfileUpdateResponse)
def update_users_me(update_data: schemas.UserProfileUpdate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    try:
        updated_user = crud.update_user_profile(
            db, 
            current_username=current_user.username, 
            new_username=update_data.username, 
            new_password=update_data.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Generate new access token because the username (sub) might have changed!
    new_token = auth.create_access_token(data={"sub": updated_user.username})
    
    return {"user": updated_user, "access_token": new_token}

@app.get("/")
def read_root():
    return {"status": "online", "message": "Supply Chain Optimizer API is running. Access /docs for Swagger UI."}

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    crud.init_db(db)

@app.post("/optimize", response_model=schemas.OptimizationResponse)
def optimize_supply_chain(request: schemas.OptimizationRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    try:
        return run_optimization(db, request, current_user.organization)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[schemas.ProcurementHistorySchema])
def get_history(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    return crud.get_procurement_history(db, current_user.organization)

@app.get("/api/orders", response_model=List[schemas.OrderSchema])
def api_get_orders(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    return crud.get_orders(db, current_user.organization)

@app.post("/api/orders", response_model=schemas.OrderSchema)
def api_create_order(request: schemas.OrderCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    return crud.create_order(db, request.model_dump(), current_user.organization)

@app.put("/api/orders/{order_id}/status", response_model=schemas.OrderSchema)
def api_update_order_status(order_id: str, request: schemas.OrderStatusUpdateRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    updated_order = crud.update_order_status(db, order_id, request.status, current_user.organization)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order

@app.get("/suppliers", response_model=List[schemas.SupplierSchema])
def get_suppliers(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    return crud.get_suppliers(db, current_user.organization)

@app.get("/routes", response_model=List[schemas.RouteSchema])
def get_routes(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    return crud.get_routes(db, current_user.organization)

@app.get("/inventory", response_model=List[schemas.InventorySchema])
def get_inventory(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    return crud.get_all_inventory(db, current_user.organization)

import pandas as pd
import io
from fastapi import UploadFile, File

@app.post("/upload/suppliers")
async def upload_suppliers(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        crud.insert_suppliers_from_df(db, df, current_user.organization)
        return {"message": f"Successfully uploaded/upserted {len(df)} suppliers"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

@app.post("/upload/routes")
async def upload_routes(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        crud.insert_routes_from_df(db, df, current_user.organization)
        return {"message": f"Successfully uploaded/upserted {len(df)} routes"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")

@app.post("/upload/inventory")
async def upload_inventory(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        crud.insert_inventory_from_df(db, df, current_user.organization)
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
def api_forecast(request: schemas.ForecastRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    res = run_forecast_agent(request.product_name, request.quantity)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Forecast", rec, current_user.organization)
    return res

@app.post("/api/suppliers/recommend", response_model=schemas.SupplierResponse)
def api_suppliers_recommend(request: schemas.SupplierRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    suppliers = crud.get_suppliers(db, current_user.organization)
    suppliers_data = [{"name": s.name, "price": s.price, "delivery_days": s.delivery_days, "rating": s.rating} for s in suppliers][:10]
    res = run_supplier_agent(suppliers_data, request.required_delivery_days)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Supplier", rec, current_user.organization)
    return res

@app.post("/api/inventory/analyze", response_model=schemas.InventoryResponse)
def api_inventory_analyze(request: schemas.InventoryRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    res = run_inventory_agent(request.product_name, request.required_quantity, request.current_stock)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Inventory", rec, current_user.organization)
    return res

@app.post("/api/routes/optimize", response_model=schemas.RouteResponse)
def api_routes_optimize(request: schemas.RouteRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    routes = crud.get_routes(db, current_user.organization)
    routes_data = [{"name": r.name, "distance_km": r.distance_km} for r in routes][:10]
    res = run_logistics_agent(routes_data, request.destination)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Route", rec, current_user.organization)
    return res

@app.post("/api/risk/analyze", response_model=schemas.RiskResponse)
def api_risk_analyze(request: schemas.RiskRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    res = run_risk_agent(request.supplier_name, request.delivery_days, request.required_delivery_days)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Risk", rec, current_user.organization)
    return res

@app.post("/api/procurement/generate", response_model=schemas.ProcurementResponse)
def api_procurement_generate(request: schemas.ProcurementRequest, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    res = run_procurement_agent(request.product_name, request.quantity_to_order, request.supplier_name, request.supplier_price, request.risk_level, request.route_name)
    rec = json.dumps(res)
    crud.create_recommendation_history(db, "Procurement", rec, current_user.organization)
    return res

@app.get("/api/recommendations", response_model=List[schemas.RecommendationHistorySchema])
def get_recommendations(db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    return crud.get_recommendation_history(db, current_user.organization)

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
