from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/api/ivr", tags=["IVR"])

def _get_module(db):
    m = db.query(models.Module).filter(models.Module.domain == "ivr").first()
    if not m:
        raise HTTPException(status_code=500, detail="Module ivr not seeded")
    return m

@router.post("/campaign")
def create_campaign(data: schemas.IVRCampaignCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = models.IVRCampaign(
        name=data.name, question=data.question,
        option_1=data.option_1, option_2=data.option_2,
        option_3=data.option_3, option_4=data.option_4,
        region_id=data.region_id, target_age=data.target_age
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return {"status": "success", "campaign_id": campaign.id}

@router.post("/response")
def record_response(data: schemas.IVRResponseCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    response = models.IVRResponse(
        campaign_id=data.campaign_id, phone=data.phone,
        response=data.response, region_id=data.region_id, duration_sec=data.duration_sec
    )
    db.add(response)
    db.add(models.CollectionLog(module_id=m.id, status="success"))
    db.add(models.BehavioralData(module_id=m.id, region_id=data.region_id, metric_name="ivr_response"))
    db.commit()
    db.refresh(response)
    return {"status": "success", "id": response.id}

@router.get("/results/{campaign_id}")
def get_results(campaign_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = db.query(models.IVRCampaign).filter(models.IVRCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    responses = db.query(models.IVRResponse).filter(models.IVRResponse.campaign_id == campaign_id).all()
    return {
        "campaign": {"id": campaign.id, "name": campaign.name, "question": campaign.question},
        "total_responses": len(responses),
        "responses": [{"id": r.id, "phone": r.phone, "response": r.response, "duration_sec": r.duration_sec} for r in responses]
    }

@router.get("/stats")
def get_ivr_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_campaigns = db.query(func.count(models.IVRCampaign.id)).scalar()
    total_responses = db.query(func.count(models.IVRResponse.id)).scalar()
    avg_duration = db.query(func.avg(models.IVRResponse.duration_sec)).scalar()
    by_region = (
        db.query(models.Region.name, func.count(models.IVRResponse.id).label("count"))
        .join(models.IVRResponse, models.IVRResponse.region_id == models.Region.id)
        .group_by(models.Region.name).all()
    )
    by_response = (
        db.query(models.IVRResponse.response, func.count(models.IVRResponse.id).label("count"))
        .group_by(models.IVRResponse.response).all()
    )
    return {
        "total_campaigns": total_campaigns,
        "total_responses": total_responses,
        "avg_duration_seconds": float(avg_duration or 0),
        "by_region": [{"region": r.name, "count": r.count} for r in by_region],
        "by_age_group": [{"age_group": r.response, "count": r.count} for r in by_response]
    }
