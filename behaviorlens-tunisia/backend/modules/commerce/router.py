from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models, schemas
from datetime import date

router = APIRouter(prefix="/api/commerce", tags=["Commerce"])

def _get_module(db):
    m = db.query(models.Module).filter(models.Module.domain == "commerce").first()
    if not m:
        raise HTTPException(status_code=500, detail="Module commerce not seeded")
    return m

@router.post("/store")
def register_store(data: schemas.StoreCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    store = models.Store(name=data.name, type=data.type, region_id=data.region_id, address=data.address)
    db.add(store)
    db.commit()
    db.refresh(store)
    return {"status": "success", "store_id": store.id}

@router.post("/sale")
def submit_sale(data: schemas.SaleCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    store = db.query(models.Store).filter(models.Store.id == data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    sale = models.POSData(
        store_id=data.store_id, product_name=data.product_name,
        category=data.category, quantity=data.quantity,
        price_dt=data.price_dt, sold_at=date.fromisoformat(data.sold_at)
    )
    db.add(sale)
    db.add(models.CollectionLog(module_id=m.id, status="success"))
    db.add(models.BehavioralData(module_id=m.id, region_id=store.region_id, metric_name="pos_sale", metric_value=data.quantity * data.price_dt))
    db.commit()
    db.refresh(sale)
    return {"status": "success", "id": sale.id}

@router.get("/top-products")
def get_top_products(limit: int = 10, db: Session = Depends(get_db), _=Depends(get_current_user)):
    products = (
        db.query(models.POSData.product_name, models.POSData.category,
                 func.sum(models.POSData.quantity).label("total_qty"),
                 func.sum(models.POSData.quantity * models.POSData.price_dt).label("total_revenue"))
        .group_by(models.POSData.product_name, models.POSData.category)
        .order_by(desc("total_qty"))
        .limit(limit).all()
    )
    return [{"product": p.product_name, "category": p.category, "quantity": int(p.total_qty or 0), "revenue": float(p.total_revenue or 0)} for p in products]

@router.get("/by-region")
def get_sales_by_region(db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = (
        db.query(models.Region.name, func.count(models.POSData.id).label("transactions"),
                 func.sum(models.POSData.quantity * models.POSData.price_dt).label("revenue"))
        .join(models.Store, models.POSData.store_id == models.Store.id)
        .join(models.Region, models.Store.region_id == models.Region.id)
        .group_by(models.Region.name).all()
    )
    return [{"region": r.name, "transactions": r.transactions, "revenue": float(r.revenue or 0)} for r in data]

@router.get("/stats")
def get_commerce_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_stores = db.query(func.count(models.Store.id)).scalar()
    total_sales = db.query(func.count(models.POSData.id)).scalar()
    total_revenue = db.query(func.sum(models.POSData.quantity * models.POSData.price_dt)).scalar()
    by_store_type = (
        db.query(models.Store.type, func.count(models.POSData.id).label("sales"))
        .join(models.POSData, models.POSData.store_id == models.Store.id)
        .group_by(models.Store.type).all()
    )
    recent = db.query(models.POSData).order_by(desc(models.POSData.created_at)).limit(10).all()
    return {
        "total_stores": total_stores,
        "total_sales": total_sales,
        "total_revenue": float(total_revenue or 0),
        "by_store_type": [{"type": r.type, "sales": r.sales} for r in by_store_type],
        "recent": [{"id": r.id, "product": r.product_name, "quantity": r.quantity, "total": float((r.quantity or 0) * (r.price_dt or 0)), "created_at": str(r.created_at)} for r in recent]
    }
