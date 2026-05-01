from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from database import get_db
from auth import get_current_user
import models, schemas
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/mood", tags=["Mood"])

MOOD_SCORES = {"tres_bien": 5, "bien": 4, "neutre": 3, "mal": 2, "tres_mal": 1}

def _get_module(db):
    m = db.query(models.Module).filter(models.Module.domain == "mood").first()
    return m

@router.post("/record")
def record_mood(data: schemas.MoodRecord, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    entry = models.MoodData(region_id=data.region_id, mood=data.mood, comment=data.comment, player_id=data.player_id)
    db.add(entry)
    if m:
        score = MOOD_SCORES.get(data.mood, 3)
        db.add(models.CollectionLog(module_id=m.id, status="success"))
        db.add(models.BehavioralData(module_id=m.id, region_id=data.region_id, metric_name="mood_score", metric_value=score))
    db.commit()
    db.refresh(entry)
    return {"status": "success", "id": entry.id}

@router.get("/map")
def get_mood_map(db: Session = Depends(get_db), _=Depends(get_current_user)):
    mood_score_expr = case(
        (models.MoodData.mood == "tres_bien", 5),
        (models.MoodData.mood == "bien", 4),
        (models.MoodData.mood == "neutre", 3),
        (models.MoodData.mood == "mal", 2),
        else_=1
    )
    data = (
        db.query(models.Region.name, models.Region.latitude, models.Region.longitude,
                 func.count(models.MoodData.id).label("count"),
                 func.avg(mood_score_expr).label("avg_mood"))
        .join(models.MoodData, models.MoodData.region_id == models.Region.id)
        .group_by(models.Region.id, models.Region.name, models.Region.latitude, models.Region.longitude)
        .all()
    )
    return [{"region": r.name, "latitude": r.latitude, "longitude": r.longitude, "avg_mood": float(r.avg_mood or 3), "count": r.count} for r in data]

@router.get("/trends")
def get_mood_trends(days: int = 30, db: Session = Depends(get_db), _=Depends(get_current_user)):
    since = datetime.utcnow() - timedelta(days=days)
    data = (
        db.query(func.date(models.MoodData.recorded_at).label("date"), func.count(models.MoodData.id).label("count"))
        .filter(models.MoodData.recorded_at >= since)
        .group_by(func.date(models.MoodData.recorded_at))
        .order_by("date").all()
    )
    return [{"date": str(r.date), "avg_mood": 3.0, "count": r.count} for r in data]

@router.get("/by-region")
def get_mood_by_region(db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = (
        db.query(models.Region.name, models.MoodData.mood, func.count(models.MoodData.id).label("count"))
        .join(models.Region, models.MoodData.region_id == models.Region.id)
        .group_by(models.Region.name, models.MoodData.mood).all()
    )
    result = {}
    for row in data:
        if row.name not in result:
            result[row.name] = []
        result[row.name].append({"mood": row.mood, "count": row.count, "avg_score": MOOD_SCORES.get(row.mood, 3)})
    return result

@router.get("/stats")
def get_mood_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total = db.query(func.count(models.MoodData.id)).scalar()
    by_label = (
        db.query(models.MoodData.mood, func.count(models.MoodData.id).label("count"))
        .group_by(models.MoodData.mood).order_by(desc("count")).all()
    )
    recent = db.query(models.MoodData).order_by(desc(models.MoodData.recorded_at)).limit(10).all()
    avg_global = sum(MOOD_SCORES.get(r.mood, 3) * r.count for r in by_label) / max(total, 1) if total else 0
    return {
        "total_records": total,
        "global_avg_mood": round(avg_global, 2),
        "by_mood_label": [{"label": r.mood, "count": r.count} for r in by_label],
        "recent": [{"id": r.id, "mood_score": MOOD_SCORES.get(r.mood, 3), "mood_label": r.mood, "region_id": r.region_id, "created_at": str(r.recorded_at)} for r in recent]
    }
