from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from auth import get_current_user
import models, schemas
import json

router = APIRouter(prefix="/api/game", tags=["Gamification"])

def _get_module(db):
    m = db.query(models.Module).filter(models.Module.domain == "gamification").first()
    if not m:
        raise HTTPException(status_code=500, detail="Module gamification not seeded")
    return m

@router.post("/play")
def submit_game_play(data: schemas.GamePlay, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = _get_module(db)
    game = db.query(models.Game).filter(models.Game.id == data.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    player = db.query(models.Player).filter(models.Player.id == data.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    session = models.GameSession(player_id=data.player_id, game_id=data.game_id, answers=data.answers, points_earned=game.points_reward)
    db.add(session)
    player.points_total += game.points_reward
    db.add(models.CollectionLog(module_id=m.id, status="success"))
    db.add(models.BehavioralData(module_id=m.id, region_id=player.region_id, metric_name="game_session", metric_value=game.points_reward))
    db.commit()
    db.refresh(session)
    return {"status": "success", "session_id": session.id, "points_earned": game.points_reward, "total_points": player.points_total}

@router.get("/list")
def list_games(db: Session = Depends(get_db), _=Depends(get_current_user)):
    games = db.query(models.Game).filter(models.Game.is_active == True).all()
    return [{"id": g.id, "name": g.name, "description": g.description, "points": g.points_reward} for g in games]

@router.post("/reward")
def convert_reward(data: schemas.RewardConvert, db: Session = Depends(get_db), _=Depends(get_current_user)):
    player = db.query(models.Player).filter(models.Player.id == data.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if player.points_total < data.points:
        raise HTTPException(status_code=400, detail="Insufficient points")
    player.points_total -= data.points
    db.commit()
    return {"status": "success", "reward_type": data.reward_type, "points_used": data.points, "remaining_points": player.points_total}

@router.get("/leaderboard")
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db), _=Depends(get_current_user)):
    players = (
        db.query(models.Player, models.Region.name.label("region_name"))
        .join(models.Region, models.Player.region_id == models.Region.id, isouter=True)
        .order_by(desc(models.Player.points_total))
        .limit(limit).all()
    )
    return [{"rank": i+1, "nickname": p.Player.nickname, "region": p.region_name, "points": p.Player.points_total} for i, p in enumerate(players)]

@router.post("/challenge")
def create_challenge(title: str, description: str, region_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    challenge = models.PhotoChallenge(title=title, description=description, points=50)
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return {"status": "success", "challenge_id": challenge.id}

@router.get("/stats")
def get_gamification_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_players = db.query(func.count(models.Player.id)).scalar()
    total_sessions = db.query(func.count(models.GameSession.id)).scalar()
    total_points = db.query(func.sum(models.Player.points_total)).scalar()
    by_game = (
        db.query(models.Game.name, func.count(models.GameSession.id).label("plays"))
        .join(models.GameSession, models.GameSession.game_id == models.Game.id)
        .group_by(models.Game.name).all()
    )
    by_region = (
        db.query(models.Region.name, func.count(models.Player.id).label("players"))
        .join(models.Player, models.Player.region_id == models.Region.id)
        .group_by(models.Region.name).all()
    )
    return {
        "total_players": total_players,
        "total_sessions": total_sessions,
        "total_points_distributed": int(total_points or 0),
        "by_game": [{"game": r.name, "plays": r.plays} for r in by_game],
        "by_region": [{"region": r.name, "players": r.players} for r in by_region]
    }
