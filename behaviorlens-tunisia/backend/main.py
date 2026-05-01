from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import timedelta
import models, schemas
from database import engine, get_db, Base
from auth import verify_password, get_password_hash, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

from modules.social_media.router import router as social_router
from modules.terrain.router import router as terrain_router
from modules.ivr.router import router as ivr_router
from modules.commerce.router import router as commerce_router
from modules.gamification.router import router as gamification_router
from modules.open_data.router import router as opendata_router
from modules.mood.router import router as mood_router
from modules.photo.router import router as photo_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BehaviorLens Tunisia API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(social_router)
app.include_router(terrain_router)
app.include_router(ivr_router)
app.include_router(commerce_router)
app.include_router(gamification_router)
app.include_router(opendata_router)
app.include_router(mood_router)
app.include_router(photo_router)

MODULE_LABELS = {
    "social_media": "Social Media", "terrain": "Terrain", "ivr": "IVR Téléphone",
    "commerce": "Commerce POS", "gamification": "Gamification", "open_data": "Open Data",
    "mood": "Baromètre Humeur", "photo": "Photo Challenge"
}

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/auth/register", response_model=schemas.Token)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    user = models.User(email=data.email, password=get_password_hash(data.password), role=data.role or "viewer")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "full_name": user.email, "role": user.role}}

@app.post("/api/auth/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    token = create_access_token({"sub": user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "full_name": user.email, "role": user.role}}

# ── Core Framework ────────────────────────────────────────────────────────────

@app.post("/api/collect")
def collect(data: schemas.CollectRequest, db: Session = Depends(get_db), _=Depends(get_current_user)):
    module = db.query(models.Module).filter(models.Module.domain == data.module_domain).first()
    if not module:
        raise HTTPException(status_code=404, detail=f"Module '{data.module_domain}' non trouvé")
    entry = models.BehavioralData(
        module_id=module.id, region_id=data.region_id,
        metric_name=data.metric_name, metric_value=data.metric_value,
        raw_data=data.raw_data, age_group=data.age_group, gender=data.gender
    )
    db.add(entry)
    db.add(models.CollectionLog(module_id=module.id, status="success"))
    db.commit()
    db.refresh(entry)
    return {"status": "success", "id": entry.id, "module": data.module_domain}

@app.get("/api/stats")
def global_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_records = db.query(func.count(models.BehavioralData.id)).scalar()
    active_modules = db.query(func.count(models.Module.id)).filter(models.Module.is_active == True).scalar()
    regions_covered = db.query(func.count(func.distinct(models.BehavioralData.region_id))).scalar()
    active_players = db.query(func.count(models.Player.id)).scalar()
    recent_activity = db.query(models.BehavioralData, models.Module.domain).join(models.Module).order_by(desc(models.BehavioralData.collected_at)).limit(10).all()
    return {
        "total_records": total_records,
        "active_modules": active_modules,
        "regions_covered": regions_covered,
        "active_players": active_players,
        "recent_activity": [
            {"id": r.BehavioralData.id, "module": r.domain, "type": r.BehavioralData.metric_name,
             "region_id": r.BehavioralData.region_id, "created_at": str(r.BehavioralData.collected_at)}
            for r in recent_activity
        ]
    }

@app.get("/api/stats/by-region")
def stats_by_region(db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = (
        db.query(models.Region.name, models.Region.latitude, models.Region.longitude, func.count(models.BehavioralData.id).label("count"))
        .join(models.BehavioralData, models.BehavioralData.region_id == models.Region.id, isouter=True)
        .group_by(models.Region.id, models.Region.name, models.Region.latitude, models.Region.longitude)
        .all()
    )
    return [{"region": r.name, "latitude": r.latitude, "longitude": r.longitude, "count": r.count or 0} for r in data]

@app.get("/api/stats/by-module")
def stats_by_module(db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = (
        db.query(models.Module.domain, models.Module.name, func.count(models.BehavioralData.id).label("count"))
        .join(models.BehavioralData, models.BehavioralData.module_id == models.Module.id, isouter=True)
        .group_by(models.Module.id, models.Module.domain, models.Module.name)
        .all()
    )
    return [{"module": r.domain, "label": MODULE_LABELS.get(r.domain, r.name), "count": r.count or 0} for r in data]

@app.get("/api/stats/by-age")
def stats_by_age(db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = (
        db.query(models.BehavioralData.age_group, func.count(models.BehavioralData.id).label("count"))
        .filter(models.BehavioralData.age_group.isnot(None))
        .group_by(models.BehavioralData.age_group)
        .order_by(desc("count")).all()
    )
    return [{"age_group": r.age_group, "count": r.count} for r in data]

@app.get("/api/modules")
def list_modules(db: Session = Depends(get_db), _=Depends(get_current_user)):
    modules = db.query(models.Module).filter(models.Module.is_active == True).all()
    return [{"id": m.id, "name": m.name, "code": m.domain, "description": m.description} for m in modules]

@app.post("/api/modules/register")
def register_module(data: schemas.ModuleRegister, db: Session = Depends(get_db), _=Depends(get_current_user)):
    existing = db.query(models.Module).filter(models.Module.domain == data.domain).first()
    if existing:
        existing.name = data.name
        existing.description = data.description
        existing.is_active = True
        db.commit()
        return {"status": "updated", "id": existing.id}
    module = models.Module(name=data.name, domain=data.domain, description=data.description, api_key=data.api_key)
    db.add(module)
    db.commit()
    db.refresh(module)
    return {"status": "registered", "id": module.id}

@app.get("/api/stats/timeline")
def stats_timeline(days: int = 30, db: Session = Depends(get_db), _=Depends(get_current_user)):
    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=days)
    data = (
        db.query(func.date(models.BehavioralData.collected_at).label("date"),
                 func.count(models.BehavioralData.id).label("count"))
        .filter(models.BehavioralData.collected_at >= since)
        .group_by(func.date(models.BehavioralData.collected_at))
        .order_by("date").all()
    )
    return [{"date": str(r.date), "count": r.count} for r in data]

@app.get("/")
def root():
    return {"message": "BehaviorLens Tunisia API", "version": "1.0.0", "docs": "/docs"}
