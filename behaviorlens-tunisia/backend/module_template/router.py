"""
Template de module BehaviorLens Tunisia
=========================================
Copie ce dossier dans backend/modules/<ton_module>/
et remplace les TODO par ta logique métier.

Étapes:
  1. cp -r backend/module_template backend/modules/mon_module
  2. Remplir les TODO ci-dessous
  3. Dans backend/main.py, ajouter:
       from modules.mon_module.router import router as mon_router
       app.include_router(mon_router)
  4. Dans backend/seed.py, ajouter ton module dans MODULES[]
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models

# TODO: Changer le préfixe et le tag
MODULE_DOMAIN = "mon_module"          # TODO: identifiant unique (snake_case)
MODULE_PREFIX = "/api/mon_module"     # TODO: préfixe URL

router = APIRouter(prefix=MODULE_PREFIX, tags=[MODULE_DOMAIN])


def _get_module(db: Session):
    m = db.query(models.Module).filter(models.Module.domain == MODULE_DOMAIN).first()
    if not m:
        raise HTTPException(status_code=500, detail=f"Module {MODULE_DOMAIN} not seeded")
    return m


# ── Endpoint de collecte ──────────────────────────────────────────────────────

@router.post("/collect")
def collect(
    # TODO: définir ton schéma dans backend/schemas.py et l'importer ici
    data: dict,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    """Reçoit des données depuis ta source externe."""
    m = _get_module(db)

    # TODO: Extraire les champs de `data` et créer les enregistrements
    # Exemple:
    # entry = models.TonModel(champ1=data["champ1"], ...)
    # db.add(entry)

    # Toujours logger dans behavioral_data pour le dashboard central
    db.add(models.BehavioralData(
        module_id=m.id,
        region_id=data.get("region_id"),
        metric_name=data.get("metric_name", "event"),   # TODO: adapter
        metric_value=data.get("metric_value"),
        raw_data=str(data),
    ))
    db.add(models.CollectionLog(module_id=m.id, status="success"))
    db.commit()

    return {"status": "success"}


# ── Endpoint de stats ─────────────────────────────────────────────────────────

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Stats agrégées pour le dashboard."""
    m = _get_module(db)
    total = (
        db.query(func.count(models.BehavioralData.id))
        .filter(models.BehavioralData.module_id == m.id)
        .scalar()
    )
    by_region = (
        db.query(models.Region.name, func.count(models.BehavioralData.id).label("count"))
        .join(models.BehavioralData, models.BehavioralData.region_id == models.Region.id)
        .filter(models.BehavioralData.module_id == m.id)
        .group_by(models.Region.name)
        .all()
    )

    return {
        "total_records": total,
        "by_region": [{"region": r.name, "count": r.count} for r in by_region],
        # TODO: ajouter tes stats spécifiques ici
    }
