from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/terrain", tags=["Terrain"])

def _get_module(db):
    m = db.query(models.Module).filter(models.Module.domain == "terrain").first()
    if not m:
        raise HTTPException(status_code=500, detail="Module terrain not seeded")
    return m

@router.post("/submit")
def submit_terrain_data(data: schemas.TerrainSubmit, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    entry = models.TerrainData(agent_id=data.agent_id, region_id=data.region_id, location=data.location, answers=data.answers, synced=True)
    db.add(entry)
    db.add(models.CollectionLog(module_id=m.id, status="success"))
    db.add(models.BehavioralData(module_id=m.id, region_id=data.region_id, metric_name="field_survey"))
    db.commit()
    db.refresh(entry)
    return {"status": "success", "id": entry.id}

@router.get("/agents")
def get_agents(db: Session = Depends(get_db), _=Depends(get_current_user)):
    agents = db.query(models.TerrainAgent).filter(models.TerrainAgent.is_active == True).all()
    return [
        {"id": a.id, "user_id": a.user_id, "zone": a.zone, "region": a.region.name if a.region else None}
        for a in agents
    ]

@router.get("/sync")
def sync_offline_data(db: Session = Depends(get_db), _=Depends(get_current_user)):
    unsynced = db.query(models.TerrainData).filter(models.TerrainData.synced == False).all()
    for r in unsynced:
        r.synced = True
    db.commit()
    return {"status": "synced", "records_synced": len(unsynced)}

@router.get("/stats")
def get_terrain_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total = db.query(func.count(models.TerrainData.id)).scalar()
    agents_count = db.query(func.count(models.TerrainAgent.id)).filter(models.TerrainAgent.is_active == True).scalar()
    by_region = (
        db.query(models.Region.name, func.count(models.TerrainData.id).label("count"))
        .join(models.TerrainData, models.TerrainData.region_id == models.Region.id)
        .group_by(models.Region.name).all()
    )
    recent = db.query(models.TerrainData).order_by(desc(models.TerrainData.captured_at)).limit(10).all()
    return {
        "total_submissions": total,
        "active_agents": agents_count,
        "by_region": [{"region": r.name, "count": r.count} for r in by_region],
        "by_age_group": [],
        "recent": [{"id": r.id, "agent_id": r.agent_id, "region_id": r.region_id, "created_at": str(r.captured_at)} for r in recent]
    }
