from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/opendata", tags=["Open Data"])

GOV_SOURCES = {
    "ins": {"population_2024": 12000000, "growth_rate": 1.1, "urban_rate": 69.3, "gdp_per_capita": 3800},
    "anme": {"energy_consumption_gwh": 15420, "renewable_percent": 4.2, "oil_import_mtoe": 3.1},
    "ministere_sante": {"hospitals": 214, "doctors_per_1000": 1.3, "infant_mortality": 15.2},
}

def _get_module(db):
    m = db.query(models.Module).filter(models.Module.domain == "open_data").first()
    return m

@router.get("/fetch")
def fetch_gov_data(source: str = "ins", db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = GOV_SOURCES.get(source, {"error": "Source not configured"})
    m = _get_module(db)
    if m:
        db.add(models.CollectionLog(module_id=m.id, status="success"))
        db.add(models.BehavioralData(module_id=m.id, metric_name=f"opendata_{source}", raw_data=str(data)))
    db.commit()
    return {"source": source, "data": data, "status": "success"}

@router.get("/stats")
def get_opendata_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    total = 0
    logs = []
    if m:
        total = db.query(func.count(models.BehavioralData.id)).filter(models.BehavioralData.module_id == m.id).scalar()
        logs_q = (
            db.query(models.CollectionLog)
            .filter(models.CollectionLog.module_id == m.id)
            .order_by(desc(models.CollectionLog.created_at))
            .limit(10).all()
        )
        logs = [{"message": f"Collection log #{l.id}", "status": l.status, "created_at": str(l.created_at)} for l in logs_q]
    return {
        "total_datasets": total,
        "available_sources": list(GOV_SOURCES.keys()),
        "recent_imports": logs
    }

@router.post("/import")
def import_dataset(data: schemas.DatasetImport, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    imported = 0
    for record in data.data:
        if m:
            db.add(models.BehavioralData(module_id=m.id, region_id=data.region_id, metric_name=f"import_{data.dataset_name}", raw_data=str(record)))
        imported += 1
    if m:
        db.add(models.CollectionLog(module_id=m.id, records_count=imported, status="success"))
    db.commit()
    return {"status": "success", "records_imported": imported, "source": data.source}
