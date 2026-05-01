from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/social", tags=["Social Media"])

def _get_module(db: Session):
    m = db.query(models.Module).filter(models.Module.domain == "social_media").first()
    if not m:
        raise HTTPException(status_code=500, detail="Module social_media not seeded")
    return m

@router.post("/collect")
def collect_social_data(data: schemas.SocialMediaCollect, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    entry = models.SocialMediaData(
        platform=data.platform, hashtag=data.hashtag,
        sentiment=data.sentiment, mentions=data.mentions, region_id=data.region_id
    )
    db.add(entry)
    db.add(models.CollectionLog(module_id=m.id, status="success"))
    db.add(models.BehavioralData(module_id=m.id, region_id=data.region_id, metric_name="social_post", metric_value=data.mentions))
    db.commit()
    db.refresh(entry)
    return {"status": "success", "id": entry.id}

@router.get("/trends")
def get_trends(limit: int = 10, db: Session = Depends(get_db), _=Depends(get_current_user)):
    trends = (
        db.query(models.SocialMediaData.hashtag, func.count(models.SocialMediaData.id).label("count"))
        .filter(models.SocialMediaData.hashtag.isnot(None))
        .group_by(models.SocialMediaData.hashtag)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [{"hashtag": t.hashtag, "count": t.count} for t in trends]

@router.get("/sentiment")
def get_sentiment_by_region(db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = (
        db.query(models.Region.name, models.SocialMediaData.sentiment, func.count(models.SocialMediaData.id).label("count"))
        .join(models.Region, models.SocialMediaData.region_id == models.Region.id, isouter=True)
        .group_by(models.Region.name, models.SocialMediaData.sentiment)
        .all()
    )
    result = {}
    for row in data:
        region = row.name or "Inconnu"
        if region not in result:
            result[region] = {}
        result[region][row.sentiment or "neutre"] = row.count
    return result

@router.get("/stats")
def get_social_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total = db.query(func.count(models.SocialMediaData.id)).scalar()
    by_platform = (
        db.query(models.SocialMediaData.platform, func.count(models.SocialMediaData.id).label("count"))
        .group_by(models.SocialMediaData.platform).all()
    )
    by_sentiment = (
        db.query(models.SocialMediaData.sentiment, func.count(models.SocialMediaData.id).label("count"))
        .group_by(models.SocialMediaData.sentiment).all()
    )
    recent = db.query(models.SocialMediaData).order_by(desc(models.SocialMediaData.captured_at)).limit(10).all()
    return {
        "total_posts": total,
        "by_platform": [{"platform": r.platform, "count": r.count} for r in by_platform],
        "by_sentiment": [{"sentiment": r.sentiment, "count": r.count} for r in by_sentiment],
        "recent": [{"id": r.id, "platform": r.platform, "hashtag": r.hashtag, "sentiment": r.sentiment, "created_at": str(r.captured_at)} for r in recent]
    }
