from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/photo", tags=["Photo"])

def _get_module(db):
    m = db.query(models.Module).filter(models.Module.domain == "photo").first()
    return m

@router.post("/challenge")
def create_challenge(title: str, description: str, points: int = 30, db: Session = Depends(get_db), _=Depends(get_current_user)):
    challenge = models.PhotoChallenge(title=title, description=description, points=points)
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return {"status": "success", "challenge_id": challenge.id}

@router.post("/submit")
def submit_photo_json(data: schemas.PhotoSubmit, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    challenge = db.query(models.PhotoChallenge).filter(models.PhotoChallenge.id == data.challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    submission = models.PhotoSubmission(
        challenge_id=data.challenge_id, player_id=data.player_id,
        region_id=data.region_id, photo_url=data.photo_url, points_given=challenge.points
    )
    db.add(submission)
    if m:
        db.add(models.CollectionLog(module_id=m.id, status="success"))
        db.add(models.BehavioralData(module_id=m.id, region_id=data.region_id, metric_name="photo_submission", metric_value=challenge.points))
    db.commit()
    db.refresh(submission)
    return {"status": "success", "id": submission.id}

@router.post("/submit-json")
def submit_photo_alias(data: schemas.PhotoSubmit, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return submit_photo_json(data, db, _)

@router.get("/challenges")
def get_challenges(db: Session = Depends(get_db), _=Depends(get_current_user)):
    challenges = db.query(models.PhotoChallenge).filter(models.PhotoChallenge.is_active == True).all()
    return [
        {
            "id": c.id, "title": c.title, "description": c.description, "points": c.points, "theme": "photo",
            "region": None,
            "submissions": db.query(func.count(models.PhotoSubmission.id)).filter(models.PhotoSubmission.challenge_id == c.id).scalar()
        } for c in challenges
    ]

@router.get("/stats")
def get_photo_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_challenges = db.query(func.count(models.PhotoChallenge.id)).scalar()
    total_submissions = db.query(func.count(models.PhotoSubmission.id)).scalar()
    by_region = (
        db.query(models.Region.name, func.count(models.PhotoSubmission.id).label("count"))
        .join(models.PhotoSubmission, models.PhotoSubmission.region_id == models.Region.id)
        .group_by(models.Region.name).all()
    )
    by_challenge = (
        db.query(models.PhotoChallenge.title, func.count(models.PhotoSubmission.id).label("count"))
        .join(models.PhotoSubmission, models.PhotoSubmission.challenge_id == models.PhotoChallenge.id)
        .group_by(models.PhotoChallenge.title).all()
    )
    recent = db.query(models.PhotoSubmission).order_by(desc(models.PhotoSubmission.submitted_at)).limit(10).all()
    return {
        "total_challenges": total_challenges,
        "total_submissions": total_submissions,
        "by_region": [{"region": r.name, "count": r.count} for r in by_region],
        "by_challenge": [{"challenge": r.title, "count": r.count} for r in by_challenge],
        "recent": [{"id": r.id, "challenge_id": r.challenge_id, "region_id": r.region_id, "created_at": str(r.submitted_at)} for r in recent]
    }
